"""Section detection and contact extraction for resume text."""

import re
from dataclasses import dataclass, field

SECTION_ALIASES: dict[str, tuple[str, ...]] = {
    "summary": (
        "summary",
        "professional summary",
        "profile",
        "objective",
        "about",
        "about me",
    ),
    "experience": (
        "experience",
        "work experience",
        "professional experience",
        "employment",
        "employment history",
        "work history",
    ),
    "education": ("education", "academic background", "academics"),
    "skills": (
        "skills",
        "technical skills",
        "core skills",
        "core competencies",
        "technologies",
        "tech stack",
    ),
    "projects": ("projects", "personal projects", "selected projects", "key projects"),
    "certifications": (
        "certifications",
        "certificates",
        "licenses",
        "certifications and licenses",
    ),
    "awards": ("awards", "honors", "awards and honors", "achievements"),
    "publications": ("publications", "papers"),
    "languages": ("languages",),
    "contact": ("contact", "contact information", "contact details"),
}

_HEADING_LOOKUP = {
    alias: key for key, aliases in SECTION_ALIASES.items() for alias in aliases
}

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"\+?\d[\d\s().\-]{7,}\d")
LINK_RE = re.compile(
    r"(?:https?://[^\s]+|(?:www\.)?(?:linkedin|github)\.com/[^\s]+)",
    re.IGNORECASE,
)

_MAX_HEADING_LENGTH = 40


@dataclass(frozen=True)
class ContactInfo:
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    links: tuple[str, ...] = field(default_factory=tuple)


def _normalize_heading(line: str) -> str:
    return re.sub(r"[\s:•\-–—]+", " ", line.strip().lower()).strip()


def match_heading(line: str) -> str | None:
    """Return the canonical section key when a line looks like a heading."""
    normalized = _normalize_heading(line)
    if not normalized or len(normalized) > _MAX_HEADING_LENGTH:
        return None
    return _HEADING_LOOKUP.get(normalized)


def split_sections(text: str) -> dict[str, list[str]]:
    """Split normalized resume text into canonical sections.

    Text before the first recognized heading is grouped under ``header``.
    Empty sections are omitted from the result.
    """
    sections: dict[str, list[str]] = {"header": []}
    current = "header"

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        heading = match_heading(line)
        if heading:
            current = heading
            sections.setdefault(current, [])
            continue

        sections.setdefault(current, []).append(line)

    return {key: lines for key, lines in sections.items() if lines}


def _find_phone(text: str) -> str | None:
    for match in PHONE_RE.finditer(text):
        candidate = match.group(0).strip()
        digits = re.sub(r"\D", "", candidate)
        if 10 <= len(digits) <= 15:
            return candidate
    return None


def _guess_name(header_lines: list[str]) -> str | None:
    stop_words = {"resume", "curriculum vitae", "cv"}
    for line in header_lines:
        candidate = line.strip()
        if not candidate or candidate.lower() in stop_words:
            continue
        if EMAIL_RE.search(candidate) or any(character.isdigit() for character in candidate):
            continue
        if match_heading(candidate):
            continue
        if len(candidate) <= 60 and len(candidate.split()) <= 5:
            return candidate
    return None


def extract_contact(text: str, header_lines: list[str]) -> ContactInfo:
    """Extract contact details from the whole document and header block."""
    email_match = EMAIL_RE.search(text)
    links = tuple(dict.fromkeys(match.group(0) for match in LINK_RE.finditer(text)))

    return ContactInfo(
        name=_guess_name(header_lines),
        email=email_match.group(0) if email_match else None,
        phone=_find_phone(text),
        links=links,
    )
