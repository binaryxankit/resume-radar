"""Text extraction from supported resume file formats."""

from io import BytesIO
from pathlib import Path

from docx import Document
from pypdf import PdfReader

SUPPORTED_EXTENSIONS = frozenset({".pdf", ".docx", ".txt"})


class UnsupportedFileType(ValueError):
    """Raised when a file extension is not supported."""

    def __init__(self, extension: str) -> None:
        super().__init__(f"Unsupported file type: {extension or '(none)'}")
        self.extension = extension


class ExtractionError(RuntimeError):
    """Raised when a supported file cannot yield usable text."""


def extract_text(filename: str, data: bytes) -> str:
    """Extract raw text from a resume file based on its extension."""
    extension = Path(filename).suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise UnsupportedFileType(extension)
    if extension == ".pdf":
        return _extract_pdf(data)
    if extension == ".docx":
        return _extract_docx(data)

    return data.decode("utf-8", errors="replace")


def _extract_pdf(data: bytes) -> str:
    try:
        reader = PdfReader(BytesIO(data))
        pages = [page.extract_text() or "" for page in reader.pages]
    except Exception as exc:  # pypdf raises a variety of errors on malformed input
        raise ExtractionError("Could not read PDF file") from exc

    text = "\n".join(pages)
    if not text.strip():
        raise ExtractionError("PDF contains no extractable text")
    return text


def _extract_docx(data: bytes) -> str:
    try:
        document = Document(BytesIO(data))
    except Exception as exc:
        raise ExtractionError("Could not read DOCX file") from exc

    parts = [paragraph.text for paragraph in document.paragraphs]
    for table in document.tables:
        for row in table.rows:
            cells = [cell.text.strip() for cell in row.cells]
            joined = " | ".join(cell for cell in cells if cell)
            if joined:
                parts.append(joined)

    text = "\n".join(parts)
    if not text.strip():
        raise ExtractionError("DOCX contains no extractable text")
    return text
