"""Reddit data provider backed by the official API through PRAW."""

from dataclasses import dataclass
from typing import Protocol

from app.core.config import get_settings


class IntelError(RuntimeError):
    """Raised when an external intelligence source cannot be read."""


@dataclass(frozen=True)
class RedditPost:
    title: str
    url: str
    subreddit: str
    score: int


class RedditProvider(Protocol):
    def search(self, query: str, limit: int = 10) -> list[RedditPost]:
        """Return relevant posts for a query, newest relevance first."""


class PrawRedditProvider:
    """Thin wrapper around PRAW that normalizes submissions."""

    def __init__(self, client_id: str, client_secret: str, user_agent: str) -> None:
        import praw

        self._reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent,
            check_for_async=False,
        )

    def search(self, query: str, limit: int = 10) -> list[RedditPost]:
        try:
            results = self._reddit.subreddit("all").search(
                query,
                sort="relevance",
                time_filter="year",
                limit=limit,
            )
            return [
                RedditPost(
                    title=submission.title,
                    url=f"https://www.reddit.com{submission.permalink}",
                    subreddit=str(submission.subreddit),
                    score=int(submission.score),
                )
                for submission in results
            ]
        except Exception as exc:  # PRAW raises several unrelated exception types
            raise IntelError(f"Reddit search failed: {exc}") from exc


def get_reddit_provider() -> RedditProvider | None:
    """Return a provider when credentials exist, otherwise ``None``."""
    settings = get_settings()
    if not settings.reddit_client_id or not settings.reddit_client_secret:
        return None

    return PrawRedditProvider(
        client_id=settings.reddit_client_id,
        client_secret=settings.reddit_client_secret,
        user_agent=settings.reddit_user_agent,
    )
