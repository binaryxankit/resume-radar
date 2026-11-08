"""Deterministic keyword extraction and matching.

This module favors reproducibility over cleverness: a curated skill lexicon with
explicit aliases, plus a frequency-based fallback when a job description uses no
recognized skills. No network calls, no randomness.
"""

import re
from collections import Counter

SKILL_ALIASES: dict[str, tuple[str, ...]] = {
    "python": ("python",),
    "javascript": ("javascript", "js"),
    "typescript": ("typescript", "ts"),
    "java": ("java",),
    "golang": ("golang",),
    "rust": ("rust",),
    "ruby": ("ruby",),
    "php": ("php",),
    "csharp": ("c#", "csharp", "c sharp"),
    "cpp": ("c++", "cpp"),
    "sql": ("sql",),
    "nosql": ("nosql",),
    "postgresql": ("postgresql", "postgres"),
    "mysql": ("mysql",),
    "mongodb": ("mongodb", "mongo"),
    "redis": ("redis",),
    "kafka": ("kafka",),
    "rabbitmq": ("rabbitmq",),
    "elasticsearch": ("elasticsearch", "elastic search"),
    "docker": ("docker",),
    "kubernetes": ("kubernetes", "k8s"),
    "terraform": ("terraform",),
    "ansible": ("ansible",),
    "aws": ("aws", "amazon web services"),
    "gcp": ("gcp", "google cloud"),
    "azure": ("azure",),
    "linux": ("linux",),
    "git": ("git",),
    "fastapi": ("fastapi",),
    "django": ("django",),
    "flask": ("flask",),
    "spring": ("spring boot", "spring"),
    "nodejs": ("node.js", "nodejs", "node"),
    "react": ("react",),
    "nextjs": ("next.js", "nextjs"),
    "vue": ("vue", "vue.js"),
    "angular": ("angular",),
    "tailwind": ("tailwind",),
    "graphql": ("graphql",),
    "rest": ("rest", "restful"),
    "grpc": ("grpc",),
    "microservices": ("microservices", "micro-services"),
    "distributed systems": ("distributed systems", "distributed system"),
    "system design": ("system design",),
    "ci/cd": ("ci/cd", "cicd", "continuous integration"),
    "testing": ("unit testing", "pytest", "jest", "testing"),
    "observability": ("observability", "monitoring"),
    "prometheus": ("prometheus",),
    "grafana": ("grafana",),
    "machine learning": ("machine learning", "ml"),
    "pytorch": ("pytorch",),
    "tensorflow": ("tensorflow",),
    "pandas": ("pandas",),
    "numpy": ("numpy",),
    "spark": ("spark", "apache spark"),
    "airflow": ("airflow",),
    "dbt": ("dbt",),
    "etl": ("etl",),
    "agile": ("agile", "scrum", "kanban"),
    "leadership": ("leadership", "mentoring", "mentorship"),
    "communication": ("communication",),
    "stakeholder management": ("stakeholder management", "stakeholders"),
}

STOPWORDS = frozenset(
    """
    a an the and or but if then else for to of in on at by with from as is are was were
    be been being this that these those it its we you they he she our your their
    will would can could should may might must have has had do does did not no
    about into over under between within across per via more most other such than
    role team work working experience years year strong good excellent ability able
    including include includes etc plus using use used build building develop
    developing developed design designing deliver delivering help support ensure
    responsible responsibilities requirements required preferred qualifications
    candidate candidates job position company opportunity apply applicants
    """.split()
)

_TOKEN_RE = re.compile(r"[a-z][a-z0-9+#.]{2,}")
_COMPOUND_SPLIT_RE = re.compile(r"[\s\-_/]+")


def _alias_pattern(alias: str) -> re.Pattern[str]:
    return re.compile(
        r"(?<![A-Za-z0-9])" + re.escape(alias) + r"(?![A-Za-z0-9])",
        re.IGNORECASE,
    )


_ALIAS_PATTERNS: dict[str, tuple[re.Pattern[str], ...]] = {
    skill: tuple(_alias_pattern(alias) for alias in aliases)
    for skill, aliases in SKILL_ALIASES.items()
}


def contains_skill(text: str, skill: str) -> bool:
    """Return True when any alias for ``skill`` appears in ``text``."""
    return any(pattern.search(text) for pattern in _ALIAS_PATTERNS.get(skill, ()))


def extract_skills(text: str) -> tuple[str, ...]:
    """Return canonical skills mentioned in ``text``, sorted for determinism."""
    return tuple(sorted(skill for skill in SKILL_ALIASES if contains_skill(text, skill)))


def top_terms(text: str, limit: int = 15) -> tuple[str, ...]:
    """Frequency-based fallback for job descriptions without known skills."""
    tokens = [
        token
        for token in _TOKEN_RE.findall(text.lower().replace("-", " "))
        if token not in STOPWORDS
    ]
    counts = Counter(tokens)
    ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    return tuple(term for term, count in ranked if count >= 2)[:limit]


def extract_job_keywords(job_description: str) -> tuple[str, ...]:
    """Skills required by a job description, with a frequency fallback."""
    skills = extract_skills(job_description)
    if skills:
        return skills
    return top_terms(job_description)


def match_keywords(
    resume_text: str, job_description: str
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Split job keywords into (matched, missing) against the resume text."""
    keywords = extract_job_keywords(job_description)
    matched: list[str] = []
    missing: list[str] = []

    for keyword in keywords:
        haystack = resume_text
        if keyword in SKILL_ALIASES:
            found = contains_skill(haystack, keyword)
        else:
            found = re.search(
                r"(?<![A-Za-z0-9])" + re.escape(keyword) + r"(?![A-Za-z0-9])",
                haystack,
                re.IGNORECASE,
            ) is not None

        (matched if found else missing).append(keyword)

    return tuple(matched), tuple(missing)
