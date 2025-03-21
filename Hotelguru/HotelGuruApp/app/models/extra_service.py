from app.extensions import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import String, Integer, Float
from typing import List
from app.models.reservation import Reservation

class ExtraService(db.Model):
    __tablename__ = "extra_service"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(500))
    price: Mapped[float] = mapped_column(Float, nullable=False)
    
    reservations: Mapped[List["Reservation"]] = relationship(secondary="reservation_extra_service", back_populates="extra_services")

    def __repr__(self) -> str:
        return f"ExtraService(id={self.id!r}, name={self.name!s}, price={self.price!r})" 