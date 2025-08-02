import { useState, useEffect } from 'react'
import { apiService } from '@/services/api'

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
      const updatedProfile = await apiService.updateProfile(data) as UserProfile
      setProfile(updatedProfile)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update profile')
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
