from collections.abc import Sequence
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select, delete, exists

from app.cache import RedisCacheDep, keys
from app.core.database import DbSession
from app.core.exceptions import CategoryNotFoundError, CategoryHasTasksError
from app.models import TaskORM
from app.models.category import CategoryORM
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate


class CategoryService:
    def __init__(self, session: DbSession, cache: RedisCacheDep):
        self.session = session
        self.cache = cache

    def create(self, category_create: CategoryCreate) -> CategoryRead:
        new_category_orm = CategoryORM(**category_create.model_dump())

        self.session.add(new_category_orm)
        self.session.commit()

        stmt = (
            select(CategoryORM)
            .where(CategoryORM.id == new_category_orm.id)
        )
        created_category_orm = self.session.scalar(stmt)

        return CategoryRead.model_validate(created_category_orm)

    def get_all(self) -> list[CategoryRead]:
        categories_orm: Sequence[CategoryORM] = self.session.scalars(select(CategoryORM)).all()
        return [CategoryRead.model_validate(category) for category in categories_orm]

    def get_by_id(self, category_id: UUID) -> CategoryRead:
        category_orm = self.session.get(CategoryORM, category_id)
        if not category_orm:
            raise CategoryNotFoundError(category_id)

        return CategoryRead.model_validate(category_orm)

    def update(self, category_id: UUID, category_update: CategoryUpdate) -> CategoryRead:
        category_orm = self.session.get(CategoryORM, category_id)
        if not category_orm:
            raise CategoryNotFoundError(category_id)

        if category_update.title:
            category_orm.title = category_update.title

        self.session.commit()

        self.cache.delete(keys.TASKS_KEY)

        return CategoryRead.model_validate(category_orm)

    def delete(self, category_id: UUID):
        has_task_stmt = select(exists().where(TaskORM.category_id == category_id))
        has_tasks = self.session.scalar(has_task_stmt)
        if has_tasks:
            raise CategoryHasTasksError(category_id)

        delete_stmt = (
            delete(CategoryORM)
            .where(CategoryORM.id == category_id)
            .returning(CategoryORM.id)
        )

        deleted_id = self.session.scalar(delete_stmt)
        if not deleted_id:
            raise CategoryNotFoundError(category_id)

        self.session.commit()


CategoryServiceDep = Annotated[CategoryService, Depends()]
