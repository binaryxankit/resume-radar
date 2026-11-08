"""Analysis request and response schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class SuggestionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category: str
    severity: str
    message: str
    evidence: str | None = None
    proposed_text: str | None = None
    accepted_at: datetime | None = None


class AnalysisSummary(BaseModel):
    id: int
    company: str
    role: str
    job_title: str
    ats_score: int
    created_at: datetime


class AnalysisOut(BaseModel):
    id: int
    company: str
    role: str
    job_title: str
    ats_score: int
    score: dict[str, Any]
    matched_keywords: list[str]
    missing_keywords: list[str]
    sections: dict[str, list[str]]
    contact: dict[str, Any]
    suggestions: list[SuggestionOut]
    resume_id: int
    resume_version_id: int
    created_at: datetime


class ReanalyzeRequest(BaseModel):
    raw_text: str = Field(min_length=1, max_length=100_000)
