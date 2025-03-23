from sqlalchemy import Column, Integer, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.extensions import db


class Duration(db.Model):
    __tablename__ = 'durations'
    
    id = Column(Integer, primary_key=True)
    reservation_id = Column(Integer, ForeignKey('reservation.id'), unique=True, nullable=False)
    arrival_date = Column(Date, nullable=False)
    departure_date = Column(Date, nullable=False)

    reservation = relationship("Reservation", back_populates="duration")
