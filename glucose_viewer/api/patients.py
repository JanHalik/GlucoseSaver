import glucose_viewer.schemas.db as schemas
import shared.db.model as models
from glucose_viewer.db.db import get_db
from fastapi import FastAPI, Request, HTTPException, Header, Depends, APIRouter
from sqlalchemy.orm import Session
router = APIRouter(prefix="/patients")
@router.post("", response_model=schemas.Patient)
def create_patient(patient: schemas.PatientCreate, db: Session = Depends(get_db)):
    db_patient = models.Patient(**patient.model_dump())
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient


@router.get("", response_model=list[schemas.Patient])
def get_patients(db: Session = Depends(get_db)):
    return db.query(models.Patient).all()

@router.get("/{patient_id}", response_model=schemas.Client)
def get_client(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(models.Patient).get(patient_id)
    if not patient:
        raise HTTPException(404)
    return patient