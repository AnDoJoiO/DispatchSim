from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.core.deps import require_role
from app.db.session import get_session
from app.models.incident import CallStatus, ChatMessage, Incident
from app.models.intervention import InterventionData
from app.models.scenario import Scenario
from app.models.user import User, UserRole
from app.schemas.history import CallDebriefingDetail, CallHistorySummary
from app.schemas.intervention import InterventionRead
from app.schemas.simulation import TranscriptMessage

router = APIRouter(prefix="/history", tags=["history"])


def _duration(start, end) -> int | None:
    if start and end:
        return max(0, int((end - start).total_seconds()))
    return None


@router.get("", response_model=List[CallHistorySummary])
def list_history(
    session: Session = Depends(get_session),
    _: User = Depends(require_role(UserRole.ADMIN, UserRole.FORMADOR)),
):
    """Llista de trucades finalitzades, ordenades de més recent a més antiga."""
    incidents = session.exec(
        select(Incident)
        .where(Incident.call_status == CallStatus.FINALITZADA)
        .order_by(Incident.call_end_at.desc())
    ).all()

    if not incidents:
        return []

    incident_ids = [i.id for i in incidents]

    # Batch: escenaris (evita N+1)
    scenario_ids = {i.scenario_id for i in incidents if i.scenario_id}
    scenarios: dict[int, str] = {}
    if scenario_ids:
        for sc in session.exec(select(Scenario).where(Scenario.id.in_(scenario_ids))).all():
            scenarios[sc.id] = sc.title

    # Batch: comptatge de missatges per incident
    msg_counts: dict[int, int] = {}
    for msg in session.exec(
        select(ChatMessage).where(ChatMessage.incident_id.in_(incident_ids))
    ).all():
        msg_counts[msg.incident_id] = msg_counts.get(msg.incident_id, 0) + 1

    return [
        CallHistorySummary(
            id=inc.id,
            type=inc.type,
            location=inc.location,
            priority=inc.priority,
            call_status=inc.call_status,
            call_start_at=inc.call_start_at,
            call_end_at=inc.call_end_at,
            duration_seconds=_duration(inc.call_start_at, inc.call_end_at),
            creator_id=inc.creator_id,
            operator_id=inc.operator_id,
            scenario_id=inc.scenario_id,
            scenario_title=scenarios.get(inc.scenario_id) if inc.scenario_id else None,
            message_count=msg_counts.get(inc.id, 0),
        )
        for inc in incidents
    ]


@router.get("/{call_id}", response_model=CallDebriefingDetail)
def get_debriefing(
    call_id: int,
    session: Session = Depends(get_session),
    _: User = Depends(require_role(UserRole.ADMIN, UserRole.FORMADOR)),
):
    """Debriefing complet: transcripció, mètriques temporals i fitxa d'intervenció."""
    incident = session.get(Incident, call_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Trucada no trobada")

    # Transcripció ordenada per timestamp
    messages = session.exec(
        select(ChatMessage)
        .where(ChatMessage.incident_id == call_id)
        .order_by(ChatMessage.timestamp)
    ).all()

    # Fitxa d'intervenció (pot no existir)
    intervention_row = session.exec(
        select(InterventionData).where(InterventionData.incident_id == call_id)
    ).first()

    # Títol de l'escenari
    scenario_title = None
    if incident.scenario_id:
        sc = session.get(Scenario, incident.scenario_id)
        if sc:
            scenario_title = sc.title

    # Mètriques temporals (derivades de columnes existents, sense migració)
    duration         = _duration(incident.call_start_at, incident.call_end_at)
    initial_response = _duration(incident.call_start_at, incident.type_decided_at)

    intervention_read = (
        InterventionRead(
            id=intervention_row.id,
            incident_id=intervention_row.incident_id,
            exact_address=intervention_row.exact_address,
            contact_phone=intervention_row.contact_phone,
            num_injured=intervention_row.num_injured,
            additional_risks=intervention_row.additional_risks,
            operator_notes=intervention_row.operator_notes,
            saved_at=intervention_row.saved_at,
        )
        if intervention_row else None
    )

    return CallDebriefingDetail(
        id=incident.id,
        type=incident.type,
        location=incident.location,
        priority=incident.priority,
        call_status=incident.call_status,
        call_start_at=incident.call_start_at,
        call_end_at=incident.call_end_at,
        duration_seconds=duration,
        creator_id=incident.creator_id,
        operator_id=incident.operator_id,
        scenario_id=incident.scenario_id,
        scenario_title=scenario_title,
        message_count=len(messages),
        initial_response_seconds=initial_response,
        transcript=[
            TranscriptMessage(role=m.role, content=m.content, timestamp=m.timestamp)
            for m in messages
        ],
        intervention=intervention_read,
    )
