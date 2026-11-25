from uuid import UUID

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.category import CategoryORM


class TaskORM(Base):
    __tablename__ = "tasks"

    category_id: Mapped[UUID] = mapped_column(ForeignKey("categories.id", ondelete="RESTRICT"))
    title: Mapped[str] = mapped_column(String(200))
    is_completed: Mapped[bool] = mapped_column(default=False)

    category: Mapped[CategoryORM] = relationship()
