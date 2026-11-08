"""Chat completion providers.

The rest of the app depends only on the ``LLMProvider`` protocol, so providers
can be swapped and tests can inject fakes without any network access.
"""

from typing import Protocol

import httpx

from app.core.config import get_settings


class LLMError(RuntimeError):
    """Raised when a provider call or response cannot be used."""


class MissingAPIKey(LLMError):
    """Raised when no API key is available for the requested provider."""


class LLMProvider(Protocol):
    async def complete(self, system: str, user: str) -> str:
        """Return the model's text response for a system/user prompt pair."""


class OpenAIProvider:
    """Minimal async client for the OpenAI chat completions API."""

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        base_url: str = "https://api.openai.com/v1",
        timeout: float = 30.0,
    ) -> None:
        self._api_key = api_key
        self._model = model
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    async def complete(self, system: str, user: str) -> str:
        payload = {
            "model": self._model,
            "temperature": 0.2,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "response_format": {"type": "json_object"},
        }

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(
                    f"{self._base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self._api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
                response.raise_for_status()
        except httpx.HTTPError as exc:
            raise LLMError(f"LLM request failed: {exc}") from exc

        try:
            return response.json()["choices"][0]["message"]["content"]
        except (KeyError, IndexError, ValueError) as exc:
            raise LLMError("LLM returned an unexpected response shape") from exc


def get_provider(api_key: str | None = None) -> OpenAIProvider:
    """Build the configured provider, preferring a user-supplied key."""
    settings = get_settings()

    if settings.llm_provider != "openai":
        raise LLMError(f"Unsupported LLM provider: {settings.llm_provider}")

    resolved_key = api_key or settings.openai_api_key
    if not resolved_key:
        raise MissingAPIKey("No OpenAI API key configured")

    return OpenAIProvider(api_key=resolved_key, model=settings.llm_model)
