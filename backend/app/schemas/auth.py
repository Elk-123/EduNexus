from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserCreate(UserBase):
    email: EmailStr
    username: str
    password: str

class UserResponse(UserBase):
    id: UUID
    onboarding_completed: bool
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse