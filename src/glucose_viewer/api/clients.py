import uuid

import glucose_viewer.schemas.db as schemas
from glucose_viewer.services.authenticate import get_user_id
import shared.db.model as models
from glucose_viewer.db.db import get_db
from fastapi import FastAPI, Request, HTTPException, Header, Depends, APIRouter
from sqlalchemy.orm import Session

router = APIRouter(prefix="/clients")
@router.post("", response_model=schemas.Client)
def create_client(client: schemas.ClientCreate, db: Session = Depends(get_db), user_id: uuid.UUID = Depends(get_user_id)):
    db_client = models.Client(**client.model_dump())
    db_client.AppUserId = user_id
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client


@router.get("", response_model=list[schemas.Client])
def get_clients(db: Session = Depends(get_db), user_id: uuid.UUID = Depends(get_user_id)):
    return db.query(models.Client).filter(models.Client.AppUserId == user_id).all()


@router.get("/{client_id}", response_model=schemas.Client)
def get_client(client_id: int, db: Session = Depends(get_db), user_id: uuid.UUID = Depends(get_user_id)):
    client = db.query(models.Client).filter(
        models.Client.id == client_id,
        models.Client.AppUserId == user_id
    ).first()
    if not client:
        raise HTTPException(404)
    return client


@router.delete("/{client_id}")
def delete_client(client_id: int, db: Session = Depends(get_db), user_id: uuid.UUID = Depends(get_user_id)):
    client = db.query(models.Client).filter(
        models.Client.id == client_id,
        models.Client.AppUserId == user_id
    ).first()
    if not client:
        raise HTTPException(404)
    db.delete(client)
    db.commit()
    return {"status": "deleted"}

@router.get("/{client_id}/patients", response_model=list[schemas.Patient])
def get_client_patients(client_id: int, db: Session = Depends(get_db), user_id: uuid.UUID = Depends(get_user_id)):

    client = db.query(models.Client).filter(
        models.Client.id == client_id,
        models.Client.AppUserId == user_id
    ).first()

    if not client:
        raise HTTPException(
            status_code=404,
            detail="Client not found"
        )

    patients = (
        db.query(models.Patient)
        .join(
            models.ClientPatientAG,
            models.Patient.id == models.ClientPatientAG.PatientID
        )
        .filter(models.ClientPatientAG.ClientID == client_id)
        .all()
    )

    return patients
