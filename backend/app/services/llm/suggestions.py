"""Turn LLM output into validated suggestion drafts."""

import json
import re

from pydantic import BaseModel, Field, ValidationError

from app.services.llm.prompts import SYSTEM_PROMPT, build_user_prompt
from app.services.llm.providers import LLMError, LLMProvider
from app.services.parsing.parser import ParsedResume
from app.services.scoring.rules import Severity
from app.services.scoring.scorer import ScoreBreakdown

_CODE_FENCE_RE = re.compile(r"^```(?:json)?\s*|\s*```$", re.IGNORECASE)


class SuggestionDraft(BaseModel):
    category: str
    severity: Severity
    message: str = Field(min_length=1)
    proposed_text: str | None = None
    evidence: str | None = None


class _SuggestionEnvelope(BaseModel):
    suggestions: list[SuggestionDraft]


def _extract_json_payload(raw: str) -> object:
    cleaned = _CODE_FENCE_RE.sub("", raw.strip())
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise LLMError("LLM response was not valid JSON") from exc


def parse_suggestions(raw: str) -> list[SuggestionDraft]:
    """Parse and validate a provider response into suggestion drafts."""
    payload = _extract_json_payload(raw)

    try:
        if isinstance(payload, list):
            return [SuggestionDraft.model_validate(item) for item in payload]
        if isinstance(payload, dict):
            return _SuggestionEnvelope.model_validate(payload).suggestions
    except (ValidationError, TypeError) as exc:
        raise LLMError("LLM suggestions failed validation") from exc

    raise LLMError("LLM response did not contain suggestions")


def suggestions_from_findings(breakdown: ScoreBreakdown) -> list[SuggestionDraft]:
    """Deterministic suggestions used when no LLM key is available."""
    return [
        SuggestionDraft(
            category=finding.category,
            severity=finding.severity,
            message=finding.message,
            evidence=finding.evidence,
        )
        for finding in breakdown.findings
    ]


async def generate_suggestions(
    parsed: ParsedResume,
    job_description: str,
    breakdown: ScoreBreakdown,
    provider: LLMProvider,
) -> list[SuggestionDraft]:
    """Ask the provider for suggestions and return validated drafts."""
    user_prompt = build_user_prompt(parsed, job_description, breakdown)
    raw = await provider.complete(SYSTEM_PROMPT, user_prompt)
    return parse_suggestions(raw)
