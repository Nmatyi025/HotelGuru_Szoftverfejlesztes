
from __future__ import annotations
from WebApp import db
from typing import List, Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Integer, Float, Boolean, String, JSON

class Room(db.Model):
    __tablename__ = "rooms"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    room_number: Mapped[int] = mapped_column(Integer, nullable=False)
    hotel_id: Mapped[int] = mapped_column(ForeignKey("hotels.id"), nullable=False)
    price_per_night: Mapped[float] = mapped_column(Float, nullable=False)
    available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    photo_urls: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)

    hotel: Mapped["Hotel"] = relationship(
        "Hotel", back_populates="rooms", lazy="joined"
    )
    bookings: Mapped[List["Booking"]] = relationship(
        "Booking", back_populates="room", cascade="all, delete-orphan", lazy="selectin"
    )
    additional_services: Mapped[List["AdditionalService"]] = relationship(
        "AdditionalService", back_populates="room", cascade="all, delete-orphan", lazy="selectin"
    )
    availability: Mapped[List["Availability"]] = relationship(
        "Availability", back_populates="room", cascade="all, delete-orphan", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Room id={self.id}, number={self.room_number}, hotel_id={self.hotel_id}>"

    @property
    def main_photo_url(self) -> Optional[str]:
        if self.photo_urls and isinstance(self.photo_urls, list) and len(self.photo_urls) > 0:
            return self.photo_urls[0]
        return None