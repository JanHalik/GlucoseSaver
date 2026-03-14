import glucose_viewer.schemas.db as schemas
import shared.db.model as models
from datetime import datetime, timedelta
from glucose_viewer.api.WebSocket import notify_entity_change, MessageType, WSOperation, EntityName
from glucose_viewer.db.db import get_db
from fastapi import FastAPI, Request, HTTPException, Header, Depends, APIRouter
from sqlalchemy.orm import Session
router = APIRouter(prefix="/measurements")
@router.post("", response_model=schemas.PatientData)
def create_measurement(data: schemas.PatientDataCreate, db: Session = Depends(get_db)):
    db_data = models.PatientData(**data.model_dump())
    db.add(db_data)
    db.commit()
    db.refresh(db_data)

    notify_entity_change(MessageType.ENTITY,WSOperation.ADD,EntityName.GLUCOSE, {"datetime":db_data.Time.isoformat(), "value": db_data.Value}, db_data.PatientID)
    return db_data


@router.get("/{patient_id}")
def get_measurements(patient_id: str, db: Session = Depends(get_db)):
    return (
        db.query(models.PatientData)
        .filter(models.PatientData.PatientID == patient_id)
        .order_by(models.PatientData.Time.desc())
        .all()
    )
@router.get("/{patient_id}/day/{day}")
def get_measurements_for_day(patient_id: str, day: datetime, db: Session = Depends(get_db)):

    start = datetime(day.year, day.month, day.day)
    end = start + timedelta(days=1)

    result = (
        db.query(models.PatientData)
        .filter(models.PatientData.PatientID == patient_id)
        .filter(models.PatientData.Time >= start)
        .filter(models.PatientData.Time < end)
        .all()
    )

    return result