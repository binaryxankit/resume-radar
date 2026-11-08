import pytest
from app.core.config import get_settings
from app.services.llm.prompts import build_user_prompt
from app.services.llm.providers import LLMError, MissingAPIKey, get_provider
from app.services.llm.suggestions import (
    SuggestionDraft,
    generate_suggestions,
    parse_suggestions,
    suggestions_from_findings,
)
from app.services.scoring import score_resume

JOB = """
We are hiring a Senior Backend Engineer.
Required: Python, PostgreSQL, Kafka, Kubernetes and Docker.
"""


class StubProvider:
    def __init__(self, response: str) -> None:
        self.response = response
        self.calls: list[tuple[str, str]] = []

    async def complete(self, system: str, user: str) -> str:
        self.calls.append((system, user))
        return self.response


def test_parse_plain_array() -> None:
    raw = '[{"category": "keyword", "severity": "warning", "message": "Add Kafka"}]'

    drafts = parse_suggestions(raw)

    assert len(drafts) == 1
    assert drafts[0].message == "Add Kafka"


def test_parse_envelope_with_code_fence() -> None:
    raw = (
        "```json\n"
        '{"suggestions": [{"category": "impact", "severity": "critical", '
        '"message": "Quantify outcomes"}]}\n'
        "```"
    )

    drafts = parse_suggestions(raw)

    assert drafts[0].severity == "critical"


def test_parse_invalid_json_raises() -> None:
    with pytest.raises(LLMError):
        parse_suggestions("not-json")


def test_parse_invalid_shape_raises() -> None:
    with pytest.raises(LLMError):
        parse_suggestions('{"unexpected": true}')


def test_suggestions_from_findings_are_valid_models(make_resume) -> None:
    breakdown = score_resume(make_resume({"header": ("Jane Doe",)}), JOB)

    drafts = suggestions_from_findings(breakdown)

    assert drafts
    assert all(isinstance(draft, SuggestionDraft) for draft in drafts)


@pytest.mark.asyncio
async def test_generate_suggestions_uses_provider(make_resume) -> None:
    parsed = make_resume()
    breakdown = score_resume(parsed, JOB)
    provider = StubProvider(
        '[{"category": "keyword", "severity": "warning", "message": "Add Kafka"}]'
    )

    drafts = await generate_suggestions(parsed, JOB, breakdown, provider)

    assert drafts[0].message == "Add Kafka"
    assert provider.calls


def test_build_user_prompt_includes_keywords(make_resume) -> None:
    parsed = make_resume()
    breakdown = score_resume(parsed, JOB)

    prompt = build_user_prompt(parsed, JOB, breakdown)

    assert "missing keywords" in prompt.lower()
    assert "kafka" in prompt.lower()


def test_get_provider_requires_api_key(monkeypatch) -> None:
    settings = get_settings()
    monkeypatch.setattr(settings, "openai_api_key", None)

    with pytest.raises(MissingAPIKey):
        get_provider()


def test_get_provider_rejects_unknown_provider(monkeypatch) -> None:
    settings = get_settings()
    monkeypatch.setattr(settings, "llm_provider", "unknown")
    monkeypatch.setattr(settings, "openai_api_key", "test-key")

    with pytest.raises(LLMError):
        get_provider()
