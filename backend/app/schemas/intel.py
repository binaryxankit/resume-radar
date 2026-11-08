"""Intelligence response schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class InsightOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    kind: str
    title: str
    summary: str
    source_url: str
    source_kind: str
    confidence: float
    fetched_at: datetime


class IntelResponse(BaseModel):
    company: str
    role: str | None
    cached: bool
    source_available: bool
    insights: list[InsightOut]
