"""Small text helpers shared across layers."""

import re

_SLUG_RE = re.compile(r"[^a-z0-9]+")


def slugify(value: str) -> str:
    """Create a stable, URL-safe slug from a display name."""
    return _SLUG_RE.sub("-", value.strip().lower()).strip("-") or "unknown"
