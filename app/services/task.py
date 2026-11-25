from collections.abc import Sequence

from uuid import UUID

from sqlalchemy import select, delete, exists
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.cache import keys, RedisCache
from app.core.exceptions import TaskNotFoundError, CategoryNotFoundError
from app.models import TaskORM, CategoryORM

from app.schemas import TaskCreate, TaskRead, TaskUpdate


class TaskService:
    def __init__(self, session: AsyncSession, cache: RedisCache):
        self.session = session
        self.cache = cache

    async def create(self, task_create: TaskCreate) -> TaskRead:
        category_exists_stmt = select(exists().where(CategoryORM.id == task_create.category_id))
        category_exists = await self.session.scalar(category_exists_stmt)

        if not category_exists:
            raise CategoryNotFoundError(task_create.category_id)

        new_task_orm = TaskORM(**task_create.model_dump())

        self.session.add(new_task_orm)
        await self.session.commit()

        stmt = (
            select(TaskORM)
            .options(joinedload(TaskORM.category))
            .where(TaskORM.id == new_task_orm.id)
        )
        created_task_orm = await self.session.scalar(stmt)

        await self.cache.delete(keys.TASKS_KEY)

        return TaskRead.model_validate(created_task_orm)

    async def get_all(self) -> list[TaskRead]:
        cache_key = keys.TASKS_KEY
        cached_tasks: list[dict] | None = await self.cache.get(cache_key)

        if cached_tasks is not None:
            return [TaskRead.model_validate(task) for task in cached_tasks]

        stmt = (
            select(TaskORM)
            .options(joinedload(TaskORM.category))
        )
        tasks_orm: Sequence[TaskORM] = (await self.session.scalars(stmt)).all()

        tasks_read = [TaskRead.model_validate(task) for task in tasks_orm]
        await self.cache.set(cache_key, [task.model_dump(mode="json") for task in tasks_read])

        return tasks_read

    async def get_by_id(self, task_id: UUID) -> TaskRead:
        task_orm = await self.session.get(
            TaskORM,
            task_id,
            options=[joinedload(TaskORM.category)]
        )
        if task_orm is None:
            raise TaskNotFoundError(task_id)

        return TaskRead.model_validate(task_orm)

    async def update(self, task_id: UUID, task_update: TaskUpdate) -> TaskRead:
        task_orm = await self.session.get(
            TaskORM,
            task_id
        )
        if task_orm is None:
            raise TaskNotFoundError(task_id)

        if task_update.title is not None:
            task_orm.title = task_update.title
        if task_update.is_completed is not None:
            task_orm.is_completed = task_update.is_completed
        if task_update.category_id is not None:
            category_exists_stmt = select(exists().where(CategoryORM.id == task_update.category_id))
            category_exists = await self.session.scalar(category_exists_stmt)

            if not category_exists:
                raise CategoryNotFoundError(task_update.category_id)

            task_orm.category_id = task_update.category_id

        await self.session.commit()

        await self.cache.delete(keys.TASKS_KEY)

        stmt = (
            select(TaskORM)
            .options(joinedload(TaskORM.category))
            .where(TaskORM.id == task_orm.id)
        )
        updated_task = await self.session.scalar(stmt)

        return TaskRead.model_validate(updated_task)

    async def delete(self, task_id: UUID) -> None:
        stmt = (
            delete(TaskORM)
            .where(TaskORM.id == task_id)
            .returning(TaskORM.id)
        )

        deleted_id = await self.session.scalar(stmt)
        if deleted_id is None:
            raise TaskNotFoundError(task_id)

        await self.session.commit()

        await self.cache.delete(keys.TASKS_KEY)
