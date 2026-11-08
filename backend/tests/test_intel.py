import app.api.routes.intel as intel_route
from app.services.intel.aggregator import aggregate_insights, build_queries
from app.services.intel.reddit import IntelError, RedditPost


class FakeProvider:
    def __init__(self, posts: list[RedditPost]) -> None:
        self.posts = posts
        self.calls = 0

    def search(self, query: str, limit: int = 10) -> list[RedditPost]:
        self.calls += 1
        return list(self.posts)


class ExplodingProvider:
    def search(self, query: str, limit: int = 10) -> list[RedditPost]:
        raise AssertionError("cache should prevent a second fetch")


class FailingProvider:
    def search(self, query: str, limit: int = 10) -> list[RedditPost]:
        raise IntelError("reddit unavailable")


POSTS = [
    RedditPost("Stripe backend interview", "https://reddit.com/r/x/1", "cscareerquestions", 120),
    RedditPost("Stripe hiring process", "https://reddit.com/r/y/2", "ExperiencedDevs", 60),
    RedditPost("Duplicate of post 1", "https://reddit.com/r/x/1", "cscareerquestions", 200),
]


def _auth_headers(client, email: str) -> dict[str, str]:
    credentials = {"email": email, "password": "supersecret"}
    client.post("/api/auth/register", json=credentials)
    token = client.post("/api/auth/login", json=credentials).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_build_queries_includes_role() -> None:
    queries = build_queries("Stripe", "Backend Engineer")

    assert queries[0] == "Stripe Backend Engineer interview"
    assert len(queries) == 3
    assert build_queries("Stripe", None) == ["Stripe interview experience"]


def test_aggregate_dedupes_and_ranks_by_score() -> None:
    drafts = aggregate_insights("Stripe", "Backend Engineer", POSTS)

    assert len(drafts) == 2
    assert drafts[0].source_url == "https://reddit.com/r/x/1"
    assert drafts[0].confidence > drafts[1].confidence
    assert all(draft.source_kind == "reddit" for draft in drafts)


def test_aggregate_respects_limit() -> None:
    assert len(aggregate_insights("Stripe", None, POSTS, limit=1)) == 1


def test_intel_returns_insights_and_caches(client, monkeypatch) -> None:
    fake = FakeProvider(POSTS)
    monkeypatch.setattr(intel_route, "get_reddit_provider", lambda: fake)
    headers = _auth_headers(client, "intel@example.com")
    params = {"company": "Stripe", "role": "Backend Engineer"}

    first = client.get("/api/intel", params=params, headers=headers)

    assert first.status_code == 200
    body = first.json()
    assert body["source_available"] is True
    assert body["cached"] is False
    assert len(body["insights"]) == 2
    assert fake.calls == 3

    monkeypatch.setattr(intel_route, "get_reddit_provider", lambda: ExplodingProvider())
    second = client.get("/api/intel", params=params, headers=headers)

    assert second.status_code == 200
    assert second.json()["cached"] is True
    assert len(second.json()["insights"]) == 2


def test_intel_without_provider_reports_unavailable(client, monkeypatch) -> None:
    monkeypatch.setattr(intel_route, "get_reddit_provider", lambda: None)
    headers = _auth_headers(client, "noprovider@example.com")

    response = client.get("/api/intel", params={"company": "Unknown"}, headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["source_available"] is False
    assert body["insights"] == []


def test_intel_handles_provider_failure(client, monkeypatch) -> None:
    monkeypatch.setattr(intel_route, "get_reddit_provider", lambda: FailingProvider())
    headers = _auth_headers(client, "failing@example.com")

    response = client.get("/api/intel", params={"company": "Stripe"}, headers=headers)

    assert response.status_code == 200
    assert response.json()["source_available"] is False


def test_intel_requires_authentication(client) -> None:
    assert client.get("/api/intel", params={"company": "Stripe"}).status_code == 401
