"""
    This module takes care of starting the API Server,
    Loading the DB and Adding the endpoints
"""
import os
from datetime import timedelta
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, jsonify
from flask import send_from_directory
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from authlib.integrations.flask_client import OAuth
from back.utils import APIException
# from back.utils import generate_sitemap
from back.admin import setup_admin
from back.models import db
from back.urls.user import users
from back.urls.skill import skills
from back.urls.category import categories
from back.urls.message import messages
from back.urls.exchange import exchanges
from back.urls.rating import ratings
from back.cloudinary.routes import cloudinary_routes


load_dotenv()


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "..", "front", "dist")

app = Flask(__name__,  static_folder=STATIC_DIR, static_url_path="/")
app.url_map.strict_slashes = False

DB_URL = os.getenv("DATABASE_URL")

if not DB_URL:
    pg_user = os.getenv("POSTGRES_USER")
    pg_pass = os.getenv("POSTGRES_PASSWORD")
    pg_db = os.getenv("POSTGRES_DB")
    pg_host = os.getenv("POSTGRES_HOST", "db")
    if pg_user and pg_pass and pg_db:
        DB_URL = f"postgresql://{pg_user}:{pg_pass}@{pg_host}:5432/{pg_db}"

if DB_URL:
    if DB_URL.startswith("postgres://"):
        DB_URL = DB_URL.replace("postgres://", "postgresql://", 1)
else:
    project_root = Path(__file__).resolve().parent.parent
    db_path = project_root / "local.db"
    DB_URL = f"sqlite:///{db_path}"

print(f" * Database in use: {DB_URL}")
app.config["SQLALCHEMY_DATABASE_URI"] = DB_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=6)
app.config["SECRET_KEY"] = os.getenv("FLASK_APP_KEY")


MIGRATIONS_DIR = os.path.join(BASE_DIR, "migrations")
MIGRATE = Migrate(app, db, directory=MIGRATIONS_DIR)
db.init_app(app)
CORS(app)
setup_admin(app)
jwt = JWTManager(app)
oauth = OAuth()


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    """ Handle/serialize errors like a JSON object """
    return jsonify(error.to_dict()), error.status_code


# @app.route('/')
# def sitemap():
    #  """ generate sitemap with all your endpoints """
    # return generate_sitemap(app)


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    """Front"""
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, "index.html")


app.register_blueprint(cloudinary_routes)
app.register_blueprint(users)
app.register_blueprint(skills)
app.register_blueprint(categories)
app.register_blueprint(messages)
app.register_blueprint(exchanges)
app.register_blueprint(ratings)
