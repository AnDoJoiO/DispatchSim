from datetime import datetime

from pydantic import BaseModel


class InterventionSave(BaseModel):
    incident_id:       int
    exact_address:     str = ""
    contact_phone:     str = ""
    num_injured:       int = 0
    additional_risks:  str = ""
    operator_notes:    str = ""


class InterventionRead(BaseModel):
    id:                int
    incident_id:       int
    exact_address:     str
    contact_phone:     str
    num_injured:       int
    additional_risks:  str
    operator_notes:    str
    saved_at:          datetime
