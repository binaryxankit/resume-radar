"""ORM model registry.

Importing this package registers every model on ``Base.metadata`` so Alembic
and ``Base.metadata.create_all`` can see the full schema.
"""

from app.models.analysis import Analysis, Suggestion
from app.models.base import Base, TimestampMixin
from app.models.company import Company
from app.models.insight import Insight
from app.models.job import Job
from app.models.resume import Resume, ResumeVersion
from app.models.role import Role
from app.models.user import User

__all__ = [
    "Analysis",
    "Base",
    "Company",
    "Insight",
    "Job",
    "Resume",
    "ResumeVersion",
    "Role",
    "Suggestion",
    "TimestampMixin",
    "User",
]
