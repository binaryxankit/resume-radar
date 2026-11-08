import pytest
from app.core.security import (
    InvalidTokenError,
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_password_hash_roundtrip() -> None:
    stored = hash_password("correct horse battery")

    assert stored != "correct horse battery"
    assert verify_password("correct horse battery", stored)
    assert not verify_password("wrong password", stored)


def test_password_hash_is_salted() -> None:
    assert hash_password("same-password") != hash_password("same-password")


def test_verify_rejects_malformed_hash() -> None:
    assert not verify_password("anything", "not-a-valid-hash")


def test_create_and_decode_token() -> None:
    token = create_access_token("42")

    assert decode_access_token(token) == "42"


def test_decode_invalid_token_raises() -> None:
    with pytest.raises(InvalidTokenError):
        decode_access_token("not-a-token")


def test_register_and_login_flow(client) -> None:
    response = client.post(
        "/api/auth/register",
        json={"email": "Jane@Example.com", "password": "supersecret"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "jane@example.com"
    user_id = body["id"]

    login = client.post(
        "/api/auth/login",
        json={"email": "jane@example.com", "password": "supersecret"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]

    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["id"] == user_id


def test_register_duplicate_email_conflicts(client) -> None:
    payload = {"email": "dup@example.com", "password": "supersecret"}

    assert client.post("/api/auth/register", json=payload).status_code == 201
    assert client.post("/api/auth/register", json=payload).status_code == 409


def test_register_rejects_short_password(client) -> None:
    response = client.post(
        "/api/auth/register",
        json={"email": "short@example.com", "password": "short"},
    )

    assert response.status_code == 422


def test_login_with_wrong_password_fails(client) -> None:
    client.post(
        "/api/auth/register",
        json={"email": "wrong@example.com", "password": "supersecret"},
    )

    response = client.post(
        "/api/auth/login",
        json={"email": "wrong@example.com", "password": "incorrect-pass"},
    )

    assert response.status_code == 401


def test_me_requires_token(client) -> None:
    assert client.get("/api/auth/me").status_code == 401


def test_me_rejects_invalid_token(client) -> None:
    response = client.get("/api/auth/me", headers={"Authorization": "Bearer nope"})

    assert response.status_code == 401
