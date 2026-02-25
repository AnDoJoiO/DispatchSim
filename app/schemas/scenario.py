from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ScenarioCreate(BaseModel):
    title:               str
    incident_type:       str
    base_location:       str
    initial_description: str
    instructions_ia:     str  # instrucciones secretas para la IA


class ScenarioRead(BaseModel):
    id:                  int
    title:               str
    incident_type:       str
    base_location:       str
    initial_description: str
    creator_id:          Optional[int]
    created_at:          datetime
    # instructions_ia se omite deliberadamente — es información secreta del formador
