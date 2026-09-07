import uuid
from datetime import datetime

from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry

from app.db.session import Base


class FieldReport(Base):
    __tablename__ = "field_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=True)
    geometry = Column(Geometry(geometry_type="POINT", srid=4326), nullable=False)
    category = Column(String, nullable=True)
    severity = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    media_ref = Column(String, nullable=True)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
