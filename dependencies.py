from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import get_db
from models import User, Admin
from auth_utils import verify_token

_bearer = HTTPBearer()
_bearer_optional = HTTPBearer(auto_error=False)


def get_current_user(
    db: Session = Depends(get_db),
    creds: HTTPAuthorizationCredentials = Depends(_bearer),
) -> User:
    payload = verify_token(creds.credentials)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = db.query(User).filter(User.id == payload.get("sub")).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def get_optional_user(
    db: Session = Depends(get_db),
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer_optional),
) -> User | None:
    if not creds:
        return None
    payload = verify_token(creds.credentials)
    if not payload:
        return None
    return db.query(User).filter(User.id == payload.get("sub")).first()


def get_current_admin(
    db: Session = Depends(get_db),
    creds: HTTPAuthorizationCredentials = Depends(_bearer),
) -> Admin:
    payload = verify_token(creds.credentials)
    if not payload or payload.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    admin = db.query(Admin).filter(Admin.id == payload.get("sub")).first()
    if not admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin not found")
    return admin
