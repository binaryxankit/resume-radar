"""Turn raw Reddit posts into deduplicated, ranked insight drafts."""

from dataclasses import dataclass

from app.services.intel.reddit import RedditPost

_MAX_POSTS_PER_QUERY = 10


@dataclass(frozen=True)
class InsightDraft:
    kind: str
    title: str
    summary: str
    source_url: str
    source_kind: str
    confidence: float


def build_queries(company: str, role: str | None) -> list[str]:
    """Build a small, focused set of Reddit search queries."""
    company = company.strip()
    queries = [f"{company} interview experience"]

    if role:
        role = role.strip()
        queries.insert(0, f"{company} {role} interview")
        queries.append(f"{company} {role} interview questions")

    return queries


def _confidence(post: RedditPost) -> float:
    return round(min(1.0, 0.35 + post.score / 500), 2)


def aggregate_insights(
    company: str,
    role: str | None,
    posts: list[RedditPost],
    limit: int = 10,
) -> list[InsightDraft]:
    """Deduplicate by URL, rank by score and cap the result set."""
    seen: set[str] = set()
    drafts: list[InsightDraft] = []
    role_label = role or "this role"

    for post in sorted(posts, key=lambda item: item.score, reverse=True):
        if post.url in seen:
            continue
        seen.add(post.url)

        drafts.append(
            InsightDraft(
                kind="interview",
                title=post.title,
                summary=f"r/{post.subreddit} discussion relevant to {company} · {role_label}.",
                source_url=post.url,
                source_kind="reddit",
                confidence=_confidence(post),
            )
        )

        if len(drafts) >= limit:
            break

    return drafts
