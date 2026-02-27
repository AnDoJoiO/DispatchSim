from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from sqlalchemy import Column, String
from sqlmodel import Field, SQLModel


class VictimStatus(str, Enum):
    CONSCIENTE   = "Consciente"
    INCONSCIENTE = "Inconsciente"
    GASP         = "GASP"


class InitialEmotion(str, Enum):
    CALMA    = "Calma"
    PANICO   = "Pánico"
    AGRESION = "Agresión"


class Scenario(SQLModel, table=True):
    id:              Optional[int] = Field(default=None, primary_key=True)
    title:           str
    incident_type:   str
    base_location:   str
    location_exact:  Optional[str]          = Field(default=None)
    victim_status:   Optional[VictimStatus] = Field(default=None, sa_column=Column(String, nullable=True))
    initial_emotion: Optional[InitialEmotion] = Field(default=None, sa_column=Column(String, nullable=True))
    instructions_ia: str                    # secreto — solo llega a la IA, nunca al frontend
    creator_id:      Optional[int]          = Field(default=None, foreign_key="app_user.id")
    created_at:      datetime               = Field(default_factory=lambda: datetime.now(timezone.utc))
