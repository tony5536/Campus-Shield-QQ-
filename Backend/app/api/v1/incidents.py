"""
Incidents API - Refactored to v1 with clean architecture.
Maintains backward compatibility.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ...core.security import get_db
from ...models.incident import Incident
from ...models.alert import Alert
from ...services.notification_service import NotificationManager
from ...core.logging import setup_logger

logger = setup_logger(__name__)
router = APIRouter()


class IncidentIn(BaseModel):
    """Input model for creating incidents."""
    camera_id: Optional[int] = None
    incident_type: str
    severity: float = 0.0
    description: Optional[str] = None
    location: Optional[str] = None
    zone: Optional[str] = None
    source: Optional[str] = None
    assigned_team: Optional[str] = None


class IncidentOut(BaseModel):
    """Output model for incidents."""
    id: int
    incident_id: Optional[int] = None
    camera_id: Optional[int] = None
    incident_type: str
    severity: float
    description: Optional[str] = None
    location: Optional[str] = None
    zone: Optional[str] = None
    source: Optional[str] = None
    assigned_team: Optional[str] = None
    status: str
    timestamp: datetime

    class Config:
        from_attributes = True


@router.post("/", response_model=IncidentOut)
def create_incident(
    payload: IncidentIn,
    db: Session = Depends(get_db)
):
    """Create a new incident."""
    from ...models.incident import IncidentStatus
    
    # Determine status based on severity (High = ACTIVE by default)
    status = IncidentStatus.ACTIVE if payload.severity >= 0.7 else IncidentStatus.RESOLVED
    
    inc = Incident(
        camera_id=payload.camera_id,
        incident_type=payload.incident_type,
        severity=payload.severity,
        description=payload.description,
        location=payload.location,
        zone=payload.zone,
        source=payload.source,
        assigned_team=payload.assigned_team,
        status=status,
    )
    db.add(inc)
    db.commit()
    db.refresh(inc)

    # Create linked alert
    alert = Alert(
        incident_id=inc.id,
        message=f"New incident: {inc.incident_type} severity={inc.severity}"
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)

    # Broadcast via notification manager
    NotificationManager.broadcast_now({
        "type": "alert",
        "alert_id": alert.id,
        "incident_id": inc.id,
        "message": alert.message
    })
    
    return inc


@router.get("/", response_model=List[IncidentOut])
def list_incidents(
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """List incidents with pagination."""
    incidents = db.query(Incident).order_by(
        Incident.timestamp.desc()
    ).offset(offset).limit(limit).all()
    
    # Convert status enum to string
    return [
        IncidentOut(
            id=inc.id,
            incident_id=inc.incident_id,
            camera_id=inc.camera_id,
            incident_type=inc.incident_type,
            severity=inc.severity,
            description=inc.description,
            location=inc.location,
            zone=inc.zone,
            source=inc.source,
            assigned_team=inc.assigned_team,
            status=inc.status.value if hasattr(inc.status, 'value') else str(inc.status),
            timestamp=inc.timestamp,
        )
        for inc in incidents
    ]


@router.get("/{incident_id}", response_model=IncidentOut)
def get_incident(
    incident_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific incident by ID."""
    inc = db.query(Incident).filter(Incident.id == incident_id).first()
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    # Convert status enum to string
    return IncidentOut(
        id=inc.id,
        incident_id=inc.incident_id,
        camera_id=inc.camera_id,
        incident_type=inc.incident_type,
        severity=inc.severity,
        description=inc.description,
        location=inc.location,
        zone=inc.zone,
        source=inc.source,
        assigned_team=inc.assigned_team,
        status=inc.status.value if hasattr(inc.status, 'value') else str(inc.status),
        timestamp=inc.timestamp,
    )

