"""
Tests for skill endpoints:
  GET    /api/skills
  GET    /api/skills/<id>
  GET    /api/skills/category/<category_id>
  POST   /api/skills
  PUT    /api/skills/<id>
  DELETE /api/skills/<id>
"""


# ── GET endpoints ─────────────────────────────────────────────────────────────

def test_get_skills_empty(client):
    res = client.get("/api/skills")
    assert res.status_code == 200
    assert res.get_json()["data"] == []


def test_get_skills_list(client, make_skill):
    make_skill(name="Python")
    make_skill(name="JavaScript")
    res = client.get("/api/skills")
    assert res.status_code == 200
    assert len(res.get_json()["data"]) == 2


def test_get_skill_found(client, make_skill):
    skill = make_skill(name="Python")
    res = client.get(f"/api/skills/{skill.id}")
    assert res.status_code == 200
    assert res.get_json()["data"]["name"] == "Python"


def test_get_skill_not_found(client):
    res = client.get("/api/skills/9999")
    assert res.status_code == 404


def test_get_skills_by_category(client, make_category, make_skill):
    cat = make_category(name="Tecnología")
    make_skill(name="Python", category_id=cat.id)
    make_skill(name="Go", category_id=cat.id)
    other_cat = make_category(name="Arte")
    make_skill(name="Dibujo", category_id=other_cat.id)

    res = client.get(f"/api/skills/category/{cat.id}")
    assert res.status_code == 200
    assert len(res.get_json()["data"]) == 2


# ── POST /api/skills ──────────────────────────────────────────────────────────

def test_create_skill_success(client, make_category, auth_headers, make_user):
    user = make_user()
    cat = make_category(name="Tecnología")
    res = client.post("/api/skills",
                      json={"name": "Python", "category_id": cat.id},
                      headers=auth_headers(user))
    assert res.status_code == 201
    assert "id" in res.get_json()["data"]


def test_create_skill_missing_name(client, make_category, auth_headers,
                                   make_user):
    user = make_user()
    cat = make_category()
    res = client.post("/api/skills",
                      json={"category_id": cat.id},
                      headers=auth_headers(user))
    assert res.status_code == 400


def test_create_skill_missing_category_id(client, auth_headers, make_user):
    user = make_user()
    res = client.post("/api/skills",
                      json={"name": "Python"},
                      headers=auth_headers(user))
    assert res.status_code == 400


def test_create_skill_no_token(client, make_category):
    cat = make_category()
    res = client.post("/api/skills",
                      json={"name": "Python", "category_id": cat.id})
    assert res.status_code == 401


# ── PUT /api/skills/<id> ──────────────────────────────────────────────────────

def test_update_skill_success(client, make_skill, make_category, auth_headers,
                              make_user):
    user = make_user()
    skill = make_skill(name="Python")
    new_cat = make_category(name="Nueva Cat")
    res = client.put(f"/api/skills/{skill.id}",
                     json={"description": "Lenguaje versátil",
                           "category_id": new_cat.id},
                     headers=auth_headers(user))
    assert res.status_code == 200
    assert res.get_json()["data"]["description"] == "Lenguaje versátil"


def test_update_skill_no_token(client, make_skill):
    skill = make_skill()
    res = client.put(f"/api/skills/{skill.id}",
                     json={"description": "desc"})
    assert res.status_code == 401


# ── DELETE /api/skills/<id> ───────────────────────────────────────────────────

def test_delete_skill_success(client, make_skill, auth_headers, make_user):
    user = make_user()
    skill = make_skill()
    res = client.delete(f"/api/skills/{skill.id}", headers=auth_headers(user))
    assert res.status_code == 200
    assert client.get(f"/api/skills/{skill.id}").status_code == 404


def test_delete_skill_no_token(client, make_skill):
    skill = make_skill()
    res = client.delete(f"/api/skills/{skill.id}")
    assert res.status_code == 401
