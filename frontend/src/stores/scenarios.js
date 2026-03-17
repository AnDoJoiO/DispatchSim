import { defineStore } from 'pinia'
import { ref } from 'vue'
import { apiFetch } from '@/api'

export const useScenarioStore = defineStore('scenarios', () => {
  const scenariosCache = ref([])

  async function loadScenarios() {
    try {
      scenariosCache.value = await apiFetch('/api/v1/scenarios')
    } catch { /* silent — cache stays stale */ }
  }

  async function createScenario(payload) {
    await apiFetch('/api/v1/scenarios', { method: 'POST', body: JSON.stringify(payload) })
    await loadScenarios()
  }

  async function deleteScenario(id) {
    await apiFetch(`/api/v1/scenarios/${id}`, { method: 'DELETE' })
    await loadScenarios()
  }

  return { scenariosCache, loadScenarios, createScenario, deleteScenario }
})
