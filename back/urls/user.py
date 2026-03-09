"""
    Users
"""
from datetime import datetime
from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from flask_jwt_extended import create_access_token, create_refresh_token
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity
from back.models import db, User, Skill, Category

users = Blueprint('users', __name__)


@users.route('/api/users')
def get_users():
    """
        Get all users
    """
    try:
        all_users = User.query.all()

        if not all_users:
            return jsonify({"message": "No users registered"}), 200

        return jsonify([u.to_dict() for u in all_users]), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({
            "error": "Database error",
            "detail": str(e.__dict__.get("orig"))
        }), 500


@users.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """
        Get a single user
    """
    try:
        user = User.query.get(user_id)

        if not user:
            return jsonify({"error": "User not found"}), 404

        usr = user.to_dict()
        usr["skills"] = [s.to_dict() for s in user.skills]
        return jsonify(usr), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({
            "error": "Database error",
            "detail": str(e.__dict__.get("orig"))
        }), 500


@users.route("/api/users/category/<int:category_id>", methods=["GET"])
def get_users_by_category(category_id):
    """
        Returns all users that have skills in a given category
    """
    category = Category.query.get_or_404(category_id)

    skill_ids = [s.id for s in category.skills]

    if not skill_ids:
        return jsonify([]), 200

    category_users = (
        User.query
        .join(User.skills)
        .filter(Skill.id.in_(skill_ids))
        .all()
    )

    return jsonify([u.to_dict() for u in category_users]), 200


@users.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """
        Delete a user
    """
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    try:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "User deleted"}), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": "Could not delete user",
                        "detail": str(e)}), 500


@users.route('/api/users', methods=["POST"])
def create_user():
    """
        Create a user
    """
    data = request.get_json() or {}
    try:
        if not data:
            return jsonify({
                "error": "Empty parameters"
            }), 400

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
                    skill = Skill.query.get(data[f])
                    if skill:
                        usr.skills.append(skill)
                else:
                    setattr(usr, f, data[f])

        db.session.add(usr)
        db.session.commit()
        return jsonify(
            {"message": "User created",
                "id": usr.id}), 201

    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Email is already registered"}), 400

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": "Error creating user",
                        "detail": str(e)}), 500


@users.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """
        Update a user
    """
    data = request.get_json() or {}

    try:
        user = User.query.get_or_404(user_id)

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
        return jsonify({"message": "User updated", "updated":
                        user.to_dict()})

    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Email is already registered"}), 400

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": "Database error",
                        "detail": str(e)}), 500


@users.route('/api/users/<int:user_id>/skill', methods=["POST"])
def update_user_skill(user_id):
    """
        Associate/Disassociate skills to/from users
    """
    data = request.get_json() or {}
    try:
        usr = User.query.get(user_id)
        skill_id = data.get("associate") or data.get("disassociate")
        skill = Skill.query.get(skill_id)

        if not usr or not skill:
            return jsonify({
                "error": "User or Skill not found"
            }), 404

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
        return jsonify(user), 201

    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Email is already registered"}), 400

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": "Error updating user skills",
                        "detail": str(e)}), 500


@users.route("/api/auth/login", methods=["POST"])
def login():
    """
        Returns an authorization token
        for accessing exclusive sections
        (login with email and password)
    """
    data = request.get_json() or {}
    email = data.get("email")
    passw = data.get("password")

    try:
        user = User.query.filter_by(email=email).first()

        if user is None or not user.verify_password(passw):
            return jsonify(
                {"error": "Incorrect email or password"}), 401

        token = create_access_token(identity=user.email)
        refresh_token = create_refresh_token(identity=user.email)
        return jsonify({
            "token": token,
            "refresh_token": refresh_token,
            "email": user.email
        }), 200

    except Exception as e:  # pylint: disable=broad-exception-caught
        return jsonify(
            {"error": "Authentication error", "detail": str(e)}), 500


@users.route("/api/auth/me", methods=["GET"])
@jwt_required()
def get_current_user():
    """
        Returns the user associated with the authorization token
    """
    email = get_jwt_identity()

    if not email:
        return jsonify({"error": "Token without email"}), 400

    user = User.query.filter_by(email=email).first()

    if not user:
        new_user = User(
            first_name="",
            last_name="",
            email=email,
            profile_picture="",
            password="google_oauth_dummy"
        )
        db.session.add(new_user)
        db.session.commit()
        user = new_user

    return jsonify(user.to_dict()), 200
