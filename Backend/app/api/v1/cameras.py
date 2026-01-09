"""
Cameras API v1 endpoints.
Provides camera management and status information.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from ...core.security import get_db
from ...models.camera import Camera
from ...core.logging import setup_logger

logger = setup_logger(__name__)
router = APIRouter()


class CameraOut(BaseModel):
    """Camera response model."""
    id: int
    name: str
    location: str
    rtsp_url: str
    status: str
    last_seen: datetime | None = None
    
    class Config:
        from_attributes = True


@router.get("/", response_model=List[CameraOut])
def list_cameras(db: Session = Depends(get_db)):
    """
    List all cameras.
    
    Returns:
    List[{
        "id": int,
        "name": str,
        "location": str,
        "rtsp_url": str,
        "status": str,
        "last_seen": datetime
    }]
    """
    cameras = db.query(Camera).all()
    
    # Mock data fallback if database is empty
    if not cameras:
        # returns the mock data list (CameraOut objects)
        mock_cameras = [
            CameraOut(
                id=1,
                name="Main Entrance Gate",
                location="Building A - North Entry",
                rtsp_url="rtsp://admin:pass@192.168.1.101:554/stream1",
                status="online",
                last_seen=datetime.utcnow()
            ),
            CameraOut(
                id=2,
                name="Cafeteria Hall",
                location="Student Center - Level 1",
                rtsp_url="rtsp://admin:pass@192.168.1.102:554/stream1",
                status="online",
                last_seen=datetime.utcnow()
            ),
            CameraOut(
                id=3,
                name="Parking Lot B",
                location="West Parking Zone",
                rtsp_url="rtsp://admin:pass@192.168.1.103:554/stream1",
                status="offline",
                last_seen=datetime.utcnow()
            ),
            CameraOut(
                id=4,
                name="Science Lab Corridor",
                location="Building C - 2nd Floor",
                rtsp_url="rtsp://admin:pass@192.168.1.104:554/stream1",
                status="online",
                last_seen=datetime.utcnow()
            )
        ]
        return mock_cameras
        
    # Convert DB objects to Pydantic models with default status if missing
    return [
        CameraOut(
            id=c.id,
            name=c.name,
            location=c.location,
            rtsp_url=c.rtsp_url,
            status=getattr(c, "status", "online"), # Default to online if field missing
            last_seen=getattr(c, "last_seen", None) or datetime.utcnow()
        )
        for c in cameras
    ]


@router.get("/{camera_id}", response_model=CameraOut)
def get_camera(camera_id: int, db: Session = Depends(get_db)):
    """
    Get a specific camera by ID.
    """
    camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    return camera


@router.post("/", response_model=CameraOut)
def create_camera(camera: CameraOut, db: Session = Depends(get_db)):
    """
    Create a new camera.
    """
    new_camera = Camera(
        name=camera.name,
        location=camera.location,
        rtsp_url=camera.rtsp_url,
        status=camera.status
    )
    db.add(new_camera)
    db.commit()
    db.refresh(new_camera)
    return new_camera
