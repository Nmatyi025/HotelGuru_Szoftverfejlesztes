
from __future__ import annotations
from WebApp import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List
from sqlalchemy.types import String, Integer
from .user import UserRole

class Role(db.Model):
    __tablename__ = "roles"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(30))

    users: Mapped[List["User"]] = relationship(
        "User",
        secondary=UserRole,
        back_populates="roles"
    )

    def __repr__(self) -> str:
        return f"Role(id={self.id!r}, name={self.name!r})"