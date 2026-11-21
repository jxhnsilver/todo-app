from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class CategoryORM(Base):
    __tablename__ = "categories"

    title: Mapped[str] = mapped_column(String(100))
