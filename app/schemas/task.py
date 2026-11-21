from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.schemas.category import CategoryRead


class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    is_completed: bool
    category: CategoryRead


class TaskCreate(BaseModel):
    category_id: UUID
    title: str


class TaskUpdate(BaseModel):
    title: str | None = None
    is_completed: bool | None = None
    category_id: UUID | None = None
