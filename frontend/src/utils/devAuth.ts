/**
 * Development authentication utilities for MantraPath
 * Provides automatic authentication during development
 */

import { authService } from '@/services/auth'
import { apiService } from '@/services/api'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

interface DevUser {
  email: string
  username: string
  password: string
  first_name: string
  last_name: string
  skip_verification?: boolean
}

export async function ensureDevAuthentication(): Promise<boolean> {
  // Only run in development mode
  if (import.meta.env.PROD) {
    return false
  }

  // Check if user is already authenticated
  if (authService.isAuthenticated()) {
    // Make sure API service has the latest token
    apiService.refreshToken()
    return true
  }

  console.log('🔧 Development mode: Setting up test authentication...')

  try {
    // Try to login with test credentials first
    try {
      await authService.login('ssharma8132@gmail.com', 'Dev@#123')
      apiService.refreshToken()
      console.log('✅ Logged in with existing test user')
      return true
    } catch (loginError) {
      console.log('Test user login failed, trying to register...')
    }

    // If login fails, try to register the test user
    try {
      await authService.register(
        'ssharma8132@gmail.com',
        'Sachin',
        'Dev@#123'
      )
      console.log('✅ Test user registered')
      
      // Try login again after registration
      await authService.login('ssharma8132@gmail.com', 'Dev@#123')
      apiService.refreshToken()
      console.log('✅ Logged in with new test user')
      return true
    } catch (registerError) {
      console.warn('❌ Could not register test user:', registerError)
    }

    return false
  } catch (error) {
    console.warn('❌ Development authentication setup failed:', error)
    return false
  }
}

/**
 * Force create a verified test user via direct API call
 */
export async function createVerifiedTestUser(): Promise<boolean> {
  try {
    // Create user directly via backend API with verification bypassed
    const response = await fetch(`${API_BASE_URL}/auth/dev/create-test-user`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: 'testuser@mantrapath.com',
        username: 'testuser',
        password: 'TestPassword123!',
        first_name: 'Test',
        last_name: 'User',
        skip_verification: true
      }),
    })

    if (response.ok) {
      console.log('✅ Created verified test user')
      return true
    } else {
      console.warn('❌ Could not create verified test user via API')
      return false
    }
  } catch (error) {
    console.warn('❌ Error creating verified test user:', error)
    return false
  }
}
