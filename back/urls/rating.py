"""
    Ratings
"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from back.utils import (get_current_user, error_response, validate, success,
                        forbidden, bad_request, not_found,
                        paginate_query, paginated_success)
from back.models import db, User, Rating, Exchange

ratings = Blueprint('ratings', __name__)


@ratings.route('/api/ratings', methods=['GET'])
def get_ratings():
    """
        List all ratings
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        pagination = paginate_query(
            Rating.query.order_by(Rating.id.desc()), page, per_page
        )
        return paginated_success([r.to_dict() for r in pagination.items], pagination)

    except SQLAlchemyError as e:
        db.session.rollback()
        return error_response("Error retrieving ratings", e)


@ratings.route('/api/ratings/<int:rating_id>', methods=['GET'])
def get_rating(rating_id):
    """
        Get a single rating
    """
    try:
        rating = db.session.get(Rating, rating_id)

        if not rating:
            return not_found("Rating")

        return success(rating.to_dict())

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
        return forbidden()

    errors = validate(data, {
        "exchange_id": ["required"],
        "rater_id":    ["required"],
        "score":       ["required", ("min", 1), ("max", 5)],
    })
    if errors:
        return bad_request(errors[0])

    try:

        exchange = db.get_or_404(Exchange, data["exchange_id"])
        rater = db.get_or_404(User, data["rater_id"])

        if rater.id == exchange.offerer_id:
            rated_id = exchange.demander_id
        else:
            rated_id = exchange.offerer_id

        if not rated_id:
            return bad_request("The exchange does not have a demander assigned yet")

        rated = db.get_or_404(User, rated_id)

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
        return success({"id": rating.id}, message="Rating created successfully", status=201)

    except IntegrityError:
        db.session.rollback()
        return bad_request("Invalid parameters")

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
        rating = db.session.get(Rating, rating_id)

        if not rating:
            return not_found("Rating")

        current = get_current_user()
        if not current or current.id != rating.rater_id:
            return forbidden()

        errors = validate(data, {
            "score": [("min", 1), ("max", 5)],
        })
        if errors:
            return bad_request(errors[0])

        fields = [
            "score", "comment"
        ]

        for f in fields:
            if f in data:
                setattr(rating, f, data[f])

        db.session.commit()
        return success(rating.to_dict())

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
        rating = db.session.get(Rating, rating_id)

        if not rating:
            return not_found("Rating")

        current = get_current_user()
        if not current or current.id != rating.rater_id:
            return forbidden()

        db.session.delete(rating)
        db.session.commit()
        return success(message="Rating deleted")

    except SQLAlchemyError as e:
        db.session.rollback()
        return error_response("Could not delete the rating", e)
