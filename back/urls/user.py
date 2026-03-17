"""
    Users
"""
from datetime import datetime
from flask import Blueprint, jsonify, request, current_app
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from flask_jwt_extended import create_access_token, create_refresh_token
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity
from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests
from back.models import db, User, Skill, Category, Rating
from back.utils import (get_current_user, error_response, validate, success,
                        forbidden, bad_request, not_found,
                        paginate_query, paginated_success)

users = Blueprint('users', __name__)


@users.route('/api/users')
def get_users():
    """
        Get all users
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        pagination = paginate_query(
            User.query.order_by(User.id), page, per_page
        )

        user_ids = [u.id for u in pagination.items]
        avg_rows = (
            db.session.query(
                Rating.rated_id,
                func.avg(Rating.score).label("avg")
            )
            .filter(Rating.rated_id.in_(user_ids))
            .group_by(Rating.rated_id)
            .all()
        )
        avg_map = {row.rated_id: row.avg for row in avg_rows}

        return paginated_success(
            [u.to_dict(rating_avg=avg_map.get(u.id, 0)) for u in pagination.items],
            pagination
        )

    except SQLAlchemyError as e:
        db.session.rollback()
        return error_response("Database error", e)


@users.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """
        Get a single user
    """
    try:
        user = db.session.get(User, user_id)

        if not user:
            return not_found("User")

        usr = user.to_dict()
        usr["skills"] = [s.to_dict() for s in user.skills]
        return success(usr)

    except SQLAlchemyError as e:
        db.session.rollback()
        return error_response("Database error", e)


@users.route("/api/users/category/<int:category_id>", methods=["GET"])
def get_users_by_category(category_id):
    """
        Returns all users that have skills in a given category
    """
    category = db.get_or_404(Category, category_id)
    skill_ids = [s.id for s in category.skills]

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    if not skill_ids:
        return jsonify({"data": [], "pagination": {
            "page": 1, "per_page": per_page, "total": 0,
            "pages": 0, "has_next": False, "has_prev": False,
        }}), 200

    pagination = paginate_query(
        User.query.join(User.skills).filter(Skill.id.in_(skill_ids)).order_by(User.id),
        page, per_page
    )

    user_ids = [u.id for u in pagination.items]
    avg_rows = (
        db.session.query(
            Rating.rated_id,
            func.avg(Rating.score).label("avg")
        )
        .filter(Rating.rated_id.in_(user_ids))
        .group_by(Rating.rated_id)
        .all()
    )
    avg_map = {row.rated_id: row.avg for row in avg_rows}

    return paginated_success(
        [u.to_dict(rating_avg=avg_map.get(u.id, 0)) for u in pagination.items],
        pagination
    )


@users.route('/api/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    """
        Delete a user
    """
    current = get_current_user()
    if not current or current.id != user_id:
        return forbidden()

    user = db.session.get(User, user_id)
    if not user:
        return not_found("User")

    try:
        db.session.delete(user)
        db.session.commit()
        return success(message="User deleted")

    except SQLAlchemyError as e:
        db.session.rollback()
        return error_response("Could not delete user", e)


@users.route('/api/users', methods=["POST"])
def create_user():
    """
        Create a user
    """
    data = request.get_json() or {}

    errors = validate(data, {
        "first_name": ["required"],
        "last_name":  ["required"],
        "email":      ["required", "email"],
        "password":   ["required", "min_password"],
        "accepts_terms": ["required"],
        "birth_date": ["date"],
    })
    if errors:
        return bad_request(errors[0])

    try:
        usr = User(
            first_name=data['first_name'], last_name=data['last_name'],
            email=data['email'],
            password=data['password'],
            accepts_terms=data['accepts_terms']
        )

        extra = [
                    "description", "birth_date", "status",
                    "gender", "profile_picture", "skill_id"
                ]

        for f in extra:
            if f in data:
                if f == "birth_date":
                    setattr(usr, f, datetime.strptime(
                        data[f], "%Y-%m-%d").date())
                elif f == "skill_id":
                    skill = db.session.get(Skill, data[f])
                    if skill:
                        usr.skills.append(skill)
                else:
                    setattr(usr, f, data[f])

        db.session.add(usr)
        db.session.commit()
        return success({"id": usr.id}, message="User created", status=201)

    except IntegrityError:
        db.session.rollback()
        return bad_request("Email is already registered")

    except SQLAlchemyError as e:
        db.session.rollback()
        return error_response("Error creating user", e)


@users.route('/api/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """
        Update a user
    """
    current = get_current_user()
    if not current or current.id != user_id:
        return forbidden()

    data = request.get_json() or {}

    errors = validate(data, {
        "email":      ["email"],
        "password":   ["min_password"],
        "birth_date": ["date"],
    })
    if errors:
        return bad_request(errors[0])

    try:
        user = db.get_or_404(User, user_id)

        fields = [
            "first_name", "last_name", "email",
            "password", "profile_picture", "gender",
            "description", "status", "birth_date"
        ]

        for f in fields:
            if f in data:
                if f == "birth_date":
                    setattr(user, f, datetime.strptime(
                        data[f], "%Y-%m-%d").date())
                else:
                    setattr(user, f, data[f])

        db.session.commit()
        return success(user.to_dict(), message="User updated")

    except IntegrityError:
        db.session.rollback()
        return bad_request("Email is already registered")

    except SQLAlchemyError as e:
        db.session.rollback()
        return error_response("Database error", e)


@users.route('/api/users/<int:user_id>/skill', methods=["POST"])
@jwt_required()
def update_user_skill(user_id):
    """
        Associate/Disassociate skills to/from users
    """
    current = get_current_user()
    if not current or current.id != user_id:
        return forbidden()

    data = request.get_json() or {}
    try:
        usr = db.session.get(User, user_id)
        skill_id = data.get("associate") or data.get("disassociate")
        skill = db.session.get(Skill, skill_id)

        if not usr or not skill:
            return not_found("User or Skill")

        if (not data) or ("associate" in data and "disassociate" in data):
            return jsonify({
                "error": "Invalid parameters"
            }), 401

        if "associate" in data:
            usr.skills.append(skill)
        elif "disassociate" in data:
            usr.skills.remove(skill)

        user = usr.to_dict()
        user["skills"] = [s.to_dict() for s in usr.skills]

        db.session.commit()
        return success(user, status=201)

    except IntegrityError:
        db.session.rollback()
        return bad_request("Email is already registered")

    except SQLAlchemyError as e:
        db.session.rollback()
        return error_response("Error updating user skills", e)


@users.route("/api/auth/login", methods=["POST"])
def login():
    """
        Returns an authorization token
        for accessing exclusive sections
        (login with email and password)
    """
    data = request.get_json() or {}

    errors = validate(data, {
        "email":    ["required"],
        "password": ["required"],
    })
    if errors:
        return bad_request(errors[0])

    email = data.get("email")
    passw = data.get("password")

    try:
        user = User.query.filter_by(email=email).first()

        if user is None or not user.verify_password(passw):
            return jsonify(
                {"error": "Incorrect email or password"}), 401

        token = create_access_token(identity=user.email)
        refresh_token = create_refresh_token(identity=user.email)
        return success({
            "token": token,
            "refresh_token": refresh_token,
            "email": user.email
        })

    except Exception as e:  # pylint: disable=broad-exception-caught
        return error_response("Authentication error", e)


@users.route("/api/auth/me", methods=["GET"])
@jwt_required()
def get_me():
    """
        Returns the user associated with the authorization token
    """
    email = get_jwt_identity()

    if not email:
        return bad_request("Token without email")

    user = User.query.filter_by(email=email).first()

    if not user:
        return not_found("User")

    return success(user.to_dict())


@users.route("/api/auth/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    """
        Issues a new access token using a valid refresh token
    """
    email = get_jwt_identity()
    new_token = create_access_token(identity=email)
    return success({"token": new_token})


@users.route("/api/auth/google/verify", methods=["POST"])
def google_verify():
    """
        Verifies a Google id_token, creates or retrieves the user,
        and returns app JWT tokens
    """
    data = request.get_json() or {}
    token = data.get("id_token")

    if not token:
        return bad_request("'id_token' is required")

    client_id = current_app.config.get("GOOGLE_CLIENT_ID")
    if not client_id:
        return jsonify({"error": "Google OAuth not configured"}), 500

    try:
        id_info = google_id_token.verify_oauth2_token(
            token, google_requests.Request(), client_id
        )
    except ValueError as e:
        return jsonify({"error": "Invalid Google token"}), 401

    google_id = id_info.get("sub")
    email = id_info.get("email")
    first_name = id_info.get("given_name", "")
    last_name = id_info.get("family_name", "")
    picture = id_info.get("picture")

    if not email or not google_id:
        return bad_request("Incomplete Google profile")

    try:
        user = User.query.filter_by(google_id=google_id).first()

        if not user:
            user = User.query.filter_by(email=email).first()
            if user:
                user.google_id = google_id
            else:
                user = User(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    profile_picture=picture,
                    google_id=google_id,
                    accepts_terms=True,
                )
                db.session.add(user)

        db.session.commit()

        access_token = create_access_token(identity=user.email)
        refresh_token = create_refresh_token(identity=user.email)
        return success({
            "token": access_token,
            "refresh_token": refresh_token,
            "email": user.email,
        })

    except SQLAlchemyError as e:
        db.session.rollback()
        return error_response("Database error", e)


@users.route("/api/logout", methods=["POST"])
def logout():
    """
        Stateless logout — JWT is invalidated client-side.
        This endpoint exists for frontend compatibility.
    """
    return success(message="Logged out")
