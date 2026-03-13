from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    Index
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Client(Base):
    __tablename__ = "Client"

    id = Column(Integer, primary_key=True, index=True)
    Login = Column(String(45), unique=True, nullable=False)
    FirstName = Column(String(45))
    LastName = Column(String(45))
    Email = Column(String(45))
    Password = Column(String, nullable=False)

    patients = relationship("ClientPatientAG", back_populates="client")


class Patient(Base):
    __tablename__ = "Patient"

    id = Column(String(60), primary_key=True, index=True)
    FirstName = Column(String(45))
    LastName = Column(String(45))

    clients = relationship("ClientPatientAG", back_populates="patient")
    data = relationship("PatientData", back_populates="patient")


class ClientPatientAG(Base):
    __tablename__ = "Client_PatientAG"

    idClientPatientAG = Column(Integer, primary_key=True, index=True)
    ClientID = Column(Integer, ForeignKey("Client.id"), nullable=False)
    PatientID = Column(String(60), ForeignKey("Patient.id"), nullable=False)

    client = relationship("Client", back_populates="patients")
    patient = relationship("Patient", back_populates="clients")


class PatientData(Base):
    __tablename__ = "Patient_data"

    id = Column(Integer, primary_key=True, index=True)
    PatientID = Column(String(60), ForeignKey("Patient.id"), nullable=False)
    Value = Column(Float, nullable=False)
    Time = Column(DateTime, nullable=False)
    Unit = Column(String(20), nullable=False)

    patient = relationship("Patient", back_populates="data")


Index("idx_patient_time", PatientData.PatientID, PatientData.Time)