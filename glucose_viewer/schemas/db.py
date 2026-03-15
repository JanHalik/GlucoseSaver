from pydantic import BaseModel, Field, SecretStr
from datetime import datetime
from shared.enums.db import PollerState as PollerStateEnum
from typing import Optional

class AppUserBase(BaseModel):
    Login: str
    Email: str | None = None
    FirstName: str | None = None
    LastName: str | None = None
    PhoneNumber: str | None = None


class AppUserCreate(AppUserBase):
    Password: SecretStr


class AppUser(AppUserBase):
    id: int

    class Config:
        from_attributes = True

class ClientBase(BaseModel):
    AppUserId: int
    Email: str | None
    Password: str

class ClientCreate(ClientBase):
    id: int

class Client(ClientBase):
    id: int

    class Config:
        from_attributes = True


class PatientBase(BaseModel):
    FirstName: str | None
    LastName: str | None
    PollerState: Optional[PollerStateEnum] = Field(default=PollerStateEnum.INACTIVE, description="The state of the poller for this patient")

class PatientCreate(PatientBase):
    id: str


class Patient(PatientBase):
    id: str
    class Config:
        from_attributes = True


class PatientDataBase(BaseModel):
    PatientID: str
    Value: float
    Time: datetime
    Unit: str


class PatientDataCreate(PatientDataBase):
    pass


class PatientData(PatientDataBase):
    id: int

    class Config:
        from_attributes = True


class ClientPatientAGBase(BaseModel):
    ClientID: int
    PatientID: str


class ClientPatientAGCreate(ClientPatientAGBase):
    pass

class ClientPatientByName(BaseModel):
    client_firstname: str
    client_lastname: str
    patient_firstname: str
    patient_lastname: str

class ClientPatientAG(ClientPatientAGBase):
    idClientPatientAG: int

    class Config:
        from_attributes = True