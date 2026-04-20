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

@router.get("/{patient_id}", response_model=schemas.Patient)
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(models.Patient).get(patient_id)
    if not patient:
        raise HTTPException(404)
    return patient

@router.put("/{patient_id}/inactivate", response_model=schemas.Patient)
def update_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(models.Patient).get(patient_id)
    if not patient:
        raise HTTPException(404)
    patient.PollerState = schemas.PollerStateEnum.INACTIVE
    db.commit()
    return patient

@router.put("/{patient_id}/activate", response_model=schemas.Patient)
def update_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(models.Patient).get(patient_id)
    if not patient:
        raise HTTPException(404)
    patient.PollerState = schemas.PollerStateEnum.ACTIVE
    db.commit()
    return patient

@router.put("/{patient_id}", response_model=schemas.Patient)
def update_patient(patient_id: int, patient: schemas.PatientBase, db: Session = Depends(get_db)):
    patient = db.query(models.Patient).get(patient_id)
    if not patient:
        raise HTTPException(404)
    patient.FirstName = patient.FirstName
    patient.LastName = patient.LastName
    patient.PollerState = patient.PollerState
    db.commit()
    return patient