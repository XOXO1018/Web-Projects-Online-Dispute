"""
通知服务：站内信 + 邮件
"""
from sqlalchemy.ext.asyncio import AsyncSession
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from typing import Optional

from app.core.config import settings
from app.models.models import Notification, NotificationType

logger = logging.getLogger(__name__)


class NotificationService:

    @staticmethod
    async def send_internal(
        db: AsyncSession,
        user_id: int,
        title: str,
        content: str,
        related_case_id: Optional[int] = None,
    ):
        """发送站内信"""
        n = Notification(
            user_id=user_id,
            type=NotificationType.INTERNAL,
            title=title,
            content=content,
            related_case_id=related_case_id,
        )
        db.add(n)
        await db.flush()
        logger.info(f"站内信已发送给用户 {user_id}: {title}")

    @staticmethod
    async def send_email(to_email: str, subject: str, body: str):
        """发送邮件"""
        if not settings.SMTP_HOST or not settings.SMTP_USER:
            logger.warning(f"邮件服务未配置，跳过发送邮件给 {to_email}: {subject}")
            return

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"[{settings.SMTP_FROM_NAME}] {subject}"
            msg["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_USER}>"
            msg["To"] = to_email
            msg.attach(MIMEText(body, "plain", "utf-8"))

            await aiosmtplib.send(
                msg,
                hostname=settings.SMTP_HOST,
                port=settings.SMTP_PORT,
                username=settings.SMTP_USER,
                password=settings.SMTP_PASSWORD,
                use_tls=settings.SMTP_TLS,
            )
            logger.info(f"邮件已发送至 {to_email}: {subject}")
        except Exception as e:
            logger.error(f"邮件发送失败: {e}")
