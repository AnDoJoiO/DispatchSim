from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel

import httpx

from app.core.config import settings
from app.core.deps import get_current_user

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
    _=Depends(get_current_user),
):
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


# Parámetros de voz por voice_id para ElevenLabs
_EL_VOICE_SETTINGS: dict[str, dict] = {
    "EXAVITQu4vr4xnSDxMaL": {"stability": 0.70, "similarity_boost": 0.80, "style": 0.15},  # Sarah – Calma
    "cgSgspJ2msm6clMCkdW9": {"stability": 0.20, "similarity_boost": 0.80, "style": 0.85},  # Jessica – Pánico
    "pNInz6obpgDQGcFmaJgB": {"stability": 0.35, "similarity_boost": 0.80, "style": 0.85},  # Adam – Agresión
}
_EL_DEFAULT_SETTINGS = {"stability": 0.50, "similarity_boost": 0.75, "style": 0.40}


class TTSRequest(BaseModel):
    text: str
    voice: str = "nova"


@router.post("/speak")
async def text_to_speech(
    req: TTSRequest,
    _=Depends(get_current_user),
):
    # ElevenLabs tiene prioridad si está configurado
    if settings.DispatchSimKeyEleven:
        voice_settings = _EL_VOICE_SETTINGS.get(req.voice, _EL_DEFAULT_SETTINGS)
        async with httpx.AsyncClient() as client:
            response = await client.post(
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
                timeout=30.0,
            )
        if response.status_code != 200:
            raise HTTPException(502, f"ElevenLabs TTS failed: {response.text}")
        return Response(content=response.content, media_type="audio/mpeg")

    # Fallback a OpenAI TTS
    if not settings.DispatchSimKeyOpenAI:
        raise HTTPException(503, "TTS service not configured")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.openai.com/v1/audio/speech",
            headers={
                "Authorization": f"Bearer {settings.DispatchSimKeyOpenAI}",
                "Content-Type": "application/json",
            },
            json={"model": "tts-1-hd", "input": req.text, "voice": req.voice},
            timeout=30.0,
        )

    if response.status_code != 200:
        raise HTTPException(502, f"TTS failed: {response.text}")

    return Response(content=response.content, media_type="audio/mpeg")
