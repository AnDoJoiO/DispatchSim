from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.core.deps import get_current_user
from app.db.session import get_session
from app.models.incident import Incident
from app.models.intervention import InterventionData
from app.models.user import User
from app.schemas.intervention import InterventionRead, InterventionSave

router = APIRouter(prefix="/interventions", tags=["interventions"])


@router.post("", response_model=InterventionRead, status_code=201)
def save_intervention(
    payload: InterventionSave,
    session: Session = Depends(get_session),
    _: User = Depends(get_current_user),
):
    if not session.get(Incident, payload.incident_id):
        raise HTTPException(status_code=404, detail="Incidència no trobada")

    # Si ya existe una ficha para este incidente, la actualiza
    existing = session.exec(
        select(InterventionData).where(InterventionData.incident_id == payload.incident_id)
    ).first()

    if existing:
        for field, value in payload.model_dump(exclude={"incident_id"}).items():
            setattr(existing, field, value)
        session.add(existing)
    else:
        existing = InterventionData(**payload.model_dump())
        session.add(existing)

    session.commit()
    session.refresh(existing)
    return existing


@router.get("/{incident_id}", response_model=InterventionRead)
def get_intervention(
    incident_id: int,
    session: Session = Depends(get_session),
    _: User = Depends(get_current_user),
):
    data = session.exec(
        select(InterventionData).where(InterventionData.incident_id == incident_id)
    ).first()
    if not data:
        raise HTTPException(status_code=404, detail="Sense fitxa per a aquest incident")
    return data
