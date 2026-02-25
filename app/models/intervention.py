from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.incident import Incident


class InterventionData(SQLModel, table=True):
    id:                 Optional[int] = Field(default=None, primary_key=True)
    incident_id:        int           = Field(foreign_key="incident.id", unique=True)
    exact_address:      str           = ""
    contact_phone:      str           = ""
    num_injured:        int           = 0
    additional_risks:   str           = ""   # CSV: "Gas,Electricitat,Químics"
    operator_notes:     str           = ""
    saved_at:           datetime      = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relationship (lazy, no DB change)
    incident: Optional["Incident"] = Relationship(back_populates="intervention")
