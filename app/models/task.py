from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class TaskORM(Base):
    __tablename__ = "tasks"
    title: Mapped[str] = mapped_column(String(200))
    is_completed: Mapped[bool] = mapped_column(default=False)
