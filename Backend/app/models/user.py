"""
User model for authentication/authorization.
For prototype we use a simple model; expand with roles/permissions in production.
"""
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from .base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(128), unique=True, index=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    role = Column(String(50), default="guard")
    created_at = Column(DateTime(timezone=True), server_default=func.now())