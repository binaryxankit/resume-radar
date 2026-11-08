"""Company and role intelligence endpoints with per-company caching."""

from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Query
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser, DbSession
from app.core.config import get_settings
from app.core.slug import slugify
from app.models import Company, Insight, Role
from app.schemas.intel import InsightOut, IntelResponse
from app.services.intel.aggregator import aggregate_insights, build_queries
from app.services.intel.reddit import IntelError, get_reddit_provider

router = APIRouter(prefix="/api/intel", tags=["intel"])

_POSTS_PER_QUERY = 10


def _aware(value: datetime) -> datetime:
    return value if value.tzinfo else value.replace(tzinfo=UTC)


def _get_or_create_company(db: Session, name: str) -> Company:
    slug = slugify(name)
    company = db.scalar(select(Company).where(Company.slug == slug))
    if company is None:
        company = Company(name=name.strip(), slug=slug, domain=None)
        db.add(company)
        db.flush()
    return company


def _get_or_create_role(db: Session, title: str | None) -> Role | None:
    if not title:
        return None

    statement = select(Role).where(Role.title == title.strip(), Role.level.is_(None))
    role = db.scalar(statement)
    if role is None:
        role = Role(title=title.strip(), level=None)
        db.add(role)
        db.flush()
    return role


def _cached_insights(db: Session, company_id: int, role_id: int | None) -> list[Insight]:
    statement = select(Insight).where(Insight.company_id == company_id)
    statement = (
        statement.where(Insight.role_id == role_id)
        if role_id is not None
        else statement.where(Insight.role_id.is_(None))
    )
    return list(
        db.scalars(statement.order_by(Insight.confidence.desc(), Insight.id.desc())).all()
    )


def _is_fresh(insights: list[Insight], ttl_seconds: int) -> bool:
    if not insights:
        return False
    newest = max(_aware(item.fetched_at) for item in insights)
    return datetime.now(UTC) - newest < timedelta(seconds=ttl_seconds)


def _response(
    company: Company,
    role: Role | None,
    insights: list[Insight],
    *,
    cached: bool,
    source_available: bool,
) -> IntelResponse:
    return IntelResponse(
        company=company.name,
        role=role.title if role else None,
        cached=cached,
        source_available=source_available,
        insights=[InsightOut.model_validate(item) for item in insights],
    )


@router.get("", response_model=IntelResponse)
def get_intel(
    current_user: CurrentUser,
    db: DbSession,
    company: Annotated[str, Query(min_length=1)],
    role: Annotated[str | None, Query()] = None,
    refresh: bool = False,
) -> IntelResponse:
    settings = get_settings()
    role = role.strip() if role else None

    company_row = _get_or_create_company(db, company)
    role_row = _get_or_create_role(db, role)
    role_id = role_row.id if role_row else None
    existing = _cached_insights(db, company_row.id, role_id)

    if existing and not refresh and _is_fresh(existing, settings.cache_ttl_seconds):
        return _response(
            company_row, role_row, existing, cached=True, source_available=True
        )

    provider = get_reddit_provider()
    if provider is None:
        db.commit()
        return _response(
            company_row, role_row, existing, cached=False, source_available=False
        )

    posts = []
    try:
        for query in build_queries(company, role):
            posts.extend(provider.search(query, limit=_POSTS_PER_QUERY))
    except IntelError:
        db.commit()
        return _response(
            company_row, role_row, existing, cached=False, source_available=False
        )

    drafts = aggregate_insights(company, role, posts)

    delete_statement = delete(Insight).where(Insight.company_id == company_row.id)
    delete_statement = (
        delete_statement.where(Insight.role_id == role_id)
        if role_id is not None
        else delete_statement.where(Insight.role_id.is_(None))
    )
    db.execute(delete_statement)

    for draft in drafts:
        db.add(
            Insight(
                company_id=company_row.id,
                role_id=role_id,
                kind=draft.kind,
                title=draft.title,
                summary=draft.summary,
                source_url=draft.source_url,
                source_kind=draft.source_kind,
                confidence=draft.confidence,
                fetched_at=datetime.now(UTC),
            )
        )
    db.commit()

    refreshed = _cached_insights(db, company_row.id, role_id)
    return _response(
        company_row, role_row, refreshed, cached=False, source_available=True
    )
