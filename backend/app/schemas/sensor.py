import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class SensorReadingCreate(BaseModel):
    sensor_id: str
    lat: float
    lon: float
    timestamp: Optional[datetime] = None
    soil_moisture: Optional[float] = None
    battery: Optional[float] = None
    quality: Optional[str] = None


class SensorReadingOut(BaseModel):
    id: uuid.UUID
    sensor_id: str
    lat: float
    lon: float
    timestamp: datetime
    soil_moisture: Optional[float] = None
    battery: Optional[float] = None
    quality: Optional[str] = None

    class Config:
        from_attributes = True
