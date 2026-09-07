import uuid
from datetime import datetime

from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from app.db.session import Base


class WeatherObservation(Base):
    __tablename__ = "weather_observations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    location_id = Column(UUID(as_uuid=True), ForeignKey("locations.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    rainfall = Column(Float, nullable=True)
    temperature = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)
    source = Column(String, nullable=True)
