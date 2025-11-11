import { createContext, useContext, useEffect, useState, useCallback } from 'react'
import { apiService } from '@/services/api'
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
          // Store user info for chatbot access
          localStorage.setItem('mantrapath_user', JSON.stringify(enhancedUser))
          setLoading(false)
          return
        } catch (error) {
          // Token is invalid, remove it
          localStorage.removeItem('mantrapath_token')
          localStorage.removeItem('mantrapath_refresh_token')
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
      // Store user info for chatbot access
      localStorage.setItem('mantrapath_user', JSON.stringify(enhancedUser))
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
      
      // Check if email verification is required
      if (result.verification_required) {
        // Email verification is required - user needs to check email
        return result
      } else {
        // No verification required - user can login immediately
        // But we still need them to login manually for security
        return {
          ...result,
          message: result.message || 'Registration successful! Please log in with your credentials.'
        }
      }
    } catch (error) {
      throw error
    }
  }

  const verifyEmail = useCallback(async (token: string) => {
    try {
      const result = await apiService.verifyEmail(token)
      return result
    } catch (error) {
      throw error
    }
  }, [])

  const resendVerification = useCallback(async (email: string) => {
    try {
      const result = await apiService.resendVerification(email)
      return result
    } catch (error) {
      throw error
    }
  }, [])

  const logout = () => {
    apiService.logout()
    localStorage.removeItem('mantrapath_user')
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