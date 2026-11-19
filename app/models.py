from uuid import uuid4, UUID

from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    id: Mapped[UUID] = mapped_column(primary_key=True, default=lambda: uuid4())


class TaskORM(Base):
    __tablename__ = "tasks"
    title: Mapped[str] = mapped_column(String(200))
    is_completed: Mapped[bool] = mapped_column(default=False)
