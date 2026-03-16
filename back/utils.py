"""
    Utils module
"""
import re
from datetime import datetime
from flask import url_for, jsonify, current_app
from flask_jwt_extended import get_jwt_identity


class APIException(Exception):
    """ APIException class """
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        """Return format Dict"""
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


def validate(data, rules):
    """
    Validate request data against a dict of rules.

    rules: { field: [validator, ...] }
    Validators:
      "required"       — field must be present and non-empty
      "email"          — must match basic email pattern
      "min_password"   — string length >= 8
      "date"           — must parse as YYYY-MM-DD
      ("min", n)       — numeric value >= n
      ("max", n)       — numeric value <= n

    Returns a list of error strings (empty means valid).
    """
    errors = []
    for field, validators in rules.items():
        value = data.get(field)
        for v in validators:
            if v == "required":
                if value is None or value == "":
                    errors.append(f"'{field}' is required")
            elif v == "email":
                if value and not re.match(
                        r"^[^@\s]+@[^@\s]+\.[^@\s]+$", str(value)):
                    errors.append(
                        f"'{field}' must be a valid email address")
            elif v == "min_password":
                if value and len(str(value)) < 8:
                    errors.append(
                        f"'{field}' must be at least 8 characters")
            elif v == "date":
                if value:
                    try:
                        datetime.strptime(str(value), "%Y-%m-%d")
                    except ValueError:
                        errors.append(
                            f"'{field}' must be in YYYY-MM-DD format")
            elif isinstance(v, tuple) and v[0] == "min":
                if value is not None:
                    try:
                        if float(value) < v[1]:
                            errors.append(
                                f"'{field}' must be at least {v[1]}")
                    except (TypeError, ValueError):
                        errors.append(f"'{field}' must be a number")
            elif isinstance(v, tuple) and v[0] == "max":
                if value is not None:
                    try:
                        if float(value) > v[1]:
                            errors.append(
                                f"'{field}' must be at most {v[1]}")
                    except (TypeError, ValueError):
                        errors.append(f"'{field}' must be a number")
    return errors


def success(data=None, message=None, status=200):
    """Return a standardised success response: {"data": ..., "message": ...}"""
    body = {}
    if data is not None:
        body["data"] = data
    if message:
        body["message"] = message
    return jsonify(body), status


def paginate_query(query, page, per_page, max_per_page=100):
    """Paginate a SQLAlchemy query. Clamps page ≥ 1 and per_page to [1, max_per_page]."""
    try:
        page = max(1, int(page))
        per_page = min(max(1, int(per_page)), max_per_page)
    except (TypeError, ValueError):
        page, per_page = 1, 20
    return query.paginate(page=page, per_page=per_page, error_out=False)


def paginated_success(items_dicts, pagination):
    """Return a paginated success response with metadata."""
    return jsonify({
        "data": items_dicts,
        "pagination": {
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages,
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev,
        }
    }), 200


def not_found(resource="Resource"):
    """Return a standardised 404 response."""
    return jsonify({"error": f"{resource} not found"}), 404


def forbidden():
    """Return a standardised 403 Forbidden response."""
    return jsonify({"error": "Forbidden"}), 403


def bad_request(message):
    """Return a standardised 400 Bad Request response."""
    return jsonify({"error": message}), 400


def error_response(message, e, status=500):
    """Return a JSON error response. Includes exception detail only in DEBUG."""
    body = {"error": message}
    if current_app.config.get("DEBUG"):
        body["detail"] = str(e)
    return jsonify(body), status


def get_current_user():
    """Return the User row matching the JWT identity (email)."""
    from back.models import User  # local import to avoid circular dependency
    email = get_jwt_identity()
    return User.query.filter_by(email=email).first()


def has_no_empty_params(rule):
    """Check params not empty"""
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)


def generate_sitemap(app):
    """View by default"""
    links = []
    for rule in app.url_map.iter_rules():
        if "GET" in rule.methods and has_no_empty_params(rule):
            url = url_for(rule.endpoint, **(rule.defaults or {}))
            links.append(url)
    links_html = "".join([
        "<li><a href='" + y + "'>" + y + "</a></li>" for y in links
        ])
    return """
        <div style="text-align: center;">
            <div style="margin-top:3rem;"><div/>
            <h1>SWAPP ENDPOINTS</h1>
            <br/>
            <br/>
            <ul style="text-align: left;">
                """ + links_html + """
            </ul>
        </div>
        """
