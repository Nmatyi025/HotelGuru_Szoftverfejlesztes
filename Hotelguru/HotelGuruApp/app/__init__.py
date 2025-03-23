from flask import Flask
from config import Config
from. extensions import db

def create_app(config_class=Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    
    from flask_migrate import Migrate
    migrate = Migrate(app, db)

    from app.models import (
        durations,
        enums,
        reservation,
        room,
        role,
        user,
        extra_service
    )

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    return app