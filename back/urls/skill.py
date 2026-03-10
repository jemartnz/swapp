"""
    Skills
"""
from sqlalchemy.exc import IntegrityError
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from back.models import db, Skill
from back.utils import error_response, validate, success

skills = Blueprint('skills', __name__)


@skills.route('/api/skills')
def get_skills():
    """
        Get all skills
    """
    all_skills = Skill.query.all()
    return success([s.to_dict() for s in all_skills])


@skills.route(
        '/api/skills/category/<int:category_id>', methods=['GET'])
def get_skills_by_category(category_id):
    """Filter skills by category"""
    category_skills = Skill.query.filter_by(
        category_id=category_id).all()
    return success([s.to_dict() for s in category_skills])


@skills.route('/api/skills/<int:skill_id>', methods=['GET'])
def get_skill(skill_id):
    """
        Get a single skill
    """
    skill = Skill.query.get_or_404(skill_id)
    return success(skill.to_dict())


@skills.route('/api/skills', methods=["POST"])
@jwt_required()
def create_skill():
    """
        Create a skill
    """
    data = request.get_json() or {}

    errors = validate(data, {
        "name":        ["required"],
        "category_id": ["required"],
    })
    if errors:
        return jsonify({"error": errors[0]}), 400

    new_skill = Skill(
        name=data["name"],
        description=data["description"],
        category_id=data["category_id"]
    )

    db.session.add(new_skill)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Skill already exists"}), 400
    return success({"id": new_skill.id}, message="Skill created successfully", status=201)


@skills.route('/api/skills/<int:skill_id>', methods=['DELETE'])
@jwt_required()
def delete_skill(skill_id):
    """
        Delete a skill
    """
    skill = Skill.query.get_or_404(skill_id)
    db.session.delete(skill)
    db.session.commit()
    return success(message="Skill deleted")


@skills.route('/api/skills/<int:skill_id>', methods=['PUT'])
@jwt_required()
def update_skill(skill_id):
    """
        Update a skill
    """
    skill = Skill.query.get_or_404(skill_id)
    data = request.get_json()

    skill.description = data.get('description', skill.description)
    skill.category_id = data.get('category_id', skill.category_id)

    db.session.commit()
    return success(skill.to_dict())
