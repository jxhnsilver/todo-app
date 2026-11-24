from collections.abc import Sequence
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select, delete
from sqlalchemy.orm import joinedload

from app.cache import keys, RedisCacheDep
from app.core.database import DbSession
from app.core.exceptions import TaskNotFoundError
from app.models import TaskORM

from app.schemas.task import TaskCreate, TaskRead, TaskUpdate


class TaskService:
    def __init__(self, session: DbSession, cache: RedisCacheDep):
        self.session = session
        self.cache = cache

    def create(self, task_create: TaskCreate) -> TaskRead:
        new_task_orm = TaskORM(**task_create.model_dump())

        self.session.add(new_task_orm)
        self.session.commit()

        stmt = (
            select(TaskORM)
            .options(joinedload(TaskORM.category))
            .where(TaskORM.id == new_task_orm.id)
        )
        created_task_orm = self.session.scalar(stmt)

        self.cache.delete(keys.TASKS_KEY)

        return TaskRead.model_validate(created_task_orm)

    def get_all(self) -> list[TaskRead]:
        cache_key = keys.TASKS_KEY
        cached_tasks: list[dict] | None = self.cache.get(cache_key)

        if cached_tasks is not None:
            return [TaskRead.model_validate(task) for task in cached_tasks]

        stmt = (
            select(TaskORM)
            .options(joinedload(TaskORM.category))
        )
        tasks_orm: Sequence[TaskORM] = self.session.scalars(stmt).all()

        tasks_read = [TaskRead.model_validate(task) for task in tasks_orm]
        self.cache.set(cache_key, [task.model_dump(mode="json") for task in tasks_read])

        return tasks_read

    def get_by_id(self, task_id: UUID) -> TaskRead:
        task_orm = self.session.get(
            TaskORM,
            task_id,
            options=[joinedload(TaskORM.category)]
        )
        if task_orm is None:
            raise TaskNotFoundError(task_id)

        return TaskRead.model_validate(task_orm)

    def update(self, task_id: UUID, task_update: TaskUpdate) -> TaskRead:
        task_orm = self.session.get(
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
            task_orm.category_id = task_update.category_id

        self.session.commit()

        self.cache.delete(keys.TASKS_KEY)

        stmt = (
            select(TaskORM)
            .options(joinedload(TaskORM.category))
            .where(TaskORM.id == task_orm.id)
        )
        updated_task = self.session.scalar(stmt)

        return TaskRead.model_validate(updated_task)

    def delete(self, task_id: UUID):
        stmt = (
            delete(TaskORM)
            .where(TaskORM.id == task_id)
            .returning(TaskORM.id)
        )

        deleted_id = self.session.scalar(stmt)
        if deleted_id is None:
            raise TaskNotFoundError(task_id)

        self.session.commit()

        self.cache.delete(keys.TASKS_KEY)


TaskServiceDep = Annotated[TaskService, Depends()]
