from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services import TaskService


@pytest.fixture
def mock_session() -> AsyncMock:
    session = AsyncMock()
    session.add = MagicMock()
    return session


@pytest.fixture
def mock_cache() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def task_service(mock_session, mock_cache) -> TaskService:
    return TaskService(session=mock_session, cache=mock_cache)
