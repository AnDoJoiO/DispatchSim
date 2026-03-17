# Maps incident initial_emotion to ElevenLabs voice ID
VOICE_MAP: dict[str, str] = {
    "Calma":    "EXAVITQu4vr4xnSDxMaL",  # Sarah
    "Pánico":   "cgSgspJ2msm6clMCkdW9",  # Jessica
    "Agresión": "pNInz6obpgDQGcFmaJgB",  # Adam
}
DEFAULT_VOICE = "EXAVITQu4vr4xnSDxMaL"  # Sarah – fallback

# ElevenLabs voice settings per voice ID
EL_VOICE_SETTINGS: dict[str, dict] = {
    "EXAVITQu4vr4xnSDxMaL": {"stability": 0.70, "similarity_boost": 0.80, "style": 0.15},  # Sarah
    "cgSgspJ2msm6clMCkdW9": {"stability": 0.20, "similarity_boost": 0.80, "style": 0.85},  # Jessica
    "pNInz6obpgDQGcFmaJgB": {"stability": 0.35, "similarity_boost": 0.80, "style": 0.85},  # Adam
}
EL_DEFAULT_SETTINGS: dict = {"stability": 0.50, "similarity_boost": 0.75, "style": 0.40}

# Maps ElevenLabs voice IDs to OpenAI TTS voice names (fallback)
EL_TO_OAI_VOICE: dict[str, str] = {
    "EXAVITQu4vr4xnSDxMaL": "nova",
    "cgSgspJ2msm6clMCkdW9": "shimmer",
    "pNInz6obpgDQGcFmaJgB": "onyx",
}
