/**
 * Unified HTTP client wrapper for MantraPath
 * - Always re-reads token from storage (no stale in-memory copy)
 * - Injects Authorization header when present
 * - Optional per-request override (noAuth)
 * - Centralized 401 handling with single warning per session
 * - Dev diagnostics for missing token
 */
import { getAuthToken, removeAuthToken, isDevMode } from '@/utils/auth'
import { getServiceUrls } from '@/config/api-config'

const { API_BASE_URL } = getServiceUrls()

export interface HttpRequestOptions extends RequestInit {
  noAuth?: boolean
  expectedStatuses?: number[]
  autoJson?: boolean
  raw?: boolean
  retry?: number
  retryDelayMs?: number
}

export interface HttpError extends Error {
  status: number
  details?: any
  response?: Response
}

let unauthorizedWarned = false
let missingTokenHintShown = false
let globalUnauthorizedHandler: (() => void) | null = null

export function setUnauthorizedHandler(handler: () => void) {
  globalUnauthorizedHandler = handler
}

function buildUrl(path: string): string {
  if (/^https?:\/\//i.test(path)) return path
  if (path.startsWith('/')) return `${API_BASE_URL}${path}`
  return `${API_BASE_URL}/${path}`
}

async function sleep(ms: number) { return new Promise(r => setTimeout(r, ms)) }

export async function httpRequest<T = any>(path: string, options: HttpRequestOptions = {}): Promise<T> {
  const {
    noAuth = false,
    expectedStatuses = [200],
    autoJson = true,
    raw = false,
    retry = 0,
    retryDelayMs = 500,
    headers: incomingHeaders,
    ...rest
  } = options

  const attemptRequest = async (attempt: number): Promise<T> => {
    const headers = new Headers(incomingHeaders || {})

    // Only set JSON content-type if not sending FormData
    if (!(rest.body instanceof FormData) && !headers.has('Content-Type')) {
      headers.set('Content-Type', 'application/json')
    }

    const token = getAuthToken()
    if (!noAuth && token) {
      headers.set('Authorization', `Bearer ${token}`)
    } else if (!noAuth && !token && isDevMode() && !missingTokenHintShown) {
      console.info('ℹ️ No auth token present; authenticated request will likely 401. In dev you can set one with window.setMoodToken().')
      missingTokenHintShown = true
    }

    const url = buildUrl(path)
    let response: Response
    try {
      response = await fetch(url, { ...rest, headers })
    } catch (networkErr: any) {
      if (attempt < retry) {
        await sleep(retryDelayMs)
        return attemptRequest(attempt + 1)
      }
      const err: HttpError = Object.assign(new Error(networkErr?.message || 'Network error'), { status: 0 })
      throw err
    }

    if (response.status === 401 && !noAuth) {
      if (!unauthorizedWarned) {
        console.warn('🔒 Received 401 Unauthorized. Clearing token and triggering handler.')
        unauthorizedWarned = true
      }
      removeAuthToken()
      if (globalUnauthorizedHandler) {
        try { globalUnauthorizedHandler() } catch { /* ignore */ }
      }
    }

    if (!expectedStatuses.includes(response.status)) {
      // Try parse JSON error
      let details: any = null
      try {
        const ct = response.headers.get('content-type') || ''
        if (ct.includes('application/json')) details = await response.json()
      } catch {/* swallow */}

      const err: HttpError = Object.assign(new Error(`HTTP ${response.status}`), { status: response.status, details, response })
      throw err
    }

    if (raw) return response as unknown as T
    if (!autoJson) return undefined as unknown as T

    if (response.status === 204) return undefined as unknown as T

    // Auto JSON parse
    return await response.json() as T
  }

  return attemptRequest(0)
}

// Convenience helpers
export const get = <T=any>(path: string, opts?: Omit<HttpRequestOptions,'method'>) => httpRequest<T>(path, { ...opts, method: 'GET' })
export const post = <T=any>(path: string, body?: any, opts?: Omit<HttpRequestOptions,'method'|'body'>) => httpRequest<T>(path, { ...opts, method: 'POST', body: body instanceof FormData ? body : (body !== undefined ? JSON.stringify(body) : undefined) })
export const put = <T=any>(path: string, body?: any, opts?: Omit<HttpRequestOptions,'method'|'body'>) => httpRequest<T>(path, { ...opts, method: 'PUT', body: body instanceof FormData ? body : (body !== undefined ? JSON.stringify(body) : undefined) })
export const del = <T=any>(path: string, opts?: Omit<HttpRequestOptions,'method'>) => httpRequest<T>(path, { ...opts, method: 'DELETE' })
