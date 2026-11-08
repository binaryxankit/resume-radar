from io import BytesIO

import pytest
from app.services.parsing.extractors import (
    ExtractionError,
    UnsupportedFileType,
    extract_text,
)
from docx import Document
from reportlab.pdfgen import canvas


def _docx_bytes(lines: list[str]) -> bytes:
    document = Document()
    for line in lines:
        document.add_paragraph(line)
    buffer = BytesIO()
    document.save(buffer)
    return buffer.getvalue()


def _pdf_bytes(lines: list[str]) -> bytes:
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)
    y = 800
    for line in lines:
        pdf.drawString(72, y, line)
        y -= 24
    pdf.save()
    return buffer.getvalue()


def test_extract_plain_text() -> None:
    assert extract_text("resume.txt", b"Jane Doe\nPython") == "Jane Doe\nPython"


def test_extract_docx() -> None:
    text = extract_text("resume.docx", _docx_bytes(["Jane Doe", "Experience", "Acme Corp"]))

    assert "Jane Doe" in text
    assert "Acme Corp" in text


def test_extract_pdf() -> None:
    text = extract_text("resume.pdf", _pdf_bytes(["Jane Doe", "Backend Engineer"]))

    assert "Jane Doe" in text


def test_unsupported_extension_raises() -> None:
    with pytest.raises(UnsupportedFileType):
        extract_text("resume.rtf", b"anything")


def test_empty_pdf_raises_extraction_error() -> None:
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)
    pdf.save()

    with pytest.raises(ExtractionError):
        extract_text("resume.pdf", buffer.getvalue())
