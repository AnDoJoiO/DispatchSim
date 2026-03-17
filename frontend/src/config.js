// ── Audio / VAD ──────────────────────────────────────────
export const VOICE_THRESHOLD  = 30    // RMS mínimo para detectar voz (0-255)
export const SILENCE_MS       = 1200  // ms de silencio antes de parar la grabación
export const MIN_DURATION_MS  = 1000  // grabaciones más cortas se descartan
export const MIN_BLOB_BYTES   = 3000  // blobs muy pequeños son silencio

// ── Controlador de trucada ───────────────────────────────
export const SILENCE_DELAY    = 15000 // ms sense resposta de l'operador → silent_trigger
export const MIC_GRACE_PERIOD = 2000  // ms d'espera abans d'activar VAD post-inici
export const TTS_RESUME_DELAY = 600   // ms post-TTS abans de reactivar micro
export const MIN_REAL_WORDS   = 2     // mínim de paraules reals per acceptar transcripció
export const WORD_RE          = /\p{L}{2,}/gu  // paraules d'almenys 2 lletres Unicode

// ── Chat ─────────────────────────────────────────────────
export const MAX_SILENCE_REACTIONS = 3
