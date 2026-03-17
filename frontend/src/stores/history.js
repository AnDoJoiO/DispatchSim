import { defineStore } from 'pinia'
import { ref } from 'vue'
import { apiFetch } from '@/api'

export const useHistoryStore = defineStore('history', () => {
  const items           = ref([])
  const filterPriority  = ref(null)
  const searchQuery     = ref('')

  async function load() {
    items.value = await apiFetch('/api/v1/history')
  }

  async function getDetail(id) {
    return apiFetch(`/api/v1/history/${id}`)
  }

  async function deleteOne(id) {
    await apiFetch(`/api/v1/history/${id}`, { method: 'DELETE' })
    await load()
  }

  async function deleteMany(ids) {
    await apiFetch('/api/v1/history', {
      method: 'DELETE', body: JSON.stringify({ ids }),
    })
    await load()
  }

  async function deleteAll() {
    await apiFetch('/api/v1/history', {
      method: 'DELETE', body: JSON.stringify({}),
    })
    await load()
  }

  return { items, filterPriority, searchQuery, load, getDetail, deleteOne, deleteMany, deleteAll }
})
