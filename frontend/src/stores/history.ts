import { defineStore } from 'pinia'
import { ref, type Ref } from 'vue'
import { apiFetch } from '@/api'
import type { CallHistorySummary, CallDebriefingDetail } from '@/types'

export const useHistoryStore = defineStore('history', () => {
  const items: Ref<CallHistorySummary[]>   = ref([])
  const filterPriority: Ref<number | null> = ref(null)
  const searchQuery = ref('')

  async function load(): Promise<void> {
    items.value = await apiFetch<CallHistorySummary[]>('/api/v1/history')
  }

  async function getDetail(id: number): Promise<CallDebriefingDetail> {
    return apiFetch<CallDebriefingDetail>(`/api/v1/history/${id}`)
  }

  async function deleteOne(id: number): Promise<void> {
    await apiFetch(`/api/v1/history/${id}`, { method: 'DELETE' })
    await load()
  }

  async function deleteMany(ids: number[]): Promise<void> {
    await apiFetch('/api/v1/history', {
      method: 'DELETE', body: JSON.stringify({ ids }),
    })
    await load()
  }

  async function deleteAll(): Promise<void> {
    await apiFetch('/api/v1/history', {
      method: 'DELETE', body: JSON.stringify({}),
    })
    await load()
  }

  return { items, filterPriority, searchQuery, load, getDetail, deleteOne, deleteMany, deleteAll }
})
