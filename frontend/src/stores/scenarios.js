import { defineStore } from 'pinia'
import { ref } from 'vue'
import { apiFetch } from '@/api'
import { t } from '@/i18n'

export const useScenarioStore = defineStore('scenarios', () => {
  const scenariosCache = ref([])

  async function loadScenarios() {
    const res = await apiFetch('/api/v1/scenarios')
    if (!res || !res.ok) return
    scenariosCache.value = await res.json()
  }

  async function createScenario(payload) {
    const res = await apiFetch('/api/v1/scenarios', { method: 'POST', body: JSON.stringify(payload) })
    if (!res || !res.ok) throw new Error(t('sys.error_scenario'))
    await loadScenarios()
  }

  async function deleteScenario(id) {
    const res = await apiFetch(`/api/v1/scenarios/${id}`, { method: 'DELETE' })
    if (res && (res.ok || res.status === 204)) await loadScenarios()
  }

  return { scenariosCache, loadScenarios, createScenario, deleteScenario }
})
