"""
    Skills
"""
from sqlalchemy.exc import IntegrityError
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from back.models import db, Skill

skills = Blueprint('skills', __name__)


@skills.route('/api/skills')
def get_skills():
    """
        Get all skills
    """
    all_skills = Skill.query.all()
    return jsonify([s.to_dict() for s in all_skills]), 200


@skills.route(
        '/api/skills/category/<int:category_id>', methods=['GET'])
def get_skills_by_category(category_id):
    """Filter skills by category"""
    category_skills = Skill.query.filter_by(
        category_id=category_id).all()
    return jsonify([s.to_dict() for s in category_skills]), 200


@skills.route('/api/skills/<int:skill_id>', methods=['GET'])
def get_skill(skill_id):
    """
        Get a single skill
    """
    skill = Skill.query.get_or_404(skill_id)
    return jsonify(skill.to_dict()), 200


@skills.route('/api/skills', methods=["POST"])
@jwt_required()
def create_skill():
    """
        Create a skill
    """
    data = request.get_json()
    if not data or not data.get("name"):
        return jsonify({
            "error": "The 'name' field is required"}), 400
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
    return jsonify({
            "id": new_skill.id
        }), 201


@skills.route('/api/skills/<int:skill_id>', methods=['DELETE'])
@jwt_required()
def delete_skill(skill_id):
    """
        Delete a skill
    """
    skill = Skill.query.get_or_404(skill_id)
    db.session.delete(skill)
    db.session.commit()
    return jsonify({"message": "Skill deleted"}), 200


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
    return jsonify({
        "id": skill.id,
        "description": skill.description,
        "category_id": skill.category_id
    }), 200
