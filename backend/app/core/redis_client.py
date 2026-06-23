"""
Redis 客户端封装
"""
import redis.asyncio as aioredis
import logging
import json
from typing import Optional, Any

from app.core.config import settings

logger = logging.getLogger(__name__)


class RedisClient:
    def __init__(self):
        self._client: Optional[aioredis.Redis] = None

    async def connect(self):
        """建立 Redis 连接"""
        self._client = aioredis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD or None,
            db=settings.REDIS_DB,
            encoding="utf-8",
            decode_responses=True,
        )
        await self._client.ping()
        logger.info(f"Redis 连接成功: {settings.REDIS_HOST}:{settings.REDIS_PORT}")

    async def disconnect(self):
        if self._client:
            await self._client.close()

    async def get(self, key: str) -> Optional[str]:
        return await self._client.get(key)

    async def set(self, key: str, value: Any, expire: int = None):
        if isinstance(value, (dict, list)):
            value = json.dumps(value, ensure_ascii=False)
        if expire:
            await self._client.setex(key, expire, value)
        else:
            await self._client.set(key, value)

    async def delete(self, key: str):
        await self._client.delete(key)

    async def exists(self, key: str) -> bool:
        return bool(await self._client.exists(key))

    async def expire(self, key: str, seconds: int):
        await self._client.expire(key, seconds)

    async def get_json(self, key: str) -> Optional[dict]:
        val = await self.get(key)
        if val:
            return json.loads(val)
        return None

    async def incr(self, key: str) -> int:
        return await self._client.incr(key)

    async def hset(self, name: str, key: str, value: Any):
        await self._client.hset(name, key, json.dumps(value) if isinstance(value, dict) else value)

    async def hget(self, name: str, key: str) -> Optional[str]:
        return await self._client.hget(name, key)

    async def publish(self, channel: str, message: Any):
        """发布 WebSocket 消息"""
        if isinstance(message, dict):
            message = json.dumps(message, ensure_ascii=False)
        await self._client.publish(channel, message)

    async def get_client(self) -> aioredis.Redis:
        return self._client


redis_client = RedisClient()
