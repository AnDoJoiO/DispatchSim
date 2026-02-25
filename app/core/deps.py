import logging
from datetime import datetime, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlmodel import Session

from app.core.security import decode_token
from app.db.session import get_session
from app.models.user import User, UserRole

bearer_scheme = HTTPBearer()
logger = logging.getLogger(__name__)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    session: Session = Depends(get_session),
) -> User:
    token = credentials.credentials
    try:
        payload = decode_token(token)
        raw = payload.get("sub")
        if raw is None:
            raise ValueError
        user_id = int(raw)
    except (JWTError, ValueError):
        logger.warning("AUTH_INVALID_TOKEN")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invàlid o expirat",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = session.get(User, user_id)
    if not user or not user.is_active:
        logger.warning("AUTH_DENIED_INACTIVE user_id=%s", user_id)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuari no trobat o inactiu",
        )
    if user.expires_at and datetime.now(timezone.utc) > user.expires_at.replace(tzinfo=timezone.utc):
        logger.warning("AUTH_DENIED_EXPIRED user_id=%s username=%r", user.id, user.username)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Compte caducat",
        )
    return user


def require_role(*roles: UserRole):
    """Dependència de fàbrica: exigeix que l'usuari tingui un dels rols indicats."""
    def _check(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            logger.warning("ACCESS_DENIED user_id=%s role=%r required=%s", current_user.id, current_user.role, [r.value for r in roles])
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Es requereix rol: {[r.value for r in roles]}",
            )
        return current_user
    return _check
