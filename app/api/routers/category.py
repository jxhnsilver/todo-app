from uuid import UUID

from fastapi import APIRouter, status, HTTPException

from app.api.dependencies import CategoryServiceDep
from app.core.exceptions import CategoryNotFoundError, CategoryHasTasksError
from app.schemas import CategoryCreate, CategoryRead, CategoryUpdate

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_category(category_create: CategoryCreate, service: CategoryServiceDep) -> CategoryRead:
    return await service.create(category_create)


@router.get("")
async def get_categories(service: CategoryServiceDep) -> list[CategoryRead]:
    return await service.get_all()


@router.get(
    "/{category_id}",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Категория не найдена"}
    })
async def get_category(category_id: UUID, service: CategoryServiceDep) -> CategoryRead:
    try:
        return await service.get_by_id(category_id)
    except CategoryNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.patch(
    "/{category_id}",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Категория не найдена"}
    })
async def update_category(category_id: UUID, category_update: CategoryUpdate,
                          service: CategoryServiceDep) -> CategoryRead:
    try:
        return await service.update(category_id, category_update)
    except CategoryNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Категория не найдена"}
    })
async def delete_category(category_id: UUID, service: CategoryServiceDep):
    try:
        await service.delete(category_id)
    except CategoryNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except CategoryHasTasksError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
