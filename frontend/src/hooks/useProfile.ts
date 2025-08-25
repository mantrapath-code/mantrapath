import { useState, useEffect } from 'react'
import { apiService } from '@/services/api'
import { authService } from '@/services/auth'

interface UserProfile {
  id: string
  user_id: string
  bio?: string
  avatar_url?: string
  timezone: string
  date_of_birth?: string
  location?: string
  theme: string
  privacy_level: string
  created_at: string
  updated_at: string
}

interface ProfileStats {
  daysActive: number
  moodEntries: number
  avgMoodScore: number
}

interface UseProfileReturn {
  profile: UserProfile | null
  stats: ProfileStats | null
  loading: boolean
  error: string | null
  updateProfile: (data: Partial<UserProfile>) => Promise<void>
  refreshProfile: () => Promise<void>
}

export function useProfile(): UseProfileReturn {
  const [profile, setProfile] = useState<UserProfile | null>(null)
  const [stats, setStats] = useState<ProfileStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchProfile = async () => {
    try {
      setLoading(true)
      setError(null)
      
      // Ensure we have authentication token
      if (!authService.isAuthenticated()) {
        console.log('🔐 Authentication required')
        setProfile(null)
        setStats(null)
        setError('Authentication required to load profile')
        return
      }

      // Refresh API service token
      apiService.refreshToken()
      
      const [profileData, statsData] = await Promise.all([
        apiService.getMyProfile(),
        apiService.getMyProfileStats()
      ])
      
      setProfile(profileData)
      setStats(statsData)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch profile')
      console.error('Profile fetch error:', err)
    } finally {
      setLoading(false)
    }
  }

  const updateProfile = async (data: Partial<UserProfile>) => {
    try {
      setError(null)
      
      // Map frontend fields to backend fields (only send supported fields)
      const updateData: any = {}
      if (data.bio !== undefined) updateData.bio = data.bio
      if (data.timezone !== undefined) updateData.timezone = data.timezone
      if (data.theme !== undefined) updateData.theme_preference = data.theme
      if (data.privacy_level !== undefined) updateData.privacy_mode = data.privacy_level === 'private'
      
      // Note: location and date_of_birth are not supported by backend ProfileUpdate schema
      // These will be ignored for now until backend support is added
      
      console.log('🔄 Updating profile with data:', updateData)
      
      // Send update to backend
      const response = await apiService.updateProfile(updateData)
      console.log('✅ Profile update response:', response)
      
      // Refresh profile data from server to ensure consistency
      await fetchProfile()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update profile')
      console.error('❌ Profile update error:', err)
      throw err
    }
  }

  const refreshProfile = async () => {
    await fetchProfile()
  }

  useEffect(() => {
    fetchProfile()
  }, [])

  return {
    profile,
    stats,
    loading,
    error,
    updateProfile,
    refreshProfile
  }
}
