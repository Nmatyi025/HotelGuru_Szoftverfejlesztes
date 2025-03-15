from flask_sqlalchemy import SQLAlchemy
from WebApp.models import Hotel, Room

class HotelManager:
    def __init__(self, db: SQLAlchemy):
        self._db = db

    @property
    def hotels(self):
        return self._db.session.query(Hotel).all()

    @property
    def rooms(self):
        return self._db.session.query(Room).all()

    def get_hotel(self, id: int):
        return self._db.session.query(Hotel).get(id)

    def add_hotel(self, hotel: Hotel):
        self._db.session.add(hotel)
        self._db.session.commit()

    def delete_hotel(self, hotel: Hotel):
        self._db.session.delete(hotel)
        self._db.session.commit()

    def search_hotels(self, search_term: str):
        return self._db.session.query(Hotel).filter(Hotel.name.ilike(f"%{search_term}%")).order_by(Hotel.name).all()
