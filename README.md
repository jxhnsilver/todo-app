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
- Docker, Docker Compose
- Redis

## Запуск

Создайте файл `.env` из шаблона (общий шаг для обоих способов запуска):

```bash
cp .env.example .env
```

---

### 1. Полный запуск в Docker (Production-like)

Поднимает API, БД и Redis одной командой. Подходит для быстрой проверки и демо.

```bash
docker compose -f docker-compose.yaml up --build -d
```

---

### 2. Локальная разработка (БД в Docker, API локально)

БД в контейнере, API на хосте — для отладки и горячей перезагрузки.

1. Установите зависимости:

   ```bash
   uv sync
   ```

2. Создайте файл `.env.local` в корне проекта и добавьте в него только следующие строки (остальные переменные подтянутся из основного `.env`):

   ```env
   POSTGRES_HOST=localhost
   POSTGRES_PORT=15432
   REDIS_HOST=localhost
   REDIS_PORT=6379
   ```

3. Запустите базу данных и Redis в Docker (сервис migrator автоматически накатит все миграции при старте):

   ```bash
   docker compose --env-file .env --env-file .env.local -f docker-compose.local.yaml up --build -d
   ```

4. Запустите FastAPI-сервер локально:

   ```bash
   uv run uvicorn app.main:app --reload
   ```

---

## Документация API (Swagger)

Swagger UI доступен после запуска по адресу: http://localhost:8000/docs
