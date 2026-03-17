import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiFetch } from '@/api'
import { t } from '@/i18n'
// Nota: import circular amb call.js — Pinia ho resol correctament perquè
// useCallStore() es crida DINS de funcions, mai durant l'avaluació del mòdul.
import { useCallStore } from '@/stores/call'

const MAX_SILENCE_REACTIONS = 3

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
      const res = await apiFetch('/api/v1/simulate/chat', {
        method: 'POST',
        body: JSON.stringify({
          incident_id:      call.currentIncidentId,
          operator_message: text,
          lang:             localStorage.getItem('dispatch_lang') || 'ca',
        }),
      })
      if (!res || !res.ok) { _addMsg('system', t('sys.error_chat')); return }
      const data = await res.json()
      _addMsg('alertant', data.content, data.voice ?? 'nova')
      if (data.call_ended) {
        const call = useCallStore()
        call._onAutoEnd()
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
      const res = await apiFetch('/api/v1/simulate/chat', {
        method: 'POST',
        body: JSON.stringify({
          incident_id:    call.currentIncidentId,
          silent_trigger: true,
          lang:           localStorage.getItem('dispatch_lang') || 'ca',
        }),
      })
      if (!res || !res.ok) return
      const data = await res.json()
      _addMsg('alertant', data.content, data.voice ?? 'nova')
      if (data.call_ended) {
        const call = useCallStore()
        call._onAutoEnd()
      }
    } finally {
      isTyping.value = false
    }
  }

  return {
    messages, isTyping, silenceCount, inputEnabled,
    sendMessage, sendSilence,
    // Exposats per useCallStore per afegir missatges de sistema i fer reset
    _addMsg, resetChat,
  }
})
