"""
Tests for rating endpoints — constraints are the main focus:
  GET    /api/ratings
  GET    /api/ratings/<id>
  POST   /api/ratings
  PUT    /api/ratings/<id>
  DELETE /api/ratings/<id>
"""


# ── GET endpoints ─────────────────────────────────────────────────────────────

def test_get_ratings_empty(client):
    res = client.get("/api/ratings")
    assert res.status_code == 200
    assert res.get_json()["data"] == []


def test_get_ratings_pagination(client, make_user, make_skill, make_exchange,
                                make_rating):
    offerer = make_user(email="offerer@test.com")
    demander = make_user(email="demander@test.com")
    skill = make_skill()
    ex1 = make_exchange(offerer_id=offerer.id, skill_id=skill.id,
                        demander_id=demander.id)
    ex2 = make_exchange(offerer_id=demander.id, skill_id=skill.id,
                        demander_id=offerer.id)
    ex3 = make_exchange(offerer_id=offerer.id, skill_id=skill.id,
                        demander_id=demander.id)
    make_rating(exchange_id=ex1.id, rater_id=offerer.id, rated_id=demander.id)
    make_rating(exchange_id=ex2.id, rater_id=demander.id, rated_id=offerer.id)
    make_rating(exchange_id=ex3.id, rater_id=offerer.id, rated_id=demander.id)

    res = client.get("/api/ratings?per_page=2")
    assert res.status_code == 200
    body = res.get_json()
    assert "pagination" in body
    assert body["pagination"]["total"] == 3
    assert len(body["data"]) == 2
    assert body["pagination"]["has_next"] is True


def test_get_ratings_list(client, make_user, make_skill, make_exchange,
                          make_rating):
    offerer = make_user(email="offerer@test.com")
    demander = make_user(email="demander@test.com")
    skill = make_skill()
    exchange = make_exchange(offerer_id=offerer.id, skill_id=skill.id,
                             demander_id=demander.id)
    make_rating(exchange_id=exchange.id, rater_id=offerer.id,
                rated_id=demander.id, score=4)

    res = client.get("/api/ratings")
    assert res.status_code == 200
    assert len(res.get_json()["data"]) == 1


def test_get_rating_found(client, make_user, make_skill, make_exchange,
                          make_rating):
    offerer = make_user(email="offerer@test.com")
    demander = make_user(email="demander@test.com")
    skill = make_skill()
    exchange = make_exchange(offerer_id=offerer.id, skill_id=skill.id,
                             demander_id=demander.id)
    rating = make_rating(exchange_id=exchange.id, rater_id=offerer.id,
                         rated_id=demander.id, score=4)

    res = client.get(f"/api/ratings/{rating.id}")
    assert res.status_code == 200
    assert res.get_json()["data"]["score"] == 4


def test_get_rating_not_found(client):
    res = client.get("/api/ratings/9999")
    assert res.status_code == 404


# ── POST /api/ratings ─────────────────────────────────────────────────────────

def test_create_rating_success(client, make_user, make_skill, make_exchange,
                               auth_headers):
    offerer = make_user(email="offerer@test.com")
    demander = make_user(email="demander@test.com")
    skill = make_skill()
    exchange = make_exchange(offerer_id=offerer.id, skill_id=skill.id,
                             demander_id=demander.id)

    res = client.post("/api/ratings",
                      json={
                          "exchange_id": exchange.id,
                          "rater_id": offerer.id,
                          "score": 5,
                      },
                      headers=auth_headers(offerer))
    assert res.status_code == 201
    assert "id" in res.get_json()["data"]


def test_create_rating_duplicate_rejected(client, make_user, make_skill,
                                          make_exchange, make_rating,
                                          auth_headers):
    """Unique constraint (exchange_id, rater_id) must be enforced."""
    offerer = make_user(email="offerer@test.com")
    demander = make_user(email="demander@test.com")
    skill = make_skill()
    exchange = make_exchange(offerer_id=offerer.id, skill_id=skill.id,
                             demander_id=demander.id)
    make_rating(exchange_id=exchange.id, rater_id=offerer.id,
                rated_id=demander.id, score=4)

    res = client.post("/api/ratings",
                      json={
                          "exchange_id": exchange.id,
                          "rater_id": offerer.id,
                          "score": 5,
                      },
                      headers=auth_headers(offerer))
    assert res.status_code == 400


def test_create_rating_no_demander(client, make_user, make_skill, make_exchange,
                                   auth_headers):
    """Exchange without demander cannot be rated."""
    offerer = make_user()
    skill = make_skill()
    exchange = make_exchange(offerer_id=offerer.id, skill_id=skill.id)

    res = client.post("/api/ratings",
                      json={
                          "exchange_id": exchange.id,
                          "rater_id": offerer.id,
                          "score": 5,
                      },
                      headers=auth_headers(offerer))
    assert res.status_code == 400


def test_create_rating_score_too_low(client, make_user, make_skill,
                                     make_exchange, auth_headers):
    offerer = make_user(email="offerer@test.com")
    demander = make_user(email="demander@test.com")
    skill = make_skill()
    exchange = make_exchange(offerer_id=offerer.id, skill_id=skill.id,
                             demander_id=demander.id)

    res = client.post("/api/ratings",
                      json={
                          "exchange_id": exchange.id,
                          "rater_id": offerer.id,
                          "score": 0,
                      },
                      headers=auth_headers(offerer))
    assert res.status_code == 400


def test_create_rating_score_too_high(client, make_user, make_skill,
                                      make_exchange, auth_headers):
    offerer = make_user(email="offerer@test.com")
    demander = make_user(email="demander@test.com")
    skill = make_skill()
    exchange = make_exchange(offerer_id=offerer.id, skill_id=skill.id,
                             demander_id=demander.id)

    res = client.post("/api/ratings",
                      json={
                          "exchange_id": exchange.id,
                          "rater_id": offerer.id,
                          "score": 6,
                      },
                      headers=auth_headers(offerer))
    assert res.status_code == 400


def test_create_rating_forbidden(client, make_user, make_skill, make_exchange,
                                 auth_headers):
    offerer = make_user(email="offerer@test.com")
    demander = make_user(email="demander@test.com")
    outsider = make_user(email="outsider@test.com")
    skill = make_skill()
    exchange = make_exchange(offerer_id=offerer.id, skill_id=skill.id,
                             demander_id=demander.id)

    res = client.post("/api/ratings",
                      json={
                          "exchange_id": exchange.id,
                          "rater_id": offerer.id,
                          "score": 4,
                      },
                      headers=auth_headers(outsider))
    assert res.status_code == 403


def test_create_rating_no_token(client, make_user, make_skill, make_exchange):
    offerer = make_user(email="offerer@test.com")
    demander = make_user(email="demander@test.com")
    skill = make_skill()
    exchange = make_exchange(offerer_id=offerer.id, skill_id=skill.id,
                             demander_id=demander.id)

    res = client.post("/api/ratings",
                      json={
                          "exchange_id": exchange.id,
                          "rater_id": offerer.id,
                          "score": 4,
                      })
    assert res.status_code == 401


# ── PUT /api/ratings/<id> ─────────────────────────────────────────────────────

def test_update_rating_success(client, make_user, make_skill, make_exchange,
                               make_rating, auth_headers):
    offerer = make_user(email="offerer@test.com")
    demander = make_user(email="demander@test.com")
    skill = make_skill()
    exchange = make_exchange(offerer_id=offerer.id, skill_id=skill.id,
                             demander_id=demander.id)
    rating = make_rating(exchange_id=exchange.id, rater_id=offerer.id,
                         rated_id=demander.id, score=3)

    res = client.put(f"/api/ratings/{rating.id}",
                     json={"score": 5, "comment": "Excelente"},
                     headers=auth_headers(offerer))
    assert res.status_code == 200
    body = res.get_json()["data"]
    assert body["score"] == 5
    assert body["comment"] == "Excelente"


def test_update_rating_forbidden(client, make_user, make_skill, make_exchange,
                                 make_rating, auth_headers):
    offerer = make_user(email="offerer@test.com")
    demander = make_user(email="demander@test.com")
    skill = make_skill()
    exchange = make_exchange(offerer_id=offerer.id, skill_id=skill.id,
                             demander_id=demander.id)
    rating = make_rating(exchange_id=exchange.id, rater_id=offerer.id,
                         rated_id=demander.id, score=3)

    res = client.put(f"/api/ratings/{rating.id}",
                     json={"score": 1},
                     headers=auth_headers(demander))
    assert res.status_code == 403


def test_update_rating_score_out_of_range(client, make_user, make_skill,
                                          make_exchange, make_rating,
                                          auth_headers):
    offerer = make_user(email="offerer@test.com")
    demander = make_user(email="demander@test.com")
    skill = make_skill()
    exchange = make_exchange(offerer_id=offerer.id, skill_id=skill.id,
                             demander_id=demander.id)
    rating = make_rating(exchange_id=exchange.id, rater_id=offerer.id,
                         rated_id=demander.id, score=3)

    res = client.put(f"/api/ratings/{rating.id}",
                     json={"score": 10},
                     headers=auth_headers(offerer))
    assert res.status_code == 400


def test_update_rating_not_found(client, make_user, auth_headers):
    user = make_user()
    res = client.put("/api/ratings/9999",
                     json={"score": 5},
                     headers=auth_headers(user))
    assert res.status_code == 404


# ── DELETE /api/ratings/<id> ──────────────────────────────────────────────────

def test_delete_rating_success(client, make_user, make_skill, make_exchange,
                               make_rating, auth_headers):
    offerer = make_user(email="offerer@test.com")
    demander = make_user(email="demander@test.com")
    skill = make_skill()
    exchange = make_exchange(offerer_id=offerer.id, skill_id=skill.id,
                             demander_id=demander.id)
    rating = make_rating(exchange_id=exchange.id, rater_id=offerer.id,
                         rated_id=demander.id, score=4)

    res = client.delete(f"/api/ratings/{rating.id}",
                        headers=auth_headers(offerer))
    assert res.status_code == 200
    assert client.get(f"/api/ratings/{rating.id}").status_code == 404


def test_delete_rating_forbidden(client, make_user, make_skill, make_exchange,
                                 make_rating, auth_headers):
    offerer = make_user(email="offerer@test.com")
    demander = make_user(email="demander@test.com")
    skill = make_skill()
    exchange = make_exchange(offerer_id=offerer.id, skill_id=skill.id,
                             demander_id=demander.id)
    rating = make_rating(exchange_id=exchange.id, rater_id=offerer.id,
                         rated_id=demander.id, score=4)

    res = client.delete(f"/api/ratings/{rating.id}",
                        headers=auth_headers(demander))
    assert res.status_code == 403


def test_delete_rating_not_found(client, make_user, auth_headers):
    user = make_user()
    res = client.delete("/api/ratings/9999", headers=auth_headers(user))
    assert res.status_code == 404
