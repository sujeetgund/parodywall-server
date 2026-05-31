from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    avatar: str
    turnstile_token: Optional[str] = None

class UserUpdate(BaseModel):
    alias: Optional[str] = None
    avatar: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    turnstile_token: Optional[str] = None

class RequestCodeRequest(BaseModel):
    email: EmailStr
    turnstile_token: Optional[str] = None

class VerifyCodeRequest(BaseModel):
    email: EmailStr
    code: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr
    turnstile_token: Optional[str] = None

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    code: str
    new_password: str

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    alias: str
    avatar: Optional[str]
    is_verified: bool
    is_superuser: bool = False
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Pin Schemas ---

class PinCreate(BaseModel):
    type: str  # 'text', 'image', 'both'
    text_content: Optional[str] = None
    image_url: Optional[str] = None
    bg_color: Optional[str] = None
    categories: list[str]

class PinResponse(BaseModel):
    id: UUID
    type: str
    text_content: Optional[str]
    image_url: Optional[str]
    bg_color: Optional[str]
    categories: list[str]
    author_alias: str
    author_avatar: Optional[str]
    is_superuser: bool
    user_id: UUID
    likes_count: int
    is_liked: bool
    is_saved: bool
    created_at: datetime

class ReportCreate(BaseModel):
    reason: Optional[str] = None
