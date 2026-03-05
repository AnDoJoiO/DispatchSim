from datetime import datetime

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    incident_id: int
    operator_message: str = Field(default="", max_length=1000)
    lang: str = 'ca'
    silent_trigger: bool = False


class ChatResponse(BaseModel):
    role: str = "assistant"
    content: str
    voice: str = "nova"


class TranscriptMessage(BaseModel):
    role: str
    content: str
    timestamp: datetime
