"""Companies that users target."""

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.insight import Insight
    from app.models.job import Job


class Company(TimestampMixin, Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    domain: Mapped[str | None] = mapped_column(String(255), nullable=True)

    jobs: Mapped[list["Job"]] = relationship(back_populates="company")
    insights: Mapped[list["Insight"]] = relationship(
        back_populates="company", cascade="all, delete-orphan"
    )
