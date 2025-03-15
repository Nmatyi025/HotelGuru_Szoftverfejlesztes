from WebApp import db
import json

class Hotel(db.Model):
    __tablename__ = "hotel"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), index=True, unique=True)
    location = db.Column(db.String(200), nullable=False)
    rooms = db.relationship('Room', back_populates='hotel', lazy='dynamic')

    def __repr__(self):
        return '<Hotel {} ({})>'.format(self.name, self.id)

    def __str__(self):
        return f"{self.name} ({self.id}), {self.location}"

    @staticmethod
    def from_form(form):
        return Hotel(name=form.name.data, location=form.location.data)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'location': self.location,
            'rooms': [room.to_dict() for room in self.rooms]  
        }

class Room(db.Model):
    __tablename__ = "room"
    id = db.Column(db.Integer, primary_key=True)
    room_number = db.Column(db.String(50), nullable=False)
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotel.id'), nullable=False)
    hotel = db.relationship('Hotel', back_populates='rooms', lazy=True)
    capacity = db.Column(db.Integer, nullable=False)
    price_per_night = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return '<Room {} ({})>'.format(self.room_number, self.id)

    def __str__(self):
        return f"Room {self.room_number} in {self.hotel.name} ({self.id})"

    @staticmethod
    def from_form(form):
        return Room(
            room_number=form.room_number.data,
            hotel_id=form.hotel_id.data,
            capacity=form.capacity.data,
            price_per_night=form.price_per_night.data
        )

    def to_dict(self):
        return {
            'id': self.id,
            'room_number': self.room_number,
            'hotel_id': self.hotel_id,
            'capacity': self.capacity,
            'price_per_night': self.price_per_night
        }
