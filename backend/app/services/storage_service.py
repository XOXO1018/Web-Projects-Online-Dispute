"""
文件存储服务：本地存储 / OSS
"""
import os
import uuid
import aiofiles
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class StorageService:
    def __init__(self):
        self.storage_type = settings.STORAGE_TYPE
        self.local_path = settings.STORAGE_LOCAL_PATH

    async def save(self, filename: str, content: bytes, prefix: str = "") -> str:
        """保存文件，返回访问 URL"""
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "bin"
        new_name = f"{uuid.uuid4().hex}.{ext}"
        if self.storage_type == "local":
            return await self._save_local(new_name, content, prefix)
        elif self.storage_type == "oss":
            return await self._save_oss(new_name, content, prefix)
        return await self._save_local(new_name, content, prefix)

    async def _save_local(self, filename: str, content: bytes, prefix: str) -> str:
        dir_path = os.path.join(self.local_path, prefix)
        os.makedirs(dir_path, exist_ok=True)
        file_path = os.path.join(dir_path, filename)
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(content)
        return f"/uploads/{prefix}/{filename}"

    async def _save_oss(self, filename: str, content: bytes, prefix: str) -> str:
        """上传到阿里云OSS (生产环境)"""
        try:
            import oss2
            auth = oss2.Auth(settings.OSS_ACCESS_KEY_ID, settings.OSS_ACCESS_KEY_SECRET)
            bucket = oss2.Bucket(auth, settings.OSS_ENDPOINT, settings.OSS_BUCKET_NAME)
            key = f"{prefix}/{filename}"
            bucket.put_object(key, content)
            return f"https://{settings.OSS_BUCKET_NAME}.{settings.OSS_ENDPOINT}/{key}"
        except Exception as e:
            logger.error(f"OSS上传失败，降级到本地存储: {e}")
            return await self._save_local(filename, content, prefix)
