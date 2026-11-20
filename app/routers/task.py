from uuid import UUID

from fastapi import APIRouter, status, HTTPException

from app.core.exceptions import TaskNotFoundError
from app.schemas.task import TaskRead, TaskCreate, TaskUpdate

from app.services.task import TaskServiceDep

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("", status_code=status.HTTP_201_CREATED)
def create_task(task_create: TaskCreate, service: TaskServiceDep) -> TaskRead:
    return service.create(task_create)


@router.get("")
def get_tasks(service: TaskServiceDep) -> list[TaskRead]:
    return service.get_all()


@router.get(
    "/{task_id}",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Задача не найдена"}
    })
def get_task(task_id: UUID, service: TaskServiceDep) -> TaskRead:
    try:
        return service.get_by_id(task_id)
    except TaskNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.patch(
    "/{task_id}",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Задача не найдена"}
    })
def update_task(task_id: UUID, task_update: TaskUpdate, service: TaskServiceDep) -> TaskRead:
    try:
        return service.update(task_id, task_update)
    except TaskNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Задача не найдена"}
    })
def delete_task(task_id: UUID, service: TaskServiceDep):
    try:
        return service.delete(task_id)
    except TaskNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
