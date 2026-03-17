import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'

// AudioContext compartit — es desbloqueja amb la primera interacció d'usuari
let _audioCtx: AudioContext | null = null
function getAudioCtx(): AudioContext {
  if (!_audioCtx) _audioCtx = new AudioContext()
  return _audioCtx
}
function closeAudioCtx(): void {
  if (_audioCtx && _audioCtx.state !== 'closed') {
    _audioCtx.close()
    _audioCtx = null
  }
}

// Desbloqueja l'AudioContext amb qualsevol clic/teclat (política autoplay del navegador)
function _unlockAudio() {
  const ctx = getAudioCtx()
  if (ctx.state === 'suspended') ctx.resume()
  document.removeEventListener('click', _unlockAudio)
  document.removeEventListener('keydown', _unlockAudio)
}
document.addEventListener('click', _unlockAudio)
document.addEventListener('keydown', _unlockAudio)

async function fetchAudioBuffer(text, voice, token) {
  try {
    const res = await fetch('/api/v1/voice/speak', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body:    JSON.stringify({ text, voice }),
    })
    if (!res.ok) {
      console.error('[TTS] API error', res.status)
      return null
    }
    const arrayBuf = await res.arrayBuffer()
    return getAudioCtx().decodeAudioData(arrayBuf)
  } catch (e) {
    console.error('[TTS] fetch/decode failed', e)
    return null
  }
}

function playBuffer(buffer) {
  return new Promise(resolve => {
    const ctx    = getAudioCtx()
    const source = ctx.createBufferSource()
    source.buffer = buffer
    source.connect(ctx.destination)
    source.onended = resolve
    source.start()
  })
}

export function useTTS() {
  const speaking = ref(false)
  let aborted = false
  let currentSource = null

  async function speak(text, voice = 'nova', { onEnd } = {}) {
    if (!text?.trim()) { onEnd?.(); return }

    aborted        = false
    speaking.value = true

    const auth = useAuthStore()

    try {
      const buffer = await fetchAudioBuffer(text.trim(), voice, auth.token)
      if (buffer && !aborted) {
        await playBuffer(buffer)
      }
    } finally {
      speaking.value = false
      currentSource  = null
      onEnd?.()
    }
  }

  function stop() {
    aborted        = true
    speaking.value = false
    try { currentSource?.stop() } catch {}
    currentSource = null
  }

  function cleanup(): void {
    stop()
    closeAudioCtx()
  }

  return { speaking, speak, stop, cleanup }
}
