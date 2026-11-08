"""Weighted, deterministic ATS scoring built on rules and keyword matching."""

from dataclasses import asdict, dataclass
from typing import Any

from app.services.parsing.parser import ParsedResume
from app.services.scoring.keywords import match_keywords
from app.services.scoring.rules import (
    RuleFinding,
    evaluate_rules,
    format_score,
    impact_score,
    section_completeness,
)

WEIGHTS = {
    "keyword": 0.40,
    "sections": 0.25,
    "impact": 0.20,
    "format": 0.15,
}


@dataclass(frozen=True)
class ScoreBreakdown:
    overall: int
    keyword_coverage: float
    section_completeness: float
    impact_score: float
    format_score: float
    matched_keywords: tuple[str, ...]
    missing_keywords: tuple[str, ...]
    findings: tuple[RuleFinding, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "overall": self.overall,
            "keyword_coverage": round(self.keyword_coverage, 4),
            "section_completeness": round(self.section_completeness, 4),
            "impact_score": round(self.impact_score, 4),
            "format_score": round(self.format_score, 4),
            "weights": WEIGHTS,
            "matched_keywords": list(self.matched_keywords),
            "missing_keywords": list(self.missing_keywords),
            "findings": [asdict(finding) for finding in self.findings],
        }


def _keyword_coverage(matched: tuple[str, ...], missing: tuple[str, ...]) -> float:
    total = len(matched) + len(missing)
    if total == 0:
        return 1.0
    return len(matched) / total


def score_resume(parsed: ParsedResume, job_description: str) -> ScoreBreakdown:
    """Score a parsed resume against a job description.

    The same inputs always produce the same output; no LLM or randomness is
    involved. Sub-scores are weighted into an overall 0-100 readiness value.
    """
    matched, missing = match_keywords(parsed.raw_text, job_description)
    coverage = _keyword_coverage(matched, missing)
    sections = section_completeness(parsed)
    impact = impact_score(parsed)
    formatting = format_score(parsed)

    overall = round(
        100
        * (
            WEIGHTS["keyword"] * coverage
            + WEIGHTS["sections"] * sections
            + WEIGHTS["impact"] * impact
            + WEIGHTS["format"] * formatting
        )
    )

    findings = evaluate_rules(parsed, missing, coverage, impact, formatting)

    return ScoreBreakdown(
        overall=overall,
        keyword_coverage=coverage,
        section_completeness=sections,
        impact_score=impact,
        format_score=formatting,
        matched_keywords=matched,
        missing_keywords=missing,
        findings=findings,
    )
