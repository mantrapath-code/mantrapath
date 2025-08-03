import { createContext, useContext, useEffect, useState } from 'react'
import { apiService } from '@/services/api'
import { ensureDevAuthentication } from '@/utils/devAuth'
import { getUserDisplayName, getUserInitials } from '@/utils/userDisplay'

interface User {
  id: string
  email: string
  username: string
  first_name?: string
  last_name?: string
  is_active: boolean
  is_verified: boolean
  role: string
  created_at?: string
  // Display utilities
  displayName?: string
  initials?: string
}

interface AuthContextType {
  user: User | null
  loading: boolean
  login: (emailOrUsername: string, password: string) => Promise<void>
  register: (userData: {
    email: string
    username: string
    password: string
    first_name: string
    last_name: string
  }) => Promise<{ message: string; verification_required: boolean }>
  logout: () => void
  isAuthenticated: boolean
  verifyEmail: (token: string) => Promise<{ message: string }>
  resendVerification: (email: string) => Promise<{ message: string }>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  // Check for existing session on mount
  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('mantrapath_token')
      if (token) {
        try {
          const userData = await apiService.getCurrentUser()
          // Enhance user data with display utilities
          const enhancedUser = {
            ...userData,
            displayName: getUserDisplayName(userData),
            initials: getUserInitials(userData)
          }
          setUser(enhancedUser)
          setLoading(false)
          return
        } catch (error) {
          // Token is invalid, remove it
          localStorage.removeItem('mantrapath_token')
          localStorage.removeItem('mantrapath_refresh_token')
        }
      }

      // If no valid session, try development auto-login
      if (!import.meta.env.PROD) {
        console.log('🔧 Development mode: Attempting auto-authentication...')
        try {
          const authSuccess = await ensureDevAuthentication()
          if (authSuccess) {
            const userData = await apiService.getCurrentUser()
            // Enhance user data with display utilities
            const enhancedUser = {
              ...userData,
              displayName: getUserDisplayName(userData),
              initials: getUserInitials(userData)
            }
            setUser(enhancedUser)
            console.log('✅ Development auto-authentication successful')
          }
        } catch (error) {
          console.warn('❌ Development auto-authentication failed:', error)
        }
      }
      
      setLoading(false)
    }

    checkAuth()
  }, [])

  const login = async (emailOrUsername: string, password: string) => {
    try {
      await apiService.login(emailOrUsername, password)
      const userData = await apiService.getCurrentUser()
      // Enhance user data with display utilities
      const enhancedUser = {
        ...userData,
        displayName: getUserDisplayName(userData),
        initials: getUserInitials(userData)
      }
      setUser(enhancedUser)
    } catch (error) {
      throw error
    }
  }

  const register = async (userData: {
    email: string
    username: string
    password: string
    first_name: string
    last_name: string
  }) => {
    try {
      const result = await apiService.register(userData)
      // Don't set user after registration since email verification is required
      return result
    } catch (error) {
      throw error
    }
  }

  const verifyEmail = async (token: string) => {
    try {
      const result = await apiService.verifyEmail(token)
      return result
    } catch (error) {
      throw error
    }
  }

  const resendVerification = async (email: string) => {
    try {
      const result = await apiService.resendVerification(email)
      return result
    } catch (error) {
      throw error
    }
  }

  const logout = () => {
    apiService.logout()
    setUser(null)
  }

  const value = {
    user,
    loading,
    login,
    register,
    logout,
    verifyEmail,
    resendVerification,
    isAuthenticated: !!user
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}