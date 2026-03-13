from pydantic import BaseModel, SecretStr
from datetime import datetime


class ClientBase(BaseModel):
    Login: str
    FirstName: str | None
    LastName: str | None
    Email: str | None


class ClientCreate(ClientBase):
    Password: SecretStr


class Client(ClientBase):
    id: int

    class Config:
        from_attributes = True


class PatientBase(BaseModel):
    FirstName: str | None
    LastName: str | None


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


class ClientPatientAG(ClientPatientAGBase):
    idClientPatientAG: int

    class Config:
        from_attributes = True