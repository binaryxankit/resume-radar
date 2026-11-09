from io import BytesIO

from docx import Document

JOB = (
    "Senior Backend Engineer. Required Python, PostgreSQL, Kafka, Kubernetes and Docker. "
    "You will design distributed systems and own reliability."
)

RESUME_LINES = [
    "Jane Doe",
    "jane@example.com",
    "+1 555 123 4567",
    "Summary",
    "Backend engineer with six years of experience.",
    "Experience",
    "Senior Engineer, Acme Corp",
    "- Built APIs handling 2M requests per day",
    "Skills",
    "Python, Docker",
    "Education",
    "BSc Computer Science",
]


def _docx_bytes(lines: list[str]) -> bytes:
    document = Document()
    for line in lines:
        document.add_paragraph(line)
    buffer = BytesIO()
    document.save(buffer)
    return buffer.getvalue()


def _auth_headers(client, email: str) -> dict[str, str]:
    credentials = {"email": email, "password": "supersecret"}
    client.post("/api/auth/register", json=credentials)
    login = client.post("/api/auth/login", json=credentials)
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _create_analysis(
    client,
    headers: dict[str, str],
    filename: str = "resume.docx",
    company: str = "Stripe",
    role: str = "Senior Backend Engineer",
):
    return client.post(
        "/api/analyses",
        headers=headers,
        data={
            "job_description": JOB,
            "company_name": company,
            "role_title": role,
            "role_level": "senior",
        },
        files={
            "file": (
                filename,
                _docx_bytes(RESUME_LINES),
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )


def test_create_analysis_returns_score_and_suggestions(client) -> None:
    headers = _auth_headers(client, "analyst@example.com")

    response = _create_analysis(client, headers)

    assert response.status_code == 201
    body = response.json()
    assert body["company"] == "Stripe"
    assert body["role"] == "Senior Backend Engineer"
    assert 0 <= body["ats_score"] <= 100
    assert "python" in body["matched_keywords"]
    assert {"kafka", "kubernetes", "postgresql"} <= set(body["missing_keywords"])
    assert body["suggestions"]
    assert body["sections"]["experience"]
    assert "Jane Doe" in body["raw_text"]


def test_create_analysis_requires_authentication(client) -> None:
    response = client.post(
        "/api/analyses",
        data={"job_description": JOB, "company_name": "Stripe", "role_title": "Engineer"},
        files={"file": ("resume.docx", _docx_bytes(RESUME_LINES))},
    )

    assert response.status_code == 401


def test_unsupported_file_type_is_rejected(client) -> None:
    headers = _auth_headers(client, "badfile@example.com")

    response = _create_analysis(client, headers, filename="resume.rtf")

    assert response.status_code == 415


def test_list_and_get_analysis(client) -> None:
    headers = _auth_headers(client, "lister@example.com")
    created = _create_analysis(client, headers).json()

    listing = client.get("/api/analyses", headers=headers)
    assert listing.status_code == 200
    history = listing.json()
    assert history["total"] == 1
    assert history["limit"] == 20
    assert history["offset"] == 0
    assert len(history["items"]) == 1
    assert history["items"][0]["id"] == created["id"]

    detail = client.get(f"/api/analyses/{created['id']}", headers=headers)
    assert detail.status_code == 200
    assert detail.json()["ats_score"] == created["ats_score"]


def test_list_analyses_paginates(client) -> None:
    headers = _auth_headers(client, "pager@example.com")
    created = [_create_analysis(client, headers).json() for _ in range(3)]

    first = client.get("/api/analyses", headers=headers, params={"limit": 2})
    body = first.json()
    assert body["total"] == 3
    assert body["limit"] == 2
    assert body["offset"] == 0
    assert len(body["items"]) == 2
    assert body["items"][0]["id"] == created[2]["id"]

    second = client.get(
        "/api/analyses", headers=headers, params={"limit": 2, "offset": 2}
    )
    assert second.json()["items"][0]["id"] == created[0]["id"]

    invalid = client.get("/api/analyses", headers=headers, params={"limit": 101})
    assert invalid.status_code == 422


def test_search_analysis_history(client) -> None:
    headers = _auth_headers(client, "searcher@example.com")
    stripe = _create_analysis(
        client, headers, company="Stripe", role="Backend Engineer"
    ).json()
    _create_analysis(client, headers, company="Linear", role="Design Engineer")

    by_company = client.get("/api/analyses", headers=headers, params={"q": " STRIPE "})
    body = by_company.json()
    assert body["total"] == 1
    assert body["items"][0]["id"] == stripe["id"]

    by_role = client.get("/api/analyses", headers=headers, params={"q": "design"})
    assert by_role.json()["total"] == 1

    missing = client.get("/api/analyses", headers=headers, params={"q": "netflix"})
    assert missing.json()["total"] == 0
    assert missing.json()["items"] == []


def test_search_history_is_private_to_owner(client) -> None:
    owner_headers = _auth_headers(client, "search-owner@example.com")
    _create_analysis(client, owner_headers, company="Stripe")

    other_headers = _auth_headers(client, "search-other@example.com")
    response = client.get("/api/analyses", headers=other_headers, params={"q": "stripe"})

    assert response.json()["total"] == 0


def test_analysis_is_private_to_owner(client) -> None:
    owner_headers = _auth_headers(client, "owner@example.com")
    created = _create_analysis(client, owner_headers).json()

    other_headers = _auth_headers(client, "intruder@example.com")
    response = client.get(f"/api/analyses/{created['id']}", headers=other_headers)

    assert response.status_code == 404


def test_export_analysis_returns_docx(client) -> None:
    headers = _auth_headers(client, "exporter@example.com")
    created = _create_analysis(client, headers).json()

    response = client.get(f"/api/analyses/{created['id']}/export", headers=headers)

    assert response.status_code == 200
    assert response.headers["content-type"].startswith(
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    assert "resume-v1.docx" in response.headers["content-disposition"]

    document = Document(BytesIO(response.content))
    paragraphs = [paragraph.text for paragraph in document.paragraphs]
    assert "SUMMARY" in paragraphs
    assert any("Built APIs" in text for text in paragraphs)


def test_reanalyze_creates_new_version(client) -> None:
    headers = _auth_headers(client, "editor@example.com")
    created = _create_analysis(client, headers).json()

    improved_text = "\n".join(
        RESUME_LINES + ["", "Additional Skills", "PostgreSQL, Kafka, Kubernetes"]
    )
    response = client.post(
        f"/api/analyses/{created['id']}/reanalyze",
        headers=headers,
        json={"raw_text": improved_text},
    )

    assert response.status_code == 200
    updated = response.json()
    assert updated["id"] != created["id"]
    assert updated["resume_version_id"] != created["resume_version_id"]
    assert updated["ats_score"] >= created["ats_score"]
    assert {"postgresql", "kafka", "kubernetes"} <= set(updated["matched_keywords"])
