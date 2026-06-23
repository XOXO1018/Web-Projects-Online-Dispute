"""
企业管理接口
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.response import success, NotFound
from app.core.security import decrypt_field
from app.models.models import Enterprise, User, UserRole

router = APIRouter()


@router.get("/my")
async def get_my_enterprise(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取当前用户所属企业信息"""
    if not current_user.enterprise_id:
        return success(None)
    result = await db.execute(
        select(Enterprise).where(Enterprise.id == current_user.enterprise_id)
    )
    ent = result.scalar_one_or_none()
    if not ent:
        raise NotFound("企业不存在")
    return success(_format_enterprise(ent))


def _format_enterprise(ent: Enterprise) -> dict:
    return {
        "id": ent.id,
        "credit_code": ent.credit_code,
        "name": ent.name,
        "legal_person": ent.legal_person,
        "business_license": ent.business_license,
        "contact_email": ent.contact_email,
        "audit_status": ent.audit_status.value,
        "country": ent.country,
        "created_at": ent.created_at.isoformat() if ent.created_at else None,
    }
