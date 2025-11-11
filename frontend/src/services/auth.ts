// Authentication service for managing tokens and user state

import { parseGatewayResponse } from '@/utils/gateway'
import { getApiBaseUrl } from '@/config/api-config'

const API_BASE_URL = getApiBaseUrl()

interface LoginResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

interface User {
  id: string
  email: string
  username: string
  first_name: string
  last_name: string
  role: string
}

class AuthService {
  private readonly ACCESS_TOKEN_KEY = 'mantrapath_token'
  private readonly REFRESH_TOKEN_KEY = 'mantrapath_refresh_token'
  private readonly USER_KEY = 'user_data'

  // Get the current access token
  getAccessToken(): string | null {
    if (typeof window === 'undefined') return null
    return localStorage.getItem(this.ACCESS_TOKEN_KEY)
  }

  // Get the current refresh token
  getRefreshToken(): string | null {
    if (typeof window === 'undefined') return null
    return localStorage.getItem(this.REFRESH_TOKEN_KEY)
  }

  // Get current user data
  getCurrentUser(): User | null {
    if (typeof window === 'undefined') return null
    const userData = localStorage.getItem(this.USER_KEY)
    return userData ? JSON.parse(userData) : null
  }

  // Store authentication data
  setAuthData(loginResponse: LoginResponse, userData?: User) {
    if (typeof window === 'undefined') return

    localStorage.setItem(this.ACCESS_TOKEN_KEY, loginResponse.access_token)
    localStorage.setItem(this.REFRESH_TOKEN_KEY, loginResponse.refresh_token)
    
    if (userData) {
      localStorage.setItem(this.USER_KEY, JSON.stringify(userData))
    }
  }

  // Clear all authentication data
  clearAuth() {
    if (typeof window === 'undefined') return

    localStorage.removeItem(this.ACCESS_TOKEN_KEY)
    localStorage.removeItem(this.REFRESH_TOKEN_KEY)
    localStorage.removeItem(this.USER_KEY)
  }

  // Check if user is authenticated
  isAuthenticated(): boolean {
    return !!this.getAccessToken()
  }

  // Register a new user
  async register(email: string, username: string, password: string): Promise<LoginResponse> {
    const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, username, password }),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Registration failed')
    }

    const gatewayResponse = await response.json()
    
    // Parse API Gateway response
    const authData = parseGatewayResponse<any>(gatewayResponse)
    const loginResponse: LoginResponse = {
      access_token: authData.access_token,
      refresh_token: authData.refresh_token,
      token_type: authData.token_type
    }
    
    // Store the tokens
    this.setAuthData(loginResponse)
    
    return loginResponse
  }

  // Login with email and password
  async login(email: string, password: string): Promise<LoginResponse> {
    const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email_or_username: email, password }),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Login failed')
    }

    const gatewayResponse = await response.json()
    
    // Parse API Gateway response
    const authData = parseGatewayResponse<any>(gatewayResponse)
    const loginResponse: LoginResponse = {
      access_token: authData.access_token,
      refresh_token: authData.refresh_token,
      token_type: authData.token_type
    }
    
    // Store the tokens
    this.setAuthData(loginResponse)
    
    return loginResponse
  }

  // Logout the user
  logout() {
    this.clearAuth()
    // Optionally redirect to login page or refresh
    if (typeof window !== 'undefined') {
      window.location.reload()
    }
  }

  // Refresh the access token
  async refreshAccessToken(): Promise<string | null> {
    const refreshToken = this.getRefreshToken()
    if (!refreshToken) return null

    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/refresh-token`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh_token: refreshToken }),
      })

      if (!response.ok) {
        // Refresh failed, clear auth data
        this.clearAuth()
        return null
      }

      const gatewayResponse = await response.json()
      
      // Parse API Gateway response
      const authData = parseGatewayResponse<any>(gatewayResponse)
      
      localStorage.setItem(this.ACCESS_TOKEN_KEY, authData.access_token)
      return authData.access_token
    } catch (error) {
      this.clearAuth()
      return null
    }
  }

}

// Export a singleton instance
export const authService = new AuthService()
export type { LoginResponse, User }
