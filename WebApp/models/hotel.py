from __future__ import annotations
from datetime import datetime
from WebApp import db
from typing import List, Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Float, JSON
from WebApp.models.amenity import hotel_amenities

class Hotel(db.Model):
    __tablename__ = "hotels"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    address: Mapped[str] = mapped_column(String(200), nullable=False)
    city: Mapped[str] = mapped_column(String(50), nullable=False)
    country: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_on: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    rating: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    photo_urls: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)

    rooms: Mapped[List["Room"]] = relationship(
        "Room", back_populates="hotel", cascade="all, delete-orphan", lazy="selectin"
    )

    amenities: Mapped[List["Amenity"]] = relationship(
        "Amenity", secondary=hotel_amenities, back_populates="hotels", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Hotel id={self.id}, name={self.name}, location={self.city}, {self.country}>"

    @property
    def main_photo_url(self) -> Optional[str]:
        if self.photo_urls and isinstance(self.photo_urls, list) and len(self.photo_urls) > 0:
            return self.photo_urls[0]
        return None