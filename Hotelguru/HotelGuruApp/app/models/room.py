from sqlalchemy import Column, Integer, String, Boolean, Text
from sqlalchemy.orm import relationship
from app.extensions import db

class Room(db.Model):
    __tablename__ = 'room'
    
    id = Column(Integer, primary_key=True)
    room_number = Column(Integer, nullable=False)
    bed_count = Column(Integer, nullable=False)
    short_description = Column(String)
    long_description = Column(Text)
    price = Column(Integer, nullable=False)
    available = Column(Boolean, default=True)
    
    reservations = relationship("Reservation", back_populates="room")