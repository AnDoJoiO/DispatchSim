from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.user import UserRole


class UserCreate(BaseModel):
    username:   str      = Field(min_length=3, max_length=50, pattern=r'^[a-zA-Z0-9_]+$')
    password:   str      = Field(min_length=6)
    role:       UserRole = UserRole.OPERADOR
    expires_at: Optional[datetime] = None


class UserLogin(BaseModel):
    username: str
    password: str


class UserRead(BaseModel):
    id:         int
    username:   str
    role:       UserRole
    is_active:  bool
    expires_at: Optional[datetime] = None


class UserUpdate(BaseModel):
    is_active:  Optional[bool]     = None
    expires_at: Optional[datetime] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type:   str = "bearer"
    user:         UserRead
