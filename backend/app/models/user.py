import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID

from app.db.session import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=True)
    phone = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="citizen")  # citizen, field_officer, district_admin, state_admin, super_admin
    language = Column(String, default="en")
    district = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
