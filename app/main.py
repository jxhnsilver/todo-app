from collections.abc import Sequence
from uuid import UUID

from fastapi import FastAPI, HTTPException, status
from sqlalchemy import select

from app.database import DbSession
from app.models import TaskORM
from app.schemas import TaskReadSchema, TaskCreateSchema, TaskUpdateSchema

app = FastAPI()


@app.post(
    "/tasks",
    status_code=status.HTTP_201_CREATED,
    tags=["Tasks"])
def create_task(payload: TaskCreateSchema, session: DbSession) -> TaskReadSchema:
    new_task_orm = TaskORM(title=payload.title, is_completed=False)
    session.add(new_task_orm)
    session.commit()

    return TaskReadSchema(
        id=new_task_orm.id,
        title=new_task_orm.title,
        is_completed=new_task_orm.is_completed,
    )


@app.get("/tasks", tags=["Tasks"])
def read_tasks(session: DbSession) -> list[TaskReadSchema]:
    tasks_from_db: Sequence[TaskORM] = session.scalars(select(TaskORM)).all()
    return [TaskReadSchema(
        id=task.id,
        title=task.title,
        is_completed=task.is_completed
    ) for task in tasks_from_db]


@app.get(
    "/tasks/{task_id}",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Задача не найдена"}
    },
    tags=["Tasks"])
def read_task(task_id: UUID, session: DbSession) -> TaskReadSchema:
    task_from_db: TaskORM | None = session.scalar(select(TaskORM).where(TaskORM.id == task_id))

    if not task_from_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задача не найдена."
        )

    return TaskReadSchema(
        id=task_from_db.id,
        title=task_from_db.title,
        is_completed=task_from_db.is_completed,
    )


@app.patch(
    "/tasks/{task_id}",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Задача не найдена"}
    },
    tags=["Tasks"])
def update_task(task_id: UUID, payload: TaskUpdateSchema, session: DbSession) -> TaskReadSchema:
    task_from_db: TaskORM | None = session.scalar(select(TaskORM).where(TaskORM.id == task_id))

    if not task_from_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задача не найдена."
        )

    if payload.title:
        task_from_db.title = payload.title
    if payload.is_completed:
        task_from_db.is_completed = payload.is_completed

    session.commit()

    return TaskReadSchema(
        id=task_from_db.id,
        title=task_from_db.title,
        is_completed=task_from_db.is_completed,
    )


@app.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Задача не найдена"}
    },
    tags=["Tasks"])
def delete_task(task_id: UUID, session: DbSession):
    task_from_db = session.get(TaskORM, task_id)

    if not task_from_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задача не найдена."
        )

    session.delete(task_from_db)
    session.commit()
