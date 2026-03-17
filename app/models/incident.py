import enum
from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Column, ForeignKey, Integer
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
    creator_id:       Optional[int]     = Field(default=None, sa_column=Column(Integer, ForeignKey("app_user.id", ondelete="SET NULL"), index=True))
    operator_id:      Optional[int]     = Field(default=None, sa_column=Column(Integer, ForeignKey("app_user.id", ondelete="SET NULL"), index=True))
    scenario_id:      Optional[int]     = Field(default=None, sa_column=Column(Integer, ForeignKey("scenario.id", ondelete="SET NULL"), index=True))
    call_status:      CallStatus        = Field(default=CallStatus.ESPERANT)
    call_start_at:    Optional[datetime] = Field(default=None)
    type_decided_at:  Optional[datetime] = Field(default=None)
    call_end_at:      Optional[datetime] = Field(default=None)

    # Relationships — passive_deletes deixa que la BD faci CASCADE
    messages:     List["ChatMessage"]          = Relationship(back_populates="incident", passive_deletes="all")
    intervention: Optional["InterventionData"] = Relationship(back_populates="incident", passive_deletes="all")


class ChatMessage(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    incident_id: int = Field(sa_column=Column(Integer, ForeignKey("incident.id", ondelete="CASCADE"), nullable=False, index=True))
    role: str  # "user" | "assistant"
    content: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    incident: Optional[Incident] = Relationship(back_populates="messages")
