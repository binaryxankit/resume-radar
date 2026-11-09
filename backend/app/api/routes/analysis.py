"""Resume analysis endpoints: upload, score, suggest, retrieve."""

from pathlib import Path
from typing import Annotated

from fastapi import (
    APIRouter,
    File,
    Form,
    Header,
    HTTPException,
    Query,
    Response,
    UploadFile,
    status,
)
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser, DbSession
from app.core.config import get_settings
from app.core.slug import slugify
from app.models import Analysis, Company, Job, Resume, ResumeVersion, Role, Suggestion
from app.schemas.analysis import (
    AnalysisHistory,
    AnalysisOut,
    AnalysisSummary,
    ReanalyzeRequest,
    SuggestionOut,
)
from app.services.export import build_resume_docx, export_filename
from app.services.llm.providers import LLMError, get_provider
from app.services.llm.suggestions import (
    SuggestionDraft,
    generate_suggestions,
    suggestions_from_findings,
)
from app.services.parsing.extractors import ExtractionError, UnsupportedFileType
from app.services.parsing.parser import ParsedResume, parse_resume, parse_resume_text
from app.services.scoring import ScoreBreakdown, score_resume

router = APIRouter(prefix="/api/analyses", tags=["analyses"])


def _get_or_create_company(db: Session, name: str, domain: str | None) -> Company:
    slug = slugify(name)
    company = db.scalar(select(Company).where(Company.slug == slug))
    if company is None:
        company = Company(name=name.strip(), slug=slug, domain=domain)
    elif domain and not company.domain:
        company.domain = domain
    return company


def _get_or_create_role(db: Session, title: str, level: str | None) -> Role:
    statement = select(Role).where(Role.title == title.strip())
    statement = (
        statement.where(Role.level == level)
        if level
        else statement.where(Role.level.is_(None))
    )
    role = db.scalar(statement)
    if role is None:
        role = Role(title=title.strip(), level=level)
    return role


def _sections_payload(parsed: ParsedResume) -> dict[str, object]:
    return {
        "sections": {key: list(lines) for key, lines in parsed.sections.items()},
        "contact": {
            "name": parsed.contact.name,
            "email": parsed.contact.email,
            "phone": parsed.contact.phone,
            "links": list(parsed.contact.links),
        },
    }


async def _build_suggestions(
    parsed: ParsedResume,
    job_description: str,
    score: ScoreBreakdown,
    api_key: str | None,
) -> list[SuggestionDraft]:
    """Use the LLM when available, otherwise fall back to rule findings."""
    try:
        provider = get_provider(api_key)
        return await generate_suggestions(parsed, job_description, score, provider)
    except LLMError:
        return suggestions_from_findings(score)


def _attach_suggestions(analysis: Analysis, drafts: list[SuggestionDraft]) -> None:
    analysis.suggestions = [
        Suggestion(
            category=draft.category,
            severity=draft.severity,
            message=draft.message,
            evidence=draft.evidence,
            proposed_text=draft.proposed_text,
        )
        for draft in drafts
    ]


def _to_out(analysis: Analysis) -> AnalysisOut:
    score = analysis.score_breakdown_json or {}
    stored = analysis.resume_version.sections_json or {}

    return AnalysisOut(
        id=analysis.id,
        company=analysis.job.company.name,
        role=analysis.job.role.title,
        job_title=analysis.job.title,
        ats_score=analysis.ats_score,
        score=score,
        matched_keywords=list(score.get("matched_keywords", [])),
        missing_keywords=list(score.get("missing_keywords", [])),
        sections=stored.get("sections", {}),
        contact=stored.get("contact", {}),
        raw_text=analysis.resume_version.raw_text,
        suggestions=[SuggestionOut.model_validate(item) for item in analysis.suggestions],
        resume_id=analysis.resume_version.resume_id,
        resume_version_id=analysis.resume_version_id,
        created_at=analysis.created_at,
    )


def _load_owned_analysis(db: Session, analysis_id: int, user_id: int) -> Analysis:
    analysis = db.get(Analysis, analysis_id)
    if analysis is None or analysis.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found"
        )
    return analysis


@router.post("", response_model=AnalysisOut, status_code=status.HTTP_201_CREATED)
async def create_analysis(
    current_user: CurrentUser,
    db: DbSession,
    file: Annotated[UploadFile, File()],
    job_description: Annotated[str, Form(min_length=20)],
    company_name: Annotated[str, Form(min_length=1)],
    role_title: Annotated[str, Form(min_length=1)],
    role_level: Annotated[str | None, Form()] = None,
    source_url: Annotated[str | None, Form()] = None,
    llm_api_key: Annotated[str | None, Header(alias="X-LLM-API-Key")] = None,
) -> AnalysisOut:
    data = await file.read()
    max_bytes = get_settings().max_upload_mb * 1024 * 1024
    if len(data) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds {get_settings().max_upload_mb} MB limit",
        )
    if not data:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="File is empty"
        )

    filename = file.filename or "resume"
    try:
        parsed = parse_resume(filename, data)
    except UnsupportedFileType as exc:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail=str(exc)
        ) from exc
    except ExtractionError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc

    score = score_resume(parsed, job_description)
    drafts = await _build_suggestions(parsed, job_description, score, llm_api_key)

    company = _get_or_create_company(db, company_name, None)
    role = _get_or_create_role(db, role_title, role_level)

    job = Job(
        user_id=current_user.id,
        company=company,
        role=role,
        title=role_title.strip(),
        description_text=job_description,
        source_url=source_url,
    )
    resume = Resume(user_id=current_user.id, filename=filename)
    version = ResumeVersion(
        resume=resume,
        version_no=1,
        raw_text=parsed.raw_text,
        sections_json=_sections_payload(parsed),
    )
    analysis = Analysis(
        user_id=current_user.id,
        resume_version=version,
        job=job,
        ats_score=score.overall,
        score_breakdown_json=score.to_dict(),
    )
    _attach_suggestions(analysis, drafts)

    db.add_all([company, role, analysis])
    db.commit()
    db.refresh(analysis)
    return _to_out(analysis)


def _summarise(analysis: Analysis) -> AnalysisSummary:
    return AnalysisSummary(
        id=analysis.id,
        company=analysis.job.company.name,
        role=analysis.job.role.title,
        job_title=analysis.job.title,
        ats_score=analysis.ats_score,
        created_at=analysis.created_at,
    )


@router.get("", response_model=AnalysisHistory)
def list_analyses(
    current_user: CurrentUser,
    db: DbSession,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> AnalysisHistory:
    base = select(Analysis).where(Analysis.user_id == current_user.id)
    total = db.scalar(select(func.count()).select_from(base.subquery())) or 0

    analyses = db.scalars(
        base.order_by(Analysis.created_at.desc(), Analysis.id.desc())
        .offset(offset)
        .limit(limit)
    ).all()

    return AnalysisHistory(
        items=[_summarise(item) for item in analyses],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{analysis_id}", response_model=AnalysisOut)
def get_analysis(
    analysis_id: int, current_user: CurrentUser, db: DbSession
) -> AnalysisOut:
    return _to_out(_load_owned_analysis(db, analysis_id, current_user.id))


@router.get("/{analysis_id}/export")
def export_analysis(
    analysis_id: int, current_user: CurrentUser, db: DbSession
) -> Response:
    analysis = _load_owned_analysis(db, analysis_id, current_user.id)
    version = analysis.resume_version
    filename = export_filename(
        slugify(Path(version.resume.filename).stem), version.version_no
    )

    return Response(
        content=build_resume_docx(version.raw_text),
        media_type=(
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ),
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/{analysis_id}/reanalyze", response_model=AnalysisOut)
async def reanalyze(
    analysis_id: int,
    payload: ReanalyzeRequest,
    current_user: CurrentUser,
    db: DbSession,
    llm_api_key: Annotated[str | None, Header(alias="X-LLM-API-Key")] = None,
) -> AnalysisOut:
    parent = _load_owned_analysis(db, analysis_id, current_user.id)
    parent_version = parent.resume_version
    resume = parent_version.resume

    try:
        parsed = parse_resume_text(payload.raw_text, filename=resume.filename)
    except ExtractionError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc

    score = score_resume(parsed, parent.job.description_text)
    drafts = await _build_suggestions(
        parsed, parent.job.description_text, score, llm_api_key
    )

    next_version_no = max(
        (version.version_no for version in resume.versions), default=0
    ) + 1
    version = ResumeVersion(
        resume=resume,
        version_no=next_version_no,
        raw_text=parsed.raw_text,
        sections_json=_sections_payload(parsed),
        parent_version_id=parent_version.id,
    )
    analysis = Analysis(
        user_id=current_user.id,
        resume_version=version,
        job=parent.job,
        ats_score=score.overall,
        score_breakdown_json=score.to_dict(),
    )
    _attach_suggestions(analysis, drafts)

    db.add_all([version, analysis])
    db.commit()
    db.refresh(analysis)
    return _to_out(analysis)
