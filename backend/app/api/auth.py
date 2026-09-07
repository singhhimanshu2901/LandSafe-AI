from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import UserRegister, UserOut, Token
from app.core.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

from fastapi.security import OAuth2PasswordBearer
from app.core.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user
    
def get_current_admin_user(user: User = Depends(get_current_user)) -> User:
    if user.role not in {"district_admin", "state_admin", "super_admin"}:
        raise HTTPException(status_code=403, detail="Not enough privileges")
    return user

ALLOWED_ROLES = {"citizen", "field_officer", "district_admin", "state_admin", "super_admin"}

@router.post("/register", response_model=UserOut)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    if payload.role not in ALLOWED_ROLES:
        raise HTTPException(status_code=400, detail=f"role must be one of {ALLOWED_ROLES}")
    existing = db.query(User).filter(User.phone == payload.phone).first()
    if existing:
        raise HTTPException(status_code=400, detail="Phone number already registered")
    user = User(
        name=payload.name, phone=payload.phone, hashed_password=hash_password(payload.password),
        role=payload.role, language=payload.language, district=payload.district,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.phone == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect phone or password")
    token = create_access_token({"sub": str(user.id), "role": user.role})
    return Token(access_token=token)
