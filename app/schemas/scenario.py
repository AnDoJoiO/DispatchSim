from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.scenario import InitialEmotion, VictimStatus


class ScenarioCreate(BaseModel):
    title:           str
    incident_type:   str
    base_location:   str
    location_exact:  Optional[str] = None
    victim_status:   Optional[VictimStatus] = None
    initial_emotion: Optional[InitialEmotion] = None
    instructions_ia: str = Field(max_length=2000)  # instrucciones secretas para la IA


class ScenarioRead(BaseModel):
    id:              int
    title:           str
    incident_type:   str
    base_location:   str
    location_exact:  Optional[str]
    victim_status:   Optional[VictimStatus]
    initial_emotion: Optional[InitialEmotion]
    creator_id:      Optional[int]
    created_at:      datetime
    # instructions_ia se omite deliberadamente — es información secreta del formador
