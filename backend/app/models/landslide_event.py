import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry

from app.db.session import Base


class LandslideEvent(Base):
    __tablename__ = "landslide_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    geometry = Column(Geometry(geometry_type="POINT", srid=4326), nullable=False)
    event_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    severity = Column(String, nullable=True)
    source = Column(String, nullable=True)
    verification_status = Column(String, default="unverified")
