"""
认证接口：登录、注册、刷新Token、登出
"""
from fastapi import APIRouter, Depends, Request, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import timedelta
import logging
import random
import string
from pydantic import BaseModel, EmailStr

from app.core.database import get_db
from app.core.security import (
    verify_password, hash_password, create_access_token,
    create_refresh_token, decode_token, encrypt_field
)
from app.core.redis_client import redis_client
from app.core.config import settings
from app.core.response import success, error, Unauthorized, AppException
from app.core.deps import get_current_user
from app.models.models import User, Enterprise, UserRole, UserStatus, AuditStatus, OperationLog
from app.services.notification_service import NotificationService
from app.services.log_service import LogService

router = APIRouter()
logger = logging.getLogger(__name__)


class LoginRequest(BaseModel):
    login_field: str  # 手机号或邮箱
    password: str
    captcha_token: str
    captcha_code: str


class RegisterEnterpriseRequest(BaseModel):
    credit_code: str
    enterprise_name: str
    legal_person: str
    legal_id_card: str
    business_license: str
    contact_phone: str
    email: EmailStr
    password: str
    real_name: str
    captcha_token: str
    captcha_code: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


@router.post("/login")
async def login(
    req: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    bg: BackgroundTasks = BackgroundTasks(),
):
    """用户登录"""
    # 验证图形验证码
    captcha_key = f"captcha:{req.captcha_token}"
    stored_code = await redis_client.get(captcha_key)
    if not stored_code or stored_code.lower() != req.captcha_code.lower():
        raise AppException(400, "验证码错误或已过期")
    await redis_client.delete(captcha_key)

    # 查找用户
    result = await db.execute(
        select(User).where(
            (User.email == req.login_field) | (User.username == req.login_field)
        )
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(req.password, user.password_hash):
        raise AppException(401, "账号或密码错误")

    if user.status == UserStatus.PENDING:
        raise AppException(403, "账号待审核，请等待管理员审核")
    if user.status == UserStatus.DISABLED:
        raise AppException(403, "账号已被禁用")

    # 生成 Token
    access_token = create_access_token({"sub": str(user.id), "role": user.role.value})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    # 存储 refresh token
    await redis_client.set(
        f"refresh_token:{user.id}",
        refresh_token,
        expire=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 86400
    )

    # 记录登录日志
    await LogService.log(
        db, user.id, "login",
        ip=request.client.host if request.client else "",
        user_agent=request.headers.get("user-agent", ""),
    )

    return success({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "real_name": user.real_name,
            "role": user.role.value,
            "enterprise_id": user.enterprise_id,
            "must_change_password": user.must_change_password,
            "language": user.language,
        }
    })


@router.post("/register")
async def register(
    req: RegisterEnterpriseRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """企业注册"""
    # 验证验证码
    captcha_key = f"captcha:{req.captcha_token}"
    stored_code = await redis_client.get(captcha_key)
    if not stored_code or stored_code.lower() != req.captcha_code.lower():
        raise AppException(400, "验证码错误或已过期")
    await redis_client.delete(captcha_key)

    # 检查邮箱是否已注册
    existing = await db.execute(select(User).where(User.email == req.email))
    if existing.scalar_one_or_none():
        raise AppException(400, "该邮箱已注册")

    # 检查企业信用代码是否已注册
    existing_ent = await db.execute(
        select(Enterprise).where(Enterprise.credit_code == req.credit_code)
    )
    enterprise = existing_ent.scalar_one_or_none()

    # 演示模式：审核状态直接通过
    audit_status = AuditStatus.APPROVED if settings.DEMO_MODE else AuditStatus.PENDING
    user_status = UserStatus.ACTIVE if settings.DEMO_MODE else UserStatus.PENDING

    if not enterprise:
        enterprise = Enterprise(
            credit_code=req.credit_code,
            name=req.enterprise_name,
            legal_person=req.legal_person,
            legal_id_card=encrypt_field(req.legal_id_card),
            business_license=req.business_license,
            contact_phone=encrypt_field(req.contact_phone),
            contact_email=req.email,
            audit_status=audit_status,
        )
        db.add(enterprise)
        await db.flush()

    # 创建企业管理员用户
    username = f"ent_{req.credit_code[-6:]}"
    user = User(
        enterprise_id=enterprise.id,
        username=username,
        phone=encrypt_field(req.contact_phone),
        email=req.email,
        password_hash=hash_password(req.password),
        role=UserRole.ENTERPRISE_ADMIN,
        real_name=req.real_name,
        id_card=encrypt_field(req.legal_id_card),
        status=user_status,
    )
    db.add(user)
    await db.commit()

    return success(
        {
            "enterprise_id": enterprise.id,
            "status": audit_status.value,
            "demo_mode": settings.DEMO_MODE,
        },
        message="注册成功" + ("，账号已自动激活（演示模式）" if settings.DEMO_MODE else "，请等待管理员审核"),
    )


@router.post("/refresh")
async def refresh_token(req: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    """刷新 Access Token"""
    payload = decode_token(req.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise Unauthorized("Refresh Token 无效")

    user_id = payload.get("sub")
    stored = await redis_client.get(f"refresh_token:{user_id}")
    if stored != req.refresh_token:
        raise Unauthorized("Refresh Token 已失效")

    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()
    if not user or user.status != UserStatus.ACTIVE:
        raise Unauthorized("用户不存在或已禁用")

    new_access_token = create_access_token({"sub": str(user.id), "role": user.role.value})
    return success({"access_token": new_access_token, "token_type": "bearer"})


@router.post("/logout")
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    """登出"""
    auth_header = request.headers.get("authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
        # 加入黑名单 (有效期 7 天)
        await redis_client.set(
            f"token_blacklist:{token[:32]}", "1",
            expire=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    await redis_client.delete(f"refresh_token:{current_user.id}")
    return success(message="已成功登出")


@router.post("/change-password")
async def change_password(
    old_password: str,
    new_password: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """修改密码"""
    if not verify_password(old_password, current_user.password_hash):
        raise AppException(400, "原密码错误")
    if len(new_password) < 8:
        raise AppException(400, "新密码长度不能少于8位")
    current_user.password_hash = hash_password(new_password)
    current_user.must_change_password = False
    await db.commit()
    return success(message="密码修改成功")
