import { useEffect, useState } from 'react'
import { authService } from '@/services/auth'
import { apiService } from '@/services/api'
import { Loader2 } from 'lucide-react'

interface AuthInitializerProps {
  children: React.ReactNode
}

export function AuthInitializer({ children }: AuthInitializerProps) {
  const [authStatus, setAuthStatus] = useState<'checking' | 'authenticated' | 'unauthenticated'>('checking')

  useEffect(() => {
    initializeAuth()
  }, [])

  const initializeAuth = async () => {
    try {
      setAuthStatus('checking')

      // Check for force logout parameter (for testing)
      const urlParams = new URLSearchParams(window.location.search)
      if (urlParams.get('logout') === 'true') {
        console.log('🔧 Force logout requested')
        authService.clearAuth()
        // Clean URL
        window.history.replaceState({}, document.title, window.location.pathname)
      }

      // Check if user is already authenticated
      if (authService.isAuthenticated()) {
        console.log('✅ User already authenticated')
        apiService.refreshToken()
        setAuthStatus('authenticated')
        return
      }

      // No existing authentication, require login
      console.log('🔐 No authentication found, user must login')
      setAuthStatus('unauthenticated')
    } catch (err) {
      console.error('Auth initialization failed:', err)
      setAuthStatus('unauthenticated')
    }
  }

  if (authStatus === 'checking') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-purple-50">
        <div className="text-center space-y-4">
          <Loader2 className="h-8 w-8 animate-spin mx-auto text-blue-600" />
          <h2 className="text-xl font-semibold text-gray-800">Initializing MantraPath...</h2>
          <p className="text-gray-600">Setting up your wellness journey</p>
        </div>
      </div>
    )
  }

  if (authStatus === 'authenticated') {
    // User is authenticated, render the app
    return <>{children}</>
  }

  // User needs to login - return null so App component can render AuthScreen
  return null
}
