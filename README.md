# todo-app

REST API сервис для управления списком задач.

## Технологии

- Python 3.14+
- FastAPI
- PostgreSQL
- SQLAlchemy 2.0
- Alembic
- Pydantic, Pydantic Settings
- uv

## Локальный запуск

1. Установите зависимости:
   ```bash
   uv sync
   ```

2. Создайте файл `.env`:
   ```bash
   cp .env.example .env
   ```

3. Запустите PostgreSQL в Docker:
   ```bash
   docker run -d --rm --name todo-postgres -p 15432:5432 -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=todo_app_db postgres:18-alpine
   ```

4. Примените миграции:
   ```bash
   uv run alembic upgrade head
   ```

5. Запустите сервер:
   ```bash
   uv run uvicorn app.main:app --reload
   ```

Документация API (Swagger): http://127.0.0.1:8000/docs
