from collections.abc import Callable

import pytest
from app.services.parsing.parser import ParsedResume
from app.services.parsing.sections import ContactInfo

DEFAULT_SECTIONS: dict[str, tuple[str, ...]] = {
    "header": (
        "Jane Doe",
        "jane@example.com",
        "+1 555 123 4567",
        "https://github.com/janedoe",
    ),
    "summary": ("Backend engineer with six years of experience.",),
    "experience": (
        "Senior Engineer, Acme Corp",
        "- Built APIs handling 2M requests per day",
        "- Cut p95 latency by 35%",
    ),
    "skills": ("Python, PostgreSQL, Docker",),
    "education": ("BSc Computer Science",),
}


@pytest.fixture
def make_resume() -> Callable[..., ParsedResume]:
    def _make(
        sections: dict[str, tuple[str, ...]] | None = None,
        contact: ContactInfo | None = None,
        raw_text: str | None = None,
    ) -> ParsedResume:
        resolved_sections = sections if sections is not None else DEFAULT_SECTIONS
        if raw_text is None:
            raw_text = "\n".join(
                line for lines in resolved_sections.values() for line in lines
            )
        if contact is None:
            contact = ContactInfo(
                name="Jane Doe",
                email="jane@example.com",
                phone="+1 555 123 4567",
                links=("https://github.com/janedoe",),
            )
        return ParsedResume(
            filename="jane-doe.pdf",
            raw_text=raw_text,
            sections=resolved_sections,
            contact=contact,
        )

    return _make
