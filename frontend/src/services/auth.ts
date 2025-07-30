// Authentication service for managing tokens and user state

interface LoginResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

interface User {
  id: string
  email: string
  username: string
  role: string
}

class AuthService {
  private readonly ACCESS_TOKEN_KEY = 'auth_token'
  private readonly REFRESH_TOKEN_KEY = 'refresh_token'
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
    const response = await fetch('http://localhost:8000/register', {
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

    const loginResponse: LoginResponse = await response.json()
    
    // Store the tokens
    this.setAuthData(loginResponse)
    
    return loginResponse
  }

  // Login with email and password
  async login(email: string, password: string): Promise<LoginResponse> {
    const response = await fetch('http://localhost:8000/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Login failed')
    }

    const loginResponse: LoginResponse = await response.json()
    
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
      const response = await fetch('http://localhost:8000/refresh-token', {
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

      const data = await response.json()
      localStorage.setItem(this.ACCESS_TOKEN_KEY, data.access_token)
      return data.access_token
    } catch (error) {
      this.clearAuth()
      return null
    }
  }

  // Auto-login for testing (register a test user if not exists)
  async autoLoginForTesting(): Promise<boolean> {
    try {
      // Try to register a test user
      await this.register(
        'testuser@mantrapath.com',
        'testuser',
        'testpassword123'
      )
      return true
    } catch (error: any) {
      // If registration fails (user exists), try to login
      if (error.message.includes('already registered')) {
        try {
          await this.login('testuser@mantrapath.com', 'testpassword123')
          return true
        } catch (loginError) {
          console.error('Auto-login failed:', loginError)
          return false
        }
      }
      console.error('Auto-registration failed:', error)
      return false
    }
  }
}

// Export a singleton instance
export const authService = new AuthService()
export type { LoginResponse, User }
