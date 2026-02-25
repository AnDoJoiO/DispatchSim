from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.core.deps import get_current_user, require_role
from app.db.session import get_session
from app.models.scenario import Scenario
from app.models.user import User, UserRole
from app.schemas.scenario import ScenarioCreate, ScenarioRead

router = APIRouter(prefix="/scenarios", tags=["scenarios"])


@router.post("", response_model=ScenarioRead, status_code=201)
def create_scenario(
    payload: ScenarioCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role(UserRole.FORMADOR, UserRole.ADMIN)),
):
    scenario = Scenario(**payload.model_dump(), creator_id=current_user.id)
    session.add(scenario)
    session.commit()
    session.refresh(scenario)
    return scenario


@router.get("", response_model=List[ScenarioRead])
def list_scenarios(
    session: Session = Depends(get_session),
    _: User = Depends(get_current_user),
):
    return session.exec(select(Scenario)).all()


@router.delete("/{scenario_id}", status_code=204)
def delete_scenario(
    scenario_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role(UserRole.FORMADOR, UserRole.ADMIN)),
):
    scenario = session.get(Scenario, scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="Escenari no trobat")
    if scenario.creator_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Només pots eliminar els teus propis escenaris")
    session.delete(scenario)
    session.commit()
