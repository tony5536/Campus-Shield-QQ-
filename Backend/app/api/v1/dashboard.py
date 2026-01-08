"""
Dashboard API endpoints for overview and statistics.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, timedelta

from ...core.security import get_db
from ...models.incident import Incident, IncidentStatus
from ...core.logging import setup_logger

logger = setup_logger(__name__)
router = APIRouter()


class DashboardOverview(BaseModel):
    """Dashboard overview response model."""
    active_alerts: int
    total_incidents_this_week: int
    cameras_online: int
    avg_response_time: float  # in minutes


class IncidentResponse(BaseModel):
    """Incident response model."""
    id: int
    incident_id: Optional[int] = None
    incident_type: str
    location: Optional[str] = None
    zone: Optional[str] = None
    timestamp: datetime
    source: Optional[str] = None
    severity: float
    description: Optional[str] = None
    status: str
    assigned_team: Optional[str] = None

    class Config:
        from_attributes = True


@router.get("/overview", response_model=DashboardOverview)
def get_dashboard_overview(db: Session = Depends(get_db)):
    """
    Get dashboard overview statistics.
    
    Returns:
        DashboardOverview with key metrics
    """
    try:
        # Calculate active alerts (ACTIVE incidents)
        active_alerts = db.query(Incident).filter(
            Incident.status == IncidentStatus.ACTIVE
        ).count()
        
        # Calculate incidents this week
        week_ago = datetime.utcnow() - timedelta(days=7)
        total_incidents_this_week = db.query(Incident).filter(
            Incident.timestamp >= week_ago
        ).count()
        
        # Mock cameras online (as specified)
        cameras_online = 24
        
        # Calculate average response time (mock for now, can be enhanced with actual response tracking)
        # For now, use a simple heuristic: High severity incidents resolved quickly
        resolved_high_severity = db.query(Incident).filter(
            Incident.status == IncidentStatus.RESOLVED,
            Incident.severity >= 0.7
        ).count()
        
        # Mock average response time (in minutes)
        # In production, this would be calculated from actual response timestamps
        avg_response_time = 15.5 if resolved_high_severity > 0 else 20.0
        
        return DashboardOverview(
            active_alerts=active_alerts,
            total_incidents_this_week=total_incidents_this_week,
            cameras_online=cameras_online,
            avg_response_time=avg_response_time
        )
    except Exception as e:
        logger.error(f"Error fetching dashboard overview: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching dashboard data: {str(e)}")


@router.get("/incidents/recent", response_model=List[IncidentResponse])
def get_recent_incidents(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Get recent incidents.
    
    Args:
        limit: Maximum number of incidents to return (default: 10)
    
    Returns:
        List of recent incidents ordered by timestamp
    """
    try:
        incidents = db.query(Incident).order_by(
            Incident.timestamp.desc()
        ).limit(limit).all()
        
        # Convert to response format (handling enum status)
        return [
            IncidentResponse(
                id=inc.id,
                incident_id=inc.incident_id,
                incident_type=inc.incident_type,
                location=inc.location,
                zone=inc.zone,
                timestamp=inc.timestamp,
                source=inc.source,
                severity=inc.severity,
                description=inc.description,
                status=inc.status.value if hasattr(inc.status, 'value') else str(inc.status),
                assigned_team=inc.assigned_team,
            )
            for inc in incidents
        ]
    except Exception as e:
        logger.error(f"Error fetching recent incidents: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching incidents: {str(e)}")


@router.get("/incidents/all", response_model=List[IncidentResponse])
def get_all_incidents(
    limit: int = 100,
    offset: int = 0,
    status: str | None = None,
    db: Session = Depends(get_db)
):
    """
    Get all incidents with optional filtering.
    
    Args:
        limit: Maximum number of incidents to return (default: 100)
        offset: Number of incidents to skip (default: 0)
        status: Filter by status (ACTIVE or RESOLVED)
    
    Returns:
        List of incidents
    """
    try:
        query = db.query(Incident)
        
        # Apply status filter if provided
        if status:
            try:
                status_enum = IncidentStatus[status.upper()]
                query = query.filter(Incident.status == status_enum)
            except KeyError:
                raise HTTPException(status_code=400, detail=f"Invalid status: {status}. Must be ACTIVE or RESOLVED")
        
        incidents = query.order_by(
            Incident.timestamp.desc()
        ).offset(offset).limit(limit).all()
        
        # Convert to response format (handling enum status)
        return [
            IncidentResponse(
                id=inc.id,
                incident_id=inc.incident_id,
                incident_type=inc.incident_type,
                location=inc.location,
                zone=inc.zone,
                timestamp=inc.timestamp,
                source=inc.source,
                severity=inc.severity,
                description=inc.description,
                status=inc.status.value if hasattr(inc.status, 'value') else str(inc.status),
                assigned_team=inc.assigned_team,
            )
            for inc in incidents
        ]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching all incidents: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching incidents: {str(e)}")

