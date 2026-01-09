from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List
from ...models.camera import Camera
from ...core.security import get_db

router = APIRouter()

class CameraIn(BaseModel):
    name: str
    rtsp_url: str
    location: str | None = None

class CameraOut(CameraIn):
    id: int
    status: str = "ONLINE"

    class Config:
        from_attributes = True

@router.post("/", response_model=CameraOut)
def create_camera(payload: CameraIn, db: Session = Depends(get_db)):
    cam = Camera(name=payload.name, rtsp_url=payload.rtsp_url, location=payload.location)
    db.add(cam)
    db.commit()
    db.refresh(cam)
    return cam

@router.get("/", response_model=List[CameraOut])
def list_cameras(db: Session = Depends(get_db)):
    cams = db.query(Camera).all()
    if not cams:
        # Return mock data for live view if DB is empty
        return [
            CameraOut(
                id=1, 
                name="Camera A", 
                rtsp_url="mock://stream", 
                location="Main Entrance", 
                status="ONLINE"
            )
        ]
    return cams

@router.get("/{camera_id}", response_model=CameraOut)
def get_camera(camera_id: int, db: Session = Depends(get_db)):
    cam = db.query(Camera).filter(Camera.id == camera_id).first()
    if not cam:
        raise HTTPException(status_code=404, detail="Camera not found")
    return cam