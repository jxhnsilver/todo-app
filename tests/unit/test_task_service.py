from unittest.mock import MagicMock, ANY
from uuid import uuid4

import pytest

from app.cache import keys
from app.core.exceptions import CategoryNotFoundError, TaskNotFoundError
from app.models import TaskORM, CategoryORM
from app.schemas import TaskCreate, TaskRead, TaskUpdate
from tests.conftest import mock_cache, mock_session


class TestTaskServiceCreate:
    async def test_create_task_success(
            self,
            task_service,
            mock_session,
            mock_cache
    ):
        category_id = uuid4()
        task_title = "Test task"

        task_create = TaskCreate(
            category_id=category_id,
            title=task_title
        )

        task_orm = TaskORM(
            id=uuid4(),
            category_id=category_id,
            title=task_title,
            is_completed=False,
            category=CategoryORM(id=category_id, title="Test category")
        )

        mock_session.scalar.side_effect = [True, task_orm]

        result = await task_service.create(task_create)

        assert isinstance(result, TaskRead)
        assert result.id == task_orm.id
        assert result.title == task_orm.title
        assert result.is_completed == task_orm.is_completed
        assert result.category.id == task_orm.category.id
        assert result.category.title == task_orm.category.title

        mock_session.add.assert_called_once()
        mock_session.commit.assert_awaited_once()
        mock_cache.delete.assert_awaited_once_with(keys.TASKS_KEY)

    async def test_create_task_category_not_found(
            self,
            task_service,
            mock_session,
            mock_cache
    ):
        category_id = uuid4()
        task_create = TaskCreate(category_id=category_id, title="Test task")

        mock_session.scalar.return_value = False

        with pytest.raises(CategoryNotFoundError) as e:
            await task_service.create(task_create)

        assert str(category_id) in str(e.value)

        mock_session.add.assert_not_called()
        mock_session.commit.assert_not_awaited()
        mock_cache.delete.assert_not_awaited()


class TestTaskServiceGetAll:
    async def test_get_all_tasks_from_db(
            self,
            task_service,
            mock_session,
            mock_cache
    ):
        mock_cache.get.return_value = None

        category_id_1 = uuid4()
        task_orm_1 = TaskORM(
            id=uuid4(),
            category_id=category_id_1,
            title="Task from db 1",
            is_completed=False,
            category=CategoryORM(id=category_id_1, title="Test category 1")
        )

        category_id_2 = uuid4()
        task_orm_2 = TaskORM(
            id=uuid4(),
            category_id=category_id_2,
            title="Task from db 2",
            is_completed=False,
            category=CategoryORM(id=category_id_2, title="Test category 2")
        )

        mock_scalars_result = MagicMock()
        mock_scalars_result.all.return_value = [task_orm_1, task_orm_2]
        mock_session.scalars.return_value = mock_scalars_result

        result = await task_service.get_all()

        assert isinstance(result, list)
        assert len(result) == 2
        assert isinstance(result[0], TaskRead)
        assert isinstance(result[1], TaskRead)
        assert result[0].id == task_orm_1.id
        assert result[1].id == task_orm_2.id

        mock_cache.get.assert_awaited_once_with(keys.TASKS_KEY)
        mock_session.scalars.assert_awaited_once()
        mock_cache.set.assert_awaited_once_with(
            keys.TASKS_KEY,
            [task.model_dump(mode="json") for task in result],
        )

    async def test_get_all_tasks_from_cache(self, task_service, mock_session, mock_cache):
        task_id = uuid4()
        task_title = "Cached task"
        category_id = uuid4()

        cached_data = [
            {
                "id": str(task_id),
                "title": task_title,
                "is_completed": False,
                "category": {
                    "id": str(category_id),
                    "title": "Test category"
                }
            },
        ]
        mock_cache.get.return_value = cached_data

        result = await task_service.get_all()

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TaskRead)
        assert result[0].id == task_id
        assert result[0].title == task_title
        assert result[0].category.id == category_id

        mock_cache.get.assert_awaited_once_with(keys.TASKS_KEY)
        mock_session.scalars.assert_not_awaited()
        mock_cache.set.assert_not_awaited()


class TestTaskServiceGetById:
    async def test_get_task_by_id_success(self, task_service, mock_session):
        task_id = uuid4()
        category_id = uuid4()
        task_orm = TaskORM(
            id=task_id,
            category_id=category_id,
            title="Test task",
            is_completed=False,
            category=CategoryORM(id=category_id, title="Test category")
        )

        mock_session.get.return_value = task_orm

        result = await task_service.get_by_id(task_id)

        assert isinstance(result, TaskRead)
        assert result.id == task_id
        assert result.title == task_orm.title
        assert result.is_completed == task_orm.is_completed
        assert result.category.id == task_orm.category.id
        assert result.category.title == task_orm.category.title

        mock_session.get.assert_awaited_once_with(
            TaskORM,
            task_orm.id,
            options=ANY,
        )

    async def test_get_task_by_id_not_found(self, task_service, mock_session):
        task_id = uuid4()
        mock_session.get.return_value = None

        with pytest.raises(TaskNotFoundError) as e:
            await task_service.get_by_id(task_id)

        assert str(task_id) in str(e.value)

        mock_session.get.assert_awaited_once_with(
            TaskORM,
            task_id,
            options=ANY,
        )


class TestTaskServiceUpdate:
    @pytest.mark.parametrize(
        "update_data",
        [
            {"title": "New title", "is_completed": True, "category_id": uuid4()},
            {"title": "Only title"},
            {"is_completed": True},
            {"category_id": uuid4()},
        ],
        ids=["all_fields", "only_title", "only_is_completed", "only_category_id"],
    )
    async def test_update_task_success(
            self,
            task_service,
            mock_session,
            mock_cache,
            update_data: dict,
    ):
        category_id = uuid4()
        task_orm = TaskORM(
            id=uuid4(),
            title="Old title",
            is_completed=False,
            category_id=category_id,
            category=CategoryORM(id=category_id, title="Test category")
        )
        task_update = TaskUpdate(**update_data)

        expected_title = update_data.get("title", task_orm.title)
        expected_completed = update_data.get("is_completed", task_orm.is_completed)
        expected_category_id = update_data.get("category_id", task_orm.category_id)

        updated_category = CategoryORM(id=expected_category_id, title="Test category")
        updated_task_orm = TaskORM(
            id=task_orm.id,
            title=expected_title,
            is_completed=expected_completed,
            category=updated_category,
        )

        mock_session.get.return_value = task_orm

        if "category_id" in update_data:
            mock_session.scalar.side_effect = [True, updated_task_orm]
        else:
            mock_session.scalar.return_value = updated_task_orm

        result = await task_service.update(task_orm.id, task_update)

        assert task_orm.title == expected_title
        assert task_orm.is_completed is expected_completed
        assert task_orm.category_id == expected_category_id

        assert result.title == expected_title
        assert result.is_completed is expected_completed
        assert result.category.id == expected_category_id

        mock_session.commit.assert_awaited_once()
        mock_cache.delete.assert_awaited_once_with(keys.TASKS_KEY)

    async def test_update_task_not_found(self, task_service, mock_session, mock_cache):
        task_id = uuid4()
        task_update = TaskUpdate(category_id=uuid4(), title="new title", is_completed=True)
        mock_session.get.return_value = None

        with pytest.raises(TaskNotFoundError) as e:
            await task_service.update(task_id, task_update)

        assert str(task_id) in str(e.value)
        mock_session.get.assert_awaited_once_with(TaskORM, task_id)
        mock_session.scalar.assert_not_awaited()
        mock_session.commit.assert_not_awaited()
        mock_cache.delete.assert_not_awaited()

    async def test_update_task_category_not_found(
            self,
            task_service,
            mock_session,
            mock_cache
    ):
        task_orm = TaskORM(
            id=uuid4(),
            category_id=uuid4(),
            title="Test task",
            is_completed=False,
            category=CategoryORM(id=uuid4(), title="Test category")
        )
        missing_category_id = uuid4()
        task_update = TaskUpdate(category_id=missing_category_id)

        mock_session.get.return_value = task_orm
        mock_session.scalar.return_value = False

        with pytest.raises(CategoryNotFoundError) as e:
            await task_service.update(task_orm.id, task_update)

        assert str(missing_category_id) in str(e.value)
        mock_session.get.assert_awaited_once_with(TaskORM, task_orm.id)
        mock_session.scalar.assert_awaited_once()
        mock_session.commit.assert_not_awaited()
        mock_cache.delete.assert_not_awaited()


class TestTaskServiceDelete:
    async def test_delete_task_success(self, task_service, mock_session, mock_cache):
        task_id = uuid4()
        mock_session.scalar.return_value = task_id

        result = await task_service.delete(task_id)

        assert result is None
        mock_session.scalar.assert_awaited_once()
        mock_session.commit.assert_awaited_once()
        mock_cache.delete.assert_awaited_once_with(keys.TASKS_KEY)

    async def test_delete_task_not_found(self, task_service, mock_session, mock_cache):
        task_id = uuid4()
        mock_session.scalar.return_value = None

        with pytest.raises(TaskNotFoundError) as e:
            await task_service.delete(task_id)

        assert str(task_id) in str(e.value)
        mock_session.scalar.assert_awaited_once()
        mock_session.commit.assert_not_awaited()
        mock_cache.delete.assert_not_awaited()
