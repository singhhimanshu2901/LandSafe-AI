import uuid
from typing import Optional

from pydantic import BaseModel


class UserRegister(BaseModel):
    name: Optional[str] = None
    phone: str
    password: str
    role: str = "citizen"
    language: str = "en"
    district: Optional[str] = None


class UserOut(BaseModel):
    id: uuid.UUID
    name: Optional[str] = None
    phone: str
    role: str
    language: str
    district: Optional[str] = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
