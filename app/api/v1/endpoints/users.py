from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.core.deps import require_role
from app.core.security import hash_password
from app.db.session import get_session
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserRead

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=List[UserRead])
def list_users(
    session: Session = Depends(get_session),
    _: User = Depends(require_role(UserRole.ADMIN, UserRole.FORMADOR)),
):
    return session.exec(select(User)).all()


@router.post("", response_model=UserRead, status_code=201)
def create_user(
    payload: UserCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.FORMADOR)),
):
    if current_user.role == UserRole.FORMADOR and payload.role != UserRole.OPERADOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Un formador només pot crear operadors",
        )
    if session.exec(select(User).where(User.username == payload.username)).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El nom d'usuari ja existeix",
        )
    user = User(
        username=payload.username,
        hashed_password=hash_password(payload.password),
        role=payload.role,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
