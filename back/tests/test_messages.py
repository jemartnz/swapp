"""
Tests for message endpoints:
  GET    /api/messages/<user_id>/sent
  GET    /api/messages/<user_id>/received
  GET    /api/messages/<id>
  POST   /api/messages
  PUT    /api/messages/<id>
  DELETE /api/messages/<id>
"""


# ── GET endpoints ─────────────────────────────────────────────────────────────

def test_get_sent_messages(client, make_user, make_message):
    sender = make_user(email="sender@test.com")
    receiver = make_user(email="receiver@test.com")
    make_message(sender_id=sender.id, receiver_id=receiver.id, content="Hi!")

    res = client.get(f"/api/messages/{sender.id}/sent")
    assert res.status_code == 200
    assert len(res.get_json()["data"]) == 1


def test_get_received_messages(client, make_user, make_message):
    sender = make_user(email="sender@test.com")
    receiver = make_user(email="receiver@test.com")
    make_message(sender_id=sender.id, receiver_id=receiver.id)

    res = client.get(f"/api/messages/{receiver.id}/received")
    assert res.status_code == 200
    assert len(res.get_json()["data"]) == 1


def test_get_sent_messages_pagination(client, make_user, make_message):
    sender = make_user(email="sender@test.com")
    receiver = make_user(email="receiver@test.com")
    for _ in range(3):
        make_message(sender_id=sender.id, receiver_id=receiver.id)

    res = client.get(f"/api/messages/{sender.id}/sent?per_page=2")
    assert res.status_code == 200
    body = res.get_json()
    assert "pagination" in body
    assert body["pagination"]["total"] == 3
    assert len(body["data"]) == 2
    assert body["pagination"]["has_next"] is True


def test_get_message_found(client, make_user, make_message):
    sender = make_user(email="sender@test.com")
    receiver = make_user(email="receiver@test.com")
    msg = make_message(sender_id=sender.id, receiver_id=receiver.id)

    res = client.get(f"/api/messages/{msg.id}")
    assert res.status_code == 200
    assert res.get_json()["data"]["content"] == "Hola!"


def test_get_message_not_found(client):
    res = client.get("/api/messages/9999")
    assert res.status_code == 404


# ── POST /api/messages ────────────────────────────────────────────────────────

def test_create_message_success(client, make_user, auth_headers):
    sender = make_user(email="sender@test.com")
    receiver = make_user(email="receiver@test.com")
    res = client.post("/api/messages",
                      json={
                          "content": "Hola!",
                          "sender_id": sender.id,
                          "receiver_id": receiver.id,
                      },
                      headers=auth_headers(sender))
    assert res.status_code == 201
    assert res.get_json()["data"]["content"] == "Hola!"


def test_create_message_forbidden(client, make_user, auth_headers):
    sender = make_user(email="sender@test.com")
    other = make_user(email="other@test.com")
    receiver = make_user(email="receiver@test.com")
    res = client.post("/api/messages",
                      json={
                          "content": "Hack",
                          "sender_id": sender.id,
                          "receiver_id": receiver.id,
                      },
                      headers=auth_headers(other))
    assert res.status_code == 403


def test_create_message_missing_content(client, make_user, auth_headers):
    sender = make_user(email="sender@test.com")
    receiver = make_user(email="receiver@test.com")
    res = client.post("/api/messages",
                      json={"sender_id": sender.id, "receiver_id": receiver.id},
                      headers=auth_headers(sender))
    assert res.status_code == 400


def test_create_message_no_token(client, make_user):
    sender = make_user(email="sender@test.com")
    receiver = make_user(email="receiver@test.com")
    res = client.post("/api/messages",
                      json={
                          "content": "Hi",
                          "sender_id": sender.id,
                          "receiver_id": receiver.id,
                      })
    assert res.status_code == 401


# ── PUT /api/messages/<id> ────────────────────────────────────────────────────

def test_update_message_success(client, make_user, make_message, auth_headers):
    sender = make_user(email="sender@test.com")
    receiver = make_user(email="receiver@test.com")
    msg = make_message(sender_id=sender.id, receiver_id=receiver.id)

    res = client.put(f"/api/messages/{msg.id}",
                     json={"content": "Actualizado"},
                     headers=auth_headers(sender))
    assert res.status_code == 200
    body = res.get_json()["data"]
    assert body["content"] == "Actualizado"
    assert body["seen"] is False


def test_update_message_resets_seen(client, make_user, make_message, auth_headers):
    """Editing content should reset seen to False."""
    from back.models import db, Message
    sender = make_user(email="sender@test.com")
    receiver = make_user(email="receiver@test.com")
    msg = make_message(sender_id=sender.id, receiver_id=receiver.id)
    msg.seen = True
    db.session.commit()

    res = client.put(f"/api/messages/{msg.id}",
                     json={"content": "Nuevo contenido"},
                     headers=auth_headers(sender))
    assert res.status_code == 200
    assert res.get_json()["data"]["seen"] is False


def test_update_message_forbidden(client, make_user, make_message, auth_headers):
    sender = make_user(email="sender@test.com")
    other = make_user(email="other@test.com")
    receiver = make_user(email="receiver@test.com")
    msg = make_message(sender_id=sender.id, receiver_id=receiver.id)

    res = client.put(f"/api/messages/{msg.id}",
                     json={"content": "Hack"},
                     headers=auth_headers(other))
    assert res.status_code == 403


# ── DELETE /api/messages/<id> ─────────────────────────────────────────────────

def test_delete_message_success(client, make_user, make_message, auth_headers):
    sender = make_user(email="sender@test.com")
    receiver = make_user(email="receiver@test.com")
    msg = make_message(sender_id=sender.id, receiver_id=receiver.id)

    res = client.delete(f"/api/messages/{msg.id}", headers=auth_headers(sender))
    assert res.status_code == 200
    assert client.get(f"/api/messages/{msg.id}").status_code == 404


def test_delete_message_forbidden(client, make_user, make_message, auth_headers):
    sender = make_user(email="sender@test.com")
    other = make_user(email="other@test.com")
    receiver = make_user(email="receiver@test.com")
    msg = make_message(sender_id=sender.id, receiver_id=receiver.id)

    res = client.delete(f"/api/messages/{msg.id}", headers=auth_headers(other))
    assert res.status_code == 403


def test_delete_message_not_found(client, make_user, auth_headers):
    user = make_user()
    res = client.delete("/api/messages/9999", headers=auth_headers(user))
    assert res.status_code == 404
