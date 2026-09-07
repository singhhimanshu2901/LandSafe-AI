import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class WeatherObservationCreate(BaseModel):
    location_id: uuid.UUID
    timestamp: Optional[datetime] = None
    rainfall: Optional[float] = None
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    source: Optional[str] = None


class WeatherObservationOut(BaseModel):
    id: uuid.UUID
    location_id: uuid.UUID
    timestamp: datetime
    rainfall: Optional[float] = None
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    source: Optional[str] = None

    class Config:
        from_attributes = True
