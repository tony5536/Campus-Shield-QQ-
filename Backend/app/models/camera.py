"""
Camera model stores RTSP/endpoints and basic metadata.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from .base import Base


class Camera(Base):
    __tablename__ = "cameras"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    rtsp_url = Column(Text, nullable=False)
    location = Column(String(256), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())