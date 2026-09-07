from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import decode_access_token
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

ROLE_HIERARCHY = ["citizen", "field_officer", "district_admin", "state_admin", "super_admin"]


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    user = db.query(User).filter(User.id == payload["sub"]).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def require_role(min_role: str):
    def checker(user: User = Depends(get_current_user)) -> User:
        if ROLE_HIERARCHY.index(user.role) < ROLE_HIERARCHY.index(min_role):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role privileges")
        return user
    return checker
