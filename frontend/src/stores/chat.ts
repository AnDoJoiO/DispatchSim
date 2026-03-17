import { defineStore } from 'pinia'
import { ref, computed, type Ref } from 'vue'
import { apiFetch, ApiError } from '@/api'
import { t } from '@/i18n'
import { MAX_SILENCE_REACTIONS } from '@/config'
import type { ChatMessage, ChatResponse } from '@/types'
// Nota: import circular amb call.ts — Pinia ho resol correctament perquè
// useCallStore() es crida DINS de funcions, mai durant l'avaluació del mòdul.
import { useCallStore } from '@/stores/call'

export const useChatStore = defineStore('chat', () => {
  const messages: Ref<ChatMessage[]> = ref([])
  const isTyping     = ref(false)
  const silenceCount = ref(0)
  let _msgId = 0

  function _addMsg(role: ChatMessage['role'], content: string, voice: string | null = null): void {
    messages.value.push({ id: ++_msgId, role, content, voice })
  }

  function resetChat(): void {
    messages.value     = []
    silenceCount.value = 0
    _msgId             = 0
  }

  const inputEnabled = computed(() => {
    const call = useCallStore()
    return call.currentIncidentId !== null && !call.callEnded && !call.interventionSaved
  })

  async function sendMessage(text: string): Promise<void> {
    const call = useCallStore()
    _addMsg('operator', text)
    isTyping.value = true
    try {
      const data = await apiFetch<ChatResponse>('/api/v1/simulate/chat', {
        method: 'POST',
        body: JSON.stringify({
          incident_id:      call.currentIncidentId,
          operator_message: text,
          lang:             localStorage.getItem('dispatch_lang') || 'ca',
        }),
      })
      const ended = data.call_ended
      _addMsg('alertant', data.content, data.voice ?? 'nova')
      if (ended) setTimeout(() => call._onAutoEnd(), 100)
    } catch (e: unknown) {
      if (e instanceof ApiError && e.status === 422) {
        messages.value.pop()
      } else {
        const detail = e instanceof ApiError ? `[${e.status}] ${e.message}` : (e as Error).message || 'Network error'
        _addMsg('system', `${t('sys.error_chat')} — ${detail}`)
      }
    } finally {
      isTyping.value = false
    }
  }

  async function sendSilence(): Promise<void> {
    const call = useCallStore()
    if (!call.callActive || call.callEnded || isTyping.value) return
    if (silenceCount.value >= MAX_SILENCE_REACTIONS) return
    silenceCount.value++
    isTyping.value = true
    try {
      const data = await apiFetch<ChatResponse>('/api/v1/simulate/chat', {
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
