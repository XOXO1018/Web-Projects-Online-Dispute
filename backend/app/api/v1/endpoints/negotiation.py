"""
在线协商接口
"""
from fastapi import APIRouter, Depends, Request, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime
from typing import Optional
import logging
from pydantic import BaseModel

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.response import success, AppException, PermissionDenied
from app.models.models import (
    Case, User, UserRole, CaseStatus, NegotiationMessage,
    MessageType, NegotiationResult
)
from app.services.notification_service import NotificationService
from app.services.log_service import LogService
from app.api.v1.endpoints.cases import _get_case_with_permission

router = APIRouter()
logger = logging.getLogger(__name__)


class StartNegotiationRequest(BaseModel):
    case_id: int
    opponent_email: str


class ConfirmResultRequest(BaseModel):
    case_id: int
    summary: str


class SignMemoRequest(BaseModel):
    case_id: int
    sms_code: str


@router.post("/start")
async def start_negotiation(
    req: StartNegotiationRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """发起协商"""
    case = await _get_case_with_permission(req.case_id, current_user, db)

    if case.negotiation_started_at:
        raise AppException(400, "协商已经发起")

    case.negotiation_started_at = datetime.now()
    timeline = case.timeline or []
    timeline.append({
        "time": datetime.now().isoformat(),
        "action": "协商发起",
        "operator": current_user.real_name,
    })
    case.timeline = timeline

    await db.commit()

    # 发送通知邮件给对方
    await NotificationService.send_email(
        req.opponent_email,
        "协商邀请",
        f"您好，{current_user.real_name} 邀请您就案件 {case.case_number} 进行在线协商。"
        f"请登录智链解纷平台查看详情。"
    )

    await LogService.log(db, current_user.id, "start_negotiation",
                         resource_type="case", resource_id=case.id,
                         ip=request.client.host if request.client else "")

    return success(message="协商已发起，已向对方发送邀请")


@router.get("/{case_id}/messages")
async def get_messages(
    case_id: int,
    page: int = 1,
    page_size: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取协商消息列表"""
    await _get_case_with_permission(case_id, current_user, db)

    from sqlalchemy import func
    result = await db.execute(
        select(NegotiationMessage)
        .where(NegotiationMessage.case_id == case_id)
        .order_by(NegotiationMessage.created_at.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    messages = result.scalars().all()

    return success([{
        "id": m.id,
        "sender_id": m.sender_id,
        "message_type": m.message_type.value,
        "content": m.content,
        "voice_text": m.voice_text,
        "is_system": m.is_system,
        "created_at": m.created_at.isoformat() if m.created_at else None,
    } for m in messages])


@router.post("/{case_id}/send-voice")
async def send_voice_message(
    case_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """上传语音消息"""
    await _get_case_with_permission(case_id, current_user, db)

    from app.services.storage_service import StorageService
    content = await file.read()
    svc = StorageService()
    url = await svc.save(file.filename or "voice.mp3", content, f"voice/{case_id}")

    # Mock语音转文字
    voice_text = "[语音消息，转写功能需配置第三方API]"

    msg = NegotiationMessage(
        case_id=case_id,
        sender_id=current_user.id,
        message_type=MessageType.VOICE,
        content=url,
        voice_text=voice_text,
    )
    db.add(msg)
    await db.commit()
    await db.refresh(msg)

    return success({"message_id": msg.id, "url": url, "voice_text": voice_text})


@router.post("/confirm-result")
async def confirm_result(
    req: ConfirmResultRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """确认协商结果，生成备忘录"""
    case = await _get_case_with_permission(req.case_id, current_user, db)

    existing = await db.execute(
        select(NegotiationResult).where(NegotiationResult.case_id == req.case_id)
    )
    nr = existing.scalar_one_or_none()

    if not nr:
        nr = NegotiationResult(case_id=req.case_id, summary=req.summary)
        db.add(nr)
    else:
        nr.summary = req.summary

    await db.commit()
    return success({"result_id": nr.id}, "协商结果已记录，等待双方签署")


@router.post("/sign-memo")
async def sign_memo(
    req: SignMemoRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """电子签署协商备忘录 (短信验证码确认)"""
    # 验证短信验证码 (Mock: 任意6位数字通过)
    from app.models.models import VerificationCode
    from sqlalchemy import func as sqlfunc

    code_result = await db.execute(
        select(VerificationCode).where(
            and_(
                VerificationCode.target == current_user.email,
                VerificationCode.code == req.sms_code,
                VerificationCode.purpose == "sign_agreement",
                VerificationCode.is_used == False,
                VerificationCode.expires_at > datetime.now(),
            )
        )
    )
    vc = code_result.scalar_one_or_none()
    # Mock模式：接受 "123456"
    mock_ok = req.sms_code == "123456"
    if not vc and not mock_ok:
        raise AppException(400, "验证码无效")
    if vc:
        vc.is_used = True

    nr_result = await db.execute(
        select(NegotiationResult).where(NegotiationResult.case_id == req.case_id)
    )
    nr = nr_result.scalar_one_or_none()
    if not nr:
        raise AppException(400, "协商结果不存在")

    now = datetime.now()
    case = await _get_case_with_permission(req.case_id, current_user, db)

    # 确定原告/被告方
    if case.enterprise_id == current_user.enterprise_id:
        nr.plaintiff_signed = True
        nr.plaintiff_signed_by = current_user.real_name
        nr.plaintiff_signed_at = now
    else:
        nr.defendant_signed = True
        nr.defendant_signed_by = current_user.real_name
        nr.defendant_signed_at = now

    # 双方都签署后结案
    if nr.plaintiff_signed and nr.defendant_signed:
        case.status = CaseStatus.CLOSED_NEGOTIATION
        case.closed_at = now
        timeline = case.timeline or []
        timeline.append({"time": now.isoformat(), "action": "协商备忘录双方签署完成", "operator": "系统"})
        case.timeline = timeline

    await db.commit()
    return success(message="签署成功")
