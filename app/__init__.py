# app/__init__.py
from flask import Flask
from flask_cors import CORS
from app.routes.audit_routes import audit_bp
from app.config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)
    app.register_blueprint(audit_bp)
    return app

app = create_app()

