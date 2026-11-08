from app.services.parsing.text import normalize_text


def test_normalize_collapses_whitespace_and_blank_runs() -> None:
    text = "Jane   Doe\r\n\r\n\r\n\r\nExperience\tEngineer"

    assert normalize_text(text) == "Jane Doe\n\nExperience Engineer"


def test_normalize_strips_outer_whitespace() -> None:
    assert normalize_text("  \n Jane Doe \n  ") == "Jane Doe"
