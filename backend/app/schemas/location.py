import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class LocationCreate(BaseModel):
    lat: float
    lon: float
    district: Optional[str] = None
    village: Optional[str] = None
    elevation: Optional[float] = None
    slope: Optional[float] = None


class LocationOut(BaseModel):
    id: uuid.UUID
    lat: float
    lon: float
    district: Optional[str] = None
    village: Optional[str] = None
    elevation: Optional[float] = None
    slope: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True
