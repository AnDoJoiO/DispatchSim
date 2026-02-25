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
    if incident.scenario_id:
        scenario = session.get(Scenario, incident.scenario_id)
        if scenario:
            instructions_ia = scenario.instructions_ia

    try:
        reply = generate_alertant_response(history, incident.type, instructions_ia)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Error de la IA: {exc}")

    # Primer missatge → registrar type_decided_at (UPDATE directe)
    if not db_messages and incident.type_decided_at is None:
        session.execute(
            sa_update(Incident)
            .where(Incident.id == incident.id)
            .values(type_decided_at=datetime.now(timezone.utc))
        )

    # Persistir mensaje del operador y respuesta de la IA
    session.add(ChatMessage(incident_id=incident.id, role="user",      content=request.operator_message))
    session.add(ChatMessage(incident_id=incident.id, role="assistant", content=reply))
    session.commit()

    return ChatResponse(content=reply)
