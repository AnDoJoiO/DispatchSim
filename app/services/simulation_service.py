import logging
from datetime import datetime, timezone

from sqlalchemy import update as sa_update
from sqlmodel import Session, select

from app.core.constants import DEFAULT_VOICE, VOICE_MAP
from app.models.incident import ChatMessage, Incident
from app.models.scenario import Scenario
from app.schemas.simulation import ChatRequest
from app.services.ai_service import generate_alertant_response

logger = logging.getLogger(__name__)

_SILENCE_PROMPT = (
    "[L'operador no ha respost durant uns segons. "
    "Reacciona de forma breu i natural: expressa nerviosisme o impaciència, "
    "demana si segueix en línia o si ve ajuda. "
    "1-2 frases màxim. No repeteixis el que ja has dit.]"
)


def process_chat(
    request: ChatRequest,
    incident: Incident,
    session: Session,
) -> tuple[str, str]:
    """Executes one simulation chat turn.

    Loads history and scenario data, persists the user message, calls the AI,
    updates type_decided_at on the first exchange, persists the assistant reply,
    and returns (reply_text, elevenlabs_voice_id).
    """
    # Load history ordered by timestamp
    db_messages = session.exec(
        select(ChatMessage)
        .where(ChatMessage.incident_id == incident.id)
        .order_by(ChatMessage.timestamp)
    ).all()

    history = [{"role": m.role, "content": m.content} for m in db_messages]

    # Load scenario overrides if the incident is linked to one
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

    # Persist user message and append to in-memory history
    if request.silent_trigger:
        # Store a neutral marker in DB; send the real prompt to the AI so it
        # reacts to the silence while preserving the user/assistant alternation.
        history.append({"role": "user", "content": _SILENCE_PROMPT})
        session.add(ChatMessage(incident_id=incident.id, role="user", content="[silenci]"))
    else:
        history.append({"role": "user", "content": request.operator_message})
        session.add(ChatMessage(incident_id=incident.id, role="user", content=request.operator_message))
    session.flush()

    reply = generate_alertant_response(
        history,
        incident.type,
        instructions_ia,
        location=location_exact or incident.location,
        victim_status=victim_status,
        initial_emotion=initial_emotion,
        description=incident.description,
        lang=request.lang,
    )

    # First exchange → register when the incident type was confirmed
    if not db_messages and incident.type_decided_at is None:
        session.execute(
            sa_update(Incident)
            .where(Incident.id == incident.id)
            .values(type_decided_at=datetime.now(timezone.utc))
        )

    session.add(ChatMessage(incident_id=incident.id, role="assistant", content=reply))
    session.commit()

    voice = VOICE_MAP.get(initial_emotion.value if initial_emotion else "", DEFAULT_VOICE)
    return reply, voice
