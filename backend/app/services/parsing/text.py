"""Text normalization helpers shared by the parsing pipeline."""

import re

_HORIZONTAL_WHITESPACE = re.compile(r"[ \t]+")
_BLANK_RUN = re.compile(r"\n{3,}")


def normalize_text(text: str) -> str:
    """Normalize line endings, horizontal whitespace and blank-line runs."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [_HORIZONTAL_WHITESPACE.sub(" ", line).strip() for line in text.split("\n")]
    return _BLANK_RUN.sub("\n\n", "\n".join(lines)).strip()
