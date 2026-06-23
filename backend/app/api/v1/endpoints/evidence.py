"""
证据文件管理接口
"""
from fastapi import APIRouter, Depends, UploadFile, File, Form, Request
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
import hashlib
import os
import uuid
import logging
from datetime import datetime

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.response import success, AppException, PermissionDenied, NotFound
from app.core.config import settings
from app.models.models import Case, Evidence, User, UserRole, CaseStatus, EvidenceType
from app.services.storage_service import StorageService
from app.services.timestamp_service import TimestampService
from app.services.log_service import LogService
from app.api.v1.endpoints.cases import _get_case_with_permission

router = APIRouter()
logger = logging.getLogger(__name__)

# 允许的文件类型白名单
ALLOWED_EXTENSIONS = {
    "pdf": "application/pdf",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "png": "image/png",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


def _check_file_allowed(filename: str) -> bool:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ext in ALLOWED_EXTENSIONS


@router.post("/{case_id}/upload")
async def upload_evidence(
    case_id: int,
    files: List[UploadFile] = File(...),
    evidence_type: EvidenceType = Form(...),
    request: Request = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """上传证据文件 (批量，最多10个)"""
    if len(files) > settings.MAX_BATCH_UPLOAD:
        raise AppException(400, f"一次最多上传 {settings.MAX_BATCH_UPLOAD} 个文件")

    case = await _get_case_with_permission(case_id, current_user, db)

    # 权限检查：协商开始后不允许删除，但可以补充
    if case.status == CaseStatus.ARCHIVED:
        raise AppException(400, "已归档案件不能上传证据")

    uploaded = []
    storage_svc = StorageService()
    ts_svc = TimestampService()

    for f in files:
        if not _check_file_allowed(f.filename):
            raise AppException(400, f"不支持的文件类型: {f.filename}")

        content = await f.read()
        file_size = len(content)

        if file_size > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
            raise AppException(400, f"文件 {f.filename} 超过大小限制 {settings.MAX_FILE_SIZE_MB}MB")

        # SHA-256 哈希
        file_hash = hashlib.sha256(content).hexdigest()

        # 存储文件
        file_url = await storage_svc.save(f.filename, content, f"evidence/{case_id}")

        # 调用存证服务
        ts_result = await ts_svc.get_timestamp(file_hash, f.filename)

        evidence = Evidence(
            case_id=case_id,
            uploaded_by_user_id=current_user.id,
            file_name=f.filename,
            file_url=file_url,
            file_size=file_size,
            file_mime=f.content_type,
            file_hash=file_hash,
            evidence_type=evidence_type,
            timestamp_cert=ts_result.get("cert"),
            storage_voucher=ts_result.get("voucher"),
        )
        db.add(evidence)
        await db.flush()

        # 更新时间轴
        timeline = case.timeline or []
        timeline.append({
            "time": datetime.now().isoformat(),
            "action": f"上传证据: {f.filename}",
            "operator": current_user.real_name,
        })
        case.timeline = timeline

        uploaded.append({
            "id": evidence.id,
            "file_name": f.filename,
            "file_hash": file_hash,
            "storage_voucher": ts_result.get("voucher"),
        })

    await db.commit()
    await LogService.log(db, current_user.id, "upload_evidence",
                         resource_type="case", resource_id=case_id,
                         detail={"count": len(files)},
                         ip=request.client.host if request and request.client else "")

    return success({"uploaded": uploaded, "count": len(uploaded)}, "证据上传成功")


@router.get("/{case_id}/list")
async def list_evidence(
    case_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取案件证据列表"""
    await _get_case_with_permission(case_id, current_user, db)

    result = await db.execute(
        select(Evidence).where(
            and_(Evidence.case_id == case_id, Evidence.is_deleted == False)
        ).order_by(Evidence.created_at.desc())
    )
    evidences = result.scalars().all()

    return success([{
        "id": e.id,
        "file_name": e.file_name,
        "file_url": e.file_url,
        "file_size": e.file_size,
        "file_mime": e.file_mime,
        "file_hash": e.file_hash,
        "evidence_type": e.evidence_type.value,
        "timestamp_cert": e.timestamp_cert,
        "storage_voucher": e.storage_voucher,
        "created_at": e.created_at.isoformat() if e.created_at else None,
    } for e in evidences])


@router.delete("/{case_id}/evidence/{evidence_id}")
async def delete_evidence(
    case_id: int,
    evidence_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除证据 (仅协商未开始前可删除)"""
    case = await _get_case_with_permission(case_id, current_user, db)

    # 协商开始后不能删除
    if case.negotiation_started_at:
        raise AppException(400, "协商开始后不能删除证据")

    result = await db.execute(
        select(Evidence).where(
            and_(Evidence.id == evidence_id, Evidence.case_id == case_id)
        )
    )
    evidence = result.scalar_one_or_none()
    if not evidence:
        raise NotFound("证据不存在")

    evidence.is_deleted = True
    await db.commit()
    return success(message="证据已删除")
