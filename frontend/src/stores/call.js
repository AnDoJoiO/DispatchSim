import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiFetch } from '@/api'
import { t } from '@/i18n'
// Imports circulars gestionats per Pinia: els usem DINS d'accions, no al nivell de mòdul.
import { useChatStore }     from '@/stores/chat'
import { useScenarioStore } from '@/stores/scenarios'

export const useCallStore = defineStore('call', () => {
  const currentIncidentId = ref(null)
  const sessionIncidents  = ref([])
  const selectedPriority  = ref(1)
  const callActive        = ref(false)
  const callEnded         = ref(false)
  const elapsed           = ref(0)
  const interventionSaved = ref(false)
  let _timer = null

  // ── Computed ──────────────────────────────────────────────
  const currentIncident = computed(() =>
    sessionIncidents.value.find(i => i.id === currentIncidentId.value) ?? null
  )

  // ── Helpers privats ───────────────────────────────────────
  function _startTimer() {
    const start = Date.now()
    elapsed.value = 0
    if (_timer) clearInterval(_timer)
    _timer = setInterval(() => {
      elapsed.value = Math.floor((Date.now() - start) / 1000)
    }, 1000)
  }

  function _stopTimer() {
    if (_timer) { clearInterval(_timer); _timer = null }
    callActive.value = false
    callEnded.value  = true
  }

  // ── Accions públiques ─────────────────────────────────────
  function setPriority(p) { selectedPriority.value = p }

  async function startIncident(body) {
    const chat      = useChatStore()
    const scenarios = useScenarioStore()
    const res = await apiFetch('/api/v1/incidents', { method: 'POST', body: JSON.stringify(body) })
    if (!res || !res.ok) { chat._addMsg('system', t('sys.error_incident')); return null }
    const inc = await res.json()
    currentIncidentId.value = inc.id
    sessionIncidents.value.push(inc)
    chat.resetChat()
    callActive.value        = true
    callEnded.value         = false
    interventionSaved.value = false
    const scLabel = body.scenario_id
      ? t('sys.scenario_label', { title: scenarios.scenariosCache.find(s => s.id === body.scenario_id)?.title || '#' + body.scenario_id })
      : ''
    chat._addMsg('system', t('sys.incident_open', { id: inc.id, type: t(`type.${inc.type}`), location: inc.location, scenario: scLabel }))
    _startTimer()
    return inc
  }

  async function endCall() {
    const chat = useChatStore()
    const res = await apiFetch(
      `/api/v1/incidents/${currentIncidentId.value}/call`, { method: 'PATCH' }
    )
    if (!res || !res.ok) return false
    _stopTimer()
    chat._addMsg('system', t('sys.call_ended'))
    return true
  }

  async function saveIntervention(payload) {
    const chat = useChatStore()
    const res = await apiFetch('/api/v1/interventions', {
      method: 'POST', body: JSON.stringify(payload),
    })
    if (!res || !(res.ok || res.status === 201)) return false
    if (callActive.value) {
      await apiFetch(`/api/v1/incidents/${currentIncidentId.value}/call`, { method: 'PATCH' })
      _stopTimer()
    }
    interventionSaved.value = true
    chat._addMsg('system', t('sys.fitxa_saved', { id: currentIncidentId.value }))
    return true
  }

  function switchIncident(inc) {
    const chat = useChatStore()
    currentIncidentId.value = inc.id
    callActive.value        = false
    callEnded.value         = false
    interventionSaved.value = false
    chat.resetChat()
    chat._addMsg('system', t('sys.incident_switched', { id: inc.id }))
  }

  return {
    currentIncidentId, sessionIncidents, selectedPriority,
    callActive, callEnded, elapsed, interventionSaved,
    currentIncident,
    setPriority, startIncident, endCall, saveIntervention, switchIncident,
  }
})
