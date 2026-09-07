import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry

from app.db.session import Base


class Road(Base):
    __tablename__ = "roads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    geometry = Column(Geometry(geometry_type="LINESTRING", srid=4326), nullable=False)
    road_type = Column(String, nullable=True)
    status = Column(String, nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow)
