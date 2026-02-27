import { defineStore } from 'pinia'
import { ref } from 'vue'
import { apiFetch } from '@/api'
import { t } from '@/i18n'

export const useUsersStore = defineStore('users', () => {
  const items = ref([])

  async function load() {
    const res = await apiFetch('/api/v1/users')
    if (!res || !res.ok) return
    items.value = await res.json()
  }

  async function create(payload) {
    const res = await apiFetch('/api/v1/users', { method: 'POST', body: JSON.stringify(payload) })
    if (!res) return { error: t('err.conn') }
    if (res.status === 409) return { error: t('err.username_taken') }
    if (res.status === 403) return { error: t('err.no_permission') }
    if (!res.ok) return { error: t('err.create_user') }
    await load()
    return { ok: true }
  }

  async function update(id, payload) {
    const res = await apiFetch(`/api/v1/users/${id}`, {
      method: 'PATCH', body: JSON.stringify(payload),
    })
    if (!res || !res.ok) {
      const data = res ? await res.json().catch(() => ({})) : {}
      throw new Error(data?.detail || t('err.update_user'))
    }
    await load()
  }

  return { items, load, create, update }
})
