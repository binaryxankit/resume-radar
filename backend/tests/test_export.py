from io import BytesIO

from app.services.export.docx import build_resume_docx, export_filename
from docx import Document

SAMPLE = """Jane Doe
jane@example.com

Summary
Backend engineer with six years of experience.

Experience
Senior Engineer, Acme Corp
- Built APIs handling 2M requests per day
- Cut p95 latency by 35%

Skills
Python, PostgreSQL, Docker
"""


def _paragraph_texts(content: bytes) -> list[str]:
    document = Document(BytesIO(content))
    return [paragraph.text for paragraph in document.paragraphs]


def test_build_resume_docx_keeps_content() -> None:
    content = build_resume_docx(SAMPLE)

    assert content.startswith(b"PK")

    paragraphs = _paragraph_texts(content)
    assert "Jane Doe" in paragraphs
    assert "SUMMARY" in paragraphs
    assert "EXPERIENCE" in paragraphs
    assert "Built APIs handling 2M requests per day" in paragraphs


def test_build_resume_docx_applies_bullet_style() -> None:
    content = build_resume_docx(SAMPLE)

    document = Document(BytesIO(content))
    bullet_paragraphs = [
        paragraph for paragraph in document.paragraphs if paragraph.style.name == "List Bullet"
    ]

    assert len(bullet_paragraphs) == 2
    assert bullet_paragraphs[0].text == "Built APIs handling 2M requests per day"


def test_export_filename_is_safe() -> None:
    assert export_filename("jane-doe", 3) == "jane-doe-v3.docx"
    assert export_filename("   ", 1) == "resume-v1.docx"
