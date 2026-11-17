from uuid import uuid4, UUID

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI()


class TaskSchema(BaseModel):
    id: UUID
    title: str
    is_completed: bool


class TaskCreateSchema(BaseModel):
    title: str


class TaskUpdateSchema(BaseModel):
    title: str | None = None
    is_completed: bool | None = None


tasks: list[TaskSchema] = []


@app.post(
    "/tasks",
    status_code=status.HTTP_201_CREATED,
    tags=["Tasks"])
def create_task(payload: TaskCreateSchema) -> TaskSchema:
    new_task = TaskSchema(id=uuid4(), title=payload.title, is_completed=False)
    tasks.append(new_task)
    return new_task


@app.get("/tasks", tags=["Tasks"])
def read_tasks() -> list[TaskSchema]:
    return tasks


@app.get(
    "/tasks/{task_id}",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Задача не найдена"}
    },
    tags=["Tasks"])
def read_task(task_id: UUID) -> TaskSchema:
    for task in tasks:
        if task.id == task_id:
            return task

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Задача не найдена."
    )


@app.patch(
    "/tasks/{task_id}",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Задача не найдена"}
    },
    tags=["Tasks"])
def update_task(task_id: UUID, payload: TaskUpdateSchema) -> TaskSchema:
    for task in tasks:
        if task.id == task_id:
            if payload.title is not None:
                task.title = payload.title
            if payload.is_completed is not None:
                task.is_completed = payload.is_completed
            return task

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Задача не найдена."
    )


@app.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Задача не найдена"}
    },
    tags=["Tasks"])
def delete_task(task_id: UUID):
    for task in tasks:
        if task.id == task_id:
            tasks.remove(task)
            return

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Задача не найдена."
    )
