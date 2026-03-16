"""
Tests for authentication endpoints:
  POST /api/auth/login
  GET  /api/auth/me
  POST /api/auth/refresh
  POST /api/auth/google/verify
  POST /api/logout
"""
from unittest.mock import patch

from flask_jwt_extended import create_refresh_token


# ── Login ─────────────────────────────────────────────────────────────────────

def test_login_success(client, make_user):
    user = make_user(email="alice@test.com", password="secret123")
    res = client.post("/api/auth/login",
                      json={"email": "alice@test.com", "password": "secret123"})
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert "token" in data
    assert "refresh_token" in data
    assert data["email"] == user.email


def test_login_wrong_password(client, make_user):
    make_user(email="alice@test.com", password="secret123")
    res = client.post("/api/auth/login",
                      json={"email": "alice@test.com", "password": "wrong"})
    assert res.status_code == 401


def test_login_unknown_email(client):
    res = client.post("/api/auth/login",
                      json={"email": "noone@test.com", "password": "secret123"})
    assert res.status_code == 401


def test_login_missing_email(client):
    res = client.post("/api/auth/login", json={"password": "secret123"})
    assert res.status_code == 400


def test_login_missing_password(client):
    res = client.post("/api/auth/login", json={"email": "alice@test.com"})
    assert res.status_code == 400


# ── /api/auth/me ──────────────────────────────────────────────────────────────

def test_get_me_success(client, make_user, auth_headers):
    user = make_user(email="alice@test.com")
    res = client.get("/api/auth/me", headers=auth_headers(user))
    assert res.status_code == 200
    assert res.get_json()["data"]["email"] == user.email


def test_get_me_no_token(client):
    res = client.get("/api/auth/me")
    assert res.status_code == 401


def test_get_me_invalid_token(client):
    res = client.get("/api/auth/me",
                     headers={"Authorization": "Bearer not.a.real.token"})
    assert res.status_code == 422


# ── Refresh token ─────────────────────────────────────────────────────────────

def test_refresh_success(client, make_user):
    user = make_user(email="alice@test.com")
    refresh_token = create_refresh_token(identity=user.email)
    res = client.post("/api/auth/refresh",
                      headers={"Authorization": f"Bearer {refresh_token}"})
    assert res.status_code == 200
    assert "token" in res.get_json()["data"]


def test_refresh_with_access_token_rejected(client, make_user, auth_headers):
    user = make_user()
    res = client.post("/api/auth/refresh", headers=auth_headers(user))
    assert res.status_code == 422


def test_refresh_no_token(client):
    res = client.post("/api/auth/refresh")
    assert res.status_code == 401


# ── Google OAuth ──────────────────────────────────────────────────────────────

GOOGLE_PAYLOAD = {
    "sub": "google-id-123",
    "email": "google@test.com",
    "given_name": "Google",
    "family_name": "User",
    "picture": "https://example.com/photo.jpg",
}


def test_google_verify_missing_token(client):
    res = client.post("/api/auth/google/verify", json={})
    assert res.status_code == 400


def test_google_verify_invalid_token(client):
    with patch("back.urls.user.google_id_token.verify_oauth2_token",
               side_effect=ValueError("bad token")):
        res = client.post("/api/auth/google/verify",
                          json={"id_token": "bad-token"})
    assert res.status_code == 401


def test_google_verify_new_user(client):
    """A new Google user is created and JWT tokens are returned."""
    with patch("back.urls.user.google_id_token.verify_oauth2_token",
               return_value=GOOGLE_PAYLOAD):
        res = client.post("/api/auth/google/verify",
                          json={"id_token": "valid-token"})
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert "token" in data
    assert "refresh_token" in data
    assert data["email"] == "google@test.com"


def test_google_verify_existing_email_links_google_id(client, make_user):
    """Existing user by email gets google_id linked."""
    user = make_user(email="google@test.com")
    assert user.google_id is None

    with patch("back.urls.user.google_id_token.verify_oauth2_token",
               return_value=GOOGLE_PAYLOAD):
        res = client.post("/api/auth/google/verify",
                          json={"id_token": "valid-token"})
    assert res.status_code == 200

    from back.models import db, User
    db.session.refresh(user)
    assert user.google_id == "google-id-123"


def test_google_verify_returning_user(client, make_user):
    """Returning Google user (google_id already set) gets tokens without duplicates."""
    user = make_user(email="google@test.com")
    from back.models import db
    user.google_id = "google-id-123"
    db.session.commit()

    with patch("back.urls.user.google_id_token.verify_oauth2_token",
               return_value=GOOGLE_PAYLOAD):
        res = client.post("/api/auth/google/verify",
                          json={"id_token": "valid-token"})
    assert res.status_code == 200

    from back.models import User
    assert User.query.filter_by(email="google@test.com").count() == 1


# ── Logout ────────────────────────────────────────────────────────────────────

def test_logout(client):
    res = client.post("/api/logout")
    assert res.status_code == 200
