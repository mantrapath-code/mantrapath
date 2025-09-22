# Story V3-FE-015: Frontend Authentication Integration Fix
**Epic**: Frontend Integration Polish  
**Priority**: P0 | **Points**: 5 | **Assignee**: Frontend Lead

## Story Description
Debug and fix frontend authentication integration issues that are causing 401 errors and preventing seamless user login/logout flows in the development environment.

## Current State Analysis
**Available Foundation**:
- ✅ Auth Service (operational on Port 8001)
- ✅ Frontend application (running on localhost:5173)
- ✅ Backend API services (18 services operational)
- ✅ Basic authentication implementation

**Identified Issues**:
- ❌ Frontend authentication flow returning 401 errors
- ❌ Session management not properly configured
- ❌ Token storage and refresh mechanism issues
- ❌ Development environment authentication setup problems

## Acceptance Criteria

### AC1: User Login/Logout Working Seamlessly
- [ ] Login form submits credentials to Auth Service successfully
- [ ] Successful login returns valid JWT token
- [ ] Token is properly stored in secure browser storage
- [ ] User state is correctly updated after login
- [ ] Logout clears token and user state
- [ ] Protected routes redirect to login when unauthenticated
- [ ] Login redirects to intended page after authentication

### AC2: Session Management Properly Configured
- [ ] JWT token validation on protected API calls
- [ ] Token expiration handling with proper user feedback
- [ ] Session persistence across browser refreshes
- [ ] Automatic logout on token expiration
- [ ] Session timeout warnings for user experience
- [ ] Concurrent session handling (optional)

### AC3: Token Refresh Mechanism Functional
- [ ] Automatic token refresh before expiration
- [ ] Refresh token rotation for enhanced security
- [ ] Graceful handling of refresh failures
- [ ] Background token refresh without user interruption
- [ ] Fallback to login when refresh fails

### AC4: Development Environment Auth Setup
- [ ] Test user accounts configured for development
- [ ] Auth service connection verified in dev environment
- [ ] API endpoint configuration validated
- [ ] CORS settings properly configured
- [ ] Environment variables correctly set

## Detailed Implementation Plan

### Task 1: Authentication Debug (2h)

#### 1.1: Debug Current Authentication Flow
```typescript
// File: frontend/src/services/auth-debug.ts
import { logger } from '@/utils/logger'

export class AuthDebugger {
  static async debugLoginFlow(credentials: LoginCredentials) {
    logger.info('Starting login debug', { email: credentials.email })
    
    try {
      // Test Auth Service connectivity
      const healthResponse = await fetch('http://localhost:8001/health')
      logger.info('Auth service health', { 
        status: healthResponse.status,
        statusText: healthResponse.statusText 
      })
      
      // Test login endpoint
      const loginResponse = await fetch('http://localhost:8001/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email_or_username: credentials.email,
          password: credentials.password
        })
      })
      
      logger.info('Login response', {
        status: loginResponse.status,
        statusText: loginResponse.statusText,
        headers: Object.fromEntries(loginResponse.headers.entries())
      })
      
      if (!loginResponse.ok) {
        const errorText = await loginResponse.text()
        logger.error('Login failed', { 
          status: loginResponse.status,
          error: errorText 
        })
        throw new Error(`Login failed: ${loginResponse.status} - ${errorText}`)
      }
      
      const loginData = await loginResponse.json()
      logger.info('Login successful', { 
        hasToken: !!loginData.access_token,
        tokenLength: loginData.access_token?.length
      })
      
      return loginData
      
    } catch (error) {
      logger.error('Login debug failed', { error: error.message })
      throw error
    }
  }
  
  static async debugTokenValidation(token: string) {
    logger.info('Starting token validation debug')
    
    try {
      // Test token with a protected endpoint
      const response = await fetch('http://localhost:8008/api/v1/insights/unified', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })
      
      logger.info('Token validation response', {
        status: response.status,
        statusText: response.statusText
      })
      
      return response.ok
      
    } catch (error) {
      logger.error('Token validation failed', { error: error.message })
      return false
    }
  }
}
```

#### 1.2: Fix API Endpoint Configuration
```typescript
// File: frontend/src/config/api.ts
export const API_CONFIG = {
  auth: {
    baseUrl: import.meta.env.VITE_AUTH_SERVICE_URL || 'http://localhost:8001',
    endpoints: {
      login: '/login',
      logout: '/logout', 
      refresh: '/refresh',
      validate: '/validate'
    }
  },
  services: {
    gateway: import.meta.env.VITE_API_GATEWAY_URL || 'http://localhost:8000',
    ml: import.meta.env.VITE_ML_SERVICE_URL || 'http://localhost:8008'
  }
}

// CORS configuration check
export const checkCorsConfiguration = async () => {
  try {
    const response = await fetch(`${API_CONFIG.auth.baseUrl}/health`, {
      method: 'OPTIONS'
    })
    
    const corsHeaders = {
      'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
      'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
      'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
    }
    
    console.log('CORS Headers:', corsHeaders)
    return corsHeaders
    
  } catch (error) {
    console.error('CORS check failed:', error)
    return null
  }
}
```

### Task 2: Session Management Implementation (2h)

#### 2.1: Enhanced Auth Store with Zustand
```typescript
// File: frontend/src/stores/authStore.ts
import { create } from 'zustand'
import { persist, subscribeWithSelector } from 'zustand/middleware'
import { AuthService } from '@/services/authService'
import { logger } from '@/utils/logger'

interface User {
  id: string
  email: string
  username: string
  profile?: any
}

interface AuthState {
  user: User | null
  token: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
  
  // Actions
  login: (credentials: LoginCredentials) => Promise<void>
  logout: () => Promise<void>
  refreshAuth: () => Promise<void>
  clearError: () => void
  setUser: (user: User) => void
}

export const useAuthStore = create<AuthState>()(
  subscribeWithSelector(
    persist(
      (set, get) => ({
        user: null,
        token: null,
        refreshToken: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,
        
        login: async (credentials) => {
          set({ isLoading: true, error: null })
          
          try {
            logger.info('Attempting login', { email: credentials.email })
            
            const authData = await AuthService.login(credentials)
            
            set({
              user: authData.user,
              token: authData.access_token,
              refreshToken: authData.refresh_token,
              isAuthenticated: true,
              isLoading: false,
              error: null
            })
            
            logger.info('Login successful', { userId: authData.user.id })
            
            // Start token refresh timer
            AuthService.startTokenRefreshTimer()
            
          } catch (error) {
            logger.error('Login failed', { error: error.message })
            set({
              user: null,
              token: null,
              refreshToken: null,
              isAuthenticated: false,
              isLoading: false,
              error: error.message
            })
            throw error
          }
        },
        
        logout: async () => {
          set({ isLoading: true })
          
          try {
            await AuthService.logout()
            
            set({
              user: null,
              token: null,
              refreshToken: null,
              isAuthenticated: false,
              isLoading: false,
              error: null
            })
            
            logger.info('Logout successful')
            
          } catch (error) {
            logger.error('Logout failed', { error: error.message })
            // Clear state anyway on logout failure
            set({
              user: null,
              token: null,
              refreshToken: null,
              isAuthenticated: false,
              isLoading: false,
              error: null
            })
          }
        },
        
        refreshAuth: async () => {
          const { refreshToken } = get()
          
          if (!refreshToken) {
            throw new Error('No refresh token available')
          }
          
          try {
            const authData = await AuthService.refreshToken(refreshToken)
            
            set({
              token: authData.access_token,
              refreshToken: authData.refresh_token || refreshToken,
              error: null
            })
            
            logger.info('Token refreshed successfully')
            
          } catch (error) {
            logger.error('Token refresh failed', { error: error.message })
            
            // Clear auth state on refresh failure
            set({
              user: null,
              token: null,
              refreshToken: null,
              isAuthenticated: false,
              error: 'Session expired. Please login again.'
            })
            
            throw error
          }
        },
        
        clearError: () => set({ error: null }),
        
        setUser: (user) => set({ user })
      }),
      {
        name: 'auth-storage',
        partialize: (state) => ({
          user: state.user,
          token: state.token,
          refreshToken: state.refreshToken,
          isAuthenticated: state.isAuthenticated
        })
      }
    )
  )
)

// Auto-refresh setup
useAuthStore.subscribe(
  (state) => state.token,
  (token) => {
    if (token) {
      AuthService.startTokenRefreshTimer()
    } else {
      AuthService.stopTokenRefreshTimer()
    }
  }
)
```

#### 2.2: Enhanced Auth Service
```typescript
// File: frontend/src/services/authService.ts
import { API_CONFIG } from '@/config/api'
import { logger } from '@/utils/logger'

export interface LoginCredentials {
  email: string
  password: string
}

export interface AuthResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
  user: {
    id: string
    email: string
    username: string
    profile?: any
  }
}

class AuthServiceImpl {
  private refreshTimer: NodeJS.Timeout | null = null
  private readonly TOKEN_REFRESH_MARGIN = 5 * 60 * 1000 // 5 minutes before expiry
  
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    try {
      const response = await fetch(`${API_CONFIG.auth.baseUrl}/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email_or_username: credentials.email,
          password: credentials.password
        })
      })
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Login failed' }))
        throw new Error(errorData.detail || `HTTP ${response.status}`)
      }
      
      const authData = await response.json()
      
      // Validate response structure
      if (!authData.access_token || !authData.user) {
        throw new Error('Invalid authentication response')
      }
      
      return authData
      
    } catch (error) {
      logger.error('Auth service login failed', { error: error.message })
      throw new Error(`Login failed: ${error.message}`)
    }
  }
  
  async logout(): Promise<void> {
    try {
      const token = this.getStoredToken()
      
      if (token) {
        await fetch(`${API_CONFIG.auth.baseUrl}/logout`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        })
      }
      
      this.stopTokenRefreshTimer()
      
    } catch (error) {
      logger.error('Logout request failed', { error: error.message })
      // Continue with logout even if server request fails
    }
  }
  
  async refreshToken(refreshToken: string): Promise<AuthResponse> {
    try {
      const response = await fetch(`${API_CONFIG.auth.baseUrl}/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          refresh_token: refreshToken
        })
      })
      
      if (!response.ok) {
        throw new Error(`Token refresh failed: HTTP ${response.status}`)
      }
      
      return await response.json()
      
    } catch (error) {
      logger.error('Token refresh failed', { error: error.message })
      throw error
    }
  }
  
  async validateToken(token: string): Promise<boolean> {
    try {
      const response = await fetch(`${API_CONFIG.auth.baseUrl}/validate`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })
      
      return response.ok
      
    } catch (error) {
      logger.error('Token validation failed', { error: error.message })
      return false
    }
  }
  
  startTokenRefreshTimer() {
    this.stopTokenRefreshTimer()
    
    // Set timer to refresh token before expiry
    this.refreshTimer = setTimeout(() => {
      this.handleTokenRefresh()
    }, this.TOKEN_REFRESH_MARGIN)
  }
  
  stopTokenRefreshTimer() {
    if (this.refreshTimer) {
      clearTimeout(this.refreshTimer)
      this.refreshTimer = null
    }
  }
  
  private async handleTokenRefresh() {
    try {
      const { refreshAuth } = await import('@/stores/authStore')
      await refreshAuth()
    } catch (error) {
      logger.error('Automatic token refresh failed', { error: error.message })
    }
  }
  
  private getStoredToken(): string | null {
    try {
      const authStorage = localStorage.getItem('auth-storage')
      const parsedStorage = authStorage ? JSON.parse(authStorage) : null
      return parsedStorage?.state?.token || null
    } catch (error) {
      return null
    }
  }
}

export const AuthService = new AuthServiceImpl()
```

### Task 3: Development Environment Setup (1h)

#### 3.1: Environment Configuration
```typescript
// File: frontend/.env.development
VITE_AUTH_SERVICE_URL=http://localhost:8001
VITE_API_GATEWAY_URL=http://localhost:8000
VITE_ML_SERVICE_URL=http://localhost:8008
VITE_LOG_LEVEL=debug

# Development test users
VITE_DEV_TEST_USER_EMAIL=dev@mantrapath.com
VITE_DEV_TEST_USER_PASSWORD=dev123
```

```typescript
// File: frontend/src/config/development.ts
export const DEV_CONFIG = {
  testUsers: [
    {
      email: 'dev@mantrapath.com',
      password: 'dev123',
      username: 'developer',
      role: 'admin'
    },
    {
      email: 'test@mantrapath.com', 
      password: 'test123',
      username: 'testuser',
      role: 'user'
    }
  ],
  
  autoLogin: import.meta.env.VITE_AUTO_LOGIN === 'true',
  
  debugMode: import.meta.env.VITE_LOG_LEVEL === 'debug'
}

// Development helper functions
export const DevHelpers = {
  async createTestUsers() {
    // Helper to create test users in development
    console.log('Creating test users for development...')
    
    for (const user of DEV_CONFIG.testUsers) {
      try {
        await fetch(`${API_CONFIG.auth.baseUrl}/register`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(user)
        })
        console.log(`Test user created: ${user.email}`)
      } catch (error) {
        console.log(`Test user may already exist: ${user.email}`)
      }
    }
  },
  
  async autoLogin() {
    if (DEV_CONFIG.autoLogin) {
      const { login } = useAuthStore.getState()
      try {
        await login(DEV_CONFIG.testUsers[0])
        console.log('Auto-login successful')
      } catch (error) {
        console.log('Auto-login failed:', error.message)
      }
    }
  }
}
```

#### 3.2: Auth Integration Testing
```typescript
// File: frontend/src/tests/auth-integration.test.ts
import { describe, it, expect, beforeEach } from 'vitest'
import { AuthService } from '@/services/authService'
import { DEV_CONFIG } from '@/config/development'

describe('Auth Integration Tests', () => {
  beforeEach(() => {
    // Clear any existing auth state
    localStorage.clear()
  })
  
  it('should login with valid credentials', async () => {
    const credentials = DEV_CONFIG.testUsers[0]
    
    const authData = await AuthService.login(credentials)
    
    expect(authData.access_token).toBeDefined()
    expect(authData.user).toBeDefined()
    expect(authData.user.email).toBe(credentials.email)
  })
  
  it('should fail login with invalid credentials', async () => {
    const invalidCredentials = {
      email: 'invalid@test.com',
      password: 'wrongpassword'
    }
    
    await expect(AuthService.login(invalidCredentials)).rejects.toThrow()
  })
  
  it('should validate valid token', async () => {
    const credentials = DEV_CONFIG.testUsers[0]
    const authData = await AuthService.login(credentials)
    
    const isValid = await AuthService.validateToken(authData.access_token)
    expect(isValid).toBe(true)
  })
  
  it('should refresh token successfully', async () => {
    const credentials = DEV_CONFIG.testUsers[0]
    const authData = await AuthService.login(credentials)
    
    if (authData.refresh_token) {
      const refreshedData = await AuthService.refreshToken(authData.refresh_token)
      expect(refreshedData.access_token).toBeDefined()
      expect(refreshedData.access_token).not.toBe(authData.access_token)
    }
  })
})
```

## Integration Points

### Frontend-Backend Integration
- **Auth Service API**: Login, logout, token refresh, validation endpoints
- **Protected Routes**: API calls requiring authentication
- **User State Management**: Synchronization between frontend and backend user state
- **Error Handling**: Graceful handling of authentication errors

### Service Dependencies
- **Auth Service (Port 8001)**: Primary authentication service
- **API Gateway (Port 8000)**: Route protection and token validation
- **ML Service (Port 8008)**: Example protected service for testing

## Performance Requirements
- **Login Response Time**: <2 seconds for successful login
- **Token Validation**: <500ms for token validation calls
- **Session Persistence**: Immediate session restoration on page refresh
- **Error Recovery**: <1 second for error state clearing
- **Token Refresh**: Background refresh without user interruption

## User Experience Requirements
- **Seamless Login**: One-click login with proper feedback
- **Clear Error Messages**: User-friendly authentication error messages
- **Session Indicators**: Clear indication of authentication status
- **Auto-Logout**: Graceful handling of session expiration
- **Remember Login**: Optional persistent login state

## Testing Strategy
- **Unit Tests**: Auth service methods and store actions
- **Integration Tests**: Complete login/logout flows
- **E2E Tests**: User authentication scenarios
- **Error Handling Tests**: Invalid credentials, network failures
- **Performance Tests**: Login response times and token refresh

## Security Considerations
- **Token Storage**: Secure storage in httpOnly cookies or secure localStorage
- **Token Expiration**: Proper handling of expired tokens
- **CSRF Protection**: CSRF token validation where applicable
- **XSS Prevention**: Secure token handling and storage
- **Password Security**: No password storage in frontend

## Risk Mitigation
1. **Service Unavailability**: Graceful degradation when auth service is down
2. **Network Issues**: Retry logic for transient network failures
3. **Token Security**: Secure token storage and transmission
4. **Session Management**: Proper cleanup on logout and session expiration
5. **User Experience**: Clear feedback for all authentication states

## Definition of Done
- [ ] User can login successfully with valid credentials
- [ ] Login errors are properly handled and displayed
- [ ] Session persists across browser refreshes
- [ ] Token refresh works automatically in background
- [ ] Logout clears all authentication state
- [ ] Protected routes redirect to login when unauthenticated
- [ ] Development environment has test users configured
- [ ] All authentication integration tests passing
- [ ] Performance requirements met
- [ ] Error handling comprehensive and user-friendly
