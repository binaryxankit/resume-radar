"""Role definitions such as Backend Engineer or Senior Data Scientist."""

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.insight import Insight
    from app.models.job import Job


class Role(TimestampMixin, Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    level: Mapped[str | None] = mapped_column(String(50), nullable=True)

    jobs: Mapped[list["Job"]] = relationship(back_populates="role")
    insights: Mapped[list["Insight"]] = relationship(
        back_populates="role", cascade="all, delete-orphan"
    )
