"""Render stored resume text as a clean, ATS-friendly DOCX document."""

from io import BytesIO

from docx import Document
from docx.shared import Pt

from app.services.parsing.sections import match_heading
from app.services.parsing.text import normalize_text

_BULLET_PREFIXES = ("-", "•", "*", "–", "—")


def _add_heading(document: Document, text: str) -> None:
    paragraph = document.add_paragraph()
    paragraph.paragraph_format.space_before = Pt(10)
    paragraph.paragraph_format.space_after = Pt(4)
    run = paragraph.add_run(text.upper())
    run.bold = True
    run.font.size = Pt(13)


def build_resume_docx(raw_text: str) -> bytes:
    """Build a DOCX file preserving headings and bullet structure."""
    document = Document()
    style = document.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(11)

    for raw_line in normalize_text(raw_text).splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if match_heading(line):
            _add_heading(document, line)
        elif line.startswith(_BULLET_PREFIXES):
            text = line.lstrip("-•*–— ").strip()
            if text:
                document.add_paragraph(text, style="List Bullet")
        else:
            document.add_paragraph(line)

    buffer = BytesIO()
    document.save(buffer)
    return buffer.getvalue()


def export_filename(stem: str, version_no: int) -> str:
    """Create a safe attachment name for an exported resume version."""
    cleaned = stem.strip() or "resume"
    return f"{cleaned}-v{version_no}.docx"
