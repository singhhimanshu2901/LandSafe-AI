import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from app.db.session import Base


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    risk_prediction_id = Column(UUID(as_uuid=True), ForeignKey("risk_predictions.id"), nullable=True)
    audience = Column(String, nullable=True)
    channel = Column(String, nullable=True)
    template = Column(String, nullable=True)
    sent_at = Column(DateTime, default=datetime.utcnow)
    delivery_status = Column(String, default="pending")
