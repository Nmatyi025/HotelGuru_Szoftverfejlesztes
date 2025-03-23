from app.extensions import db
from sqlalchemy import Column, Table, ForeignKey

UserRole = Table(
    "user_roles",
    db.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("role_id", ForeignKey("roles.id"), primary_key=True)
) 