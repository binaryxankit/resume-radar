"""High-level resume parsing orchestration."""

from dataclasses import dataclass

from app.services.parsing.extractors import ExtractionError, extract_text
from app.services.parsing.sections import ContactInfo, extract_contact, split_sections
from app.services.parsing.text import normalize_text


@dataclass(frozen=True)
class ParsedResume:
    """Structured representation of an uploaded resume."""

    filename: str
    raw_text: str
    sections: dict[str, tuple[str, ...]]
    contact: ContactInfo

    def section_text(self, key: str) -> str:
        """Join the lines of a section into a single string."""
        return "\n".join(self.sections.get(key, ()))

    @property
    def section_keys(self) -> tuple[str, ...]:
        return tuple(self.sections)


def parse_resume(filename: str, data: bytes) -> ParsedResume:
    """Extract, normalize and structure a resume file."""
    return parse_resume_text(extract_text(filename, data), filename=filename)


def parse_resume_text(text: str, filename: str = "resume") -> ParsedResume:
    """Normalize and structure already-extracted resume text."""
    normalized = normalize_text(text)
    if not normalized.strip():
        raise ExtractionError("Resume contains no extractable text")

    raw_sections = split_sections(normalized)
    sections = {key: tuple(lines) for key, lines in raw_sections.items()}
    contact = extract_contact(normalized, raw_sections.get("header", []))

    return ParsedResume(
        filename=filename,
        raw_text=normalized,
        sections=sections,
        contact=contact,
    )
