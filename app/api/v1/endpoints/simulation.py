import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import update as sa_update
from sqlmodel import Session, select

from app.core.deps import get_current_user
from app.core.rate_limit import chat_limiter
from app.db.session import get_session
from app.models.incident import CallStatus, ChatMessage, Incident
from app.models.scenario import Scenario
from app.models.user import User
from app.schemas.simulation import ChatRequest, ChatResponse
from app.services.ai_service import generate_alertant_response

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/simulate/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    chat_limiter.check(str(current_user.id))
    incident = session.get(Incident, request.incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incidència no trobada")
    if incident.call_status != CallStatus.EN_CURS:
        raise HTTPException(
            status_code=409,
            detail="La trucada no està en curs" if incident.call_status == CallStatus.ESPERANT
                   else "La trucada ja ha estat finalitzada",
        )

    # Reconstruir historial desde la BD ordenado por timestamp
    db_messages = session.exec(
        select(ChatMessage)
        .where(ChatMessage.incident_id == request.incident_id)
        .order_by(ChatMessage.timestamp)
    ).all()

    history = [{"role": m.role, "content": m.content} for m in db_messages]
    history.append({"role": "user", "content": request.operator_message})

    instructions_ia = None
    location_exact  = None
    victim_status   = None
    initial_emotion = None
    if incident.scenario_id:
        scenario = session.get(Scenario, incident.scenario_id)
        if scenario:
            instructions_ia = scenario.instructions_ia
            location_exact  = scenario.location_exact
            victim_status   = scenario.victim_status
            initial_emotion = scenario.initial_emotion

    # Persistir el missatge de l'operador abans de cridar la IA
    user_msg = ChatMessage(incident_id=incident.id, role="user", content=request.operator_message)
    session.add(user_msg)
    session.flush()

    try:
        reply = generate_alertant_response(
            history, incident.type, instructions_ia,
            location_exact, victim_status, initial_emotion,
            lang=request.lang,
        )
    except Exception as exc:
        logger.exception("Error en generate_alertant_response (incident_id=%s): %s", request.incident_id, exc)
        session.commit()  # guardar el missatge de l'operador tot i l'error
        raise HTTPException(status_code=502, detail="El servei de simulació no està disponible en aquest moment.")

    # Primer missatge → registrar type_decided_at (UPDATE directe)
    if not db_messages and incident.type_decided_at is None:
        session.execute(
            sa_update(Incident)
            .where(Incident.id == incident.id)
            .values(type_decided_at=datetime.now(timezone.utc))
        )

    session.add(ChatMessage(incident_id=incident.id, role="assistant", content=reply))
    session.commit()

    return ChatResponse(content=reply)
