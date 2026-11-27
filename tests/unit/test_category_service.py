from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from app.cache import keys
from app.core.exceptions import CategoryNotFoundError, CategoryHasTasksError
from app.models import CategoryORM
from app.schemas import CategoryCreate, CategoryRead, CategoryUpdate
from tests.conftest import mock_session


class TestCategoryServiceCreate:
    async def test_create_category_success(self, category_service, mock_session):
        title = "Test category"
        category_create = CategoryCreate(title=title)

        category_orm = CategoryORM(
            id=uuid4(),
            title=title
        )

        mock_session.scalar.return_value = category_orm

        result = await category_service.create(category_create)

        assert isinstance(result, CategoryRead)
        assert result.id == category_orm.id
        assert result.title == category_orm.title

        mock_session.add.assert_called_once()
        mock_session.commit.assert_awaited_once()


class TestCategoryServiceGetAll:
    async def test_get_all_categories_success(self, category_service, mock_session):
        category_orm_1 = CategoryORM(id=uuid4(), title="Test category 1")
        category_orm_2 = CategoryORM(id=uuid4(), title="Test category 2")

        mock_scalars_result = MagicMock()
        mock_scalars_result.all.return_value = [category_orm_1, category_orm_2]
        mock_session.scalars.return_value = mock_scalars_result

        result = await category_service.get_all()

        assert isinstance(result, list)
        assert len(result) == 2
        assert isinstance(result[0], CategoryRead)
        assert isinstance(result[1], CategoryRead)
        assert result[0].id == category_orm_1.id
        assert result[1].id == category_orm_2.id

        mock_session.scalars.assert_awaited_once()


class TestCategoryServiceGetById:
    async def test_get_category_by_id_success(self, category_service, mock_session):
        category_id = uuid4()
        category_orm = CategoryORM(id=category_id, title="Test title")

        mock_session.get.return_value = category_orm

        result = await category_service.get_by_id(category_id)

        assert isinstance(result, CategoryRead)
        assert result.id == category_orm.id
        assert result.title == category_orm.title

        mock_session.get.assert_awaited_once_with(CategoryORM, category_id)

    async def test_get_category_by_id_not_found(self, category_service, mock_session):
        category_id = uuid4()
        mock_session.get.return_value = None

        with pytest.raises(CategoryNotFoundError) as e:
            await category_service.get_by_id(category_id)

        assert str(category_id) in str(e.value)

        mock_session.get.assert_awaited_once_with(CategoryORM, category_id)


class TestCategoryServiceUpdate:
    @pytest.mark.parametrize(
        "update_data",
        [
            {"title": "New title"}
        ],
        ids=["only_title"]
    )
    async def test_update_category_success(
            self,
            category_service,
            mock_session,
            mock_cache,
            update_data: dict
    ):
        category_id = uuid4()
        category_orm = CategoryORM(id=category_id, title="Old title")

        category_update = CategoryUpdate(**update_data)

        expected_title = update_data.get("title", category_orm.title)

        mock_session.get.return_value = category_orm

        result = await category_service.update(category_id, category_update)

        assert isinstance(result, CategoryRead)
        assert result.title == expected_title

        mock_session.commit.assert_awaited_once()
        mock_cache.delete.assert_awaited_once_with(keys.TASKS_KEY)

    async def test_update_category_not_found(
            self,
            category_service,
            mock_session,
            mock_cache
    ):
        category_id = uuid4()
        category_update = CategoryUpdate(title="new title")
        mock_session.get.return_value = None

        with pytest.raises(CategoryNotFoundError) as e:
            await category_service.update(category_id, category_update)

        assert str(category_id) in str(e.value)
        mock_session.get.assert_awaited_once_with(CategoryORM, category_id)
        mock_session.commit.assert_not_awaited()
        mock_cache.delete.assert_not_awaited()


class TestCategoryServiceDelete:
    async def test_delete_category_success(
            self,
            category_service,
            mock_session
    ):
        category_id = uuid4()
        mock_session.scalar.side_effect = [False, category_id]

        result = await category_service.delete(category_id)

        assert result is None
        assert mock_session.scalar.await_count == 2
        mock_session.commit.assert_awaited_once()

    async def test_delete_category_not_found(self, category_service, mock_session):
        category_id = uuid4()
        mock_session.scalar.side_effect = [False, None]

        with pytest.raises(CategoryNotFoundError) as e:
            await category_service.delete(category_id)

        assert str(category_id) in str(e.value)
        assert mock_session.scalar.await_count == 2

    async def test_delete_category_has_tasks(self, category_service, mock_session):
        category_id = uuid4()
        mock_session.scalar.return_value = True

        with pytest.raises(CategoryHasTasksError) as e:
            await category_service.delete(category_id)

        assert str(category_id) in str(e.value)
        mock_session.scalar.assert_awaited_once()
