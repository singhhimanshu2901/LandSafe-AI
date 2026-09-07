import uuid

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry

from app.db.session import Base


class Infrastructure(Base):
    __tablename__ = "infrastructure"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    geometry = Column(Geometry(geometry_type="POINT", srid=4326), nullable=False)
    type = Column(String, nullable=True)
    name = Column(String, nullable=True)
    importance = Column(String, nullable=True)
