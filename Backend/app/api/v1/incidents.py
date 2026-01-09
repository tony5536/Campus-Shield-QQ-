"""
Incidents API - Refactored to v1 with clean architecture.
Uses CANONICAL IncidentResponse schema for all responses.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ...core.security import get_db
from ...models.incident import Incident, IncidentStatus
from ...models.alert import Alert
from ...schemas.incident import (
    IncidentCreate,
    IncidentResponse,
    IncidentListResponse,
    IncidentUpdate
)
from ...services.notification_service import NotificationManager
from ...core.logging import setup_logger

logger = setup_logger(__name__)
router = APIRouter()

def _incident_to_response(inc: Incident) -> IncidentResponse:
    """Convert SQLAlchemy Incident model to canonical IncidentResponse."""
    return IncidentResponse(
        incident_id=inc.id,
        incident_type=inc.incident_type,
        timestamp=inc.timestamp.isoformat() if inc.timestamp else datetime.utcnow().isoformat(),
        location=inc.location or "Unknown",
        zone=inc.zone,
        source=inc.source,
        severity=_normalize_severity(inc.severity),
        description=inc.description,
        status=inc.status.value if hasattr(inc.status, 'value') else str(inc.status)
    )


def _normalize_severity(severity):
    """Convert numeric or string severity to canonical form."""
    if isinstance(severity, str):
        sev_upper = severity.upper()
        if sev_upper in ("HIGH", "CRITICAL", "URGENT"):
            return "HIGH"
        if sev_upper in ("MEDIUM", "MED", "WARNING"):
            return "MEDIUM"
        return "LOW"
    
    if isinstance(severity, (int, float)):
        if severity >= 0.7:
            return "HIGH"
        if severity >= 0.4:
            return "MEDIUM"
        return "LOW"
    
    return "LOW"


@router.post("/", response_model=IncidentResponse)
def create_incident(
    payload: IncidentCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new incident.
    
    Request body must include:
    - incident_type: str (required)
    - location: str (required)
    - severity: "low" | "medium" | "high" (normalized)
    - description: str (optional)
    - zone: str (optional)
    - source: str (optional)
    
    Returns canonical IncidentResponse.
    """
    # Determine status based on severity
    status = IncidentStatus.ACTIVE if payload.severity == "high" else IncidentStatus.RESOLVED
    
    inc = Incident(
        incident_type=payload.incident_type,
        severity=payload.severity,
        description=payload.description,
        location=payload.location,
        zone=payload.zone,
        source=payload.source,
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

    # Broadcast via notification manager
    NotificationManager.broadcast_now({
        "type": "alert",
        "alert_id": alert.id,
        "incident_id": inc.id,
        "message": alert.message
    })
    
    logger.info(f"Created incident {inc.id}: {inc.incident_type} (severity={inc.severity})")
    return _incident_to_response(inc)


@router.get("", response_model=IncidentListResponse, include_in_schema=False)
@router.get("/", response_model=IncidentListResponse)
def list_incidents(
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    List all incidents with pagination.
    
    Returns:
    {
        "total": int,
        "incidents": [IncidentResponse, ...]
    }
    """
    total = db.query(Incident).count()
    incidents = db.query(Incident).order_by(
        Incident.timestamp.desc()
    ).offset(offset).limit(limit).all()
    
    return IncidentListResponse(
        total=total,
        incidents=[_incident_to_response(inc) for inc in incidents]
    )


@router.get("/{incident_id}", response_model=IncidentResponse)
def get_incident(
    incident_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific incident by ID.
    
    Returns canonical IncidentResponse or 404 if not found.
    """
    inc = db.query(Incident).filter(Incident.id == incident_id).first()
    if not inc:
        raise HTTPException(
            status_code=404,
            detail=f"Incident with ID {incident_id} not found"
        )
    
    logger.info(f"Fetched incident {incident_id}")
    return _incident_to_response(inc)


@router.patch("/{incident_id}", response_model=IncidentResponse)
def update_incident(
    incident_id: int,
    payload: IncidentUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an incident (all fields optional).
    
    Returns updated canonical IncidentResponse.
    """
    inc = db.query(Incident).filter(Incident.id == incident_id).first()
    if not inc:
        raise HTTPException(
            status_code=404,
            detail=f"Incident with ID {incident_id} not found"
        )
    
    # Update only provided fields
    if payload.incident_type is not None:
        inc.incident_type = payload.incident_type
    if payload.location is not None:
        inc.location = payload.location
    if payload.zone is not None:
        inc.zone = payload.zone
    if payload.source is not None:
        inc.source = payload.source
    if payload.severity is not None:
        inc.severity = payload.severity
    if payload.description is not None:
        inc.description = payload.description
    if payload.status is not None:
        inc.status = IncidentStatus[payload.status]
    
    db.commit()
    db.refresh(inc)
    
    logger.info(f"Updated incident {incident_id}")
    return _incident_to_response(inc)

