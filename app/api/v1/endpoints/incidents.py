from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import update as sa_update
from sqlmodel import Session, select

from app.core.deps import get_current_user
from app.db.session import get_session
from app.models.incident import CallStatus, ChatMessage, Incident
from app.models.scenario import Scenario
from app.models.user import User
from app.schemas.incident import IncidentCreate
from app.schemas.simulation import TranscriptMessage

router = APIRouter()


@router.post("/incidents", response_model=Incident, status_code=201)
def create_incident(
    payload: IncidentCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    now = datetime.now(timezone.utc)
    if payload.scenario_id:
        scenario = session.get(Scenario, payload.scenario_id)
        if not scenario:
            raise HTTPException(status_code=404, detail="Escenari no trobat")
        parts = [scenario.location_exact or scenario.base_location]
        if scenario.victim_status:
            parts.append(f"Víctima: {scenario.victim_status}")
        if scenario.initial_emotion:
            parts.append(f"Emoció alertant: {scenario.initial_emotion}")
        incident = Incident(
            scenario_id=scenario.id,
            type=scenario.incident_type,
            location=scenario.base_location,
            description=" · ".join(parts),
            priority=payload.priority,
            creator_id=current_user.id,
            call_status=CallStatus.EN_CURS,
            call_start_at=now,
        )
    else:
        incident = Incident(
            type=payload.type,
            location=payload.location,
            description=payload.description,
            priority=payload.priority,
            creator_id=current_user.id,
            call_status=CallStatus.EN_CURS,
            call_start_at=now,
        )
    session.add(incident)
    session.commit()
    session.refresh(incident)
    return incident


@router.get("/incidents", response_model=List[Incident])
def list_incidents(
    session: Session = Depends(get_session),
    _: User = Depends(get_current_user),
):
    return session.exec(select(Incident)).all()


@router.get("/incidents/{incident_id}", response_model=Incident)
def get_incident(
    incident_id: int,
    session: Session = Depends(get_session),
    _: User = Depends(get_current_user),
):
    incident = session.get(Incident, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incidencia no encontrada")
    return incident


@router.delete("/incidents/{incident_id}", status_code=204)
def delete_incident(
    incident_id: int,
    session: Session = Depends(get_session),
    _: User = Depends(get_current_user),
):
    incident = session.get(Incident, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incidencia no encontrada")
    session.delete(incident)
    session.commit()


@router.patch("/incidents/{incident_id}/call", response_model=Incident)
def end_call(
    incident_id: int,
    session: Session = Depends(get_session),
    _: User = Depends(get_current_user),
):
    """Finalitza la trucada: UPDATE directe SQL sense carregar l'objecte sencer."""
    incident = session.get(Incident, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incidència no trobada")
    if incident.call_status == CallStatus.FINALITZADA:
        raise HTTPException(status_code=409, detail="La trucada ja està finalitzada")

    session.execute(
        sa_update(Incident)
        .where(Incident.id == incident_id)
        .values(
            call_status=CallStatus.FINALITZADA,
            call_end_at=datetime.now(timezone.utc),
        )
    )
    session.commit()
    session.refresh(incident)
    return incident


@router.get("/incidents/{incident_id}/transcript", response_model=List[TranscriptMessage])
def get_transcript(
    incident_id: int,
    session: Session = Depends(get_session),
    _: User = Depends(get_current_user),
):
    if not session.get(Incident, incident_id):
        raise HTTPException(status_code=404, detail="Incidencia no encontrada")
    messages = session.exec(
        select(ChatMessage)
        .where(ChatMessage.incident_id == incident_id)
        .order_by(ChatMessage.timestamp)
    ).all()
    return [TranscriptMessage(role=m.role, content=m.content, timestamp=m.timestamp) for m in messages]
