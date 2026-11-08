from app.services.scoring import score_resume

JOB = """
We are hiring a Senior Backend Engineer.

Required: Python, PostgreSQL, Kafka, Kubernetes and Docker.
You will design distributed systems and own reliability.
"""


def test_score_is_within_range(make_resume) -> None:
    result = score_resume(make_resume(), JOB)

    assert 0 <= result.overall <= 100
    assert result.keyword_coverage == 0.5
    assert "python" in result.matched_keywords
    assert "kafka" in result.missing_keywords


def test_strong_resume_scores_above_weak_one(make_resume) -> None:
    strong = score_resume(make_resume(), JOB)
    weak = score_resume(
        make_resume({"header": ("Jane Doe",)}),
        JOB,
    )

    assert strong.overall > weak.overall


def test_missing_keywords_produce_keyword_finding(make_resume) -> None:
    result = score_resume(make_resume(), JOB)

    keyword_findings = [
        finding for finding in result.findings if finding.category == "keyword"
    ]
    assert keyword_findings
    assert "kafka" in keyword_findings[0].message


def test_scoring_is_deterministic(make_resume) -> None:
    first = score_resume(make_resume(), JOB)
    second = score_resume(make_resume(), JOB)

    assert first == second


def test_to_dict_is_serializable(make_resume) -> None:
    payload = score_resume(make_resume(), JOB).to_dict()

    assert payload["overall"] == score_resume(make_resume(), JOB).overall
    assert isinstance(payload["missing_keywords"], list)
    assert isinstance(payload["findings"], list)


def test_no_job_keywords_yields_full_coverage(make_resume) -> None:
    result = score_resume(make_resume(), "Bring your best self.")

    assert result.keyword_coverage == 1.0
    assert result.missing_keywords == ()
