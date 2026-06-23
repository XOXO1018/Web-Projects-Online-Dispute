"""
操作日志服务
"""
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.models.models import OperationLog


class LogService:
    @staticmethod
    async def log(
        db: AsyncSession,
        user_id: Optional[int],
        action: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[int] = None,
        detail: Optional[dict] = None,
        ip: str = "",
        user_agent: str = "",
    ):
        log = OperationLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            detail=detail,
            ip=ip,
            user_agent=user_agent,
        )
        db.add(log)
        await db.flush()
