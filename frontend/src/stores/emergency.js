import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiFetch } from '@/api'

export const useEmergencyStore = defineStore('emergency', () => {
  // Scenarios
  const scenariosCache = ref([])

  // Active incident
  const currentIncidentId = ref(null)
  const sessionIncidents  = ref([])
  const selectedPriority  = ref(1)

  // Chat
  const messages  = ref([])  // { id, role: 'operator'|'alertant'|'system', content }
  const isTyping  = ref(false)

  // Call state
  const callActive        = ref(false)
  const callEnded         = ref(false)
  const elapsed           = ref(0)
  const interventionSaved = ref(false)

  // Chronometer (non-reactive interval handle)
  let _timer = null
  let _msgId  = 0

  // ── Computed ──────────────────────────────────────────────
  const inputEnabled = computed(() =>
    currentIncidentId.value !== null && !callEnded.value && !interventionSaved.value
  )

  const currentIncident = computed(() =>
    sessionIncidents.value.find(i => i.id === currentIncidentId.value) ?? null
  )

  // ── Internal helpers ──────────────────────────────────────
  function _addMsg(role, content) {
    messages.value.push({ id: ++_msgId, role, content })
  }

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

  // ── Public actions ────────────────────────────────────────
  async function loadScenarios() {
    const res = await apiFetch('/api/v1/scenarios')
    if (!res || !res.ok) return
    scenariosCache.value = await res.json()
  }

  function setPriority(p) { selectedPriority.value = p }

  async function startIncident(body) {
    const res = await apiFetch('/api/v1/incidents', { method: 'POST', body: JSON.stringify(body) })
    if (!res || !res.ok) { _addMsg('system', "Error creant l'incident"); return null }
    const inc = await res.json()
    currentIncidentId.value  = inc.id
    sessionIncidents.value.push(inc)
    messages.value           = []
    callActive.value         = true
    callEnded.value          = false
    interventionSaved.value  = false
    const scLabel = body.scenario_id
      ? ` · Escenari: ${scenariosCache.value.find(s => s.id === body.scenario_id)?.title || '#' + body.scenario_id}`
      : ''
    _addMsg('system', `Incident #${inc.id} obert · ${inc.type} · ${inc.location}${scLabel}`)
    _startTimer()
    return inc
  }

  async function sendMessage(text) {
    _addMsg('operator', text)
    isTyping.value = true
    try {
      const res = await apiFetch('/api/v1/simulate/chat', {
        method: 'POST',
        body: JSON.stringify({ incident_id: currentIncidentId.value, operator_message: text }),
      })
      if (!res || !res.ok) { _addMsg('system', 'Error de comunicació'); return }
      const data = await res.json()
      _addMsg('alertant', data.content)
    } finally {
      isTyping.value = false
    }
  }

  async function endCall() {
    const res = await apiFetch(
      `/api/v1/incidents/${currentIncidentId.value}/call`, { method: 'PATCH' }
    )
    if (!res || !res.ok) return false
    _stopTimer()
    _addMsg('system', 'Trucada finalitzada · Omple la fitxa i guarda la intervenció')
    return true
  }

  async function saveIntervention(payload) {
    const res = await apiFetch('/api/v1/interventions', {
      method: 'POST', body: JSON.stringify(payload),
    })
    if (!res || !(res.ok || res.status === 201)) return false
    if (callActive.value) {
      await apiFetch(`/api/v1/incidents/${currentIncidentId.value}/call`, { method: 'PATCH' })
      _stopTimer()
    }
    interventionSaved.value = true
    _addMsg('system', `Fitxa guardada · Incident #${currentIncidentId.value}`)
    return true
  }

  function switchIncident(inc) {
    currentIncidentId.value = inc.id
    messages.value          = []
    callActive.value        = false
    callEnded.value         = false
    interventionSaved.value = false
    _addMsg('system', `Canviat a Incident #${inc.id}`)
  }

  async function createScenario(payload) {
    const res = await apiFetch('/api/v1/scenarios', { method: 'POST', body: JSON.stringify(payload) })
    if (!res || !res.ok) throw new Error("Error creant l'escenari")
    await loadScenarios()
  }

  async function deleteScenario(id) {
    const res = await apiFetch(`/api/v1/scenarios/${id}`, { method: 'DELETE' })
    if (res && (res.ok || res.status === 204)) await loadScenarios()
  }

  return {
    scenariosCache, currentIncidentId, sessionIncidents, selectedPriority,
    messages, isTyping, callActive, callEnded, elapsed, interventionSaved,
    inputEnabled, currentIncident,
    loadScenarios, setPriority, startIncident, sendMessage, endCall,
    saveIntervention, switchIncident, createScenario, deleteScenario,
  }
})
