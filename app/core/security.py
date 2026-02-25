from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings


# ── Hashing ──────────────────────────────────────────────────────────────────

def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    hashed_bytes = hashed.encode("utf-8") if isinstance(hashed, str) else hashed
    return bcrypt.checkpw(plain.encode("utf-8"), hashed_bytes)


# ── JWT ───────────────────────────────────────────────────────────────────────

def create_access_token(data: dict) -> str:
    payload = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload["exp"] = expire
    # sub debe ser string según RFC 7519 (python-jose lo valida)
    if "sub" in payload:
        payload["sub"] = str(payload["sub"])
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    """Decodifica y valida el token. Lanza JWTError si es inválido o expirado."""
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
