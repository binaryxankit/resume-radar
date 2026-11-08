from app.services.scoring.keywords import (
    contains_skill,
    extract_job_keywords,
    extract_skills,
    match_keywords,
    top_terms,
)


def test_extract_skills_uses_canonical_names() -> None:
    skills = extract_skills("We use Python, PostgreSQL, Docker and Kubernetes.")

    assert skills == ("docker", "kubernetes", "postgresql", "python")


def test_extract_skills_handles_aliases() -> None:
    assert "kubernetes" in extract_skills("Experience with k8s is required")
    assert "python" in extract_skills("Strong PYTHON background")


def test_contains_skill_respects_word_boundaries() -> None:
    assert contains_skill("I use c++ daily", "cpp")
    assert not contains_skill("I use csharp", "cpp")


def test_match_keywords_splits_matched_and_missing() -> None:
    resume = "Built services in Python and deployed with Docker."
    job = "We need Python, Docker, Kafka and Kubernetes."

    matched, missing = match_keywords(resume, job)

    assert "python" in matched
    assert "docker" in matched
    assert "kafka" in missing
    assert "kubernetes" in missing


def test_top_terms_falls_back_for_unknown_domains() -> None:
    job = "salesforce hubspot salesforce hubspot crm crm integration integration"

    keywords = extract_job_keywords(job)

    assert "salesforce" in keywords
    assert "hubspot" in keywords


def test_top_terms_ignores_single_occurrences() -> None:
    assert "unique" not in top_terms("unique repeated repeated")
