import uuid
from datetime import datetime

from sqlalchemy import Column, String, Float, DateTime
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry

from app.db.session import Base


class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sensor_id = Column(String, nullable=False, index=True)
    geometry = Column(Geometry(geometry_type="POINT", srid=4326), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    soil_moisture = Column(Float, nullable=True)
    battery = Column(Float, nullable=True)
    quality = Column(String, nullable=True)
