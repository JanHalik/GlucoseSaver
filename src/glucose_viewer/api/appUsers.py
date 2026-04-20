import glucose_viewer.schemas.db as schemas
import shared.db.model as models
from glucose_viewer.db.db import get_db
from glucose_viewer.general.security import hash_password
from fastapi import FastAPI, Request, HTTPException, Header, Depends, APIRouter
from sqlalchemy.orm import Session
from glucose_viewer.services.authenticate import create_token_for_user_mem as create_token
import uuid

router = APIRouter(prefix="/appusers")
@router.post("", response_model=schemas.AppUser)
def create_appuser(user: schemas.AppUserCreate, db: Session = Depends(get_db)):

    user_data = user.model_dump()

    user_data["Password"] = hash_password(user_data["Password"].get_secret_value())
    user_data["id"] = uuid.uuid4().bytes

    db_user = models.AppUser(**user_data)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user
@router.get("", response_model=list[schemas.AppUser])
def get_appusers(db: Session = Depends(get_db)):

    return db.query(models.AppUser).all()

@router.get("/{user_id}", response_model=schemas.AppUser)
def get_appuser(user_id: uuid.UUID, db: Session = Depends(get_db)):

    user = db.query(models.AppUser).filter(
        models.AppUser.id == user_id
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="AppUser not found")

    return user

@router.put("/{user_id}", response_model=schemas.AppUser)
def update_appuser(user_id: uuid.UUID, user: schemas.AppUserCreate, db: Session = Depends(get_db)):

    db_user = db.query(models.AppUser).filter(
        models.AppUser.id == user_id
    ).first()

    if not db_user:
        raise HTTPException(status_code=404)

    update_data = user.model_dump()

    if "Password" in update_data:
        update_data["Password"] = hash_password(update_data["Password"])

    for key, value in update_data.items():
        setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)

    return db_user

@router.delete("/{user_id}")
def delete_appuser(user_id: uuid.UUID, db: Session = Depends(get_db)):

    user = db.query(models.AppUser).filter(
        models.AppUser.id == user_id
    ).first()

    if not user:
        raise HTTPException(status_code=404)

    db.delete(user)
    db.commit()

    return {"status": "deleted"}

@router.get("/{user_id}/clients")
def get_appuser_clients(user_id: uuid.UUID, db: Session = Depends(get_db)):

    clients = (
        db.query(models.Client)
        .filter(models.Client.AppUserId == user_id)
        .all()
    )

    return clients

@router.post("/auth", response_model=schemas.AuthResponse)
def authenticate(data: schemas.AuthenticateAppUser, db: Session = Depends(get_db)):
    user = db.query(models.AppUser).filter(
        models.AppUser.username == data.Login,
        models.AppUser.password == hash_password(data.Password.get_secret_value())
    ).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # generování UUID
    user_id = user.id

    # vytvoření tokenu
    token = create_token(user_id)

    return schemas.AuthResponse(
        access_token=token
    )