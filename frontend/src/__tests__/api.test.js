import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { apiFetch, ApiError } from '@/api'

// Mock global fetch
const mockFetch = vi.fn()
vi.stubGlobal('fetch', mockFetch)

// Mock localStorage
const storage = {}
vi.stubGlobal('localStorage', {
  getItem: (k) => storage[k] ?? null,
  setItem: (k, v) => { storage[k] = v },
  removeItem: (k) => { delete storage[k] },
})

// Mock location.reload
vi.stubGlobal('location', { reload: vi.fn() })

function jsonResponse(body, status = 200) {
  return Promise.resolve({
    ok: status >= 200 && status < 300,
    status,
    json: () => Promise.resolve(body),
    text: () => Promise.resolve(JSON.stringify(body)),
  })
}

describe('apiFetch', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    mockFetch.mockReset()
    Object.keys(storage).forEach(k => delete storage[k])
  })

  it('returns parsed JSON on success', async () => {
    mockFetch.mockReturnValue(jsonResponse({ id: 1, name: 'test' }))
    const data = await apiFetch('/api/v1/test')
    expect(data).toEqual({ id: 1, name: 'test' })
  })

  it('returns null on 204', async () => {
    mockFetch.mockReturnValue(Promise.resolve({
      ok: true, status: 204, json: () => Promise.resolve(null),
    }))
    const data = await apiFetch('/api/v1/test', { method: 'DELETE' })
    expect(data).toBeNull()
  })

  it('throws ApiError on 4xx', async () => {
    mockFetch.mockReturnValue(jsonResponse({ detail: 'Not found' }, 404))
    await expect(apiFetch('/api/v1/test')).rejects.toThrow(ApiError)
    try {
      await apiFetch('/api/v1/test')
    } catch (e) {
      expect(e.status).toBe(404)
      expect(e.message).toBe('Not found')
    }
  })

  it('throws ApiError on 5xx', async () => {
    mockFetch.mockReturnValue(jsonResponse({}, 500))
    await expect(apiFetch('/api/v1/test')).rejects.toThrow(ApiError)
  })

  it('sends Authorization header when token exists', async () => {
    storage.dispatch_token = 'my-jwt'
    // Re-create pinia so auth store reads the token
    setActivePinia(createPinia())
    mockFetch.mockReturnValue(jsonResponse({ ok: true }))
    await apiFetch('/api/v1/test')
    const [, opts] = mockFetch.mock.calls[0]
    expect(opts.headers['Authorization']).toBe('Bearer my-jwt')
  })

  it('sets Content-Type to application/json', async () => {
    mockFetch.mockReturnValue(jsonResponse({}))
    await apiFetch('/api/v1/test')
    const [, opts] = mockFetch.mock.calls[0]
    expect(opts.headers['Content-Type']).toBe('application/json')
  })

  it('auto-logouts on 401', async () => {
    storage.dispatch_token = 'expired'
    setActivePinia(createPinia())
    mockFetch.mockReturnValue(jsonResponse({}, 401))
    await expect(apiFetch('/api/v1/test')).rejects.toThrow(ApiError)
    expect(storage.dispatch_token).toBeUndefined()
  })
})
