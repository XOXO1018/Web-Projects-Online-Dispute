"""
Agora 视频会议服务 (含 Mock 实现)
"""
import hashlib
import hmac
import time
import struct
import base64
import uuid
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class AgoraService:
    def __init__(self):
        self.app_id = settings.AGORA_APP_ID or "mock_app_id"
        self.app_cert = settings.AGORA_APP_CERTIFICATE or ""
        self.mock = settings.AGORA_ENABLE_MOCK or not settings.AGORA_APP_ID

    def generate_rtc_token(self, channel_name: str, uid: int, expire_seconds: int = 3600) -> str:
        """生成 Agora RTC Token"""
        if self.mock:
            mock_token = f"mock_token_{channel_name}_{uid}_{int(time.time())}"
            logger.info(f"[Mock Agora] 生成Token: channel={channel_name}, uid={uid}")
            return mock_token
        try:
            return self._build_token(channel_name, uid, expire_seconds)
        except Exception as e:
            logger.error(f"Agora Token 生成失败: {e}")
            return f"error_token_{channel_name}"

    def generate_meeting_link(self, channel_name: str) -> str:
        """生成会议链接"""
        if self.mock:
            return f"/meeting/{channel_name}?mock=true"
        return f"https://zjfl.example.com/meeting/{channel_name}"

    def _build_token(self, channel: str, uid: int, expire: int) -> str:
        """简化版 Agora Token 构建 (实际应使用官方SDK)"""
        ts = int(time.time()) + expire
        msg = f"{self.app_id}{channel}{uid}{ts}"
        signature = hmac.new(
            self.app_cert.encode(), msg.encode(), hashlib.sha256
        ).hexdigest()
        token_data = base64.b64encode(
            f"006{self.app_id}{signature}{ts}".encode()
        ).decode()
        return token_data
