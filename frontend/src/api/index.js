import { useAuthStore } from '@/stores/auth'

export class ApiError extends Error {
  constructor(status, detail) {
    super(detail)
    this.status = status
  }
}

/**
 * Fetch wrapper amb JWT. Llança ApiError si la resposta no és ok.
 * Retorna la resposta JSON parseada, o null per respostes 204 (no content).
 */
export async function apiFetch(url, options = {}) {
  const auth = useAuthStore()
  const headers = { 'Content-Type': 'application/json', ...options.headers }
  if (auth.token) headers['Authorization'] = `Bearer ${auth.token}`
  const res = await fetch(url, { ...options, headers })
  if (res.status === 401) { auth.logout(); throw new ApiError(401, 'Sessió expirada') }
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new ApiError(res.status, body.detail || `Error ${res.status}`)
  }
  if (res.status === 204) return null
  return res.json()
}
