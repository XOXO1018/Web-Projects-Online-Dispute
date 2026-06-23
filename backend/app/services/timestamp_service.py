"""
存证服务：SHA-256 哈希 + 时间戳 (Mock实现)
"""
import hashlib
import uuid
import logging
from datetime import datetime
from app.core.config import settings

logger = logging.getLogger(__name__)


class TimestampService:
    async def get_timestamp(self, file_hash: str, filename: str) -> dict:
        """获取时间戳证书和存证编号"""
        if settings.TIMESTAMP_SERVICE_PROVIDER == "mock":
            return self._mock_timestamp(file_hash, filename)
        return await self._real_timestamp(file_hash, filename)

    def _mock_timestamp(self, file_hash: str, filename: str) -> dict:
        """Mock存证 - 演示模式"""
        voucher = f"MOCK-{uuid.uuid4().hex[:12].upper()}"
        cert = f"MOCK_CERT_{datetime.now().strftime('%Y%m%d%H%M%S')}_{file_hash[:8]}"
        logger.info(f"[Mock存证] 文件: {filename}, 哈希: {file_hash[:16]}..., 存证号: {voucher}")
        return {"voucher": voucher, "cert": cert, "timestamp": datetime.now().isoformat()}

    async def _real_timestamp(self, file_hash: str, filename: str) -> dict:
        """对接真实存证API (预留)"""
        import httpx
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    settings.TIMESTAMP_API_URL,
                    headers={"Authorization": f"Bearer {settings.TIMESTAMP_API_KEY}"},
                    json={"hash": file_hash, "filename": filename},
                    timeout=10,
                )
                data = resp.json()
                return {"voucher": data.get("voucher_id"), "cert": data.get("cert_url")}
        except Exception as e:
            logger.error(f"存证API调用失败: {e}")
            return self._mock_timestamp(file_hash, filename)
