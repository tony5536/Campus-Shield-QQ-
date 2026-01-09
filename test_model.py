from datetime import datetime
from pydantic import BaseModel

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

try:
    c = CameraOut(
        id=1,
        name="Main Entrance Gate",
        location="Building A - North Entry",
        rtsp_url="rtsp://admin:pass@192.168.1.101:554/stream1",
        status="online",
        last_seen=datetime.utcnow()
    )
    print("Success:", c)
except Exception as e:
    print("Error:", e)
