"""Structural and formatting rules applied to a parsed resume."""

import re
from dataclasses import dataclass

from app.services.parsing.parser import ParsedResume

REQUIRED_SECTIONS = ("experience", "education", "skills")

_BULLET_RE = re.compile(r"^\s*[-*•·]\s+(.*)$")
_NUMBER_RE = re.compile(r"\d")


@dataclass(frozen=True)
class RuleFinding:
    category: str
    severity: str
    message: str
    evidence: str | None = None


def section_completeness(parsed: ParsedResume) -> float:
    """Fraction of required sections present, with a small optional bonus."""
    present_required = sum(key in parsed.sections for key in REQUIRED_SECTIONS)
    required_ratio = present_required / len(REQUIRED_SECTIONS)

    optional = ("summary", "projects", "certifications")
    optional_ratio = sum(key in parsed.sections for key in optional) / len(optional)

    return min(1.0, required_ratio * 0.85 + optional_ratio * 0.15)


def _experience_bullets(parsed: ParsedResume) -> list[str]:
    lines = list(parsed.sections.get("experience", ()))
    bullets: list[str] = []
    for line in lines:
        match = _BULLET_RE.match(line)
        if match:
            bullets.append(match.group(1).strip())
    if bullets:
        return bullets

    sentences = re.split(r"(?<=[.!?])\s+", " ".join(lines))
    return [sentence.strip() for sentence in sentences if len(sentence.strip()) > 20]


def impact_score(parsed: ParsedResume) -> float:
    """Share of experience statements that contain a measurable outcome."""
    statements = _experience_bullets(parsed)
    if not statements:
        return 0.0

    quantified = sum(1 for statement in statements if _NUMBER_RE.search(statement))
    return quantified / len(statements)


def format_score(parsed: ParsedResume) -> float:
    """Heuristic readability/parseability score between 0 and 1."""
    score = 0.0

    if parsed.contact.email:
        score += 0.4
    if parsed.contact.phone:
        score += 0.2
    if parsed.contact.links:
        score += 0.1

    longest_line = max((len(line) for line in parsed.raw_text.splitlines()), default=0)
    if longest_line <= 160:
        score += 0.2

    if " | " not in parsed.raw_text:
        score += 0.1

    return min(1.0, score)


def evaluate_rules(
    parsed: ParsedResume,
    missing_keywords: tuple[str, ...],
    keyword_coverage: float,
    impact: float,
    formatting: float,
) -> tuple[RuleFinding, ...]:
    """Produce human-readable findings from the deterministic signals."""
    findings: list[RuleFinding] = []

    if "experience" not in parsed.sections:
        findings.append(
            RuleFinding(
                category="section",
                severity="critical",
                message="Add a dedicated Experience section with role, company and dates.",
            )
        )
    if "education" not in parsed.sections:
        findings.append(
            RuleFinding(
                category="section",
                severity="warning",
                message="Add an Education section; many ATS parsers expect one.",
            )
        )
    if "skills" not in parsed.sections:
        findings.append(
            RuleFinding(
                category="section",
                severity="warning",
                message="Add a Skills section so keyword coverage can be evaluated.",
            )
        )

    if missing_keywords:
        preview = ", ".join(missing_keywords[:8])
        findings.append(
            RuleFinding(
                category="keyword",
                severity="critical" if keyword_coverage < 0.5 else "warning",
                message=f"Add missing role keywords to your experience or skills: {preview}.",
                evidence=f"{len(missing_keywords)} keyword(s) missing from the job description.",
            )
        )

    if not parsed.contact.email:
        findings.append(
            RuleFinding(
                category="contact",
                severity="critical",
                message="Add a professional email address to the resume header.",
            )
        )
    elif not parsed.contact.phone:
        findings.append(
            RuleFinding(
                category="contact",
                severity="info",
                message="Consider adding a phone number to the header.",
            )
        )

    if impact < 0.5:
        findings.append(
            RuleFinding(
                category="impact",
                severity="warning",
                message="Quantify more experience bullets with numbers, percentages or scope.",
                evidence=f"{round(impact * 100)}% of experience statements are quantified.",
            )
        )

    if " | " in parsed.raw_text:
        findings.append(
            RuleFinding(
                category="format",
                severity="warning",
                message="Table-like content detected; ATS parsers may not read it cleanly.",
            )
        )

    if formatting < 0.6:
        findings.append(
            RuleFinding(
                category="format",
                severity="info",
                message="Simplify formatting and keep lines under 160 characters.",
            )
        )

    return tuple(findings)
