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
    const devToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyNmU2NzE2YS1lNGJkLTRmMmYtYTBiYi1lYzc0MjkwMjEyMmYiLCJlbWFpbCI6InNhQGdtYWlsLmNvbSIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzU4NzgwODIxLCJ0eXBlIjoiYWNjZXNzIn0.sVOxX_CW5cpwy0ffjNKhem2aMrNS2La_m0wMRBFnUeY'
    setAuthToken(devToken)
    console.log('✅ Dev token set for testing')
    console.log('🔧 Token preview:', devToken.substring(0, 30) + '...')
    return;
  }
  console.log('⚠️ setDevToken only works in development mode')
}

/**
 * Global debug function - can be called from browser console
 */
declare global {
  interface Window {
    setMoodToken: () => void;
    debugAuth: () => void;
  }
}

// Make functions available globally for debugging
if (typeof window !== 'undefined') {
  window.setMoodToken = setDevToken;
  window.debugAuth = () => {
    console.log('🔍 Auth Debug Info:');
    console.log('📍 Environment:', isDevMode() ? 'Development' : 'Production');
    console.log('🎫 Current token:', getAuthToken() ? 'Present' : 'Missing');
    if (getAuthToken()) {
      console.log('🎫 Token preview:', getAuthToken()!.substring(0, 30) + '...');
    }
    console.log('✨ To set token manually: window.setMoodToken()');
  };
}
