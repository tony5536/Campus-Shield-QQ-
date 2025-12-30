from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List
from ...models.alert import Alert
from ...utils.security import get_db

router = APIRouter()

class AlertOut(BaseModel):
    id: int
    incident_id: int | None
    message: str
    acknowledged: bool

    class Config:
        from_attributes = True

@router.get("/", response_model=List[AlertOut])
def list_alerts(db: Session = Depends(get_db)):
    return db.query(Alert).order_by(Alert.created_at.desc()).limit(200).all()

@router.post("/{alert_id}/ack")
def acknowledge(alert_id: int, actor: str = "guard", db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.acknowledged = True
    alert.acknowledged_by = actor
    db.add(alert)
    db.commit()
    return {"status": "acknowledged", "id": alert_id}