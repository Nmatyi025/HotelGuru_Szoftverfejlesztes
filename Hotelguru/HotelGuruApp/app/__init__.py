from apiflask import APIFlask
from config import Config
from app.extensions import db
from app.models import *

def create_app(config_class=Config):
    app = APIFlask(__name__, json_errors=True, docs_path="/swagger", title="Hotelguru API", version="1.0.0")
    app.config.from_object(config_class)

    db.init_app(app)

    from flask_migrate import Migrate
    migrate = Migrate(app, db)

    # Register the main blueprint
    from app.blueprints import bp as bp_default
    app.register_blueprint(bp_default, url_prefix='/api')

    return app