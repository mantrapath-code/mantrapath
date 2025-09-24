/**
 * Authentication utilities for MantraPath
 */

/**
 * Check if we're in development mode
 */
export function isDevMode(): boolean {
  return import.meta.env.DEV
}

/**
 * Get auth token from localStorage
 */
export function getAuthToken(): string | null {
  return localStorage.getItem('mantrapath_token')
}

/**
 * Set auth token in localStorage
 */
export function setAuthToken(token: string): void {
  localStorage.setItem('mantrapath_token', token)
}

/**
 * Remove auth token from localStorage
 */
export function removeAuthToken(): void {
  localStorage.removeItem('mantrapath_token')
}

/**
 * Check if user is authenticated
 */
export function isAuthenticated(): boolean {
  const token = getAuthToken()
  return !!token
}

/**
 * Development helper to set a valid token for testing
 */
export function setDevToken(): void {
  if (isDevMode()) {
    const devToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyNmU2NzE2YS1lNGJkLTRmMmYtYTBiYi1lYzc0MjkwMjEyMmYiLCJlbWFpbCI6InNhQGdtYWlsLmNvbSIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzU4NzUzMDM3LCJ0eXBlIjoiYWNjZXNzIn0.rCMzher_zuFCdlIGl4NnIUQwfUq7AzVkP9TWqSjcS2k'
    setAuthToken(devToken)
    console.log('Dev token set for testing')
  }
}
