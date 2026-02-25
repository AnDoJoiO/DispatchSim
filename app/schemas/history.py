from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from app.models.incident import CallStatus
from app.schemas.intervention import InterventionRead
from app.schemas.simulation import TranscriptMessage


class CallHistorySummary(BaseModel):
    """Vista resumida d'una trucada finalitzada per a la taula del historial."""
    id:               int
    type:             str
    location:         str
    priority:         int
    call_status:      CallStatus
    call_start_at:    Optional[datetime]
    call_end_at:      Optional[datetime]
    duration_seconds: Optional[int]       # call_end_at - call_start_at
    creator_id:       Optional[int]
    operator_id:      Optional[int]
    scenario_id:      Optional[int]
    scenario_title:   Optional[str]
    message_count:    int


class CallDebriefingDetail(CallHistorySummary):
    """Detall complet d'una trucada: transcripció, mètriques i fitxa d'intervenció."""
    initial_response_seconds: Optional[int]   # type_decided_at - call_start_at
    transcript:               List[TranscriptMessage]
    intervention:             Optional[InterventionRead]
