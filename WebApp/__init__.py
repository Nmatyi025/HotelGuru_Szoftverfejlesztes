from apiflask import APIFlask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.orm import DeclarativeBase
#import flask

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)




app = APIFlask(__name__, json_errors=True, docs_path="/swagger", title="Hotel Guru Api")
app.config["SECRET_KEY"] = "qweasdweasd"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mydb.db"

db.init_app(app)
migrate = Migrate(app, db)

from WebApp.blueprints import bp as main_bp
app.register_blueprint(main_bp, url_prefix="/api")

from WebApp import routes, models

