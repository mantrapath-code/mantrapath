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
 * Auto-set dev token if none exists (for development convenience)
 */
export function ensureDevTokenExists(): void {
  if (isDevMode() && !getAuthToken()) {
    console.log('🚀 No token found in dev mode, auto-setting demo token...')
    setDevToken()
  }
}

/**
 * Development helper to set a valid token for testing
 */
export function setDevToken(): void {
  if (isDevMode()) {
    const devToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkZW1vLXVzZXItMTIzIiwiZW1haWwiOiJkZW1vQG1hbnRyYXBhdGguY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3NTg5NzIwNjQsImV4cCI6MTc1OTA1ODQ2NH0.2TF-5HQCGfw6XEOurGjsnBc4e37JNRdJhKla5uK9lF0'
    setAuthToken(devToken)
    console.log('✅ Dev token set for testing (24h validity)')
    console.log('🔧 Token user: demo@mantrapath.com')
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
