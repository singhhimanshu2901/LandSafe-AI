import uuid
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


class RiskFactor(BaseModel):
    feature: str
    contribution: float


class RiskPredictionOut(BaseModel):
    id: uuid.UUID
    location_id: uuid.UUID
    timestamp: datetime
    probability: Optional[float] = None
    score: Optional[float] = None
    level: Optional[str] = None
    model_version: Optional[str] = None

    class Config:
        from_attributes = True


class RiskPredictionDetail(RiskPredictionOut):
    top_factors: List[RiskFactor] = []
