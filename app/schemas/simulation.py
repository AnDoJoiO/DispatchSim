from datetime import datetime

from pydantic import BaseModel


class ChatRequest(BaseModel):
    incident_id: int
    operator_message: str
    lang: str = 'ca'


class ChatResponse(BaseModel):
    role: str = "assistant"
    content: str


class TranscriptMessage(BaseModel):
    role: str
    content: str
    timestamp: datetime
