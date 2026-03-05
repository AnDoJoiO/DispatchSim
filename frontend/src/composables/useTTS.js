import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'

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

    aborted        = false
    speaking.value = true

    const auth = useAuthStore()

    try {
      if (aborted) return
      const url = await fetchAudioUrl(text.trim(), voice, auth.token)
      if (url && !aborted) await playUrl(url)
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
