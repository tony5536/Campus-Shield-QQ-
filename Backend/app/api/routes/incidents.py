from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List
from ...models.incident import Incident
from ...models.alert import Alert
from ...utils.security import get_db
from ...services.notification_service import NotificationManager

router = APIRouter()

class IncidentIn(BaseModel):
    camera_id: int | None = None
    incident_type: str
    severity: float = 0.0
    description: str | None = None

class IncidentOut(IncidentIn):
    id: int
    status: str

    class Config:
        from_attributes = True

@router.post("/", response_model=IncidentOut)
def create_incident(payload: IncidentIn, db: Session = Depends(get_db)):
    inc = Incident(
        camera_id=payload.camera_id,
        incident_type=payload.incident_type,
        severity=payload.severity,
        description=payload.description,
    )
    db.add(inc)
    db.commit()
    db.refresh(inc)

    # create a linked alert
    alert = Alert(incident_id=inc.id, message=f"New incident: {inc.incident_type} severity={inc.severity}")
    db.add(alert)
    db.commit()
    db.refresh(alert)

    # broadcast via notification manager
    NotificationManager.broadcast_now({
        "type": "alert",
        "alert_id": alert.id,
        "incident_id": inc.id,
        "message": alert.message
    })
    return inc

@router.get("/", response_model=List[IncidentOut])
def list_incidents(db: Session = Depends(get_db)):
    return db.query(Incident).order_by(Incident.timestamp.desc()).limit(100).all()

@router.get("/{incident_id}", response_model=IncidentOut)
def get_incident(incident_id: int, db: Session = Depends(get_db)):
    inc = db.query(Incident).filter(Incident.id == incident_id).first()
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")
    return inc