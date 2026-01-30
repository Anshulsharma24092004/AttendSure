from flask import Flask
from .config import Config
from app.extensions import db, migrate
from app.models import *

def create_app():
    app = Flask(__name__)
    app.config.from_object("app.config.Config")

    db.init_app(app)
    migrate.init_app(app, db)


    return app

