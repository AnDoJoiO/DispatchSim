import asyncio
import logging
from datetime import datetime, timezone

from sqlalchemy import delete as sa_delete, or_
from sqlmodel import Session, select

from app.db.session import engine
from app.models.incident import ChatMessage, Incident
from app.models.intervention import InterventionData
from app.models.user import User

logger = logging.getLogger(__name__)

CLEANUP_INTERVAL_SECONDS = 3600  # cada hora


def run_expired_user_cleanup() -> int:
    """
    Borra tots els usuaris expirats (expires_at <= ara) i totes les dades
    associades (incidents, missatges, intervencions).
    Retorna el nombre d'usuaris eliminats.
    """
    with Session(engine) as session:
        now = datetime.now(timezone.utc)

        expired_users = [
            u for u in session.exec(
                select(User).where(User.expires_at.is_not(None))
            ).all()
            if u.expires_at.replace(tzinfo=timezone.utc) <= now
        ]

        if not expired_users:
            return 0

        user_ids = [u.id for u in expired_users]

        # Incidents on l'usuari és creador o operador
        incident_ids = [
            inc.id for inc in session.exec(
                select(Incident).where(
                    or_(
                        Incident.creator_id.in_(user_ids),
                        Incident.operator_id.in_(user_ids),
                    )
                )
            ).all()
        ]

        if incident_ids:
            session.execute(
                sa_delete(InterventionData).where(InterventionData.incident_id.in_(incident_ids))
            )
            session.execute(
                sa_delete(ChatMessage).where(ChatMessage.incident_id.in_(incident_ids))
            )
            session.execute(
                sa_delete(Incident).where(Incident.id.in_(incident_ids))
            )

        session.execute(sa_delete(User).where(User.id.in_(user_ids)))
        session.commit()

        logger.info(
            "Cleanup: %d usuari(s) expirat(s) eliminat(s) · %d incident(s) eliminat(s)",
            len(user_ids), len(incident_ids),
        )
        return len(user_ids)


async def expired_user_cleanup_loop() -> None:
    """Loop de background: executa la neteja just en arrencar i cada hora."""
    await asyncio.sleep(5)  # espera que la BD estigui llesta
    while True:
        try:
            run_expired_user_cleanup()
        except Exception:
            logger.exception("Error durant la neteja d'usuaris expirats")
        await asyncio.sleep(CLEANUP_INTERVAL_SECONDS)
