import { defineStore } from 'pinia'
import { ref } from 'vue'
import { apiFetch } from '@/api'
import { t } from '@/i18n'

export const useHistoryStore = defineStore('history', () => {
  const items           = ref([])
  const filterPriority  = ref(null)
  const searchQuery     = ref('')

  async function load() {
    const res = await apiFetch('/api/v1/history')
    if (!res || !res.ok) throw new Error(t('err.load_history'))
    items.value = await res.json()
  }

  async function getDetail(id) {
    const res = await apiFetch(`/api/v1/history/${id}`)
    if (!res || !res.ok) throw new Error(t('err.load_detail'))
    return res.json()
  }

  async function deleteOne(id) {
    const res = await apiFetch(`/api/v1/history/${id}`, { method: 'DELETE' })
    if (!res || !res.ok) throw new Error(t('err.delete'))
    await load()
  }

  async function deleteMany(ids) {
    const res = await apiFetch('/api/v1/history', {
      method: 'DELETE', body: JSON.stringify({ ids }),
    })
    if (!res || !res.ok) throw new Error(t('err.delete'))
    await load()
  }

  async function deleteAll() {
    const res = await apiFetch('/api/v1/history', {
      method: 'DELETE', body: JSON.stringify({}),
    })
    if (!res || !res.ok) throw new Error(t('err.delete'))
    await load()
  }

  return { items, filterPriority, searchQuery, load, getDetail, deleteOne, deleteMany, deleteAll }
})
