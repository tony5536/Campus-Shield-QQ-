#!/usr/bin/env python
"""
Initialize database schema by creating tables from SQLAlchemy models.
"""
from Backend.app.models.base import Base
from Backend.app.models.user import User
from Backend.app.models.camera import Camera
from Backend.app.models.incident import Incident
from Backend.app.models.alert import Alert
from Backend.app.config.settings import settings
from sqlalchemy import create_engine

print("Creating database engine...")
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)

print("Creating tables from SQLAlchemy models...")
Base.metadata.create_all(bind=engine)

print("✓ Database initialized successfully!")
print(f"Database URL: {settings.database_url}")
