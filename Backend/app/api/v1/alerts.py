"""
Alerts API - Refactored to v1.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ...core.security import get_db
from ...models.alert import Alert
from ...core.logging import setup_logger

logger = setup_logger(__name__)
router = APIRouter()


class AlertOut(BaseModel):
    """Output model for alerts."""
    id: int
    incident_id: int
    message: str
    acknowledged: bool
    acknowledged_by: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True


@router.get("/", response_model=List[AlertOut])
def list_alerts(
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List recent alerts."""
    return db.query(Alert).order_by(
        Alert.timestamp.desc()
    ).limit(limit).all()


@router.get("/{alert_id}", response_model=AlertOut)
def get_alert(
    alert_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific alert by ID."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert

