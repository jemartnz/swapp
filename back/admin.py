"""
    This module is for admin
"""
import os
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from .models import db, User, Category, Exchange
from .models import Skill, Message, Rating
from .admin_views import UserAdmin  # pyright: ignore[reportMissingImports]


def setup_admin(app):
    """Config of app"""
    app.secret_key = os.environ.get('FLASK_APP_KEY', 'sample key')
    app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
    admin = Admin(app, name='Swapp Admin')
    admin.add_view(UserAdmin(User, db.session))
    admin.add_view(ModelView(Category, db.session))
    admin.add_view(ModelView(Skill, db.session))
    admin.add_view(ModelView(Exchange, db.session))
    admin.add_view(ModelView(Rating, db.session))
    admin.add_view(ModelView(Message, db.session))
