from typing import Optional

from pydantic import BaseModel, Field, model_validator


class IncidentCreate(BaseModel):
    scenario_id:  Optional[int] = None
    type:         Optional[str] = None
    location:     Optional[str] = None
    description:  Optional[str] = None
    priority:     int = Field(..., ge=1, le=5)

    @model_validator(mode="after")
    def check_required_without_scenario(self) -> "IncidentCreate":
        if self.scenario_id is None:
            missing = [f for f in ("type", "location", "description") if not getattr(self, f)]
            if missing:
                raise ValueError(f"Camps obligatoris sense scenario_id: {missing}")
        return self
