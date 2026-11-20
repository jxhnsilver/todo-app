from collections.abc import Sequence
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select

from app.core.database import DbSession
from app.core.exceptions import TaskNotFoundError
from app.models.task import TaskORM

from app.schemas.task import TaskCreate, TaskRead, TaskUpdate


class TaskService:
    def __init__(self, session: DbSession):
        self.session = session

    def create(self, task_create: TaskCreate) -> TaskRead:
        new_task_orm = TaskORM(title=task_create.title, is_completed=False)
        self.session.add(new_task_orm)
        self.session.commit()

        return TaskRead(
            id=new_task_orm.id,
            title=new_task_orm.title,
            is_completed=new_task_orm.is_completed,
        )

    def get_all(self) -> list[TaskRead]:
        tasks_from_db: Sequence[TaskORM] = self.session.scalars(select(TaskORM)).all()
        return [TaskRead(
            id=task.id,
            title=task.title,
            is_completed=task.is_completed
        ) for task in tasks_from_db]

    def get_by_id(self, task_id: UUID) -> TaskRead:
        task_from_db: TaskORM | None = self.session.scalar(select(TaskORM).where(TaskORM.id == task_id))

        if not task_from_db:
            raise TaskNotFoundError(task_id)

        return TaskRead(
            id=task_from_db.id,
            title=task_from_db.title,
            is_completed=task_from_db.is_completed,
        )

    def update(self, task_id: UUID, task_update: TaskUpdate) -> TaskRead:
        task_from_db: TaskORM | None = self.session.scalar(select(TaskORM).where(TaskORM.id == task_id))

        if not task_from_db:
            raise TaskNotFoundError(task_id)

        if task_update.title:
            task_from_db.title = task_update.title
        if task_update.is_completed:
            task_from_db.is_completed = task_update.is_completed

        self.session.commit()

        return TaskRead(
            id=task_from_db.id,
            title=task_from_db.title,
            is_completed=task_from_db.is_completed,
        )

    def delete(self, task_id: UUID):
        task_from_db = self.session.get(TaskORM, task_id)

        if not task_from_db:
            raise TaskNotFoundError(task_id)

        self.session.delete(task_from_db)
        self.session.commit()


TaskServiceDep = Annotated[TaskService, Depends()]
