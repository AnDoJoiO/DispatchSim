import logging

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel

import httpx

from app.core.config import settings
from app.core.constants import EL_DEFAULT_SETTINGS, EL_TO_OAI_VOICE, EL_VOICE_SETTINGS
from app.core.deps import get_current_user
from app.core.rate_limit import transcribe_limiter, tts_limiter
from app.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/voice", tags=["voice"])

# Frases que Whisper alucina con silencio o ruido de fondo
_WHISPER_HALLUCINATIONS = {
    "amara.org", "amara", "subtítulos", "subtitulado", "subtitles",
    "transcripción", "transcription", "sous-titres", "sous titres",
    "thank you for watching", "thanks for watching", "gràcies per veure",
    "gracias por ver", "suscríbete", "subscribe",
}

def _is_hallucination(text: str) -> bool:
    lower = text.lower().strip()
    return any(h in lower for h in _WHISPER_HALLUCINATIONS)


@router.post("/transcribe")
async def transcribe_audio(
    audio: UploadFile = File(...),
    lang: str = Query(default="ca"),
    current_user: User = Depends(get_current_user),
):
    transcribe_limiter.check(str(current_user.id))
    if not settings.DispatchSimKeyOpenAI:
        raise HTTPException(503, "Transcription service not configured")

    audio_bytes = await audio.read()

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.openai.com/v1/audio/transcriptions",
            headers={"Authorization": f"Bearer {settings.DispatchSimKeyOpenAI}"},
            files={"file": ("audio.webm", audio_bytes, "audio/webm")},
            data={"model": "whisper-1", "language": lang},
            timeout=30.0,
        )

    if response.status_code != 200:
        raise HTTPException(502, f"Transcription failed: {response.text}")

    text = response.json().get("text", "").strip()
    if _is_hallucination(text):
        return {"text": ""}

    return {"text": text}




class TTSRequest(BaseModel):
    text: str
    voice: str = "nova"


@router.post("/speak")
async def text_to_speech(
    req: TTSRequest,
    current_user: User = Depends(get_current_user),
):
    tts_limiter.check(str(current_user.id))
    # ElevenLabs tiene prioridad si está configurado
    if settings.DispatchSimKeyEleven:
        voice_settings = EL_VOICE_SETTINGS.get(req.voice, EL_DEFAULT_SETTINGS)
        async with httpx.AsyncClient() as client:
            el_response = await client.post(
                f"https://api.elevenlabs.io/v1/text-to-speech/{req.voice}",
                headers={
                    "xi-api-key": settings.DispatchSimKeyEleven,
                    "Content-Type": "application/json",
                },
                json={
                    "text": req.text,
                    "model_id": "eleven_multilingual_v2",
                    "voice_settings": voice_settings,
                },
                timeout=60.0,
            )
        if el_response.status_code == 200:
            return Response(content=el_response.content, media_type="audio/mpeg")
        logger.error("ElevenLabs TTS error %s: %s", el_response.status_code, el_response.text[:300])
        # Si ElevenLabs falla, intentar OpenAI como fallback

    # OpenAI TTS
    if not settings.DispatchSimKeyOpenAI:
        raise HTTPException(503, "TTS service not configured")

    # Mapear voice IDs de ElevenLabs a voces válidas de OpenAI
    _EL_TO_OAI = {
        "EXAVITQu4vr4xnSDxMaL": "nova",
        "cgSgspJ2msm6clMCkdW9": "shimmer",
        "pNInz6obpgDQGcFmaJgB": "onyx",
    }
    oai_voice = _EL_TO_OAI.get(req.voice, req.voice if req.voice in {"alloy","echo","fable","onyx","nova","shimmer"} else "nova")

    async with httpx.AsyncClient() as client:
        oai_response = await client.post(
            "https://api.openai.com/v1/audio/speech",
            headers={
                "Authorization": f"Bearer {settings.DispatchSimKeyOpenAI}",
                "Content-Type": "application/json",
            },
            json={"model": "tts-1-hd", "input": req.text, "voice": oai_voice},
            timeout=60.0,
        )

    if oai_response.status_code != 200:
        logger.error("OpenAI TTS error %s: %s", oai_response.status_code, oai_response.text[:300])
        raise HTTPException(502, f"TTS failed: {oai_response.text}")

    return Response(content=oai_response.content, media_type="audio/mpeg")
