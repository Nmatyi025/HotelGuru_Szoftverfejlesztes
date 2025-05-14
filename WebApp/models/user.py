
from __future__ import annotations
from WebApp import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import String, Integer
from sqlalchemy import ForeignKey, Column, Table
from typing import List, Optional
from werkzeug.security import generate_password_hash, check_password_hash

UserRole = Table(
    "userroles",
    db.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True)
)

class User(db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    email: Mapped[Optional[str]] = mapped_column(String(120), nullable=True, unique=True)
    password: Mapped[str] = mapped_column(String(128), nullable=False)
    phone : Mapped[str] = mapped_column(String(15), nullable=True, unique=True)

    roles: Mapped[List["Role"]] = relationship(
        "Role",
        secondary=UserRole,
        back_populates="users")

    bookings: Mapped[List["Booking"]] = relationship(
        "Booking", back_populates="user", cascade="all, delete-orphan", lazy="selectin")

    def __repr__(self) -> str:
        return f"<User id={self.id}, username={self.username}>"

    def set_password(self, password: str) -> None:
        self.password = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)