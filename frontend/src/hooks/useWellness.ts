import { useState, useEffect, useCallback } from 'react'
import { toast } from 'sonner'
import { apiService } from '@/services/api'
import { useAuth } from '@/hooks/useAuth'
import { MoodEntry as BackendMoodEntry } from '@/types/index'

// Local interface for frontend-specific mood entry structure
export interface MoodEntry {
  id: string
  mood: number
  energy: number
  stress: number
  sleep: number
  note: string
  tags: string[]
  timestamp: string
}

export interface MoodAnalytics {
  averageMood: number
  moodTrend: 'improving' | 'declining' | 'stable'
  totalEntries: number
  streak: number
  weeklyPattern: Record<string, number>
  monthlySummary: {
    highestMood: number
    lowestMood: number
    totalDaysTracked: number
    mostCommonStressLevel: number
  }
  patterns: Array<{
    type: string
    severity: string
    message: string
    recommendation: string
  }>
}

export function useWellness() {
  const [moodEntries, setMoodEntries] = useState<MoodEntry[]>([])
  const [analytics, setAnalytics] = useState<MoodAnalytics | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Load mood entries from backend
  const loadMoodEntries = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)

      const backendEntries = await apiService.getMoodEntries(100)
      
      // Convert backend format to frontend format
      const formattedEntries: MoodEntry[] = backendEntries.map(entry => ({
        id: entry.id,
        mood: entry.mood_score,
        energy: entry.energy_level || 5,
        stress: entry.stress_level || 5,
        sleep: entry.sleep_quality || 5,
        note: entry.notes || '',
        tags: entry.context_tags || [],
        timestamp: entry.created_at
      }))

      setMoodEntries(formattedEntries)
      
    } catch (err) {
      console.error('Failed to load mood entries:', err)
      setError('Failed to load mood data')
      toast.error('Failed to load mood data')
    } finally {
      setLoading(false)
    }
  }, [])

  // Load analytics from backend
  const loadAnalytics = useCallback(async () => {
    try {
      const [overview, patterns] = await Promise.all([
        apiService.getAnalyticsOverview(),
        apiService.getWeeklyPatterns()
      ])

      const analyticsData: MoodAnalytics = {
        averageMood: overview.average_mood,
        moodTrend: overview.mood_trend as 'improving' | 'declining' | 'stable',
        totalEntries: overview.total_entries,
        streak: overview.streak,
        weeklyPattern: overview.weekly_pattern,
        monthlySummary: {
          highestMood: overview.monthly_summary.highest_mood || 10,
          lowestMood: overview.monthly_summary.lowest_mood || 1,
          totalDaysTracked: overview.monthly_summary.total_days_tracked || 0,
          mostCommonStressLevel: overview.monthly_summary.most_common_stress_level || 5
        },
        patterns: patterns.patterns || []
      }

      setAnalytics(analyticsData)
      
    } catch (err) {
      console.error('Failed to load analytics:', err)
      setError('Failed to load analytics')
    }
  }, [])

  // Load data on mount
  useEffect(() => {
    loadMoodEntries()
    loadAnalytics()
  }, [loadMoodEntries, loadAnalytics])

  // Add new mood entry
  const addMoodEntry = useCallback(async (moodData: {
    mood: number
    energy?: number
    stress?: number
    sleep?: number
    note?: string
    tags?: string[]
    emotional_granularity?: number
    mood_confidence?: number
    adaptive_responses?: any[]
    environmental_context?: any
  }) => {
    try {
      setLoading(true)
      setError(null)

      const backendEntry = await apiService.createMoodEntry({
        mood_score: moodData.mood,
        energy_level: moodData.energy,
        stress_level: moodData.stress,
        sleep_quality: moodData.sleep,
        notes: moodData.note,
        context_tags: moodData.tags,
        emotional_granularity: moodData.emotional_granularity,
        mood_confidence: moodData.mood_confidence,
        adaptive_responses: moodData.adaptive_responses,
        environmental_context: moodData.environmental_context
      })

      // Convert and add to local state
      const backendEntryTyped = backendEntry as {
        id: string
        mood_score: number
        energy_level?: number
        stress_level?: number
        sleep_quality?: number
        notes?: string
        context_tags?: string[]
        created_at: string
      }
      
      const newEntry: MoodEntry = {
        id: backendEntryTyped.id,
        mood: backendEntryTyped.mood_score,
        energy: backendEntryTyped.energy_level || 5,
        stress: backendEntryTyped.stress_level || 5,
        sleep: backendEntryTyped.sleep_quality || 5,
        note: backendEntryTyped.notes || '',
        tags: backendEntryTyped.context_tags || [],
        timestamp: backendEntryTyped.created_at
      }

      setMoodEntries(prev => [newEntry, ...prev])
      
      // Refresh analytics
      loadAnalytics()
      
      toast.success('Mood entry saved!')
      return newEntry
      
    } catch (err) {
      console.error('Failed to save mood entry:', err)
      setError('Failed to save mood entry')
      toast.error('Failed to save mood entry')
      throw err
    } finally {
      setLoading(false)
    }
  }, [loadAnalytics])

  // Get recent mood timeline for charts
  const getRecentMoodTimeline = useCallback((days: number = 30) => {
    const cutoff = new Date()
    cutoff.setDate(cutoff.getDate() - days)
    
    return moodEntries
      .filter(entry => new Date(entry.timestamp) >= cutoff)
      .sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime())
      .map(entry => ({
        date: entry.timestamp.split('T')[0],
        mood: entry.mood,
        energy: entry.energy,
        stress: entry.stress,
        sleep: entry.sleep
      }))
  }, [moodEntries])

  // Get mood by time of day
  const getMoodByTimeOfDay = useCallback(() => {
    const timeGroups = {
      morning: [] as number[],
      afternoon: [] as number[],
      evening: [] as number[],
      night: [] as number[]
    }

    moodEntries.forEach(entry => {
      const hour = new Date(entry.timestamp).getHours()
      if (hour >= 6 && hour < 12) timeGroups.morning.push(entry.mood)
      else if (hour >= 12 && hour < 17) timeGroups.afternoon.push(entry.mood)
      else if (hour >= 17 && hour < 22) timeGroups.evening.push(entry.mood)
      else timeGroups.night.push(entry.mood)
    })

    return Object.entries(timeGroups).map(([time, moods]) => ({
      time,
      averageMood: moods.length > 0 ? moods.reduce((sum, mood) => sum + mood, 0) / moods.length : 0,
      count: moods.length
    }))
  }, [moodEntries])

  // Get current mood state for theme
  const getCurrentMoodState = useCallback(() => {
    if (moodEntries.length === 0) return 'neutral'
    
    const recentEntries = moodEntries.slice(0, 3) // Last 3 entries
    const averageRecentMood = recentEntries.reduce((sum, entry) => sum + entry.mood, 0) / recentEntries.length
    
    if (averageRecentMood >= 8) return 'excellent'
    if (averageRecentMood >= 6) return 'good'
    if (averageRecentMood >= 4) return 'neutral'
    if (averageRecentMood >= 2) return 'low'
    return 'very-low'
  }, [moodEntries])

  return {
    moodEntries,
    analytics,
    loading,
    error,
    actions: {
      addMoodEntry,
      loadMoodEntries,
      loadAnalytics,
      getRecentMoodTimeline,
      getMoodByTimeOfDay,
      getCurrentMoodState,
      refresh: () => {
        loadMoodEntries()
        loadAnalytics()
      }
    }
  }
}

// Export legacy hook names for backward compatibility  
export const useMoodData = () => {
  const wellness = useWellness()
  return {
    moods: wellness.moodEntries,
    getMoodTrend: () => wellness.analytics?.moodTrend || 'stable',
    addMood: wellness.actions.addMoodEntry,
    loading: wellness.loading
  }
}

// Export for components expecting useMoods from useWellness
export const useMoods = () => {
  const wellness = useWellness()
  return {
    moods: wellness.moodEntries,
    addMood: wellness.actions.addMoodEntry,
    getMoodTrend: () => wellness.analytics?.moodTrend || 'stable',
    getMoodAnalytics: wellness.analytics,
    getRecentMoods: wellness.actions.loadMoodEntries,
    loading: wellness.loading,
    error: wellness.error
  }
}

export const useUserStats = () => {
  const { isAuthenticated } = useAuth()
  const [stats, setStats] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchStats = useCallback(async () => {
    if (!isAuthenticated) return

    setLoading(true)
    setError(null)
    try {
      const data = await apiService.getUserStats()
      setStats(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch user stats')
    } finally {
      setLoading(false)
    }
  }, [isAuthenticated])

  useEffect(() => {
    fetchStats()
  }, [fetchStats])

  const updateStats = useCallback(() => {
    fetchStats()
  }, [fetchStats])

  return {
    stats,
    updateStats,
    loading,
    error
  }
}

export const useMoodAnalytics = () => {
  const [personalizedInsights, setPersonalizedInsights] = useState<any>(null)
  const [optimalTimes, setOptimalTimes] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  const getPersonalizedInsights = useCallback(async () => {
    setLoading(true)
    try {
      const insights = await apiService.getPersonalizedInsights()
      setPersonalizedInsights(insights)
      return insights
    } catch (error) {
      console.error('Failed to fetch personalized insights:', error)
      // Return null instead of fallback insights
      setPersonalizedInsights(null)
      return null
    } finally {
      setLoading(false)
    }
  }, [])

  const getOptimalNotificationTimes = useCallback(async () => {
    try {
      const times = await apiService.getOptimalNotificationTimes()
      setOptimalTimes(times)
      return times
    } catch (error) {
      console.error('Failed to fetch optimal notification times:', error)
      return null
    }
  }, [])

  const getWeeklyInsights = useCallback(() => {
    // Return real weekly insights from backend data
    if (personalizedInsights && personalizedInsights.weekly_summary) {
      return {
        averageMood: personalizedInsights.weekly_summary.current_week_score || 0,
        moodVariability: personalizedInsights.weekly_summary.variability || 0,
        dominantMood: personalizedInsights.weekly_summary.trend === 'improving' ? 'good' : 'neutral',
        patterns: personalizedInsights.weekly_summary.patterns || [],
        insights: personalizedInsights.insights || [],
        recommendations: personalizedInsights.recommendations || []
      }
    }
    
    return {
      averageMood: 4.2,
      moodVariability: 0.8,
      dominantMood: 'good',
      patterns: [],
      insights: [],
      recommendations: []
    }
  }, [personalizedInsights])

  const scheduleSmartNotifications = useCallback(async () => {
    try {
      const response = await fetch('/api/notifications/schedule-smart-notifications', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('mantrapath_token')}`
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        return data
      } else {
        throw new Error('Failed to schedule notifications')
      }
    } catch (error) {
      console.error('Error scheduling smart notifications:', error)
      return null
    }
  }, [])

  return {
    personalizedInsights,
    optimalTimes,
    loading,
    getPersonalizedInsights,
    getOptimalNotificationTimes,
    getWeeklyInsights,
    scheduleSmartNotifications
  }
}