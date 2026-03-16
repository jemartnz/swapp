"""
Shared fixtures for all test modules.

DATABASE_URL is overridden via os.environ BEFORE back.app is imported so that
Flask-SQLAlchemy builds its engine with SQLite in-memory from the start.
StaticPool ensures every connection shares the same in-memory database.
"""
import os

# Must be set before importing back.app so the module-level DB_URL detection
# in app.py picks up SQLite instead of whatever is in the real .env file.
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ.setdefault("FLASK_APP_KEY", "test-secret-key")

import pytest
from sqlalchemy.pool import StaticPool
from flask_jwt_extended import create_access_token

from back.app import app as flask_app
from back.models import db, User, Category, Skill, Exchange, Message, Rating


# ── App & client ──────────────────────────────────────────────────────────────

@pytest.fixture(scope="function")
def app():
    """
    Flask app configured for testing.
    The engine is lazily created on the first db.create_all() call and uses
    SQLite in-memory + StaticPool (set via SQLALCHEMY_ENGINE_OPTIONS).
    Once created the engine is reused across all function-scoped tests;
    create_all / drop_all manage the schema isolation between tests.
    """
    flask_app.config.update({
        "TESTING": True,
        "SQLALCHEMY_ENGINE_OPTIONS": {
            "connect_args": {"check_same_thread": False},
            "poolclass": StaticPool,
        },
        "JWT_SECRET_KEY": "test-secret-key-long-enough-for-hmac-sha256",
        "DEBUG": False,
        "GOOGLE_CLIENT_ID": "test-client-id",
    })

    ctx = flask_app.app_context()
    ctx.push()
    db.create_all()

    yield flask_app

    db.session.remove()
    db.drop_all()
    ctx.pop()


@pytest.fixture
def client(app):
    return app.test_client()


# ── Factories ─────────────────────────────────────────────────────────────────

@pytest.fixture
def make_user():
    """Returns a factory that creates and commits a User row."""
    counter = {"n": 0}

    def _make(email=None, password="password123",
              first_name="Test", last_name="User", accepts_terms=True):
        counter["n"] += 1
        if email is None:
            email = f"user{counter['n']}@test.com"
        user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            accepts_terms=accepts_terms,
        )
        user.password = password
        db.session.add(user)
        db.session.commit()
        return user

    return _make


@pytest.fixture
def make_category():
    """Returns a factory that creates and commits a Category row."""
    counter = {"n": 0}

    def _make(name=None):
        counter["n"] += 1
        if name is None:
            name = f"Categoria {counter['n']}"
        cat = Category(name=name)
        db.session.add(cat)
        db.session.commit()
        return cat

    return _make


@pytest.fixture
def make_skill():
    """Returns a factory that creates and commits a Skill row."""
    counter = {"n": 0}

    def _make(name=None, category_id=None, description=""):
        counter["n"] += 1
        if name is None:
            name = f"Skill {counter['n']}"
        if category_id is None:
            cat = Category(name=f"Cat-auto-{counter['n']}")
            db.session.add(cat)
            db.session.flush()
            category_id = cat.id
        skill = Skill(name=name, description=description, category_id=category_id)
        db.session.add(skill)
        db.session.commit()
        return skill

    return _make


@pytest.fixture
def make_exchange():
    """Returns a factory that creates and commits an Exchange row."""
    def _make(offerer_id, skill_id, demander_id=None, is_completed=False):
        exchange = Exchange(
            offerer_id=offerer_id,
            skill_id=skill_id,
            demander_id=demander_id,
            is_completed=is_completed,
        )
        db.session.add(exchange)
        db.session.commit()
        return exchange

    return _make


@pytest.fixture
def make_message():
    """Returns a factory that creates and commits a Message row."""
    def _make(sender_id, receiver_id, content="Hola!"):
        msg = Message(
            sender_id=sender_id,
            receiver_id=receiver_id,
            content=content,
        )
        db.session.add(msg)
        db.session.commit()
        return msg

    return _make


@pytest.fixture
def make_rating():
    """Returns a factory that creates and commits a Rating row."""
    def _make(exchange_id, rater_id, rated_id, score=5, comment=None):
        rating = Rating(
            exchange_id=exchange_id,
            rater_id=rater_id,
            rated_id=rated_id,
            score=score,
            comment=comment,
        )
        db.session.add(rating)
        db.session.commit()
        return rating

    return _make


# ── Auth helpers ──────────────────────────────────────────────────────────────

@pytest.fixture
def auth_headers():
    """
    Returns a helper that generates JWT Authorization headers for a given user.
    Requires an active app context (provided by the `app` fixture).
    """
    def _make(user):
        token = create_access_token(identity=user.email)
        return {"Authorization": f"Bearer {token}"}

    return _make
