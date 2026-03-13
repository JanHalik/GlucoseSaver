import glucose_viewer.schemas.db as schemas
import shared.db.model as models
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
    return db_data


@router.get("/{patient_id}")
def get_measurements(patient_id: str, db: Session = Depends(get_db)):
    return (
        db.query(models.PatientData)
        .filter(models.PatientData.PatientID == patient_id)
        .order_by(models.PatientData.Time.desc())
        .all()
    )