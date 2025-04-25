# models/booking.py
from __future__ import annotations
from datetime import datetime, date
from WebApp import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Date, Integer, String

class Booking(db.Model):
    __tablename__ = "bookings"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    created_on: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)

    user: Mapped["User"] = relationship(
        "User", back_populates="bookings", lazy="joined"
    )
    room: Mapped["Room"] = relationship(
        "Room", back_populates="bookings", lazy="joined"
    )

    def __repr__(self) -> str:
        return (
            f"<Booking id={self.id}, user_id={self.user_id}, room_id={self.room_id}, "
            f"from {self.start_date} to {self.end_date}, status={self.status}>"
        )