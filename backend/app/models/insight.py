"""Company and role intelligence gathered from public sources."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.company import Company
    from app.models.role import Role


class Insight(TimestampMixin, Base):
    __tablename__ = "insights"

    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), index=True
    )
    role_id: Mapped[int | None] = mapped_column(
        ForeignKey("roles.id", ondelete="CASCADE"), nullable=True, index=True
    )

    kind: Mapped[str] = mapped_column(String(50))
    title: Mapped[str] = mapped_column(String(300))
    summary: Mapped[str] = mapped_column(Text)
    source_url: Mapped[str] = mapped_column(String(2048))
    source_kind: Mapped[str] = mapped_column(String(50))
    confidence: Mapped[float] = mapped_column(Float, default=0.5)
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    company: Mapped["Company"] = relationship(back_populates="insights")
    role: Mapped["Role | None"] = relationship(back_populates="insights")
