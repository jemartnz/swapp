"""
    Categories
"""
from sqlalchemy.exc import IntegrityError
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from back.models import db, Category
from back.utils import error_response, validate

categories = Blueprint('categories', __name__)


@categories.route('/api/categories')
def get_categories():
    """
        Get all categories
    """
    all_categories = Category.query.all()
    if not all_categories:
        return jsonify({"error": "No categories registered"}), 404

    result = []
    for c in all_categories:
        cat = c.to_dict()
        cat["skills"] = [s.to_dict() for s in c.skills]
        result.append(cat)

    return jsonify(result), 200


@categories.route('/api/categories/<int:category_id>', methods=['GET'])
def get_category(category_id):
    """
        Get a single category
    """
    category = Category.query.get_or_404(category_id)
    return jsonify(category.to_dict())


@categories.route('/api/categories', methods=['POST'])
@jwt_required()
def create_category():
    """
        Create a category
    """
    data = request.get_json() or {}

    errors = validate(data, {"name": ["required"]})
    if errors:
        return jsonify({"error": errors[0]}), 400

    name = data.get("name")
    new_category = Category(name=name)
    db.session.add(new_category)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Category already exists"}), 400

    return jsonify({"message": "Category created successfully",
                    "category": new_category.to_dict()}), 201


@categories.route('/api/categories/<int:category_id>', methods=['PUT'])
@jwt_required()
def update_category(category_id):
    """
        Update a category
    """
    category = Category.query.get_or_404(category_id)
    data = request.get_json()

    category.name = data.get('name', category.name)

    db.session.commit()

    return jsonify({
        "id": category.id,
        "name": category.name,
    })


@categories.route('/api/categories/<int:category_id>', methods=['DELETE'])
@jwt_required()
def delete_category(category_id):
    """
        Delete a category
    """
    category = Category.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    return jsonify({
        "message": "Category deleted"
    })
