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

# Palabras sueltas que Whisper alucina — match exacto (evita falsos positivos con substring)
_HALLUCINATION_EXACT = {
    "amara.org", "amara", "subtítulos", "subtitulado", "subtitles",
    "transcripción", "transcription", "sous-titres", "sous titres",
    "suscríbete", "subscribe",
    "you", "thank you", "thanks", "bye", "goodbye", "okay", "ok",
    "gràcies", "gracias", "merci", "adiós", "adéu", "vale",
    "...", "…", "eh", "ah", "oh", "um", "hm", "hmm", "mm",
    "sí", "si", "no", "ja", "oui", "yes",
    "música", "music", "aplausos", "risas", "silencio",
}
# Frases más largas — match por substring
_HALLUCINATION_SUBSTR = {
    "thank you for watching", "thanks for watching", "gràcies per veure",
    "gracias por ver", "subtitulado por", "sous-titres par",
    "antarctica films", "cc por", "copyright", "todos los derechos",
    "all rights reserved", "tots els drets",
}
_MIN_TRANSCRIPTION_CHARS = 8  # mínimo de caracteres para considerar una transcripción válida

import re
_PUNCT_RE = re.compile(r'[^\w\s]', re.UNICODE)

def _is_hallucination(text: str) -> bool:
    lower = text.lower().strip()
    # Match exacto (sin puntuación) para palabras sueltas
    clean = _PUNCT_RE.sub('', lower).strip()
    if clean in _HALLUCINATION_EXACT:
        logger.debug("Whisper hallucination (exact): %r", text)
        return True
    # Substring match para frases largas conocidas
    if any(h in lower for h in _HALLUCINATION_SUBSTR):
        logger.debug("Whisper hallucination (substr): %r", text)
        return True
    # Texto demasiado corto → probablemente ruido
    if len(clean) < _MIN_TRANSCRIPTION_CHARS:
        logger.debug("Whisper hallucination (short, %d chars): %r", len(clean), text)
        return True
    # Repetición de palabras/frases — alucinación clásica de Whisper
    words = clean.split()
    if len(words) >= 3:
        unique = set(words)
        if len(unique) <= len(words) * 0.4:
            logger.debug("Whisper hallucination (repetition): %r", text)
            return True
    return False


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
    _MAX_AUDIO_BYTES = 5 * 1024 * 1024  # 5 MB
    if len(audio_bytes) > _MAX_AUDIO_BYTES:
        raise HTTPException(413, "L'arxiu d'àudio supera el límit de 5 MB")
    # WebM/EBML magic bytes: 0x1A 0x45 0xDF 0xA3
    if len(audio_bytes) < 4 or audio_bytes[:4] != b'\x1a\x45\xdf\xa3':
        raise HTTPException(415, "Format d'àudio no vàlid (es requereix WebM)")

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

    _OAI_VOICES = {"alloy", "echo", "fable", "onyx", "nova", "shimmer"}
    oai_voice = EL_TO_OAI_VOICE.get(req.voice, req.voice if req.voice in _OAI_VOICES else "nova")

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
