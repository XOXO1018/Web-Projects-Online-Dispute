"""
管理后台接口 (仅平台管理员)
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import Optional
from pydantic import BaseModel

from app.core.database import get_db
from app.core.deps import require_platform_admin
from app.core.response import success, NotFound
from app.core.security import hash_password, encrypt_field
from app.models.models import (
    User, Enterprise, Case, AuditStatus, UserStatus,
    UserRole, CaseStatus
)

router = APIRouter()


# ---- 企业审核 ----

@router.get("/enterprises")
async def list_enterprises(
    audit_status: Optional[AuditStatus] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20),
    _: User = Depends(require_platform_admin),
    db: AsyncSession = Depends(get_db),
):
    conditions = []
    if audit_status:
        conditions.append(Enterprise.audit_status == audit_status)

    total_r = await db.execute(
        select(func.count(Enterprise.id)).where(and_(*conditions) if conditions else True)
    )
    total = total_r.scalar()

    result = await db.execute(
        select(Enterprise)
        .where(and_(*conditions) if conditions else True)
        .order_by(Enterprise.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    enterprises = result.scalars().all()

    return success({
        "total": total,
        "items": [{
            "id": e.id,
            "credit_code": e.credit_code,
            "name": e.name,
            "legal_person": e.legal_person,
            "contact_email": e.contact_email,
            "audit_status": e.audit_status.value,
            "created_at": e.created_at.isoformat() if e.created_at else None,
        } for e in enterprises],
    })


@router.put("/enterprises/{enterprise_id}/audit")
async def audit_enterprise(
    enterprise_id: int,
    audit_status: AuditStatus,
    note: Optional[str] = None,
    _: User = Depends(require_platform_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Enterprise).where(Enterprise.id == enterprise_id))
    ent = result.scalar_one_or_none()
    if not ent:
        raise NotFound("企业不存在")

    ent.audit_status = audit_status
    ent.audit_note = note

    # 同步更新企业用户状态
    user_result = await db.execute(
        select(User).where(User.enterprise_id == enterprise_id)
    )
    for user in user_result.scalars().all():
        user.status = UserStatus.ACTIVE if audit_status == AuditStatus.APPROVED else UserStatus.DISABLED

    await db.commit()
    return success(message=f"企业审核状态已更新为: {audit_status.value}")


# ---- 调解员管理 ----

class CreateMediatorRequest(BaseModel):
    real_name: str
    email: str
    phone: str
    domain: str
    intro: str
    success_rate: float = 0.0
    rating: float = 5.0


@router.post("/mediators")
async def create_mediator(
    req: CreateMediatorRequest,
    _: User = Depends(require_platform_admin),
    db: AsyncSession = Depends(get_db),
):
    user = User(
        username=f"mediator_{req.email.split('@')[0]}",
        phone=encrypt_field(req.phone),
        email=req.email,
        password_hash=hash_password("Mediator@123"),
        role=UserRole.MEDIATOR,
        real_name=req.real_name,
        status=UserStatus.ACTIVE,
        mediator_domain=req.domain,
        mediator_intro=req.intro,
        mediator_success_rate=req.success_rate,
        mediator_rating=req.rating,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return success({"id": user.id}, "调解员账号已创建，初始密码为 Mediator@123")


@router.get("/mediators")
async def list_mediators(
    page: int = Query(1),
    page_size: int = Query(20),
    _: User = Depends(require_platform_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User)
        .where(User.role == UserRole.MEDIATOR)
        .order_by(User.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    mediators = result.scalars().all()
    return success([{
        "id": m.id,
        "real_name": m.real_name,
        "email": m.email,
        "domain": m.mediator_domain,
        "success_rate": float(m.mediator_success_rate or 0),
        "rating": float(m.mediator_rating or 5),
        "status": m.status.value,
    } for m in mediators])


# ---- 全局案件查看 ----

@router.get("/cases")
async def list_all_cases(
    status: Optional[CaseStatus] = Query(None),
    page: int = Query(1),
    page_size: int = Query(20),
    _: User = Depends(require_platform_admin),
    db: AsyncSession = Depends(get_db),
):
    conditions = []
    if status:
        conditions.append(Case.status == status)

    total_r = await db.execute(
        select(func.count(Case.id)).where(and_(*conditions) if conditions else True)
    )
    result = await db.execute(
        select(Case)
        .where(and_(*conditions) if conditions else True)
        .order_by(Case.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    return success({
        "total": total_r.scalar(),
        "items": [{
            "id": c.id,
            "case_number": c.case_number,
            "opponent_name": c.opponent_name,
            "opponent_country": c.opponent_country,
            "amount": float(c.amount),
            "status": c.status.value,
            "enterprise_id": c.enterprise_id,
            "created_at": c.created_at.isoformat() if c.created_at else None,
        } for c in result.scalars().all()],
    })


# ---- 统计 Dashboard ----

@router.get("/dashboard")
async def admin_dashboard(
    _: User = Depends(require_platform_admin),
    db: AsyncSession = Depends(get_db),
):
    total_users = await db.execute(select(func.count(User.id)))
    total_enterprises = await db.execute(select(func.count(Enterprise.id)))
    total_cases = await db.execute(select(func.count(Case.id)))
    pending_audit = await db.execute(
        select(func.count(Enterprise.id)).where(Enterprise.audit_status == AuditStatus.PENDING)
    )
    return success({
        "total_users": total_users.scalar(),
        "total_enterprises": total_enterprises.scalar(),
        "total_cases": total_cases.scalar(),
        "pending_audit": pending_audit.scalar(),
    })
