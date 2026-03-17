import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiFetch, ApiError } from '@/api'
import { t } from '@/i18n'
import { MAX_SILENCE_REACTIONS } from '@/config'
// Nota: import circular amb call.js — Pinia ho resol correctament perquè
// useCallStore() es crida DINS de funcions, mai durant l'avaluació del mòdul.
import { useCallStore } from '@/stores/call'

export const useChatStore = defineStore('chat', () => {
  const messages     = ref([])
  const isTyping     = ref(false)
  const silenceCount = ref(0)
  let _msgId = 0

  // ── Helpers internos ──────────────────────────────────────
  function _addMsg(role, content, voice = null) {
    messages.value.push({ id: ++_msgId, role, content, voice })
  }

  function resetChat() {
    messages.value     = []
    silenceCount.value = 0
    _msgId             = 0
  }

  // inputEnabled: pot xatejar? Depèn de l'estat de trucada (callStore)
  const inputEnabled = computed(() => {
    const call = useCallStore()
    return call.currentIncidentId !== null && !call.callEnded && !call.interventionSaved
  })

  // ── Accions públiques ─────────────────────────────────────
  async function sendMessage(text) {
    const call = useCallStore()
    _addMsg('operator', text)
    isTyping.value = true
    try {
      const data = await apiFetch('/api/v1/simulate/chat', {
        method: 'POST',
        body: JSON.stringify({
          incident_id:      call.currentIncidentId,
          operator_message: text,
          lang:             localStorage.getItem('dispatch_lang') || 'ca',
        }),
      })
      const ended = data.call_ended
      _addMsg('alertant', data.content, data.voice ?? 'nova')
      // Demorar auto-end perquè el watcher de messages pugui iniciar speak()
      // abans que el watcher de callEnded faci stopTTS()
      if (ended) setTimeout(() => call._onAutoEnd(), 100)
    } catch (e) {
      if (e instanceof ApiError && e.status === 422) {
        // Backend rejected noise — remove the operator bubble silently
        messages.value.pop()
      } else {
        _addMsg('system', t('sys.error_chat'))
      }
    } finally {
      isTyping.value = false
    }
  }

  async function sendSilence() {
    const call = useCallStore()
    if (!call.callActive || call.callEnded || isTyping.value) return
    if (silenceCount.value >= MAX_SILENCE_REACTIONS) return
    silenceCount.value++
    isTyping.value = true
    try {
      const data = await apiFetch('/api/v1/simulate/chat', {
        method: 'POST',
        body: JSON.stringify({
          incident_id:    call.currentIncidentId,
          silent_trigger: true,
          lang:           localStorage.getItem('dispatch_lang') || 'ca',
        }),
      })
      const ended = data.call_ended
      _addMsg('alertant', data.content, data.voice ?? 'nova')
      if (ended) setTimeout(() => call._onAutoEnd(), 100)
    } catch {
      // silent — silence reaction failed, not critical
    } finally {
      isTyping.value = false
    }
  }

  return {
    messages, isTyping, silenceCount, inputEnabled,
    sendMessage, sendSilence,
    _addMsg, resetChat,
  }
})
