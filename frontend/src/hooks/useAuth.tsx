import { createContext, useContext, useEffect, useState } from 'react'
import { apiService } from '@/services/api'

interface User {
  id: string
  email: string
  username: string
  first_name?: string
  last_name?: string
  is_active: boolean
  role: string
  created_at?: string
}

interface AuthContextType {
  user: User | null
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (userData: {
    email: string
    username: string
    password: string
    first_name?: string
    last_name?: string
  }) => Promise<void>
  logout: () => void
  isAuthenticated: boolean
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
          setUser(userData)
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

  const login = async (email: string, password: string) => {
    try {
      await apiService.login(email, password)
      const userData = await apiService.getCurrentUser()
      setUser(userData)
    } catch (error) {
      throw error
    }
  }

  const register = async (userData: {
    email: string
    username: string
    password: string
    first_name?: string
    last_name?: string
  }) => {
    try {
      await apiService.register(userData)
      const user = await apiService.getCurrentUser()
      setUser(user)
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