from sqlalchemy import Column, Integer, Enum, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.extensions import db
from .enums import Status, PaymentMethod

reservation_extra_service = Table(
    'reservation_extra_service', db.metadata,
    Column('reservation_id', ForeignKey('reservation.id'), primary_key=True),
    Column('extra_service_id', ForeignKey('extra_service.id'), primary_key=True)
)

class Reservation(db.Model):
    __tablename__ = 'reservation'
    
    id = Column(Integer, primary_key=True)
    room_id = Column(Integer, ForeignKey('room.id'))
    guest_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    payment_method = Column(Enum(PaymentMethod))
    status = Column(Enum(Status))
    
    room = relationship("Room", back_populates="reservations")
    guest = relationship("User", back_populates="reservations")
    extra_services = relationship("ExtraService", secondary=reservation_extra_service, back_populates="reservations")