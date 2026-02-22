import os

from flask import Flask
from config import Config
from .extensions import db, login_manager


def create_app():
    app = Flask(__name__)
    app.config['FLASK_KEY'] = os.environ.get('FLASK_KEY')
    app.config.from_object(Config)

    # Database initialization
    db.init_app(app)

    login_manager.init_app(app)

    from .routes import main
    app.register_blueprint(main)

    return app