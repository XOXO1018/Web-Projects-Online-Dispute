"""
通知系统接口
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.response import success
from app.models.models import Notification, User

router = APIRouter()


@router.get("")
async def list_notifications(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    unread_only: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取通知列表"""
    conditions = [Notification.user_id == current_user.id]
    if unread_only:
        conditions.append(Notification.is_read == False)

    total_r = await db.execute(
        select(func.count()).where(and_(*conditions))
    )
    total = total_r.scalar()

    unread_r = await db.execute(
        select(func.count()).where(
            and_(Notification.user_id == current_user.id, Notification.is_read == False)
        )
    )
    unread_count = unread_r.scalar()

    result = await db.execute(
        select(Notification)
        .where(and_(*conditions))
        .order_by(Notification.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    notifications = result.scalars().all()

    return success({
        "total": total,
        "unread_count": unread_count,
        "items": [{
            "id": n.id,
            "type": n.type.value,
            "title": n.title,
            "content": n.content,
            "is_read": n.is_read,
            "related_case_id": n.related_case_id,
            "created_at": n.created_at.isoformat() if n.created_at else None,
        } for n in notifications],
    })


@router.put("/{notification_id}/read")
async def mark_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Notification).where(
            and_(Notification.id == notification_id, Notification.user_id == current_user.id)
        )
    )
    n = result.scalar_one_or_none()
    if n:
        n.is_read = True
        await db.commit()
    return success(message="已标记为已读")


@router.put("/read-all")
async def mark_all_as_read(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Notification).where(
            and_(Notification.user_id == current_user.id, Notification.is_read == False)
        )
    )
    for n in result.scalars().all():
        n.is_read = True
    await db.commit()
    return success(message="全部已读")
