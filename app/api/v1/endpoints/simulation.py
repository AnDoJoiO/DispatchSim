import logging
import re

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.core.deps import get_current_user
from app.core.rate_limit import chat_limiter
from app.db.session import get_session
from app.models.incident import CallStatus, ChatMessage, Incident
from app.models.user import User
from app.schemas.simulation import ChatRequest, ChatResponse
from app.services.simulation_service import process_chat

router = APIRouter()
logger = logging.getLogger(__name__)

_WORD_RE = re.compile(r'\w{2,}', re.UNICODE)
_MIN_REAL_WORDS = 2


@router.post("/simulate/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if not request.silent_trigger:
        chat_limiter.check(str(current_user.id))
        # Descartar missatges amb menys de 2 paraules reals (soroll transcrit)
        real_words = _WORD_RE.findall(request.operator_message)
        if len(real_words) < _MIN_REAL_WORDS:
            logger.debug("Chat rejected (noise, %d words): %r", len(real_words), request.operator_message)
            raise HTTPException(status_code=422, detail="Missatge massa curt o sense contingut")
    else:
        # Validate silent_trigger: only allowed if last message is from assistant
        last_msg = session.exec(
            select(ChatMessage)
            .where(ChatMessage.incident_id == request.incident_id)
            .order_by(ChatMessage.timestamp.desc())  # type: ignore[union-attr]
        ).first()
        if last_msg and last_msg.role != "assistant":
            raise HTTPException(status_code=409, detail="silent_trigger requereix que l'últim missatge sigui de l'assistant")

    incident = session.get(Incident, request.incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incidència no trobada")
    if incident.call_status != CallStatus.EN_CURS:
        raise HTTPException(
            status_code=409,
            detail="La trucada no està en curs" if incident.call_status == CallStatus.ESPERANT
                   else "La trucada ja ha estat finalitzada",
        )

    try:
        reply, voice, call_ended = process_chat(request, incident, session)
    except Exception as exc:
        logger.exception("Error en process_chat (incident_id=%s): %s", request.incident_id, exc)
        err_type = type(exc).__name__
        raise HTTPException(status_code=502, detail=f"Simulació no disponible ({err_type})")

    return ChatResponse(content=reply, voice=voice, call_ended=call_ended)
