from pydantic import BaseModel, Field

from app.models.user import UserRole


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6)
    role:     UserRole = UserRole.OPERADOR


class UserLogin(BaseModel):
    username: str
    password: str


class UserRead(BaseModel):
    id:        int
    username:  str
    role:      UserRole
    is_active: bool


class TokenResponse(BaseModel):
    access_token: str
    token_type:   str = "bearer"
    user:         UserRead
