"""
    Ratings
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from back.utils import get_current_user, error_response
from back.models import db, User, Rating, Exchange

ratings = Blueprint('ratings', __name__)


@ratings.route('/api/ratings', methods=['GET'])
def get_ratings():
    """
        List all ratings
    """
    try:
        all_ratings = Rating.query.all()

        if not all_ratings:
            return jsonify({"message": "No ratings registered"}), 404

        return jsonify([r.to_dict() for r in all_ratings]), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        return error_response("Error retrieving ratings", e)


@ratings.route('/api/ratings/<int:rating_id>', methods=['GET'])
def get_rating(rating_id):
    """
        Get a single rating
    """
    try:
        rating = Rating.query.get(rating_id)

        if not rating:
            return jsonify({"error": "Rating not found"}), 404

        return jsonify(rating.to_dict())

    except SQLAlchemyError as e:
        db.session.rollback()
        return error_response("Database error", e)


@ratings.route('/api/ratings', methods=["POST"])
@jwt_required()
def create_rating():
    """
        Create a rating
    """
    data = request.get_json() or {}
    current = get_current_user()
    if not current or current.id != data.get("rater_id"):
        return jsonify({"error": "Forbidden"}), 403

    try:
        required_fields = ["exchange_id", "rater_id", "score"]
        missing = [f for f in required_fields if f not in data]

        if missing:
            return jsonify({
                "error":
                f"Missing required fields: {', '.join(missing)}"
            }), 400

        exchange = Exchange.query.get_or_404(data["exchange_id"])
        rater = User.query.get_or_404(data["rater_id"])

        if rater.id == exchange.offerer_id:
            rated_id = exchange.demander_id
        else:
            rated_id = exchange.offerer_id

        if not rated_id:
            return jsonify({
                "error":
                "The exchange does not have a demander assigned yet"}), 400

        rated = User.query.get_or_404(rated_id)

        rating = Rating(
            exchange_id=exchange.id,
            rater_id=rater.id,
            rated_id=rated.id,
            score=data["score"]
        )

        if "comment" in data:
            setattr(rating, "comment", data["comment"])

        db.session.add(rating)
        db.session.commit()
        return jsonify({"id": rating.id}), 201

    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Invalid parameters"}), 400

    except SQLAlchemyError as e:
        db.session.rollback()
        return error_response("Error creating rating", e)


@ratings.route('/api/ratings/<int:rating_id>', methods=['PUT'])
@jwt_required()
def update_rating(rating_id):
    """
        Update a rating
    """
    data = request.get_json() or {}

    try:
        rating = Rating.query.get(rating_id)

        if not rating:
            return jsonify({"error": "Rating not found"}), 404

        current = get_current_user()
        if not current or current.id != rating.rater_id:
            return jsonify({"error": "Forbidden"}), 403
        if not data:
            return jsonify({"error": "Incomplete parameters"}), 400

        fields = [
            "score", "comment"
        ]

        for f in fields:
            if f in data:
                setattr(rating, f, data[f])

        db.session.commit()
        return jsonify(rating.to_dict()), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        return error_response("Database error", e)


@ratings.route(
        '/api/ratings/<int:rating_id>', methods=['DELETE'])
@jwt_required()
def delete_rating(rating_id):
    """
        Delete a rating
    """
    try:
        rating = Rating.query.get(rating_id)

        if not rating:
            return jsonify({"error": "Rating not found"}), 404

        current = get_current_user()
        if not current or current.id != rating.rater_id:
            return jsonify({"error": "Forbidden"}), 403

        db.session.delete(rating)
        db.session.commit()
        return jsonify({"message": "Rating deleted"}), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        return error_response("Could not delete the rating", e)
