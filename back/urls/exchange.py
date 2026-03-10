"""
    Exchanges
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from back.utils import get_current_user, error_response, validate, success
from back.models import db, Exchange, User, Skill

exchanges = Blueprint("exchanges", __name__)


@exchanges.route("/api/exchanges", methods=["GET"])
def get_exchanges():
    """
        List all exchanges
    """
    try:
        all_exchanges = Exchange.query.all()

        return success([e.to_dict() for e in all_exchanges])

    except SQLAlchemyError as e:
        db.session.rollback()
        return error_response("Error retrieving exchanges", e)


@exchanges.route("/api/exchanges/<int:exchange_id>", methods=["GET"])
def get_exchange(exchange_id):
    """
        Get a specific exchange
    """
    try:
        exchange = Exchange.query.get(exchange_id)

        if not exchange:
            return jsonify({"error": "Exchange not found"}), 404

        return success(exchange.to_dict())

    except SQLAlchemyError as e:
        db.session.rollback()
        return error_response("Database error", e)


@exchanges.route(
        "/api/exchanges/offerer/<int:user_id>", methods=["GET"])
def get_offered_exchanges(user_id):
    """
        Get all exchanges created by the user (as offerer)
    """
    try:
        user_exchanges = Exchange.query.filter_by(
            offerer_id=user_id).all()

        return success([e.to_dict() for e in user_exchanges])

    except SQLAlchemyError as e:
        db.session.rollback()
        return error_response("Error retrieving offered exchanges", e)


@exchanges.route(
        "/api/exchanges/demander/<int:user_id>", methods=["GET"])
def get_demanded_exchanges(user_id):
    """
        Get all exchanges where the user has been a demander
    """
    try:
        user_exchanges = Exchange.query.filter_by(
            demander_id=user_id).all()

        return success([e.to_dict() for e in user_exchanges])

    except SQLAlchemyError as e:
        db.session.rollback()
        return error_response("Error retrieving demanded exchanges", e)


@exchanges.route("/api/exchanges", methods=["POST"])
@jwt_required()
def create_exchange():
    """
        Create a new exchange between users
    """
    data = request.get_json() or {}

    current = get_current_user()
    if not current or current.id != data.get("offerer_id"):
        return jsonify({"error": "Forbidden"}), 403

    errors = validate(data, {
        "offerer_id": ["required"],
        "skill_id":   ["required"],
    })
    if errors:
        return jsonify({"error": errors[0]}), 400

    try:

        offerer = User.query.get_or_404(data["offerer_id"])
        skill = Skill.query.get_or_404(data["skill_id"])

        exchange = Exchange(
            offerer_id=offerer.id,
            skill_id=skill.id
        )

        db.session.add(exchange)
        db.session.commit()

        return success({"id": exchange.id},
                       message="Exchange created successfully", status=201)

    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Invalid or duplicate data"}), 400

    except SQLAlchemyError as e:
        db.session.rollback()
        return error_response("Database error", e)


@exchanges.route(
        "/api/exchanges/<int:exchange_id>/complete", methods=["PUT"])
@jwt_required()
def complete_exchange(exchange_id):
    """
        Mark an exchange as completed
    """
    try:
        exchange = Exchange.query.get(exchange_id)

        if not exchange:
            return jsonify({"error": "Exchange not found"}), 404

        current = get_current_user()
        if not current or current.id not in (
                exchange.offerer_id, exchange.demander_id):
            return jsonify({"error": "Forbidden"}), 403

        if exchange.is_completed:
            return jsonify({
                "error": "Exchange is already completed"}), 400

        exchange.is_completed = True
        exchange.completed_at = db.func.now()

        db.session.commit()
        return success(message="Exchange completed successfully")

    except SQLAlchemyError as e:
        db.session.rollback()
        return error_response("Error completing the exchange", e)


@exchanges.route(
        "/api/exchanges/user/<int:user_id>", methods=["GET"])
def get_exchanges_by_user(user_id):
    """
        Get all exchanges in which a user participates
    """
    try:
        user_exchanges = Exchange.query.filter(
            (Exchange.offerer_id == user_id) |
            (Exchange.demander_id == user_id)
        ).all()

        return success([e.to_dict() for e in user_exchanges])

    except SQLAlchemyError as e:
        db.session.rollback()
        return error_response("Database error", e)


@exchanges.route(
        "/api/exchanges/join/<int:exchange_id>", methods=["PUT"])
@jwt_required()
def assign_demander(exchange_id):
    """
        Allow a user to assign themselves as demander of an exchange
    """
    data = request.get_json() or {}

    current = get_current_user()
    if not current or current.id != data.get("user_id"):
        return jsonify({"error": "Forbidden"}), 403

    try:
        demander_id = data.get("user_id")
        if not demander_id:
            return jsonify({
                "error": "Must provide user_id"}), 400

        exchange = Exchange.query.get(exchange_id)
        if not exchange:
            return jsonify({"error": "Exchange not found"}), 404

        if exchange.demander_id is not None:
            return jsonify({
                "error": "Exchange already has a demander assigned"
            }), 400

        if exchange.offerer_id == demander_id:
            return jsonify({
                "error": "The offerer cannot be their own demander"
            }), 400

        demander = User.query.get(demander_id)
        if not demander:
            return jsonify({"error": "Demander user not found"}), 404

        exchange.demander_id = demander.id
        db.session.commit()

        return success(exchange.to_dict(),
                       message="User assigned as demander successfully")

    except SQLAlchemyError as e:
        db.session.rollback()
        return error_response("Error assigning demander to exchange", e)


@exchanges.route(
        "/api/exchanges/<int:exchange_id>", methods=["DELETE"])
@jwt_required()
def delete_exchange(exchange_id):
    """
        Delete an exchange (only if not completed)
    """
    try:
        exchange = Exchange.query.get(exchange_id)

        if not exchange:
            return jsonify({"error": "Exchange not found"}), 404

        current = get_current_user()
        if not current or current.id != exchange.offerer_id:
            return jsonify({"error": "Forbidden"}), 403

        if exchange.is_completed:
            return jsonify({
                "error": "Cannot delete a completed exchange"
            }), 400

        db.session.delete(exchange)
        db.session.commit()
        return success(message="Exchange deleted successfully")

    except SQLAlchemyError as e:
        db.session.rollback()
        return error_response("Error deleting the exchange", e)
