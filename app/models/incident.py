import enum
from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.intervention import InterventionData


class CallStatus(str, enum.Enum):
    ESPERANT    = "esperant"
    EN_CURS     = "en_curs"
    FINALITZADA = "finalitzada"


class Incident(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    type: str
    location: str
    description: str
    priority: int
    created_at:       datetime          = Field(default_factory=lambda: datetime.now(timezone.utc))
    creator_id:       Optional[int]     = Field(default=None, foreign_key="app_user.id")
    operator_id:      Optional[int]     = Field(default=None, foreign_key="app_user.id")
    scenario_id:      Optional[int]     = Field(default=None, foreign_key="scenario.id")
    call_status:      CallStatus        = Field(default=CallStatus.ESPERANT)
    call_start_at:    Optional[datetime] = Field(default=None)
    type_decided_at:  Optional[datetime] = Field(default=None)
    call_end_at:      Optional[datetime] = Field(default=None)

    # Relationships (lazy, no DB change)
    messages:     List["ChatMessage"]          = Relationship(back_populates="incident")
    intervention: Optional["InterventionData"] = Relationship(back_populates="incident")


class ChatMessage(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    incident_id: int = Field(foreign_key="incident.id")
    role: str  # "user" | "assistant"
    content: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    incident: Optional[Incident] = Relationship(back_populates="messages")
