"""Prompt construction for resume suggestions."""

from app.services.parsing.parser import ParsedResume
from app.services.scoring.scorer import ScoreBreakdown

SYSTEM_PROMPT = """You are a precise resume editor and ATS analyst.
You receive a resume, a job description and a deterministic score breakdown.
Return actionable edits only, grounded in the provided text.

Respond with a JSON object of the form:
{"suggestions": [
  {"category": "keyword|section|impact|format|contact",
   "severity": "critical|warning|info",
   "message": "what to change and why, in one or two sentences",
   "proposed_text": "concrete replacement text, or null",
   "evidence": "short quote or signal from the resume/job description, or null"}
]}

Rules:
- Never invent employers, degrees, metrics or experience the candidate does not have.
- Prefer quantified, role-relevant phrasing when rewriting.
- Maximum 8 suggestions, highest impact first.
- Do not output anything outside the JSON object."""

_MAX_RESUME_CHARS = 6000
_MAX_JOB_CHARS = 4000


def build_user_prompt(
    parsed: ParsedResume,
    job_description: str,
    breakdown: ScoreBreakdown,
) -> str:
    """Compose the user prompt from structured scoring context."""
    matched = ", ".join(breakdown.matched_keywords) or "(none)"
    missing = ", ".join(breakdown.missing_keywords) or "(none)"

    return (
        "JOB DESCRIPTION\n"
        f"{job_description[:_MAX_JOB_CHARS]}\n\n"
        "RESUME TEXT\n"
        f"{parsed.raw_text[:_MAX_RESUME_CHARS]}\n\n"
        "SCORE BREAKDOWN\n"
        f"overall: {breakdown.overall}\n"
        f"keyword coverage: {round(breakdown.keyword_coverage * 100)}%\n"
        f"matched keywords: {matched}\n"
        f"missing keywords: {missing}\n"
        f"impact score: {round(breakdown.impact_score * 100)}%\n"
        f"format score: {round(breakdown.format_score * 100)}%\n"
    )
