from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from ...core.logging import setup_logger
from ...models.incident import Incident, IncidentStatus
from ...models.camera import Camera
from ...core.security import get_db

logger = setup_logger(__name__)
router = APIRouter()


@router.get("/metrics")
def get_dashboard_metrics(db: Session = Depends(get_db)):
    """
    GET /api/dashboard/metrics
    Returns key dashboard metrics required by frontend.
    """
    logger.info("Route hit: GET /api/dashboard/metrics")
    try:
        # Active alerts: count incidents with ACTIVE status
        active_alerts = db.query(Incident).filter(Incident.status == IncidentStatus.ACTIVE).count()

        # Total incidents
        total_incidents = db.query(Incident).count()

        # Cameras online: count cameras in DB
        try:
            cameras_online = db.query(Camera).count()
        except Exception:
            cameras_online = 0

        # Average response time: compute average age (minutes) of RESOLVED incidents
        now = datetime.utcnow()
        resolved_incidents = db.query(Incident).filter(Incident.status == IncidentStatus.RESOLVED).all()
        if resolved_incidents:
            total_minutes = 0.0
            for inc in resolved_incidents:
                if inc.timestamp:
                    delta = now - inc.timestamp.replace(tzinfo=None) if hasattr(inc.timestamp, 'tzinfo') else now - inc.timestamp
                    total_minutes += max(delta.total_seconds() / 60.0, 0.0)
            avg_minutes = total_minutes / len(resolved_incidents)
        else:
            # Fallback to average age of all incidents (real data, not placeholder)
            all_incidents = db.query(Incident).all()
            if all_incidents:
                total_minutes = 0.0
                for inc in all_incidents:
                    if inc.timestamp:
                        delta = now - inc.timestamp.replace(tzinfo=None) if hasattr(inc.timestamp, 'tzinfo') else now - inc.timestamp
                        total_minutes += max(delta.total_seconds() / 60.0, 0.0)
                avg_minutes = total_minutes / len(all_incidents)
            else:
                avg_minutes = 0.0

        avg_response_time = f"{int(round(avg_minutes))}m"

        payload = {
            "active_alerts": int(active_alerts),
            "total_incidents": int(total_incidents),
            "cameras_online": int(cameras_online),
            "avg_response_time": avg_response_time,
        }

        logger.info("Response /api/dashboard/metrics: %s", payload)
        return payload
    except Exception as e:
        logger.exception("Error in GET /api/dashboard/metrics")
        raise HTTPException(status_code=500, detail=str(e))
