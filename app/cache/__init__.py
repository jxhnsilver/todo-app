from typing import Annotated
from fastapi import Depends

from app.cache.redis import RedisCache
from app.core.config import settings

cache = RedisCache(settings.redis_url)


def get_cache() -> RedisCache:
    return cache


RedisCacheDep = Annotated[RedisCache, Depends(get_cache)]
