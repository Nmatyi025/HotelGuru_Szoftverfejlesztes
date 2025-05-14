from apiflask import APIFlask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.orm import DeclarativeBase
from config import Config
from WebApp.extensions import db
from flask import render_template

def create_app(test_config=None):
    app = APIFlask(__name__, json_errors=True, docs_path="/swagger", title="Hotel Guru Api")

    app.config.from_object(Config)

    db.init_app(app)

    from flask_migrate import Migrate
    migrate = Migrate(app, db, render_as_batch=True)

    from WebApp.blueprints import bp as main_bp
    app.register_blueprint(main_bp, url_prefix="/api")

    from WebApp.routes import register_routes
    register_routes(app)

    @app.template_filter('has_role')
    def has_role_filter(user, role_name):
        if not user or 'roles' not in user:
            return False
        return role_name in user['roles']

    app.jinja_env.globals['has_role'] = has_role_filter

    @app.route('/')
    def home():
        return render_template('index.html')  

    return app
