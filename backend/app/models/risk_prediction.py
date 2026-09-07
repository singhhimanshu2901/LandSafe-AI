import uuid
from datetime import datetime

from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from app.db.session import Base


class RiskPrediction(Base):
    __tablename__ = "risk_predictions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    location_id = Column(UUID(as_uuid=True), ForeignKey("locations.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    probability = Column(Float, nullable=True)
    score = Column(Float, nullable=True)
    level = Column(String, nullable=True)
    model_version = Column(String, nullable=True)
