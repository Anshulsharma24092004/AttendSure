from flask import Flask
from .config import Config
from app.extensions import db, migrate
from app.models import *
from .auth import auth_bp
from .attendance import attendance_bp
from .classes import classes_bp
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object("app.config.Config")
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(auth_bp, url_prefix='/auth')

    app.register_blueprint(attendance_bp, url_prefix='/attendance')

    app.register_blueprint(classes_bp, url_prefix="/classes")


    return app

