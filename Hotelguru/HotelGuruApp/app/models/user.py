from app.extensions import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import String, Integer
from typing import List, Optional
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.associations import UserRole
from app.models.role import Role

class User(db.Model):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    email: Mapped[Optional[str]] = mapped_column(String(100), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(30))
    
    roles: Mapped[List["Role"]] = relationship(secondary=UserRole, back_populates="users")
    
    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.name!s}, email={self.email!r})"

    def set_password(self, password):
        self.password = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password, password)

    def has_role(self, role_name: str) -> bool:
        return any(role.name == role_name for role in self.roles)