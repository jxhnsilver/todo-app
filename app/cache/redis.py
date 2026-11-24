import json
import logging
from typing import Any

import redis

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

    def get(self, key: str) -> Any | None:
        try:
            raw = self.__redis.get(key)
            if not raw:
                return None
            return json.loads(raw)
        except redis.RedisError as e:
            logger.warning(f"Redis GET failed for key '{key}': {e}")
            return None

    def set(self, key: str, value: Any, ttl: int = DEFAULT_TTL) -> None:
        try:
            serialized = json.dumps(value)
            self.__redis.setex(key, ttl, serialized)
        except redis.RedisError as e:
            logger.warning(f"Redis SET failed for key '{key}': {e}")
            return None

    def delete(self, key: str) -> None:
        try:
            self.__redis.delete(key)
        except redis.RedisError as e:
            logger.warning(f"Redis DELETE failed for key '{key}': {e}")
            return  None
