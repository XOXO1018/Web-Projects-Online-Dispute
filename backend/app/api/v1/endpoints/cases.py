"""
案件管理接口
"""
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from datetime import datetime
from typing import Optional
import random
import string
import logging

from pydantic import BaseModel
from app.core.database import get_db
from app.core.deps import get_current_user, require_enterprise_user
from app.core.response import success, AppException, PermissionDenied, NotFound
from app.models.models import (
    Case, User, Enterprise, UserRole, CaseStatus,
    ContractType, DisputeMethod, NegotiationMessage, MessageType
)
from app.services.notification_service import NotificationService
from app.services.log_service import LogService

router = APIRouter()
logger = logging.getLogger(__name__)


def generate_case_number() -> str:
    date_str = datetime.now().strftime("%Y%m%d")
    rand = "".join(random.choices(string.digits, k=4))
    return f"CASE{date_str}{rand}"


class CreateCaseRequest(BaseModel):
    opponent_name: str
    opponent_country: str
    contract_type: ContractType
    amount: float
    dispute_desc: str
    contract_date: datetime
    incident_date: datetime
    expected_method: DisputeMethod


class CaseQueryParams(BaseModel):
    case_number: Optional[str] = None
    opponent_name: Optional[str] = None
    status: Optional[CaseStatus] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    page: int = 1
    page_size: int = 20


@router.post("")
async def create_case(
    req: CreateCaseRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """创建新案件 (企业管理员或法务)"""
    allowed_roles = {UserRole.ENTERPRISE_ADMIN, UserRole.LEGAL}
    if current_user.role not in allowed_roles:
        raise PermissionDenied("只有企业管理员或法务可以创建案件")

    case_number = generate_case_number()
    # 确保唯一
    while True:
        existing = await db.execute(select(Case).where(Case.case_number == case_number))
        if not existing.scalar_one_or_none():
            break
        case_number = generate_case_number()

    timeline = [{"time": datetime.now().isoformat(), "action": "案件创建", "operator": current_user.real_name}]

    case = Case(
        case_number=case_number,
        enterprise_id=current_user.enterprise_id,
        created_by_user_id=current_user.id,
        opponent_name=req.opponent_name,
        opponent_country=req.opponent_country,
        contract_type=req.contract_type,
        amount=req.amount,
        dispute_desc=req.dispute_desc,
        contract_date=req.contract_date,
        incident_date=req.incident_date,
        expected_method=req.expected_method,
        status=CaseStatus.NEGOTIATING,
        timeline=timeline,
    )
    db.add(case)
    await db.commit()
    await db.refresh(case)

    await LogService.log(db, current_user.id, "create_case",
                         resource_type="case", resource_id=case.id,
                         ip=request.client.host if request.client else "")

    return success({"case_id": case.id, "case_number": case.case_number}, "案件创建成功")


@router.get("")
async def list_cases(
    case_number: Optional[str] = Query(None),
    opponent_name: Optional[str] = Query(None),
    status: Optional[CaseStatus] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """查询案件列表"""
    conditions = []

    # 数据隔离
    if current_user.role == UserRole.PLATFORM_ADMIN:
        pass  # 管理员可查所有
    elif current_user.role in {UserRole.ENTERPRISE_ADMIN, UserRole.LEGAL}:
        conditions.append(Case.enterprise_id == current_user.enterprise_id)
    elif current_user.role == UserRole.SALESPERSON:
        conditions.append(Case.created_by_user_id == current_user.id)
    elif current_user.role == UserRole.MEDIATOR:
        # 调解员只能看被分配的案件
        from app.models.models import MediationRequest
        subq = select(MediationRequest.case_id).where(
            MediationRequest.mediator_assigned_id == current_user.id
        )
        conditions.append(Case.id.in_(subq))

    if case_number:
        conditions.append(Case.case_number.contains(case_number))
    if opponent_name:
        conditions.append(Case.opponent_name.contains(opponent_name))
    if status:
        conditions.append(Case.status == status)
    if start_date:
        conditions.append(Case.created_at >= start_date)
    if end_date:
        conditions.append(Case.created_at <= end_date)

    query = select(Case)
    if conditions:
        query = query.where(and_(*conditions))
    query = query.order_by(Case.created_at.desc())

    # 分页
    total_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_result.scalar()

    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    cases = result.scalars().all()

    return success({
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [_format_case(c) for c in cases],
    })


@router.get("/statistics")
async def get_case_statistics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """工作台统计数据"""
    conditions = []
    if current_user.role in {UserRole.ENTERPRISE_ADMIN, UserRole.LEGAL}:
        conditions.append(Case.enterprise_id == current_user.enterprise_id)
    elif current_user.role == UserRole.SALESPERSON:
        conditions.append(Case.created_by_user_id == current_user.id)

    result = await db.execute(
        select(Case.status, func.count(Case.id))
        .where(and_(*conditions) if conditions else True)
        .group_by(Case.status)
    )
    stats = {row[0].value: row[1] for row in result.all()}
    return success(stats)


@router.get("/{case_id}")
async def get_case_detail(
    case_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取案件详情"""
    case = await _get_case_with_permission(case_id, current_user, db)
    return success(_format_case_detail(case))


@router.put("/{case_id}/archive")
async def archive_case(
    case_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """归档案件 (仅管理员)"""
    if current_user.role != UserRole.PLATFORM_ADMIN:
        raise PermissionDenied("只有平台管理员可以归档案件")
    case = await _get_case_with_permission(case_id, current_user, db)
    closed_statuses = {CaseStatus.CLOSED_NEGOTIATION, CaseStatus.CLOSED_MEDIATION, CaseStatus.CLOSED_FAILED}
    if case.status not in closed_statuses:
        raise AppException(400, "只有已结案的案件可以归档")
    case.status = CaseStatus.ARCHIVED
    await db.commit()
    return success(message="案件已归档")


async def _get_case_with_permission(case_id: int, user: User, db: AsyncSession) -> Case:
    """获取案件并验证权限"""
    result = await db.execute(select(Case).where(Case.id == case_id))
    case = result.scalar_one_or_none()
    if not case:
        raise NotFound("案件不存在")

    if user.role == UserRole.PLATFORM_ADMIN:
        return case
    if user.role in {UserRole.ENTERPRISE_ADMIN, UserRole.LEGAL}:
        if case.enterprise_id != user.enterprise_id:
            raise PermissionDenied("无权访问此案件")
        return case
    if user.role == UserRole.SALESPERSON:
        if case.created_by_user_id != user.id:
            raise PermissionDenied("无权访问此案件")
        return case
    if user.role == UserRole.MEDIATOR:
        from app.models.models import MediationRequest
        req_result = await db.execute(
            select(MediationRequest).where(
                and_(
                    MediationRequest.case_id == case_id,
                    MediationRequest.mediator_assigned_id == user.id,
                )
            )
        )
        if not req_result.scalar_one_or_none():
            raise PermissionDenied("无权访问此案件")
        return case
    raise PermissionDenied()


def _format_case(case: Case) -> dict:
    return {
        "id": case.id,
        "case_number": case.case_number,
        "opponent_name": case.opponent_name,
        "opponent_country": case.opponent_country,
        "contract_type": case.contract_type.value,
        "amount": float(case.amount),
        "status": case.status.value,
        "expected_method": case.expected_method.value,
        "created_at": case.created_at.isoformat() if case.created_at else None,
    }


def _format_case_detail(case: Case) -> dict:
    base = _format_case(case)
    base.update({
        "dispute_desc": case.dispute_desc,
        "contract_date": case.contract_date.isoformat() if case.contract_date else None,
        "incident_date": case.incident_date.isoformat() if case.incident_date else None,
        "negotiation_started_at": case.negotiation_started_at.isoformat() if case.negotiation_started_at else None,
        "closed_at": case.closed_at.isoformat() if case.closed_at else None,
        "close_summary": case.close_summary,
        "timeline": case.timeline or [],
        "enterprise_id": case.enterprise_id,
    })
    return base
