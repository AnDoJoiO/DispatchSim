import { defineStore } from 'pinia'
import { ref, computed, type Ref } from 'vue'
import { apiFetch } from '@/api'
import { t } from '@/i18n'
import type { Incident, InterventionSave } from '@/types'
// Imports circulars gestionats per Pinia: els usem DINS d'accions, no al nivell de mòdul.
import { useChatStore }     from '@/stores/chat'
import { useScenarioStore } from '@/stores/scenarios'

export const useCallStore = defineStore('call', () => {
  const currentIncidentId: Ref<number | null> = ref(null)
  const sessionIncidents: Ref<Incident[]>     = ref([])
  const selectedPriority  = ref(1)
  const callActive        = ref(false)
  const callEnded         = ref(false)
  const elapsed           = ref(0)
  const interventionSaved = ref(false)
  let _timer: ReturnType<typeof setInterval> | null = null

  const currentIncident = computed<Incident | null>(() =>
    sessionIncidents.value.find(i => i.id === currentIncidentId.value) ?? null
  )

  function _startTimer(): void {
    const start = Date.now()
    elapsed.value = 0
    if (_timer) clearInterval(_timer)
    _timer = setInterval(() => {
      elapsed.value = Math.floor((Date.now() - start) / 1000)
    }, 1000)
  }

  function _stopTimer(): void {
    if (_timer) { clearInterval(_timer); _timer = null }
    callActive.value = false
    callEnded.value  = true
  }

  function setPriority(p: number): void { selectedPriority.value = p }

  async function startIncident(body: { scenario_id?: number; type?: string; location?: string; description?: string; priority: number }): Promise<Incident | null> {
    const chat      = useChatStore()
    const scenarios = useScenarioStore()
    try {
      const inc = await apiFetch<Incident>('/api/v1/incidents', { method: 'POST', body: JSON.stringify(body) })
      currentIncidentId.value = inc.id
      sessionIncidents.value.push(inc)
      chat.resetChat()
      callActive.value        = true
      callEnded.value         = false
      interventionSaved.value = false
      const scLabel = body.scenario_id
        ? t('sys.scenario_label', { title: scenarios.scenariosCache.find((s: any) => s.id === body.scenario_id)?.title || '#' + body.scenario_id })
        : ''
      chat._addMsg('system', t('sys.incident_open', { id: inc.id, type: t(`type.${inc.type}`), location: inc.location, scenario: scLabel }))
      _startTimer()
      return inc
    } catch {
      chat._addMsg('system', t('sys.error_incident'))
      return null
    }
  }

  async function endCall(): Promise<boolean> {
    const chat = useChatStore()
    try {
      await apiFetch(`/api/v1/incidents/${currentIncidentId.value}/call`, { method: 'PATCH' })
      _stopTimer()
      chat._addMsg('system', t('sys.call_ended'))
      return true
    } catch {
      return false
    }
  }

  function _onAutoEnd(): void {
    const chat = useChatStore()
    _stopTimer()
    chat._addMsg('system', t('sys.call_ended'))
  }

  async function saveIntervention(payload: InterventionSave): Promise<boolean> {
    const chat = useChatStore()
    try {
      await apiFetch('/api/v1/interventions', {
        method: 'POST', body: JSON.stringify(payload),
      })
      if (callActive.value) {
        try { await apiFetch(`/api/v1/incidents/${currentIncidentId.value}/call`, { method: 'PATCH' }) } catch {}
        _stopTimer()
      }
      interventionSaved.value = true
      chat._addMsg('system', t('sys.fitxa_saved', { id: currentIncidentId.value }))
      return true
    } catch {
      return false
    }
  }

  function switchIncident(inc: Incident): void {
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
    setPriority, startIncident, endCall, _onAutoEnd, saveIntervention, switchIncident,
  }
})
