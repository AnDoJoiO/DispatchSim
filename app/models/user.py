import enum
from typing import Optional

from sqlmodel import Field, SQLModel


class UserRole(str, enum.Enum):
    ADMIN    = "admin"
    FORMADOR = "formador"
    OPERADOR = "operador"


class User(SQLModel, table=True):
    __tablename__ = "app_user"

    id:              Optional[int] = Field(default=None, primary_key=True)
    username:        str           = Field(unique=True, index=True)
    hashed_password: str
    role:            UserRole      = Field(default=UserRole.OPERADOR)
    is_active:       bool          = Field(default=True)
