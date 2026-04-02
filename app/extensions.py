"""
Flask extension instances used throughout the application.

Extensions are instantiated here WITHOUT being bound to a Flask app,
following the Application Factory pattern. They are later initialized
with the app instance inside `create_app()` in __init__.py using
the `extension.init_app(app)` pattern.

This approach avoids circular imports and allows the extensions to be
imported and shared freely across models.py, routes.py, and other modules.
"""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager


class Base(DeclarativeBase):
    """
    Custom SQLAlchemy declarative base class.

    All database models inherit indirectly from this class through
    db.Model (SQLAlchemy uses this Base when constructing the ORM).

    Extending DeclarativeBase allows for future customization such as:
        - Adding shared columns (e.g. created_at, updated_at) to all models
        - Custom metadata or naming conventions
        - Type annotation map configuration
    """
    pass


# ─────────────────────────────────────────────
#  DATABASE EXTENSION
# ─────────────────────────────────────────────

# SQLAlchemy ORM instance — provides db.Model, db.session, db.select, etc.
# model_class=Base ensures our custom Base is used for all models
db = SQLAlchemy(model_class=Base)


# ─────────────────────────────────────────────
#  AUTHENTICATION EXTENSION
# ─────────────────────────────────────────────

# Flask-Login manager — handles user session management:
#   - Tracks the currently logged-in user via current_user proxy
#   - Enforces @login_required on protected routes
#   - Calls the @login_manager.user_loader callback to reload
#     the user object from the session on each request
login_manager = LoginManager()
