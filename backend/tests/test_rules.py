import pytest
from app.services.scoring.rules import (
    evaluate_rules,
    format_score,
    impact_score,
    section_completeness,
)


def test_section_completeness_rewards_full_resume(make_resume) -> None:
    parsed = make_resume()

    assert section_completeness(parsed) > 0.85


def test_section_completeness_penalizes_missing_sections(make_resume) -> None:
    parsed = make_resume({"header": ("Jane Doe",), "summary": ("Engineer",)})

    assert section_completeness(parsed) == pytest.approx(0.05)


def test_impact_score_counts_quantified_bullets(make_resume) -> None:
    parsed = make_resume()

    assert impact_score(parsed) == pytest.approx(1.0)


def test_impact_score_zero_without_numbers(make_resume) -> None:
    parsed = make_resume(
        {
            "experience": (
                "Senior Engineer",
                "- Built reliable distributed services for the platform team",
                "- Improved developer experience across the org",
            )
        }
    )

    assert impact_score(parsed) == pytest.approx(0.0)


def test_format_score_full_marks(make_resume) -> None:
    assert format_score(make_resume()) == pytest.approx(1.0)


def test_evaluate_rules_flags_missing_keywords_and_email(make_resume) -> None:
    from app.services.parsing.sections import ContactInfo

    parsed = make_resume(
        {"experience": ("Engineer", "- Built things")},
        contact=ContactInfo(),
    )

    findings = evaluate_rules(parsed, ("kafka",), 0.2, 0.1, 0.1)
    categories = {finding.category for finding in findings}
    severities = {finding.severity for finding in findings}

    assert "keyword" in categories
    assert "contact" in categories
    assert "critical" in severities
