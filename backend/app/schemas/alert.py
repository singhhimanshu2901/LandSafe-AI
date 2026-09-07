import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AlertCreate(BaseModel):
    risk_prediction_id: Optional[uuid.UUID] = None
    audience: str
    channel: str  # sms | push | dashboard
    template: str


class AlertOut(BaseModel):
    id: uuid.UUID
    risk_prediction_id: Optional[uuid.UUID] = None
    audience: str
    channel: str
    template: str
    sent_at: datetime
    delivery_status: str

    class Config:
        from_attributes = True
