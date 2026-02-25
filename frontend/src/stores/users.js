import { defineStore } from 'pinia'
import { ref } from 'vue'
import { apiFetch } from '@/api'

export const useUsersStore = defineStore('users', () => {
  const items = ref([])

  async function load() {
    const res = await apiFetch('/api/v1/users')
    if (!res || !res.ok) return
    items.value = await res.json()
  }

  async function create(payload) {
    const res = await apiFetch('/api/v1/users', { method: 'POST', body: JSON.stringify(payload) })
    if (!res) return { error: 'Error de connexió' }
    if (res.status === 409) return { error: "El nom d'usuari ja existeix" }
    if (res.status === 403) return { error: 'No tens permís' }
    if (!res.ok) return { error: "Error creant l'usuari" }
    await load()
    return { ok: true }
  }

  async function update(id, payload) {
    const res = await apiFetch(`/api/v1/users/${id}`, {
      method: 'PATCH', body: JSON.stringify(payload),
    })
    if (!res || !res.ok) {
      const data = res ? await res.json().catch(() => ({})) : {}
      throw new Error(data?.detail || "Error actualitzant l'usuari")
    }
    await load()
  }

  return { items, load, create, update }
})
