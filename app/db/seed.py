"""
Seed inicial: crea l'usuari admin si no n'hi ha cap a la BD.
S'executa a l'arrencada quan ADMIN_USERNAME i ADMIN_PASSWORD estan definits.
"""
import logging

from sqlmodel import Session, select

from app.core.security import hash_password
from app.db.session import engine
from app.models.user import User, UserRole

logger = logging.getLogger(__name__)


def seed_admin(username: str, password: str) -> None:
    with Session(engine) as session:
        existing = session.exec(
            select(User).where(User.role == UserRole.ADMIN)
        ).first()
        if existing:
            logger.info("Seed: ja existeix un admin ('%s'), s'omet.", existing.username)
            return
        admin = User(
            username=username,
            hashed_password=hash_password(password),
            role=UserRole.ADMIN,
            is_active=True,
        )
        session.add(admin)
        session.commit()
        logger.info("Seed: admin '%s' creat correctament.", username)
