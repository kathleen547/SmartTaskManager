import os

from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config['FLASK_KEY'] = os.environ.get('FLASK_KEY')

    from .routes import main
    app.register_blueprint(main)

    return app