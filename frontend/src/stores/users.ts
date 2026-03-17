import { defineStore } from 'pinia'
import { ref } from 'vue'
import { apiFetch } from '@/api'

export const useUsersStore = defineStore('users', () => {
  const items = ref([])

  async function load() {
    try {
      items.value = await apiFetch('/api/v1/users')
    } catch { /* silent */ }
  }

  async function create(payload) {
    await apiFetch('/api/v1/users', { method: 'POST', body: JSON.stringify(payload) })
    await load()
  }

  async function update(id, payload) {
    await apiFetch(`/api/v1/users/${id}`, {
      method: 'PATCH', body: JSON.stringify(payload),
    })
    await load()
  }

  return { items, load, create, update }
})
