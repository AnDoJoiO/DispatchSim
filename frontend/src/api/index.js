import { useAuthStore } from '@/stores/auth'

export async function apiFetch(url, options = {}) {
  const auth = useAuthStore()
  const headers = { 'Content-Type': 'application/json', ...options.headers }
  if (auth.token) headers['Authorization'] = `Bearer ${auth.token}`
  const res = await fetch(url, { ...options, headers })
  if (res.status === 401) { auth.logout(); return null }
  return res
}
