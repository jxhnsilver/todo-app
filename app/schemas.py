from uuid import UUID

from pydantic import BaseModel


class TaskReadSchema(BaseModel):
    id: UUID
    title: str
    is_completed: bool


class TaskCreateSchema(BaseModel):
    title: str


class TaskUpdateSchema(BaseModel):
    title: str | None = None
    is_completed: bool | None = None
