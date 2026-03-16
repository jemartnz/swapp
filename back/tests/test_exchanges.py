"""
Tests for exchange endpoints — full lifecycle:
  GET    /api/exchanges
  GET    /api/exchanges/<id>
  GET    /api/exchanges/offerer/<user_id>
  GET    /api/exchanges/demander/<user_id>
  GET    /api/exchanges/user/<user_id>
  POST   /api/exchanges
  PUT    /api/exchanges/<id>/complete
  PUT    /api/exchanges/join/<id>
  DELETE /api/exchanges/<id>
"""


# ── GET endpoints ─────────────────────────────────────────────────────────────

def test_get_exchanges_empty(client):
    res = client.get("/api/exchanges")
    assert res.status_code == 200
    assert res.get_json()["data"] == []


def test_get_exchanges_list(client, make_user, make_skill, make_exchange):
    offerer = make_user()
    skill = make_skill()
    make_exchange(offerer_id=offerer.id, skill_id=skill.id)

    res = client.get("/api/exchanges")
    assert res.status_code == 200
    assert len(res.get_json()["data"]) == 1


def test_get_exchange_found(client, make_user, make_skill, make_exchange):
    offerer = make_user()
    skill = make_skill()
    exchange = make_exchange(offerer_id=offerer.id, skill_id=skill.id)

    res = client.get(f"/api/exchanges/{exchange.id}")
    assert res.status_code == 200
    assert res.get_json()["data"]["offerer_id"] == offerer.id


def test_get_exchange_not_found(client):
    res = client.get("/api/exchanges/9999")
    assert res.status_code == 404


def test_get_exchanges_by_offerer(client, make_user, make_skill, make_exchange):
    offerer = make_user()
    other = make_user(email="other@test.com")
    skill = make_skill()
    make_exchange(offerer_id=offerer.id, skill_id=skill.id)
    make_exchange(offerer_id=other.id, skill_id=skill.id)

    res = client.get(f"/api/exchanges/offerer/{offerer.id}")
    assert res.status_code == 200
    assert len(res.get_json()["data"]) == 1


def test_get_exchanges_by_user(client, make_user, make_skill, make_exchange):
    offerer = make_user(email="offerer@test.com")
    demander = make_user(email="demander@test.com")
    unrelated = make_user(email="unrelated@test.com")
    skill = make_skill()
    make_exchange(offerer_id=offerer.id, skill_id=skill.id,
                  demander_id=demander.id)
    make_exchange(offerer_id=unrelated.id, skill_id=skill.id)

    res = client.get(f"/api/exchanges/user/{offerer.id}")
    assert res.status_code == 200
    assert len(res.get_json()["data"]) == 1


# ── POST /api/exchanges ───────────────────────────────────────────────────────

def test_create_exchange_success(client, make_user, make_skill, auth_headers):
    offerer = make_user()
    skill = make_skill()
    res = client.post("/api/exchanges",
                      json={"offerer_id": offerer.id, "skill_id": skill.id},
                      headers=auth_headers(offerer))
    assert res.status_code == 201
    assert "id" in res.get_json()["data"]


def test_create_exchange_forbidden(client, make_user, make_skill, auth_headers):
    offerer = make_user(email="offerer@test.com")
    other = make_user(email="other@test.com")
    skill = make_skill()
    res = client.post("/api/exchanges",
                      json={"offerer_id": offerer.id, "skill_id": skill.id},
                      headers=auth_headers(other))
    assert res.status_code == 403


def test_create_exchange_missing_skill_id(client, make_user, auth_headers):
    offerer = make_user()
    res = client.post("/api/exchanges",
                      json={"offerer_id": offerer.id},
                      headers=auth_headers(offerer))
    assert res.status_code == 400


def test_create_exchange_no_token(client, make_user, make_skill):
    offerer = make_user()
    skill = make_skill()
    res = client.post("/api/exchanges",
                      json={"offerer_id": offerer.id, "skill_id": skill.id})
    assert res.status_code == 401


# ── PUT /api/exchanges/join/<id> ──────────────────────────────────────────────

def test_join_exchange_success(client, make_user, make_skill, make_exchange,
                               auth_headers):
    offerer = make_user(email="offerer@test.com")
    demander = make_user(email="demander@test.com")
    skill = make_skill()
    exchange = make_exchange(offerer_id=offerer.id, skill_id=skill.id)

    res = client.put(f"/api/exchanges/join/{exchange.id}",
                     json={"user_id": demander.id},
                     headers=auth_headers(demander))
    assert res.status_code == 200
    assert res.get_json()["data"]["demander_id"] == demander.id


def test_join_exchange_self_assignment_rejected(client, make_user, make_skill,
                                                make_exchange, auth_headers):
    offerer = make_user()
    skill = make_skill()
    exchange = make_exchange(offerer_id=offerer.id, skill_id=skill.id)

    res = client.put(f"/api/exchanges/join/{exchange.id}",
                     json={"user_id": offerer.id},
                     headers=auth_headers(offerer))
    assert res.status_code == 400


def test_join_exchange_already_has_demander(client, make_user, make_skill,
                                            make_exchange, auth_headers):
    offerer = make_user(email="offerer@test.com")
    demander = make_user(email="demander@test.com")
    third = make_user(email="third@test.com")
    skill = make_skill()
    exchange = make_exchange(offerer_id=offerer.id, skill_id=skill.id,
                             demander_id=demander.id)

    res = client.put(f"/api/exchanges/join/{exchange.id}",
                     json={"user_id": third.id},
                     headers=auth_headers(third))
    assert res.status_code == 400


def test_join_exchange_not_found(client, make_user, auth_headers):
    user = make_user()
    res = client.put("/api/exchanges/join/9999",
                     json={"user_id": user.id},
                     headers=auth_headers(user))
    assert res.status_code == 404


def test_join_exchange_forbidden(client, make_user, make_skill, make_exchange,
                                 auth_headers):
    offerer = make_user(email="offerer@test.com")
    demander = make_user(email="demander@test.com")
    other = make_user(email="other@test.com")
    skill = make_skill()
    exchange = make_exchange(offerer_id=offerer.id, skill_id=skill.id)

    res = client.put(f"/api/exchanges/join/{exchange.id}",
                     json={"user_id": demander.id},
                     headers=auth_headers(other))
    assert res.status_code == 403


# ── PUT /api/exchanges/<id>/complete ─────────────────────────────────────────

def test_complete_exchange_by_offerer(client, make_user, make_skill,
                                      make_exchange, auth_headers):
    offerer = make_user(email="offerer@test.com")
    demander = make_user(email="demander@test.com")
    skill = make_skill()
    exchange = make_exchange(offerer_id=offerer.id, skill_id=skill.id,
                             demander_id=demander.id)

    res = client.put(f"/api/exchanges/{exchange.id}/complete",
                     headers=auth_headers(offerer))
    assert res.status_code == 200


def test_complete_exchange_by_demander(client, make_user, make_skill,
                                       make_exchange, auth_headers):
    offerer = make_user(email="offerer@test.com")
    demander = make_user(email="demander@test.com")
    skill = make_skill()
    exchange = make_exchange(offerer_id=offerer.id, skill_id=skill.id,
                             demander_id=demander.id)

    res = client.put(f"/api/exchanges/{exchange.id}/complete",
                     headers=auth_headers(demander))
    assert res.status_code == 200


def test_complete_exchange_forbidden(client, make_user, make_skill,
                                     make_exchange, auth_headers):
    offerer = make_user(email="offerer@test.com")
    demander = make_user(email="demander@test.com")
    outsider = make_user(email="outsider@test.com")
    skill = make_skill()
    exchange = make_exchange(offerer_id=offerer.id, skill_id=skill.id,
                             demander_id=demander.id)

    res = client.put(f"/api/exchanges/{exchange.id}/complete",
                     headers=auth_headers(outsider))
    assert res.status_code == 403


def test_complete_exchange_already_completed(client, make_user, make_skill,
                                             make_exchange, auth_headers):
    offerer = make_user(email="offerer@test.com")
    demander = make_user(email="demander@test.com")
    skill = make_skill()
    exchange = make_exchange(offerer_id=offerer.id, skill_id=skill.id,
                             demander_id=demander.id, is_completed=True)

    res = client.put(f"/api/exchanges/{exchange.id}/complete",
                     headers=auth_headers(offerer))
    assert res.status_code == 400


def test_complete_exchange_not_found(client, make_user, auth_headers):
    user = make_user()
    res = client.put("/api/exchanges/9999/complete", headers=auth_headers(user))
    assert res.status_code == 404


# ── DELETE /api/exchanges/<id> ────────────────────────────────────────────────

def test_delete_exchange_success(client, make_user, make_skill, make_exchange,
                                 auth_headers):
    offerer = make_user()
    skill = make_skill()
    exchange = make_exchange(offerer_id=offerer.id, skill_id=skill.id)

    res = client.delete(f"/api/exchanges/{exchange.id}",
                        headers=auth_headers(offerer))
    assert res.status_code == 200
    assert client.get(f"/api/exchanges/{exchange.id}").status_code == 404


def test_delete_exchange_forbidden(client, make_user, make_skill, make_exchange,
                                   auth_headers):
    offerer = make_user(email="offerer@test.com")
    other = make_user(email="other@test.com")
    skill = make_skill()
    exchange = make_exchange(offerer_id=offerer.id, skill_id=skill.id)

    res = client.delete(f"/api/exchanges/{exchange.id}",
                        headers=auth_headers(other))
    assert res.status_code == 403


def test_delete_completed_exchange_rejected(client, make_user, make_skill,
                                            make_exchange, auth_headers):
    offerer = make_user()
    skill = make_skill()
    exchange = make_exchange(offerer_id=offerer.id, skill_id=skill.id,
                             is_completed=True)

    res = client.delete(f"/api/exchanges/{exchange.id}",
                        headers=auth_headers(offerer))
    assert res.status_code == 400


def test_delete_exchange_not_found(client, make_user, auth_headers):
    user = make_user()
    res = client.delete("/api/exchanges/9999", headers=auth_headers(user))
    assert res.status_code == 404
