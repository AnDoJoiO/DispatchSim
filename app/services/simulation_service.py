import logging
import re
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import update as sa_update
from sqlmodel import Session, select

from app.core.constants import DEFAULT_VOICE, VOICE_MAP
from app.models.incident import CallStatus, ChatMessage, Incident
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


_END_MARKER = "[FI]"

# Pattern that matches only punctuation, symbols, digits and whitespace (no letters)
_NON_WORD_RE = re.compile(r'^[\W\d_]+$', re.UNICODE)


def _is_empty_input(text: str) -> bool:
    """Return True if *text* is too empty or incoherent to be a real operator turn."""
    stripped = text.strip()
    if not stripped:
        return True
    # Only punctuation / symbols / digits — no letters at all
    if _NON_WORD_RE.match(stripped):
        return True
    # Remove all non-letter characters, then count words
    words = re.findall(r'[^\W\d_]+', stripped, re.UNICODE)
    return len(words) < 2


def process_chat(
    request: ChatRequest,
    incident: Incident,
    session: Session,
) -> tuple[str, str, bool]:
    """Executes one simulation chat turn.

    Loads history and scenario data, persists the user message, calls the AI,
    updates type_decided_at on the first exchange, persists the assistant reply,
    and returns (reply_text, elevenlabs_voice_id, call_ended).
    """
    logger.debug("process_chat started for incident_id=%s", incident.id)

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

    # Build in-memory history for the AI (DB persistence deferred to commit)
    if request.silent_trigger:
        # Store a neutral marker in DB; send the real prompt to the AI so it
        # reacts to the silence while preserving the user/assistant alternation.
        history.append({"role": "user", "content": _SILENCE_PROMPT})
        user_msg = ChatMessage(incident_id=incident.id, role="user", content="[silenci]")
    else:
        if _is_empty_input(request.operator_message):
            raise HTTPException(status_code=422, detail="Operator message too short or empty")
        history.append({"role": "user", "content": request.operator_message})
        user_msg = ChatMessage(incident_id=incident.id, role="user", content=request.operator_message)

    # Limit context sent to the AI: keep only the last 20 messages
    # (the current user message is already the last element)
    _MAX_HISTORY = 20
    if len(history) > _MAX_HISTORY:
        history = history[-_MAX_HISTORY:]

    logger.debug(
        "Calling AI for incident_id=%s with %d messages",
        incident.id, len(history),
    )

    try:
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
    except Exception:
        logger.error(
            "AI call failed for incident_id=%s", incident.id, exc_info=True,
        )
        raise

    # First exchange → register when the incident type was confirmed
    if not db_messages and incident.type_decided_at is None:
        session.execute(
            sa_update(Incident)
            .where(Incident.id == incident.id)
            .values(type_decided_at=datetime.now(timezone.utc))
        )

    # Detect end-of-call marker and strip it from the visible reply
    call_ended = _END_MARKER in reply
    clean_reply = reply.replace(_END_MARKER, "").strip()

    # If AI signals end of call, finalize it
    if call_ended:
        logger.info("Call ended for incident_id=%s", incident.id)
        session.execute(
            sa_update(Incident)
            .where(Incident.id == incident.id)
            .values(
                call_status=CallStatus.FINALITZADA,
                call_end_at=datetime.now(timezone.utc),
            )
        )

    # Persist both messages atomically — if AI failed, nothing is written
    session.add(user_msg)
    session.add(ChatMessage(incident_id=incident.id, role="assistant", content=clean_reply))
    session.commit()

    voice = VOICE_MAP.get(initial_emotion if initial_emotion else "", DEFAULT_VOICE)
    return clean_reply, voice, call_ended
