from pydantic import BaseModel, Field
from datetime import datetime

class Glucose(BaseModel):
    PatientID: str = Field(..., description="ID of the patient")
    Value: float = Field(..., description="Glucose value in mmol/l")
    Time: datetime = Field(..., description="Timestamp of the glucose measurement")
    Unit: str = Field("mmol/l", description="Unit of the glucose value, default is mmol/l")
