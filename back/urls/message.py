"""
    Messages
"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from back.models import db, Message
from back.utils import (get_current_user, error_response, validate, success,
                        forbidden, bad_request, not_found,
                        paginate_query, paginated_success)
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

messages = Blueprint('messages', __name__)


@messages.route('/api/messages/<int:user_id>/sent')
def get_sent_messages(user_id):
    """
        List messages sent by the user
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        pagination = paginate_query(
            Message.query.filter_by(sender_id=user_id)
            .order_by(Message.sent_at.desc()),
            page, per_page
        )
        return paginated_success([m.to_dict() for m in pagination.items], pagination)

    except SQLAlchemyError as e:
        db.session.rollback()
        return error_response("Database error", e)


@messages.route('/api/messages/<int:user_id>/received')
def get_received_messages(user_id):
    """
        List messages received by the user
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        pagination = paginate_query(
            Message.query.filter_by(receiver_id=user_id)
            .order_by(Message.sent_at.desc()),
            page, per_page
        )
        return paginated_success([m.to_dict() for m in pagination.items], pagination)

    except SQLAlchemyError as e:
        db.session.rollback()
        return error_response("Database error", e)


@messages.route('/api/messages/<int:message_id>', methods=['GET'])
def get_message(message_id):
    """
        Get a single message
    """
    try:
        msg = db.get_or_404(Message, message_id)
        return success(msg.to_dict())

    except SQLAlchemyError as e:
        db.session.rollback()
        return error_response("Database error", e)


@messages.route('/api/messages', methods=["POST"])
@jwt_required()
def create_message():
    """
        Create a message
    """
    data = request.get_json() or {}
    current = get_current_user()
    if not current or current.id != data.get("sender_id"):
        return forbidden()

    errors = validate(data, {
        "content":     ["required"],
        "sender_id":   ["required"],
        "receiver_id": ["required"],
    })
    if errors:
        return bad_request(errors[0])

    try:
        msg = Message(
            content=data['content'],
            sender_id=data['sender_id'],
            receiver_id=data['receiver_id']
        )
        db.session.add(msg)
        db.session.commit()
        return success(msg.to_dict(), status=201)

    except IntegrityError:
        db.session.rollback()
        return bad_request("Invalid sender or receiver")

    except SQLAlchemyError as e:
        db.session.rollback()
        return error_response("Error creating message", e)


@messages.route('/api/messages/<int:message_id>', methods=['PUT'])
@jwt_required()
def update_message(message_id):
    """
        Update a message
    """
    data = request.get_json() or {}

    try:
        msg = db.get_or_404(Message, message_id)

        current = get_current_user()
        if not current or current.id != msg.sender_id:
            return forbidden()

        if not data:
            return bad_request("Incomplete parameters")

        fields = [
            "content", "seen"
        ]

        for f in fields:
            if f in data:
                setattr(msg, f, data[f])

        if "content" in data:
            setattr(msg, "seen", False)

        db.session.commit()
        return success(msg.to_dict())

    except SQLAlchemyError as e:
        db.session.rollback()
        return error_response("Database error", e)


@messages.route('/api/messages/<int:message_id>', methods=['DELETE'])
@jwt_required()
def delete_message(message_id):
    """
        Delete a message
    """
    try:
        msg = db.session.get(Message, message_id)

        if not msg:
            return not_found("Message")

        current = get_current_user()
        if not current or current.id != msg.sender_id:
            return forbidden()

        db.session.delete(msg)
        db.session.commit()
        return success(message="Message deleted")

    except SQLAlchemyError as e:
        db.session.rollback()
        return error_response("Could not delete the message", e)
