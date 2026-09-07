from datetime import datetime, timedelta

from jose import jwt, JWTError
from passlib.context import CryptContext

from app.core.config import settings

import bcrypt

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 12


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()

def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode(), hashed.encode())
    except:
        return False


def create_access_token(data: dict, expires_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str):
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None
