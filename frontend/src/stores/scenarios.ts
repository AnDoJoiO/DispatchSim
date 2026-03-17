import { defineStore } from 'pinia'
import { ref, type Ref } from 'vue'
import { apiFetch } from '@/api'
import type { Scenario, ScenarioCreate } from '@/types'

export const useScenarioStore = defineStore('scenarios', () => {
  const scenariosCache: Ref<Scenario[]> = ref([])

  async function loadScenarios(): Promise<void> {
    try {
      scenariosCache.value = await apiFetch<Scenario[]>('/api/v1/scenarios')
    } catch { /* silent — cache stays stale */ }
  }

  async function createScenario(payload: ScenarioCreate): Promise<void> {
    await apiFetch('/api/v1/scenarios', { method: 'POST', body: JSON.stringify(payload) })
    await loadScenarios()
  }

  async function deleteScenario(id: number): Promise<void> {
    await apiFetch(`/api/v1/scenarios/${id}`, { method: 'DELETE' })
    await loadScenarios()
  }

  return { scenariosCache, loadScenarios, createScenario, deleteScenario }
})
