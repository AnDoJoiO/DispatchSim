import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('dispatch_token'))
  const user  = ref(JSON.parse(localStorage.getItem('dispatch_user') || 'null'))

  const isLoggedIn  = computed(() => !!token.value && !!user.value)
  const canManage   = computed(() => ['admin', 'formador'].includes(user.value?.role))
  const isAdmin     = computed(() => user.value?.role === 'admin')

  async function login(username, password) {
    const res = await fetch('/api/v1/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    })
    if (!res.ok) {
      const data = await res.json()
      throw new Error(data.detail || 'Error')
    }
    const data = await res.json()
    token.value = data.access_token
    user.value  = data.user
    localStorage.setItem('dispatch_token', token.value)
    localStorage.setItem('dispatch_user', JSON.stringify(user.value))
  }

  function logout() {
    token.value = null
    user.value  = null
    localStorage.removeItem('dispatch_token')
    localStorage.removeItem('dispatch_user')
    location.reload()
  }

  return { token, user, isLoggedIn, canManage, isAdmin, login, logout }
})
