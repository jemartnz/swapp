from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from back.models import db, User
from back.utils import get_current_user, error_response, success, forbidden, bad_request, not_found
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
        return forbidden()

    try:
        user = db.session.get(User, user_id)
        if not user:
            return not_found("User")

        if "image" not in request.files:
            return bad_request("No image was sent")

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

        return success(
            {"profile_picture": user.profile_picture},
            message="Profile picture updated"
        )

    except Exception as e:
        db.session.rollback()
        return error_response("Error uploading image", e)
