from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.cache import RedisCache
from app.core.config import settings
from app.db import SessionLocal
from app.services import TaskService, CategoryService


def get_db() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        yield session


DbSession = Annotated[Session, Depends(get_db)]

_redis_cache = RedisCache(settings.redis_url)


def get_redis() -> RedisCache:
    return _redis_cache


RedisCacheDep = Annotated[RedisCache, Depends(get_redis)]


def get_task_service(session: DbSession, cache: RedisCacheDep) -> TaskService:
    return TaskService(session=session, cache=cache)


TaskServiceDep = Annotated[TaskService, Depends(get_task_service)]


def get_category_service(session: DbSession, cache: RedisCacheDep) -> CategoryService:
    return CategoryService(session=session, cache=cache)


CategoryServiceDep = Annotated[CategoryService, Depends(get_category_service)]
