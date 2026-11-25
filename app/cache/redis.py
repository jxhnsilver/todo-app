import json
import logging
from typing import Any

import redis.asyncio as redis

logger = logging.getLogger(__name__)


class RedisCache:
    DEFAULT_TTL = 300  # 5 min

    def __init__(self, redis_url: str):
        self.__redis = redis.from_url(
            url=redis_url,
            decode_responses=True,
            socket_connect_timeout=2.0,
            socket_timeout=2.0
        )

    async def get(self, key: str) -> Any | None:
        try:
            raw = await self.__redis.get(key)
            if not raw:
                return None
            return json.loads(raw)
        except redis.RedisError as e:
            logger.warning(f"Redis GET failed for key '{key}': {e}")
            return None

    async def set(self, key: str, value: Any, ttl: int = DEFAULT_TTL) -> None:
        try:
            serialized = json.dumps(value, ensure_ascii=False)
            await self.__redis.setex(key, ttl, serialized)
        except redis.RedisError as e:
            logger.warning(f"Redis SET failed for key '{key}': {e}")
            return None

    async def delete(self, key: str) -> None:
        try:
            await self.__redis.delete(key)
        except redis.RedisError as e:
            logger.warning(f"Redis DELETE failed for key '{key}': {e}")
            return None

    async def close(self):
        await self.__redis.aclose()
