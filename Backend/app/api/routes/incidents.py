from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List
from ...models.incident import Incident, IncidentStatus
from ...models.alert import Alert
from ...utils.security import get_db
from ...services.notification_service import NotificationManager
import datetime
import logging


def _incident_to_dict(inc: Incident) -> dict:
    """Serialize Incident ORM to a frontend-safe dict.

    - Enums -> strings
    - timestamps -> ISO strings
    - text fields -> strings (default empty)
    - array fields -> [] if missing or null
    """
    # Defensive defaults
    def safe_str(v):
        return v if isinstance(v, str) else (str(v) if v is not None else "")

    def severity_to_str(v):
        """Normalize severity into standardized string values: LOW, MEDIUM, HIGH."""
        logger = logging.getLogger(__name__)
        if v is None:
            return "LOW"
        # If enum-like with .value
        if hasattr(v, 'value'):
            try:
                sval = str(v.value)
            except Exception:
                sval = str(v)
        else:
            sval = str(v)

        sval_clean = sval.strip().lower()
        # Known textual mappings
        if sval_clean in ("critical", "high"):
            return "HIGH"
        if sval_clean in ("medium", "med"):
            return "MEDIUM"
        if sval_clean in ("low", "minor"):
            return "LOW"

        # Try numeric conversion
        try:
            num = float(sval_clean)
            if num >= 0.66:
                return "HIGH"
            if num >= 0.33:
                return "MEDIUM"
            return "LOW"
        except Exception:
            logger.warning("Unexpected severity value '%s' for incident id=%s; defaulting to LOW", sval, getattr(inc, 'id', None))
            return "LOW"

    status = getattr(inc, 'status', None)
    # status might be an IncidentStatus or string
    if isinstance(status, IncidentStatus):
        status_val = status.value
    else:
        status_val = str(status) if status is not None else "ACTIVE"

    ts = getattr(inc, 'timestamp', None)
    if isinstance(ts, datetime.datetime):
        ts_val = ts.isoformat()
    else:
        ts_val = None

    return {
        "id": int(inc.id) if inc.id is not None else None,
        "incident_id": int(inc.incident_id) if getattr(inc, 'incident_id', None) is not None else None,
        "camera_id": int(inc.camera_id) if getattr(inc, 'camera_id', None) is not None else None,
        "incident_type": safe_str(getattr(inc, 'incident_type', '')),
        "severity": severity_to_str(getattr(inc, 'severity', None)),
        "status": status_val,
        "description": safe_str(getattr(inc, 'description', '')),
        "location": safe_str(getattr(inc, 'location', '')),
        "zone": safe_str(getattr(inc, 'zone', '')),
        "source": safe_str(getattr(inc, 'source', '')),
        "assigned_team": safe_str(getattr(inc, 'assigned_team', '')),
        "timestamp": ts_val,
    }

router = APIRouter()

@router.get('/recent')
def recent_incidents(limit: int = 10, db: Session = Depends(get_db)):
    """
    GET /api/incidents/recent
    Returns recent incidents in simplified shape required by frontend.
    """
    logger = logging.getLogger(__name__)
    logger.info("Route hit: GET /api/incidents/recent")
    try:
        rows = db.query(Incident).order_by(Incident.timestamp.desc()).limit(limit).all()
        out = []
        for r in rows:
            d = _incident_to_dict(r)
            title = d.get('incident_type') or d.get('description') or f"Incident {d.get('id')}"
            out.append({
                'id': d.get('id'),
                'title': title,
                'timestamp': d.get('timestamp'),
                'severity': d.get('severity'),
                'status': d.get('status'),
            })
        logger.info("Response /api/incidents/recent: %s", out)
        return { 'incidents': out }
    except Exception as e:
        logger.exception("Error in GET /api/incidents/recent")
        raise HTTPException(status_code=500, detail=str(e))

class IncidentIn(BaseModel):
    camera_id: int | None = None
    incident_type: str
    severity: float = 0.0
    description: str | None = None

class IncidentOut(IncidentIn):
    id: int
    status: str
    severity: str

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
    return _incident_to_dict(inc)

@router.get("/", response_model=List[IncidentOut])
def list_incidents(db: Session = Depends(get_db)):
    rows = db.query(Incident).order_by(Incident.timestamp.desc()).limit(100).all()
    return [_incident_to_dict(r) for r in rows]

@router.get("/{incident_id}", response_model=IncidentOut)
def get_incident(incident_id: int, db: Session = Depends(get_db)):
    inc = db.query(Incident).filter(Incident.id == incident_id).first()
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")
    return _incident_to_dict(inc)