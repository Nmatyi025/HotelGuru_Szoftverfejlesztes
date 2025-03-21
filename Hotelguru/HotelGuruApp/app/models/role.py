from app.extensions import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import String, Integer
from typing import List
from app.models.associations import UserRole
from app.models.user import User

class Role(db.Model):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    
    users: Mapped[List["User"]] = relationship(secondary=UserRole, back_populates="roles")

    def __repr__(self) -> str:
        return f"Role(id={self.id!r}, name={self.name!s})"