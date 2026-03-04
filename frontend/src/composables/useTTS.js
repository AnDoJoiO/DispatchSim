import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'

// Divide el texto en frases por puntuación
function splitSentences(text) {
  return text.split(/(?<=[.!?…])\s+/).map(s => s.trim()).filter(Boolean)
}

async function fetchAudioUrl(text, voice, token) {
  const res = await fetch('/api/v1/voice/speak', {
    method:  'POST',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
    body:    JSON.stringify({ text, voice }),
  })
  if (!res.ok) return null
  return URL.createObjectURL(await res.blob())
}

function playUrl(url) {
  return new Promise(resolve => {
    const audio = new Audio(url)
    audio.onended = () => { URL.revokeObjectURL(url); resolve() }
    audio.onerror = ()  => { resolve() }
    audio.play().catch(resolve)
  })
}

export function useTTS() {
  const speaking = ref(false)
  let aborted = false

  async function speak(text, voice = 'nova', { onEnd } = {}) {
    if (!text?.trim()) { onEnd?.(); return }

    aborted      = false
    speaking.value = true

    const auth      = useAuthStore()
    const sentences = splitSentences(text)

    // Pre-cargar todas las frases en paralelo, reproducir en orden
    const urlPromises = sentences.map(s => fetchAudioUrl(s, voice, auth.token))

    try {
      let first = true
      for (const urlPromise of urlPromises) {
        if (aborted) break
        const url = await urlPromise
        if (!url || aborted) break
        // Pequeño margen en la primera frase para que el subsistema de audio se inicialice
        if (first) { await new Promise(r => setTimeout(r, 150)); first = false }
        await playUrl(url)
      }
    } finally {
      speaking.value = false
      onEnd?.()
    }
  }

  function stop() {
    aborted        = true
    speaking.value = false
  }

  return { speaking, speak, stop }
}
