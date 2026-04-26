from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from app.config import Config
from app.models import db
from app.routes.auth import auth_bp
from app.routes.maintenance import maintenance_bp
from app.routes.dummy import dummy_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    JWTManager(app)
    CORS(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(maintenance_bp)
    app.register_blueprint(dummy_bp)

    with app.app_context():
        db.create_all()  # Create tables if they do not exist

    return app
