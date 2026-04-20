import glucose_viewer.schemas.db as schemas
import shared.db.model as models
from glucose_viewer.db.db import get_db
from fastapi import FastAPI, Request, HTTPException, Header, Depends, APIRouter
from sqlalchemy.orm import Session
router = APIRouter(prefix="/client-patient")
@router.post("", response_model=schemas.ClientPatientAG)
def create_relation(rel: schemas.ClientPatientAGCreate, db: Session = Depends(get_db)):
    db_rel = models.ClientPatientAG(**rel.model_dump())
    db.add(db_rel)
    db.commit()
    db.refresh(db_rel)
    return db_rel

@router.delete("/{ClientID}/{PatientID}")
def delete_relation(ClientID: int, PatientID:str, db: Session = Depends(get_db)):
    relation = models.ClientPatientAG(
        ClientID=ClientID,
        PatientID=PatientID
    )
    if not relation:
        raise HTTPException(404)
    db.delete(relation)
    db.commit()
    return {"status": "deleted"}

@router.get("")
def get_relations(db: Session = Depends(get_db)):
    return db.query(models.ClientPatientAG).all()

@router.post("/by-name", response_model=schemas.ClientPatientAG)
def create_relation_by_name(
    rel: schemas.ClientPatientByName,
    db: Session = Depends(get_db)
):

    # find client
    client = (
        db.query(models.Client)
        .filter(
            models.Client.FirstName == rel.client_firstname,
            models.Client.LastName == rel.client_lastname
        )
        .first()
    )

    if not client:
        raise HTTPException(
            status_code=404,
            detail="Client not found"
        )

    # find patient
    patient = (
        db.query(models.Patient)
        .filter(
            models.Patient.FirstName == rel.patient_firstname,
            models.Patient.LastName == rel.patient_lastname
        )
        .first()
    )

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    # create relation
    relation = models.ClientPatientAG(
        ClientID=client.id,
        PatientID=patient.id
    )

    db.add(relation)
    db.commit()
    db.refresh(relation)

    return relation