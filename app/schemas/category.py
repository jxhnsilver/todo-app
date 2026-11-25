from uuid import UUID

from pydantic import ConfigDict, BaseModel


class CategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str

class CategoryCreate(BaseModel):
    title: str


class CategoryUpdate(BaseModel):
    title: str | None = None
