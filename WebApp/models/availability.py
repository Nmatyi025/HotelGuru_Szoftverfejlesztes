# models/availability.py
from __future__ import annotations
from datetime import date
from WebApp import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Date, Integer, Boolean

class Availability(db.Model):
    __tablename__ = "availability"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"), nullable=False)
    availability_date: Mapped[date] = mapped_column(Date, nullable=False)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    room: Mapped["Room"] = relationship(
        "Room", back_populates="availability", lazy="joined"
    )

    def __repr__(self) -> str:
        return f"<Availability room_id={self.room_id}, date={self.availability_date}, available={self.is_available}>"