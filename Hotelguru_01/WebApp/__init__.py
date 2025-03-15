from flask import Flask
from config import db_config
from urllib.parse import quote_plus
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)

# required for web forms
app.config["SECRET_KEY"] = "SecretKey123"

# required for SQLAlchemy
config = db_config()
db_uri = "mysql+mysqlconnector://%s:%s@%s/%s?charset=utf8mb4" % \
    (config["user"], quote_plus(config["password"]), config["host"], config["database"])
app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]= False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from WebApp import routes, models, apiroutes
