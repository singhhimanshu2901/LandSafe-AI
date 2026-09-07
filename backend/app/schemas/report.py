import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class FieldReportCreate(BaseModel):
    user_id: Optional[uuid.UUID] = None
    lat: float
    lon: float
    category: str
    severity: Optional[str] = None
    description: Optional[str] = None
    media_ref: Optional[str] = None


class FieldReportOut(BaseModel):
    id: uuid.UUID
    user_id: Optional[uuid.UUID] = None
    lat: float
    lon: float
    category: str
    severity: Optional[str] = None
    description: Optional[str] = None
    media_ref: Optional[str] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
