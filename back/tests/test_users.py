"""
Tests for user endpoints:
  GET    /api/users
  GET    /api/users/<id>
  GET    /api/users/category/<id>
  POST   /api/users
  PUT    /api/users/<id>
  DELETE /api/users/<id>
  POST   /api/users/<id>/skill
"""


# ── GET /api/users ────────────────────────────────────────────────────────────

def test_get_users_empty(client):
    res = client.get("/api/users")
    assert res.status_code == 200
    assert res.get_json()["data"] == []


def test_get_users_returns_list(client, make_user):
    make_user(email="a@test.com")
    make_user(email="b@test.com")
    res = client.get("/api/users")
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert len(data) == 2
    assert "rating_average" in data[0]


def test_get_users_pagination_meta(client, make_user):
    for i in range(3):
        make_user(email=f"u{i}@test.com")
    res = client.get("/api/users?per_page=2")
    assert res.status_code == 200
    body = res.get_json()
    assert "pagination" in body
    assert body["pagination"]["total"] == 3
    assert body["pagination"]["pages"] == 2
    assert body["pagination"]["has_next"] is True
    assert body["pagination"]["has_prev"] is False
    assert len(body["data"]) == 2


def test_get_users_page_2(client, make_user):
    for i in range(3):
        make_user(email=f"p{i}@test.com")
    res = client.get("/api/users?page=2&per_page=2")
    assert res.status_code == 200
    body = res.get_json()
    assert len(body["data"]) == 1
    assert body["pagination"]["has_prev"] is True
    assert body["pagination"]["has_next"] is False


# ── GET /api/users/<id> ───────────────────────────────────────────────────────

def test_get_user_found(client, make_user, make_skill):
    skill = make_skill()
    user = make_user()
    user.skills.append(skill)
    from back.models import db
    db.session.commit()

    res = client.get(f"/api/users/{user.id}")
    assert res.status_code == 200
    body = res.get_json()["data"]
    assert body["email"] == user.email
    assert len(body["skills"]) == 1


def test_get_user_not_found(client):
    res = client.get("/api/users/9999")
    assert res.status_code == 404


# ── GET /api/users/category/<id> ──────────────────────────────────────────────

def test_get_users_by_category(client, make_user, make_category, make_skill):
    cat = make_category(name="Tecnología")
    skill = make_skill(name="Python", category_id=cat.id)
    user = make_user()
    user.skills.append(skill)
    from back.models import db
    db.session.commit()

    res = client.get(f"/api/users/category/{cat.id}")
    assert res.status_code == 200
    assert len(res.get_json()["data"]) == 1


def test_get_users_by_category_no_skills(client, make_category):
    cat = make_category()
    res = client.get(f"/api/users/category/{cat.id}")
    assert res.status_code == 200
    assert res.get_json()["data"] == []


# ── POST /api/users ───────────────────────────────────────────────────────────

def test_create_user_success(client):
    res = client.post("/api/users", json={
        "first_name": "Ana",
        "last_name": "García",
        "email": "ana@test.com",
        "password": "secure123",
        "accepts_terms": True,
    })
    assert res.status_code == 201
    assert "id" in res.get_json()["data"]


def test_create_user_duplicate_email(client, make_user):
    make_user(email="ana@test.com")
    res = client.post("/api/users", json={
        "first_name": "Ana",
        "last_name": "García",
        "email": "ana@test.com",
        "password": "secure123",
        "accepts_terms": True,
    })
    assert res.status_code == 400


def test_create_user_missing_required_field(client):
    res = client.post("/api/users", json={
        "last_name": "García",
        "email": "ana@test.com",
        "password": "secure123",
        "accepts_terms": True,
    })
    assert res.status_code == 400


def test_create_user_weak_password(client):
    res = client.post("/api/users", json={
        "first_name": "Ana",
        "last_name": "García",
        "email": "ana@test.com",
        "password": "short",
        "accepts_terms": True,
    })
    assert res.status_code == 400


def test_create_user_invalid_email(client):
    res = client.post("/api/users", json={
        "first_name": "Ana",
        "last_name": "García",
        "email": "not-an-email",
        "password": "secure123",
        "accepts_terms": True,
    })
    assert res.status_code == 400


# ── PUT /api/users/<id> ───────────────────────────────────────────────────────

def test_update_user_success(client, make_user, auth_headers):
    user = make_user()
    res = client.put(f"/api/users/{user.id}",
                     json={"first_name": "Nuevo"},
                     headers=auth_headers(user))
    assert res.status_code == 200
    assert res.get_json()["data"]["first_name"] == "Nuevo"


def test_update_user_forbidden(client, make_user, auth_headers):
    owner = make_user(email="owner@test.com")
    other = make_user(email="other@test.com")
    res = client.put(f"/api/users/{owner.id}",
                     json={"first_name": "Hack"},
                     headers=auth_headers(other))
    assert res.status_code == 403


def test_update_user_no_token(client, make_user):
    user = make_user()
    res = client.put(f"/api/users/{user.id}", json={"first_name": "Nuevo"})
    assert res.status_code == 401


def test_update_user_duplicate_email(client, make_user, auth_headers):
    user1 = make_user(email="user1@test.com")
    make_user(email="user2@test.com")
    res = client.put(f"/api/users/{user1.id}",
                     json={"email": "user2@test.com"},
                     headers=auth_headers(user1))
    assert res.status_code == 400


# ── DELETE /api/users/<id> ────────────────────────────────────────────────────

def test_delete_user_success(client, make_user, auth_headers):
    user = make_user()
    res = client.delete(f"/api/users/{user.id}", headers=auth_headers(user))
    assert res.status_code == 200
    assert client.get(f"/api/users/{user.id}").status_code == 404


def test_delete_user_forbidden(client, make_user, auth_headers):
    owner = make_user(email="owner@test.com")
    other = make_user(email="other@test.com")
    res = client.delete(f"/api/users/{owner.id}", headers=auth_headers(other))
    assert res.status_code == 403


def test_delete_user_no_token(client, make_user):
    user = make_user()
    res = client.delete(f"/api/users/{user.id}")
    assert res.status_code == 401


# ── POST /api/users/<id>/skill ────────────────────────────────────────────────

def test_associate_skill_success(client, make_user, make_skill, auth_headers):
    user = make_user()
    skill = make_skill()
    res = client.post(f"/api/users/{user.id}/skill",
                      json={"associate": skill.id},
                      headers=auth_headers(user))
    assert res.status_code == 201
    skills = res.get_json()["data"]["skills"]
    assert any(s["id"] == skill.id for s in skills)


def test_disassociate_skill_success(client, make_user, make_skill, auth_headers):
    user = make_user()
    skill = make_skill()
    user.skills.append(skill)
    from back.models import db
    db.session.commit()

    res = client.post(f"/api/users/{user.id}/skill",
                      json={"disassociate": skill.id},
                      headers=auth_headers(user))
    assert res.status_code == 201
    skills = res.get_json()["data"]["skills"]
    assert not any(s["id"] == skill.id for s in skills)


def test_associate_skill_forbidden(client, make_user, make_skill, auth_headers):
    owner = make_user(email="owner@test.com")
    other = make_user(email="other@test.com")
    skill = make_skill()
    res = client.post(f"/api/users/{owner.id}/skill",
                      json={"associate": skill.id},
                      headers=auth_headers(other))
    assert res.status_code == 403


def test_associate_skill_not_found(client, make_user, auth_headers):
    user = make_user()
    res = client.post(f"/api/users/{user.id}/skill",
                      json={"associate": 9999},
                      headers=auth_headers(user))
    assert res.status_code == 404
