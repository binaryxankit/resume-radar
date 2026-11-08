from io import BytesIO

from app.services.parsing import parse_resume
from docx import Document


def _docx_bytes(lines: list[str]) -> bytes:
    document = Document()
    for line in lines:
        document.add_paragraph(line)
    buffer = BytesIO()
    document.save(buffer)
    return buffer.getvalue()


def test_parse_resume_end_to_end() -> None:
    data = _docx_bytes(
        [
            "Jane Doe",
            "jane@example.com | +1 (555) 123-4567",
            "",
            "Summary",
            "Backend engineer with 6 years of experience.",
            "",
            "Experience",
            "Senior Engineer, Acme Corp",
            "",
            "Skills",
            "Python, PostgreSQL",
        ]
    )

    parsed = parse_resume("jane-doe.docx", data)

    assert parsed.filename == "jane-doe.docx"
    assert parsed.contact.email == "jane@example.com"
    assert parsed.contact.name == "Jane Doe"
    assert "experience" in parsed.section_keys
    assert "Acme Corp" in parsed.section_text("experience")
    assert "Python" in parsed.section_text("skills")
