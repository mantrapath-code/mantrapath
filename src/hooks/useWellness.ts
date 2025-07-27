import { useState, useEffect, useCallback } from 'react'
import { toast } from 'sonner'
import { apiService } from '@/services/api'

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
        context_tags: moodData.tags
      })

      // Convert and add to local state
      const newEntry: MoodEntry = {
        id: backendEntry.id,
        mood: backendEntry.mood_score,
        energy: backendEntry.energy_level || 5,
        stress: backendEntry.stress_level || 5,
        sleep: backendEntry.sleep_quality || 5,
        note: backendEntry.notes || '',
        tags: backendEntry.context_tags || [],
        timestamp: backendEntry.created_at
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

export const useUserStats = () => {
  // Mock user stats for now - this should connect to backend later
  return {
    stats: {
      moodStreak: 5,
      journalStreak: 3,
      communityContributions: 12,
      unlockedThemes: ['default', 'calm'],
      badges: ['early-bird', 'consistent-tracker'],
      currentTheme: 'default'
    },
    updateStats: () => {}
  }
}

export const useMoodAnalytics = () => {
  const getWeeklyInsights = useCallback(() => {
    // Mock weekly insights for now - this should connect to backend analytics
    return {
      averageMood: 4.2,
      moodVariability: 0.8,
      dominantMood: 'good',
      patterns: [],
      insights: [],
      recommendations: []
    }
  }, [])

  return {
    getWeeklyInsights
  }
}