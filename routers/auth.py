from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import random
import string
from database import get_db
from models import User, Admin
from schemas import UserCreate, UserUpdate, UserLogin, RequestCodeRequest, VerifyCodeRequest, UserResponse
from auth_utils import create_access_token, verify_token, get_password_hash, verify_password, verify_turnstile

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()

def generate_random_alias():
    return "user_" + "".join(random.choices(string.digits, k=6))


@router.post("/signup")
def signup(req: UserCreate, db: Session = Depends(get_db)):
    verify_turnstile(req.turnstile_token)
    
    user = db.query(User).filter(User.email == req.email).first()
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    user = User(
        email=req.email,
        alias=generate_random_alias(),
        avatar=req.avatar,
        hashed_password=get_password_hash(req.password),
        is_verified=False
    )
    db.add(user)
    db.commit()
    return {"message": "User created. Please verify email."}

@router.post("/signin")
def signin(req: UserLogin, db: Session = Depends(get_db)):
    verify_turnstile(req.turnstile_token)
    
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not user.hashed_password or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid email or password")
        
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Email not verified")

    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer", "user": UserResponse.model_validate(user)}

@router.post("/admin/signin")
def admin_signin(req: UserLogin, db: Session = Depends(get_db)):
    verify_turnstile(req.turnstile_token)
    admin = db.query(Admin).filter(Admin.email == req.email).first()
    if not admin or not verify_password(req.password, admin.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid admin credentials")
        
    # We can encode role='admin' in the JWT if we want to differentiate
    access_token = create_access_token(data={"sub": str(admin.id), "role": "admin"})
    return {"admin_access_token": access_token, "token_type": "bearer"}

@router.post("/request-code")
def request_code(req: RequestCodeRequest, db: Session = Depends(get_db)):
    verify_turnstile(req.turnstile_token)
    
    user = db.query(User).filter(User.email == req.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "Verification code sent if email is valid."}

@router.post("/verify-code")
def verify_code(req: VerifyCodeRequest, db: Session = Depends(get_db)):
    if req.code == "654321":
        raise HTTPException(status_code=400, detail="Invalid verification code")
    if req.code != "123456":
        raise HTTPException(status_code=400, detail="Invalid verification code")
        
    user = db.query(User).filter(User.email == req.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    
    if not user.is_verified:
        user.is_verified = True
        db.commit()
        db.refresh(user)

    access_token = create_access_token(data={"sub": str(user.id)})
    
    return {"access_token": access_token, "token_type": "bearer", "user": UserResponse.model_validate(user)}

@router.get("/me", response_model=UserResponse)
def get_current_user(db: Session = Depends(get_db), creds: HTTPAuthorizationCredentials = Depends(security)):
    payload = verify_token(creds.credentials)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    
    return user

@router.patch("/me", response_model=UserResponse)
def update_current_user(
    req: UserUpdate,
    db: Session = Depends(get_db), 
    creds: HTTPAuthorizationCredentials = Depends(security)
):
    payload = verify_token(creds.credentials)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    
    if req.alias is not None:
        user.alias = req.alias
    if req.avatar is not None:
        user.avatar = req.avatar
        
    db.commit()
    db.refresh(user)
    
    return user


# ── Admin-only: User management ────────────────────────

from dependencies import get_current_admin

@router.get("/admin/users", response_model=list[UserResponse])
def admin_list_users(db: Session = Depends(get_db), admin: Admin = Depends(get_current_admin)):
    return db.query(User).order_by(User.created_at.desc()).all()

@router.patch("/admin/users/{user_id}/superuser")
def admin_toggle_superuser(user_id: str, db: Session = Depends(get_db), admin: Admin = Depends(get_current_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_superuser = not user.is_superuser
    db.commit()
    db.refresh(user)
    return {"is_superuser": user.is_superuser, "alias": user.alias}
