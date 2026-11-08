from app.services.parsing.sections import (
    extract_contact,
    match_heading,
    split_sections,
)

RESUME_TEXT = """Jane Doe
jane@example.com | +1 (555) 123-4567
linkedin.com/in/janedoe

Summary
Backend engineer with 6 years building APIs.

Experience
Senior Engineer, Acme Corp
- Built distributed services

Skills
Python, PostgreSQL

Education
BSc Computer Science
"""


def test_match_heading_normalizes_case_and_punctuation() -> None:
    assert match_heading("EXPERIENCE") == "experience"
    assert match_heading("Technical Skills:") == "skills"
    assert match_heading("Not a section heading at all") is None


def test_split_sections_groups_lines() -> None:
    sections = split_sections(RESUME_TEXT)

    assert set(sections) >= {"header", "summary", "experience", "skills", "education"}
    assert sections["header"][0] == "Jane Doe"
    assert any("Acme Corp" in line for line in sections["experience"])


def test_extract_contact_reads_header_and_body() -> None:
    sections = split_sections(RESUME_TEXT)
    contact = extract_contact(RESUME_TEXT, sections["header"])

    assert contact.name == "Jane Doe"
    assert contact.email == "jane@example.com"
    assert contact.phone is not None
    assert "linkedin.com/in/janedoe" in contact.links
