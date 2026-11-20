from uuid import UUID

from pydantic import BaseModel


class TaskRead(BaseModel):
    id: UUID
    title: str
    is_completed: bool


class TaskCreate(BaseModel):
    title: str


class TaskUpdate(BaseModel):
    title: str | None = None
    is_completed: bool | None = None
