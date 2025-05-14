from __future__ import annotations
from WebApp import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Integer, String, Table

hotel_amenities = Table(
    "hotel_amenities",
    db.metadata,
    db.Column("hotel_id", db.Integer, db.ForeignKey("hotels.id"), primary_key=True),
    db.Column("amenity_id", db.Integer, db.ForeignKey("amenities.id"), primary_key=True)
)

class Amenity(db.Model):
    __tablename__ = "amenities"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    icon: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    
    hotels: Mapped[list["Hotel"]] = relationship(
        "Hotel", secondary=hotel_amenities, back_populates="amenities"
    )
    
    def __repr__(self) -> str:
        return f"<Amenity id={self.id}, name={self.name}>"