"""
用户管理接口
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.response import success, AppException
from app.core.security import hash_password, encrypt_field, decrypt_field
from app.models.models import User, UserRole

router = APIRouter()


class UpdateProfileRequest(BaseModel):
    notify_email: Optional[bool] = None
    notify_sms: Optional[bool] = None
    language: Optional[str] = None
    real_name: Optional[str] = None


@router.get("/me")
async def get_my_profile(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return success({
        "id": current_user.id,
        "username": current_user.username,
        "real_name": current_user.real_name,
        "email": current_user.email,
        "role": current_user.role.value,
        "enterprise_id": current_user.enterprise_id,
        "notify_email": current_user.notify_email,
        "notify_sms": current_user.notify_sms,
        "language": current_user.language,
        "mediator_domain": current_user.mediator_domain,
        "mediator_intro": current_user.mediator_intro,
        "mediator_success_rate": float(current_user.mediator_success_rate or 0),
        "mediator_rating": float(current_user.mediator_rating or 5),
    })


@router.put("/me")
async def update_my_profile(
    req: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新个人信息"""
    if req.notify_email is not None:
        current_user.notify_email = req.notify_email
    if req.notify_sms is not None:
        current_user.notify_sms = req.notify_sms
    if req.language is not None:
        current_user.language = req.language
    if req.real_name is not None:
        current_user.real_name = req.real_name
    await db.commit()
    return success(message="个人信息更新成功")


@router.get("/send-sign-code")
async def send_sign_code(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """发送签署验证码 (Mock: 直接返回)"""
    from datetime import datetime, timedelta
    from app.models.models import VerificationCode
    import random

    code = str(random.randint(100000, 999999))
    vc = VerificationCode(
        target=current_user.email,
        code=code,
        purpose="sign_agreement",
        expires_at=datetime.now() + timedelta(minutes=10),
    )
    db.add(vc)
    await db.commit()

    # 演示模式直接返回验证码
    from app.core.config import settings
    if settings.DEMO_MODE:
        return success({"code": code, "note": "演示模式下直接显示验证码"})

    # 生产模式发短信（预留）
    return success({"note": "验证码已发送至手机/邮箱"})
