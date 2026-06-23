"""
认证依赖项 - JWT 验证与 RBAC 权限控制
"""
from fastapi import Depends, HTTPException, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
import logging

from app.core.database import get_db
from app.core.security import decode_token
from app.core.redis_client import redis_client
from app.models.models import User, UserRole, UserStatus
from app.core.response import Unauthorized, PermissionDenied

logger = logging.getLogger(__name__)
bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """从 JWT 获取当前用户"""
    if not credentials:
        raise Unauthorized("缺少认证令牌")

    token = credentials.credentials
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise Unauthorized("令牌无效或已过期")

    user_id = payload.get("sub")
    if not user_id:
        raise Unauthorized("令牌数据异常")

    # 检查 token 是否已被撤销 (登出时加入黑名单)
    blacklisted = await redis_client.exists(f"token_blacklist:{token[:32]}")
    if blacklisted:
        raise Unauthorized("令牌已失效，请重新登录")

    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()
    if not user:
        raise Unauthorized("用户不存在")
    if user.status != UserStatus.ACTIVE:
        raise Unauthorized("账号未激活或已被禁用")

    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    return current_user


def require_roles(*roles: UserRole):
    """角色权限装饰器工厂"""
    async def checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise PermissionDenied(f"此操作需要角色: {', '.join(r.value for r in roles)}")
        return current_user
    return checker


async def require_platform_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.PLATFORM_ADMIN:
        raise PermissionDenied("需要平台管理员权限")
    return current_user


async def require_mediator(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.MEDIATOR:
        raise PermissionDenied("需要调解员权限")
    return current_user


async def require_enterprise_user(current_user: User = Depends(get_current_user)) -> User:
    """要求为企业用户（企业管理员、法务、业务员）"""
    enterprise_roles = {UserRole.ENTERPRISE_ADMIN, UserRole.LEGAL, UserRole.SALESPERSON}
    if current_user.role not in enterprise_roles:
        raise PermissionDenied("需要企业用户权限")
    return current_user
