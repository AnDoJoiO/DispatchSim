import { defineStore } from 'pinia'
import { ref, type Ref } from 'vue'
import { apiFetch } from '@/api'
import type { User } from '@/types'

export const useUsersStore = defineStore('users', () => {
  const items: Ref<User[]> = ref([])

  async function load(): Promise<void> {
    try {
      items.value = await apiFetch<User[]>('/api/v1/users')
    } catch { /* silent */ }
  }

  async function create(payload: { username: string; password: string; role: string; expires_at?: string }): Promise<void> {
    await apiFetch('/api/v1/users', { method: 'POST', body: JSON.stringify(payload) })
    await load()
  }

  async function update(id: number, payload: { is_active?: boolean; expires_at?: string | null }): Promise<void> {
    await apiFetch(`/api/v1/users/${id}`, {
      method: 'PATCH', body: JSON.stringify(payload),
    })
    await load()
  }

  return { items, load, create, update }
})
