from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache import RedisCache
from app.core.config import settings
from app.db import AsyncSessionLocal
from app.services import TaskService, CategoryService


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


DbAsyncSession = Annotated[AsyncSession, Depends(get_db)]

_redis_cache = RedisCache(settings.redis_url)


def get_redis() -> RedisCache:
    return _redis_cache


RedisCacheDep = Annotated[RedisCache, Depends(get_redis)]


def get_task_service(session: DbAsyncSession, cache: RedisCacheDep) -> TaskService:
    return TaskService(session=session, cache=cache)


TaskServiceDep = Annotated[TaskService, Depends(get_task_service)]


def get_category_service(session: DbAsyncSession, cache: RedisCacheDep) -> CategoryService:
    return CategoryService(session=session, cache=cache)


CategoryServiceDep = Annotated[CategoryService, Depends(get_category_service)]
