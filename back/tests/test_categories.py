"""
Tests for category endpoints:
  GET    /api/categories
  GET    /api/categories/<id>
  POST   /api/categories
  PUT    /api/categories/<id>
  DELETE /api/categories/<id>
"""


# ── GET endpoints ─────────────────────────────────────────────────────────────

def test_get_categories_empty(client):
    res = client.get("/api/categories")
    assert res.status_code == 200
    assert res.get_json()["data"] == []


def test_get_categories_includes_skills(client, make_category, make_skill):
    cat = make_category(name="Tecnología")
    make_skill(name="Python", category_id=cat.id)
    make_skill(name="Go", category_id=cat.id)

    res = client.get("/api/categories")
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert len(data) == 1
    assert len(data[0]["skills"]) == 2


def test_get_category_found(client, make_category):
    cat = make_category(name="Arte")
    res = client.get(f"/api/categories/{cat.id}")
    assert res.status_code == 200
    assert res.get_json()["data"]["name"] == "Arte"


def test_get_category_not_found(client):
    res = client.get("/api/categories/9999")
    assert res.status_code == 404


# ── POST /api/categories ──────────────────────────────────────────────────────

def test_create_category_success(client, make_user, auth_headers):
    user = make_user()
    res = client.post("/api/categories",
                      json={"name": "Tecnología"},
                      headers=auth_headers(user))
    assert res.status_code == 201
    assert res.get_json()["data"]["name"] == "Tecnología"


def test_create_category_duplicate_name(client, make_user, make_category,
                                        auth_headers):
    user = make_user()
    make_category(name="Tecnología")
    res = client.post("/api/categories",
                      json={"name": "Tecnología"},
                      headers=auth_headers(user))
    assert res.status_code == 400


def test_create_category_missing_name(client, make_user, auth_headers):
    user = make_user()
    res = client.post("/api/categories", json={}, headers=auth_headers(user))
    assert res.status_code == 400


def test_create_category_no_token(client):
    res = client.post("/api/categories", json={"name": "Tecnología"})
    assert res.status_code == 401


# ── PUT /api/categories/<id> ──────────────────────────────────────────────────

def test_update_category_success(client, make_user, make_category, auth_headers):
    user = make_user()
    cat = make_category(name="Arte")
    res = client.put(f"/api/categories/{cat.id}",
                     json={"name": "Arte Digital"},
                     headers=auth_headers(user))
    assert res.status_code == 200
    assert res.get_json()["data"]["name"] == "Arte Digital"


def test_update_category_no_token(client, make_category):
    cat = make_category()
    res = client.put(f"/api/categories/{cat.id}", json={"name": "Nuevo"})
    assert res.status_code == 401


# ── DELETE /api/categories/<id> ───────────────────────────────────────────────

def test_delete_category_success(client, make_user, make_category, auth_headers):
    user = make_user()
    cat = make_category()
    res = client.delete(f"/api/categories/{cat.id}", headers=auth_headers(user))
    assert res.status_code == 200
    assert client.get(f"/api/categories/{cat.id}").status_code == 404


def test_delete_category_no_token(client, make_category):
    cat = make_category()
    res = client.delete(f"/api/categories/{cat.id}")
    assert res.status_code == 401
