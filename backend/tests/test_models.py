from app.models import Base
from sqlalchemy.orm import configure_mappers

CORE_TABLES = {
    "users",
    "companies",
    "roles",
    "jobs",
    "resumes",
    "resume_versions",
    "analyses",
    "suggestions",
    "insights",
}


def test_metadata_registers_core_tables() -> None:
    assert CORE_TABLES <= set(Base.metadata.tables)


def test_mappers_configure_without_errors() -> None:
    configure_mappers()


def test_resume_version_is_unique_per_resume() -> None:
    table = Base.metadata.tables["resume_versions"]

    assert "uq_resume_version" in {constraint.name for constraint in table.constraints}


def test_analysis_references_user_resume_and_job() -> None:
    table = Base.metadata.tables["analyses"]
    foreign_keys = {fk.parent.name for fk in table.foreign_keys}

    assert {"user_id", "resume_version_id", "job_id"} <= foreign_keys


def test_insight_records_provenance() -> None:
    columns = Base.metadata.tables["insights"].columns

    assert {"source_url", "source_kind", "fetched_at", "confidence"} <= set(columns.keys())
