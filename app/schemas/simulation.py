from datetime import datetime

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    incident_id: int
    operator_message: str = Field(max_length=1000)
    lang: str = 'ca'


class ChatResponse(BaseModel):
    role: str = "assistant"
    content: str


class TranscriptMessage(BaseModel):
    role: str
    content: str
    timestamp: datetime
