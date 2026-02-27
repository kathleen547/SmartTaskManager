import os
from dotenv import load_dotenv
from flask import Flask
from config import Config
from flask_bootstrap import Bootstrap5
from .extensions import db, login_manager

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get('SECRET_KEY')
    app.config.from_object(Config)
    Bootstrap5(app)
    # Database initialization
    db.init_app(app)

    login_manager.init_app(app)

    from .routes import main
    app.register_blueprint(main)

    return app