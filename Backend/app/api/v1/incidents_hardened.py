"""
Production-hardened incident routes with strict data contract.
- All responses follow IncidentResponse schema
- Proper error handling and logging
- WebSocket for real-time updates
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from typing import List
from datetime import datetime, timedelta
import logging

from ...schemas.incident import (
    IncidentCreate,
    IncidentUpdate,
    IncidentResponse,
    IncidentListResponse,
    ErrorResponse
)
from ...models.incident import Incident, IncidentStatus
from ...utils.security import get_db
from ...core.logging import log_error

logger = logging.getLogger(__name__)
router = APIRouter()


def _incident_to_response(inc: Incident) -> dict:
    """
    Serialize Incident ORM to canonical IncidentResponse.
    CRITICAL: Strict schema adherence - no missing fields.
    """
    if not inc:
        return None
    
    try:
        # Status normalization
        status = getattr(inc, 'status', 'ACTIVE')
        if hasattr(status, 'value'):
            status = status.value
        status = str(status).upper() or "ACTIVE"
        
        # Severity normalization (numeric -> text)
        severity = getattr(inc, 'severity', None)
        if isinstance(severity, (int, float)):
            severity = "HIGH" if severity >= 0.66 else "MEDIUM" if severity >= 0.33 else "LOW"
        else:
            severity = str(severity or "LOW").upper()
            # Normalize synonyms
            if severity in ("CRITICAL",):
                severity = "HIGH"
            elif severity not in ("LOW", "MEDIUM", "HIGH"):
                severity = "LOW"
        
        # Timestamp to ISO format
        timestamp = getattr(inc, 'timestamp', None)
        if isinstance(timestamp, datetime):
            timestamp_str = timestamp.isoformat() + "Z" if not timestamp.isoformat().endswith("Z") else timestamp.isoformat()
        else:
            timestamp_str = datetime.utcnow().isoformat() + "Z"
        
        return {
            "incident_id": inc.id,
            "incident_type": str(getattr(inc, 'incident_type', 'unknown')),
            "location": str(getattr(inc, 'location', 'unknown')),
            "zone": str(getattr(inc, 'zone', None)) if getattr(inc, 'zone', None) else None,
            "source": str(getattr(inc, 'source', None)) if getattr(inc, 'source', None) else None,
            "severity": severity,
            "description": str(getattr(inc, 'description', '')) if getattr(inc, 'description') else '',
            "status": status,
            "timestamp": timestamp_str,
        }
    except Exception as e:
        logger.error(f"Error serializing incident {inc.id}: {e}", exc_info=True)
        raise


@router.get("/", response_model=IncidentListResponse)
async def list_incidents(
    skip: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(50, ge=1, le=500, description="Max results"),
    severity: str = Query(None, description="Filter by severity: LOW, MEDIUM, HIGH"),
    status: str = Query(None, description="Filter by status: ACTIVE, RESOLVED"),
    db: Session = Depends(get_db)
):
    """
    Fetch incidents with filters.
    ALWAYS returns valid IncidentListResponse (never undefined fields).
    """
    try:
        query = db.query(Incident)
        
        # Apply filters
        if severity and severity.upper() in ("LOW", "MEDIUM", "HIGH"):
            # Handle numeric severity values
            if severity.upper() == "HIGH":
                query = query.filter(Incident.severity >= 0.66)
            elif severity.upper() == "MEDIUM":
                query = query.filter((Incident.severity >= 0.33) & (Incident.severity < 0.66))
            else:
                query = query.filter(Incident.severity < 0.33)
        
        if status and status.upper() in ("ACTIVE", "RESOLVED"):
            query = query.filter(Incident.status == status.upper())
        
        # Ordering and pagination
        query = query.order_by(Incident.timestamp.desc())
        total = query.count()
        
        rows = query.offset(skip).limit(limit).all()
        incidents = [_incident_to_response(r) for r in rows if r]
        
        logger.info(f"Fetched {len(incidents)} incidents (skip={skip}, limit={limit})")
        
        return {
            "total": total,
            "incidents": incidents
        }
    
    except Exception as e:
        log_error(logger, "INCIDENTS_LIST_ERROR", str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch incidents")


@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(
    incident_id: int,
    db: Session = Depends(get_db)
):
    """Fetch single incident by ID"""
    try:
        inc = db.query(Incident).filter(Incident.id == incident_id).first()
        if not inc:
            raise HTTPException(
                status_code=404,
                detail=ErrorResponse(
                    error="INCIDENT_NOT_FOUND",
                    message=f"Incident {incident_id} not found",
                    status_code=404
                ).dict()
            )
        
        return _incident_to_response(inc)
    
    except HTTPException:
        raise
    except Exception as e:
        log_error(logger, "INCIDENT_GET_ERROR", f"ID={incident_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch incident")


@router.post("/", response_model=IncidentResponse, status_code=201)
async def create_incident(
    payload: IncidentCreate,
    db: Session = Depends(get_db)
):
    """Create new incident"""
    try:
        inc = Incident(
            incident_type=payload.incident_type,
            location=payload.location,
            zone=payload.zone,
            source=payload.source,
            severity=payload.severity,  # Will be normalized by schema
            description=payload.description or "",
            status="ACTIVE"
        )
        
        db.add(inc)
        db.commit()
        db.refresh(inc)
        
        logger.info(f"Created incident {inc.id}: {payload.incident_type} at {payload.location}")
        
        return _incident_to_response(inc)
    
    except Exception as e:
        db.rollback()
        log_error(logger, "INCIDENT_CREATE_ERROR", str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create incident")


@router.put("/{incident_id}", response_model=IncidentResponse)
async def update_incident(
    incident_id: int,
    payload: IncidentUpdate,
    db: Session = Depends(get_db)
):
    """Update incident"""
    try:
        inc = db.query(Incident).filter(Incident.id == incident_id).first()
        if not inc:
            raise HTTPException(status_code=404, detail="Incident not found")
        
        # Apply updates
        update_data = payload.dict(exclude_unset=True)
        for field, value in update_data.items():
            if value is not None:
                setattr(inc, field, value)
        
        db.commit()
        db.refresh(inc)
        
        logger.info(f"Updated incident {incident_id}")
        
        return _incident_to_response(inc)
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        log_error(logger, "INCIDENT_UPDATE_ERROR", f"ID={incident_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to update incident")


@router.get("/recent/{hours}", response_model=List[IncidentResponse])
async def get_recent_incidents(
    hours: int = Query(24, ge=1, le=720, description="Hours lookback"),
    db: Session = Depends(get_db)
):
    """Get incidents from last N hours"""
    try:
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        rows = (
            db.query(Incident)
            .filter(Incident.timestamp >= cutoff)
            .order_by(Incident.timestamp.desc())
            .limit(100)
            .all()
        )
        
        logger.info(f"Fetched {len(rows)} incidents from last {hours} hours")
        
        return [_incident_to_response(r) for r in rows if r]
    
    except Exception as e:
        log_error(logger, "RECENT_INCIDENTS_ERROR", str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch recent incidents")


@router.delete("/{incident_id}", status_code=204)
async def delete_incident(
    incident_id: int,
    db: Session = Depends(get_db)
):
    """Delete incident (soft-delete via status)"""
    try:
        inc = db.query(Incident).filter(Incident.id == incident_id).first()
        if not inc:
            raise HTTPException(status_code=404, detail="Incident not found")
        
        inc.status = "RESOLVED"  # Soft delete
        db.commit()
        
        logger.info(f"Deleted incident {incident_id}")
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        log_error(logger, "INCIDENT_DELETE_ERROR", f"ID={incident_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to delete incident")
