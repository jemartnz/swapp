from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from back.models import db, User
from back.utils import get_current_user, error_response, success
from back.cloudinary.config import cloudinary
import cloudinary.uploader
from werkzeug.utils import secure_filename

cloudinary_routes = Blueprint("cloudinary_routes", __name__)


@cloudinary_routes.route(
        "/api/users/<int:user_id>/profile-picture", methods=["POST"])
@jwt_required()
def upload_profile_picture(user_id):
    """
    Upload or update a user's profile picture on Cloudinary
    """
    current = get_current_user()
    if not current or current.id != user_id:
        return jsonify({"error": "Forbidden"}), 403

    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        if "image" not in request.files:
            return jsonify({"error": "No image was sent"}), 400

        image = request.files["image"]
        safe_name = secure_filename(image.filename)

        result = cloudinary.uploader.upload(
            image,
            folder="users_profile",
            public_id=f"user_{user_id}_{safe_name}",
            overwrite=True,
            resource_type="image"
        )

        user.profile_picture = result.get("secure_url")
        db.session.commit()

        return jsonify({
            "message": "Profile picture updated",
            "profile_picture": user.profile_picture
        }), 200

    except Exception as e:
        db.session.rollback()
        return error_response("Error uploading image", e)
