from __future__ import annotations
from WebApp import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Integer, Float, String

class AdditionalService(db.Model):
    __tablename__ = "additional_services"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    price: Mapped[float] = mapped_column(Float, nullable=False)

    room: Mapped["Room"] = relationship(
        "Room", back_populates="additional_services", lazy="joined"
    )

    def __repr__(self) -> str:
        return f"<AdditionalService id={self.id}, room_id={self.room_id}, name={self.name}, price={self.price}>"