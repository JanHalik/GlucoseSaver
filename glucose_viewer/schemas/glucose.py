from pydantic import BaseModel, Field
from datetime import datetime

class Glucose(BaseModel):
    value: float = Field(..., description="Glucose value in mmol/l")
    timestamp: datetime = Field(..., description="Timestamp of the glucose measurement")
