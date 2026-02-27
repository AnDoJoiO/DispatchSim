from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class VictimStatus(str, Enum):
    CONSCIENTE   = "Consciente"
    INCONSCIENTE = "Inconsciente"
    GASP         = "GASP"


class InitialEmotion(str, Enum):
    CALMA     = "Calma"
    PANICO    = "Pánico"
    AGRESION  = "Agresión"


class ScenarioCreate(BaseModel):
    title:          str
    incident_type:  str
    base_location:  str
    location_exact: str
    victim_status:  VictimStatus
    initial_emotion: InitialEmotion
    instructions_ia: str  # instrucciones secretas para la IA


class ScenarioRead(BaseModel):
    id:              int
    title:           str
    incident_type:   str
    base_location:   str
    location_exact:  Optional[str]
    victim_status:   Optional[str]
    initial_emotion: Optional[str]
    creator_id:      Optional[int]
    created_at:      datetime
    # instructions_ia se omite deliberadamente — es información secreta del formador
