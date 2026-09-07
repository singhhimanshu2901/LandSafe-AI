import uuid
from datetime import datetime

from sqlalchemy import Column, String, Float, DateTime
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry

from app.db.session import Base


class Location(Base):
    __tablename__ = "locations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    geometry = Column(Geometry(geometry_type="POINT", srid=4326), nullable=False)
    district = Column(String, nullable=True)
    village = Column(String, nullable=True)
    elevation = Column(Float, nullable=True)
    slope = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
