from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


class Scenario(SQLModel, table=True):
    id:              Optional[int] = Field(default=None, primary_key=True)
    title:           str
    incident_type:   str
    base_location:   str
    location_exact:  Optional[str] = Field(default=None)
    victim_status:   Optional[str] = Field(default=None)
    initial_emotion: Optional[str] = Field(default=None)
    instructions_ia: str           # secreto — solo llega a la IA, nunca al frontend
    creator_id:      Optional[int] = Field(default=None, foreign_key="app_user.id")
    created_at:      datetime      = Field(default_factory=lambda: datetime.now(timezone.utc))
