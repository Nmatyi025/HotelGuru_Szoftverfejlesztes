from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

#Adatbázis konfiguráció
class Base(DeclarativeBase):
    pass
db = SQLAlchemy(model_class=Base)

#Authentikáció
from apiflask import HTTPTokenAuth
auth = HTTPTokenAuth()
