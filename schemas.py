from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class RequestCodeRequest(BaseModel):
    email: EmailStr

class VerifyCodeRequest(BaseModel):
    email: EmailStr
    code: str

class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    alias: str
    avatar: Optional[str]
    is_verified: bool
    created_at: datetime

    model_config = {"from_attributes": True}
