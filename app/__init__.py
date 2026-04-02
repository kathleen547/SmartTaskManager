"""
Application factory for the Flask app.

Uses the factory pattern (create_app) to allow flexible configuration,
testing, and multiple app instances. Initializes all extensions
and registers blueprints here.
"""

import os
from dotenv import load_dotenv
from flask import Flask
from config import Config
from flask_bootstrap import Bootstrap5
from .extensions import db, login_manager

# Load environment variables from .env file before app creation
load_dotenv()


def create_app():
    """
    Flask application factory function.

    Creates and configures the Flask app instance:
        - Loads config from Config object
        - Initializes extensions (SQLAlchemy, LoginManager, Bootstrap)
        - Registers the main Blueprint with all routes

    Returns:
        Flask: The fully configured Flask application instance.
    """
    app = Flask(__name__)

    # Load secret key from environment variable for session security
    app.secret_key = os.environ.get('SECRET_KEY')

    # Apply configuration settings from config.py
    app.config.from_object(Config)

    # Initialize Bootstrap5 for front-end styling support
    Bootstrap5(app)

    # Bind SQLAlchemy to this app instance
    db.init_app(app)

    # Bind Flask-Login to this app instance
    login_manager.init_app(app)

    # Import and register routes Blueprint (imported here to avoid circular imports)
    from .routes import main
    app.register_blueprint(main)

    return app