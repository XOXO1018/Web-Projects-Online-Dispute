"""
调解模块接口
"""
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime, timedelta
from typing import Optional, List
import logging
from pydantic import BaseModel

from app.core.database import get_db
from app.core.deps import get_current_user, require_mediator
from app.core.response import success, AppException, PermissionDenied, NotFound
from app.models.models import (
    Case, User, UserRole, CaseStatus, MediationRequest, MediationMeeting,
    MediationAgreement, MediationStatus, UserStatus
)
from app.services.notification_service import NotificationService
from app.services.agora_service import AgoraService
from app.services.pdf_service import PDFService
from app.api.v1.endpoints.cases import _get_case_with_permission

router = APIRouter()
logger = logging.getLogger(__name__)


class ApplyMediationRequest(BaseModel):
    case_id: int
    demand_text: str


class SelectMediatorRequest(BaseModel):
    request_id: int
    mediator_id: int


class ScheduleMeetingRequest(BaseModel):
    request_id: int
    scheduled_time: datetime


class MediatorOpinionRequest(BaseModel):
    meeting_id: int
    opinion: str
    success: bool
    agreement_content: Optional[str] = None


@router.post("/apply")
async def apply_mediation(
    req: ApplyMediationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """申请调解"""
    case = await _get_case_with_permission(req.case_id, current_user, db)

    if case.status not in {CaseStatus.NEGOTIATING}:
        raise AppException(400, "当前案件状态不允许申请调解")

    mediation_req = MediationRequest(
        case_id=req.case_id,
        applicant_id=current_user.id,
        demand_text=req.demand_text,
        status=MediationStatus.PENDING,
    )
    db.add(mediation_req)
    case.status = CaseStatus.MEDIATING
    timeline = case.timeline or []
    timeline.append({
        "time": datetime.now().isoformat(),
        "action": "提交调解申请",
        "operator": current_user.real_name,
    })
    case.timeline = timeline
    await db.commit()
    await db.refresh(mediation_req)

    return success({"request_id": mediation_req.id}, "调解申请已提交")


@router.get("/mediators/recommend")
async def recommend_mediators(
    case_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """推荐调解员"""
    result = await db.execute(
        select(User).where(
            and_(User.role == UserRole.MEDIATOR, User.status == UserStatus.ACTIVE)
        ).order_by(User.mediator_rating.desc()).limit(5)
    )
    mediators = result.scalars().all()

    return success([{
        "id": m.id,
        "real_name": m.real_name,
        "domain": m.mediator_domain,
        "intro": m.mediator_intro,
        "success_rate": float(m.mediator_success_rate or 0),
        "rating": float(m.mediator_rating or 5.0),
        "case_count": m.mediator_case_count,
    } for m in mediators])


@router.post("/select-mediator")
async def select_mediator(
    req: SelectMediatorRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """选择调解员"""
    result = await db.execute(
        select(MediationRequest).where(MediationRequest.id == req.request_id)
    )
    med_req = result.scalar_one_or_none()
    if not med_req:
        raise NotFound("调解申请不存在")

    case = await _get_case_with_permission(med_req.case_id, current_user, db)

    mediator_result = await db.execute(
        select(User).where(and_(User.id == req.mediator_id, User.role == UserRole.MEDIATOR))
    )
    mediator = mediator_result.scalar_one_or_none()
    if not mediator:
        raise NotFound("调解员不存在")

    med_req.selected_mediator_id = req.mediator_id
    med_req.mediator_assigned_id = req.mediator_id
    med_req.status = MediationStatus.ASSIGNED

    await db.commit()

    # 通知调解员
    await NotificationService.send_internal(
        db, mediator.id,
        f"新调解案件：{case.case_number}",
        f"您已被分配到案件 {case.case_number}，请登录平台查看详情。",
        related_case_id=case.id,
    )

    return success(message="调解员选择成功")


@router.post("/schedule-meeting")
async def schedule_meeting(
    req: ScheduleMeetingRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """调解员创建调解会议"""
    if current_user.role != UserRole.MEDIATOR:
        raise PermissionDenied("只有调解员可以创建会议")

    result = await db.execute(
        select(MediationRequest).where(MediationRequest.id == req.request_id)
    )
    med_req = result.scalar_one_or_none()
    if not med_req or med_req.mediator_assigned_id != current_user.id:
        raise PermissionDenied("无权操作此调解申请")

    # 生成 Agora 频道名
    agora = AgoraService()
    channel_name = f"case_{med_req.case_id}_{int(datetime.now().timestamp())}"
    meeting_link = agora.generate_meeting_link(channel_name)

    meeting = MediationMeeting(
        request_id=req.request_id,
        channel_name=channel_name,
        meeting_link=meeting_link,
        scheduled_time=req.scheduled_time,
        status="scheduled",
    )
    db.add(meeting)

    # 更新请求状态
    med_req.status = MediationStatus.IN_PROGRESS

    await db.commit()
    await db.refresh(meeting)

    # 获取案件信息并通知双方
    case_result = await db.execute(select(Case).where(Case.id == med_req.case_id))
    case = case_result.scalar_one_or_none()
    if case:
        timeline = case.timeline or []
        timeline.append({
            "time": datetime.now().isoformat(),
            "action": f"调解会议已安排：{req.scheduled_time.strftime('%Y-%m-%d %H:%M')}",
            "operator": current_user.real_name,
        })
        case.timeline = timeline
        await db.commit()

    return success({
        "meeting_id": meeting.id,
        "meeting_link": meeting_link,
        "channel_name": channel_name,
        "scheduled_time": req.scheduled_time.isoformat(),
    }, "调解会议已创建")


@router.get("/meetings/{meeting_id}/token")
async def get_meeting_token(
    meeting_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取 Agora 会议 Token"""
    result = await db.execute(
        select(MediationMeeting).where(MediationMeeting.id == meeting_id)
    )
    meeting = result.scalar_one_or_none()
    if not meeting:
        raise NotFound("会议不存在")

    agora = AgoraService()
    token = agora.generate_rtc_token(meeting.channel_name, current_user.id)

    return success({
        "token": token,
        "channel_name": meeting.channel_name,
        "app_id": agora.app_id,
        "uid": current_user.id,
    })


@router.post("/opinion")
async def submit_mediator_opinion(
    req: MediatorOpinionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """调解员提交意见和调解结果"""
    if current_user.role != UserRole.MEDIATOR:
        raise PermissionDenied("只有调解员可以提交意见")

    result = await db.execute(select(MediationMeeting).where(MediationMeeting.id == req.meeting_id))
    meeting = result.scalar_one_or_none()
    if not meeting:
        raise NotFound("会议不存在")

    meeting.mediator_opinion = req.opinion
    meeting.actual_end_time = datetime.now()
    meeting.status = "ended"

    # 获取调解请求和案件
    med_req_result = await db.execute(
        select(MediationRequest).where(MediationRequest.id == meeting.request_id)
    )
    med_req = med_req_result.scalar_one_or_none()
    case_result = await db.execute(select(Case).where(Case.id == med_req.case_id))
    case = case_result.scalar_one_or_none()

    now = datetime.now()
    if req.success:
        # 调解成功：生成协议PDF
        agreement_content = req.agreement_content or ""
        pdf_svc = PDFService()
        pdf_url = await pdf_svc.generate_agreement(case, agreement_content)

        agreement = MediationAgreement(
            case_id=case.id,
            agreement_content=agreement_content,
            agreement_pdf_url=pdf_url,
        )
        db.add(agreement)
        case.status = CaseStatus.MEDIATING  # 等待签署后改为 CLOSED_MEDIATION

        timeline = case.timeline or []
        timeline.append({
            "time": now.isoformat(),
            "action": "调解成功，和解协议已生成，等待双方签署",
            "operator": current_user.real_name,
        })
        case.timeline = timeline
        med_req.status = MediationStatus.COMPLETED

    else:
        case.status = CaseStatus.CLOSED_FAILED
        med_req.status = MediationStatus.FAILED
        timeline = case.timeline or []
        timeline.append({
            "time": now.isoformat(),
            "action": "调解失败",
            "operator": current_user.real_name,
        })
        case.timeline = timeline

    await db.commit()
    return success(message="调解意见已提交")


@router.post("/agreements/{agreement_id}/sign")
async def sign_agreement(
    agreement_id: int,
    sms_code: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """签署调解协议"""
    # Mock 模式：验证码 "123456" 通过
    if sms_code != "123456":
        raise AppException(400, "验证码错误")

    result = await db.execute(
        select(MediationAgreement).where(MediationAgreement.id == agreement_id)
    )
    agreement = result.scalar_one_or_none()
    if not agreement:
        raise NotFound("协议不存在")

    case_result = await db.execute(select(Case).where(Case.id == agreement.case_id))
    case = case_result.scalar_one_or_none()

    now = datetime.now()
    if case.enterprise_id == current_user.enterprise_id:
        agreement.signed_by_plaintiff = True
        agreement.plaintiff_sign_time = now
        agreement.plaintiff_signer_name = current_user.real_name
    else:
        agreement.signed_by_defendant = True
        agreement.defendant_sign_time = now
        agreement.defendant_signer_name = current_user.real_name

    if agreement.signed_by_plaintiff and agreement.signed_by_defendant:
        agreement.signed_at = now
        case.status = CaseStatus.CLOSED_MEDIATION
        case.closed_at = now
        timeline = case.timeline or []
        timeline.append({"time": now.isoformat(), "action": "和解协议双方签署完成", "operator": "系统"})
        case.timeline = timeline

    await db.commit()
    return success(message="签署成功")


@router.get("/export/{case_id}")
async def export_case_materials(
    case_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """导出案件材料 (转仲裁用)"""
    case = await _get_case_with_permission(case_id, current_user, db)

    # 收集案件信息
    ev_result = await db.execute(
        select(MediationRequest).where(MediationRequest.case_id == case_id)
    )
    requests = ev_result.scalars().all()

    export_data = {
        "case": {
            "case_number": case.case_number,
            "status": case.status.value,
            "amount": float(case.amount),
            "dispute_desc": case.dispute_desc,
        },
        "mediation_requests": [
            {"id": r.id, "demand_text": r.demand_text, "status": r.status.value}
            for r in requests
        ],
        "export_time": datetime.now().isoformat(),
        "note": "V1.0 仅导出，V2.0 对接仲裁机构API",
    }

    return success(export_data, "案件材料导出成功（V1.0 仅JSON，V2.0将对接仲裁机构）")
