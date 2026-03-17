import { useAuthStore } from '@/stores/auth'

export class ApiError extends Error {
  status: number
  constructor(status: number, detail: string) {
    super(detail)
    this.status = status
  }
}

export async function apiFetch<T = any>(url: string, options: RequestInit = {}): Promise<T> {
  const auth = useAuthStore()
  const headers: Record<string, string> = { 'Content-Type': 'application/json', ...options.headers as Record<string, string> }
  if (auth.token) headers['Authorization'] = `Bearer ${auth.token}`
  const res = await fetch(url, { ...options, headers })
  if (res.status === 401) { auth.logout(); throw new ApiError(401, 'Sessió expirada') }
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new ApiError(res.status, body.detail || `Error ${res.status}`)
  }
  if (res.status === 204) return null as T
  return res.json()
}
