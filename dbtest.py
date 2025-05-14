from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
import json
from datetime import datetime, date, timedelta
import random

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

class Hotel(db.Model):
    __tablename__ = 'hotels'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    country = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    created_on = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    rating = db.Column(db.Float, default=0.0, nullable=False)
    photo_urls = db.Column(db.JSON, nullable=True)

    @property
    def main_photo_url(self):
        if self.photo_urls and isinstance(self.photo_urls, list) and len(self.photo_urls) > 0:
            return self.photo_urls[0]
        return None

class Room(db.Model):
    __tablename__ = 'rooms'
    id = db.Column(db.Integer, primary_key=True)
    room_number = db.Column(db.Integer, nullable=False)
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotels.id'), nullable=False)
    price_per_night = db.Column(db.Float, nullable=False)
    available = db.Column(db.Boolean, default=True, nullable=False)
    description = db.Column(db.String(500), nullable=True)
    photo_urls = db.Column(db.JSON, nullable=True)

    @property
    def main_photo_url(self):
        if self.photo_urls and isinstance(self.photo_urls, list) and len(self.photo_urls) > 0:
            return self.photo_urls[0]
        return None

class Availability(db.Model):
    __tablename__ = 'availability'
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False)
    availability_date = db.Column(db.Date, nullable=False)
    is_available = db.Column(db.Boolean, default=True, nullable=False)

class Amenity(db.Model):
    __tablename__ = 'amenities'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    icon = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200), nullable=True)

with app.app_context():
    db.create_all()
    Availability.query.delete()
    Room.query.delete()
    Hotel.query.delete()
    Amenity.query.delete()
    db.session.commit()
    hotels = [
        Hotel(
            name="Luxury Palace Hotel",
            address="123 Main Street",
            city="Paris",
            country="France",
            description="Experience luxury in the heart of Paris",
            rating=4.7,
            photo_urls=["https://source.unsplash.com/random/800x600/?luxury-hotel"]
        ),
        Hotel(
            name="Mountain View Resort",
            address="456 Peak Avenue",
            city="Zurich",
            country="Switzerland",
            description="Breathtaking alpine views and premium amenities",
            rating=4.5,
            photo_urls=["https://source.unsplash.com/random/800x600/?mountain-resort"]
        ),
        Hotel(
            name="Beachside Bungalows",
            address="789 Shore Drive",
            city="Santorini",
            country="Greece",
            description="Relax in paradise with our oceanfront bungalows",
            rating=4.8,
            photo_urls=["https://source.unsplash.com/random/800x600/?beach-bungalow"]
        )
    ]
    for hotel in hotels:
        db.session.add(hotel)
    db.session.commit()
    hotels_from_db = Hotel.query.all()
    for hotel in hotels_from_db:
        for i in range(1, 6):
            price = 100 + (hotel.rating * 50) + (i * 10)
            room = Room(
                room_number=i,
                hotel_id=hotel.id,
                price_per_night=price,
                available=True,
                description=f"Room {i} in {hotel.name}",
                photo_urls=["https://source.unsplash.com/random/600x400/?hotel-room"]
            )
            db.session.add(room)
    db.session.commit()
    print("Adding availability test data...")
    today = date.today()
    rooms = Room.query.all()
    for room in rooms:
        print(f"Adding availability data for room {room.room_number} in hotel {room.hotel_id}")
        if room.room_number == 1:
            for i in range(5):
                booking_date = today + timedelta(days=i)
                availability = Availability(
                    room_id=room.id,
                    availability_date=booking_date,
                    is_available=False
                )
                db.session.add(availability)
        elif room.room_number == 2:
            days_until_saturday = (5 - today.weekday()) % 7
            if days_until_saturday == 0:
                days_until_saturday = 7
            next_saturday = today + timedelta(days=days_until_saturday)
            next_sunday = next_saturday + timedelta(days=1)
            second_saturday = next_saturday + timedelta(days=7)
            second_sunday = next_sunday + timedelta(days=7)
            for booking_date in [next_saturday, next_sunday, second_saturday, second_sunday]:
                availability = Availability(
                    room_id=room.id,
                    availability_date=booking_date,
                    is_available=False
                )
                db.session.add(availability)
        elif room.room_number == 3:
            if room.hotel_id == 1:
                for i in range(14):
                    blocking_date = today + timedelta(days=i)
                    availability = Availability(
                        room_id=room.id,
                        availability_date=blocking_date,
                        is_available=False
                    )
                    db.session.add(availability)
            elif room.hotel_id == 2:
                start_date = today + timedelta(days=30)
                for i in range(14):
                    blocking_date = start_date + timedelta(days=i)
                    availability = Availability(
                        room_id=room.id,
                        availability_date=blocking_date,
                        is_available=False
                    )
                    db.session.add(availability)
        else:
            used_days = set()
            for _ in range(8):
                while True:
                    random_days = random.randint(1, 60)
                    if random_days not in used_days:
                        used_days.add(random_days)
                        break
                booking_date = today + timedelta(days=random_days)
                availability = Availability(
                    room_id=room.id,
                    availability_date=booking_date,
                    is_available=False
                )
                db.session.add(availability)
    db.session.commit()
    hotel_count = Hotel.query.count()
    room_count = Room.query.count()
    availability_count = Availability.query.count()
    print(f"Added {hotel_count} hotels, {room_count} rooms, and {availability_count} availability records to the database.")
    amenities = [
        Amenity(name="Free WiFi", icon="wifi", description="High-speed internet access"),
        Amenity(name="Parking", icon="p-square", description="On-site parking available"),
        Amenity(name="Breakfast", icon="cup-hot", description="Complimentary breakfast"),
        Amenity(name="Swimming Pool", icon="water", description="Indoor/outdoor pool"),
        Amenity(name="Air Conditioning", icon="snow", description="Climate control in all areas"),
        Amenity(name="24/7 Reception", icon="shield-check", description="Front desk always available"),
        Amenity(name="Fitness Center", icon="bicycle", description="Gym access"),
        Amenity(name="Restaurant", icon="cup-straw", description="On-site dining")
    ]
    for amenity in amenities:
        db.session.add(amenity)
    db.session.commit()
    for hotel in hotels_from_db:
        num_amenities = random.randint(4, 6)
        hotel_amenities = random.sample(amenities, num_amenities)
        hotel.amenities = hotel_amenities
    db.session.commit()
