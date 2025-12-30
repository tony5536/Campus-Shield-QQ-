"""
Incident model stores detected events and metadata.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.sql import func
from .base import Base


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(Integer, ForeignKey("cameras.id"), nullable=True)
    incident_type = Column(String(128), nullable=False)
    severity = Column(Float, default=0.0)
    status = Column(String(50), default="open")
    description = Column(Text, nullable=True)
    location = Column(String(256), nullable=True)
    source = Column(String(128), nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())