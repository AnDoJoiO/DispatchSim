import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'

// Mock localStorage + location before any store import
const storage = {}
vi.stubGlobal('localStorage', {
  getItem: (k) => storage[k] ?? null,
  setItem: (k, v) => { storage[k] = v },
  removeItem: (k) => { delete storage[k] },
})
vi.stubGlobal('location', { reload: vi.fn() })

import { useAuthStore } from '@/stores/auth'
import { useAppStore } from '@/stores/app'

// Mock fetch for auth store
const mockFetch = vi.fn()
vi.stubGlobal('fetch', mockFetch)

describe('useAuthStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    Object.keys(storage).forEach(k => delete storage[k])
    mockFetch.mockReset()
  })

  it('starts logged out', () => {
    const auth = useAuthStore()
    expect(auth.isLoggedIn).toBe(false)
    expect(auth.token).toBeNull()
    expect(auth.user).toBeNull()
  })

  it('login stores token and user', async () => {
    mockFetch.mockReturnValue(Promise.resolve({
      ok: true,
      json: () => Promise.resolve({
        access_token: 'jwt-123',
        user: { id: 1, username: 'admin', role: 'admin', is_active: true },
      }),
    }))
    const auth = useAuthStore()
    await auth.login('admin', 'pass')
    expect(auth.isLoggedIn).toBe(true)
    expect(auth.token).toBe('jwt-123')
    expect(auth.user.username).toBe('admin')
    expect(storage.dispatch_token).toBe('jwt-123')
  })

  it('login throws on failure', async () => {
    mockFetch.mockReturnValue(Promise.resolve({
      ok: false,
      json: () => Promise.resolve({ detail: 'Credencials incorrectes' }),
    }))
    const auth = useAuthStore()
    await expect(auth.login('x', 'y')).rejects.toThrow('Credencials incorrectes')
  })

  it('logout clears state', async () => {
    storage.dispatch_token = 'jwt'
    storage.dispatch_user = JSON.stringify({ id: 1, role: 'admin' })
    setActivePinia(createPinia())
    const auth = useAuthStore()
    expect(auth.isLoggedIn).toBe(true)
    auth.logout()
    expect(auth.isLoggedIn).toBe(false)
    expect(storage.dispatch_token).toBeUndefined()
  })

  it('canManage is true for admin and formador', () => {
    storage.dispatch_user = JSON.stringify({ role: 'admin' })
    storage.dispatch_token = 'x'
    setActivePinia(createPinia())
    expect(useAuthStore().canManage).toBe(true)

    storage.dispatch_user = JSON.stringify({ role: 'formador' })
    setActivePinia(createPinia())
    expect(useAuthStore().canManage).toBe(true)

    storage.dispatch_user = JSON.stringify({ role: 'operador' })
    setActivePinia(createPinia())
    expect(useAuthStore().canManage).toBe(false)
  })

  it('isAdmin only for admin role', () => {
    storage.dispatch_user = JSON.stringify({ role: 'admin' })
    storage.dispatch_token = 'x'
    setActivePinia(createPinia())
    expect(useAuthStore().isAdmin).toBe(true)

    storage.dispatch_user = JSON.stringify({ role: 'formador' })
    setActivePinia(createPinia())
    expect(useAuthStore().isAdmin).toBe(false)
  })
})

describe('useAppStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    Object.keys(storage).forEach(k => delete storage[k])
  })

  it('defaults to emergency tab', () => {
    const app = useAppStore()
    expect(app.activeTab).toBe('emergency')
  })

  it('showTab changes activeTab', () => {
    const app = useAppStore()
    app.showTab('history')
    expect(app.activeTab).toBe('history')
  })

  it('toggleTheme switches between light and dark', () => {
    const app = useAppStore()
    const initial = app.theme
    app.toggleTheme()
    expect(app.theme).not.toBe(initial)
    app.toggleTheme()
    expect(app.theme).toBe(initial)
  })
})
