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


@router.get("")
def get_relations(db: Session = Depends(get_db)):
    return db.query(models.ClientPatientAG).all()