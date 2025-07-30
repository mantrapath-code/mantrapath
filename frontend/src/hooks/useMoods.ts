import { useState, useCallback, useEffect } from 'react'
import { toast } from 'sonner'
import { apiService } from '@/services/api'
import { MoodEntry } from '@/types'

/**
 * Mood-specific hook for tracking and managing mood entries
 * Connects to the backend API for real-time data
 */
export function useMoods() {
  const [moods, setMoods] = useState<MoodEntry[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Convert mood string to numeric scale for backend
  const moodToNumber = (mood: MoodEntry['mood']): number => {
    const moodMap = {
      'very-low': 1,
      'low': 2,
      'neutral': 3,
      'good': 4,
      'excellent': 5
    }
    return moodMap[mood] || 3
  }

  // Convert mood number back to string for frontend
  const numberToMood = (score: number): MoodEntry['mood'] => {
    if (score <= 1.5) return 'very-low'
    if (score <= 2.5) return 'low'
    if (score <= 3.5) return 'neutral'
    if (score <= 4.5) return 'good'
    return 'excellent'
  }

  // Convert energy string to number for backend
  const energyToNumber = (energy: 'high' | 'medium' | 'low'): number => {
    const energyMap = { 'low': 1, 'medium': 3, 'high': 5 }
    return energyMap[energy] || 3
  }

  // Add new mood entry with backend integration
  const addMood = useCallback(async (
    mood: MoodEntry['mood'],
    note?: string,
    triggers?: string[]
  ): Promise<MoodEntry> => {
    try {
      setLoading(true)
      setError(null)

      // Create mood entry in backend
      const backendEntry = await apiService.createMoodEntry({
        mood_score: moodToNumber(mood),
        notes: note,
        context_tags: triggers
      })

      // Convert backend response to frontend format
      const moodEntry: MoodEntry = {
        id: backendEntry.id,
        mood,
        mood_level: moodToNumber(mood),
        timestamp: Date.now(),
        note,
        triggers,
        created_at: backendEntry.created_at
      }

      // Update local state
      setMoods(prev => [moodEntry, ...prev])

      toast.success(`Mood logged as ${mood}!`)
      return moodEntry
      
    } catch (err) {
      console.error('Failed to add mood entry:', err)
      setError('Failed to save mood entry')
      toast.error('Failed to save mood entry')
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  // Get mood trend from recent entries
  const getMoodTrend = useCallback(async (): Promise<'positive' | 'concerning' | 'stable'> => {
    try {
      const recentEntries = await apiService.getMoodEntries(7) // Last 7 entries
      
      if (recentEntries.length < 3) return 'stable'
      
      const recentScores = recentEntries.slice(0, 5).map(entry => entry.mood_score)
      const averageRecent = recentScores.reduce((sum, score) => sum + score, 0) / recentScores.length
      
      // Check for concerning pattern (3+ low mood entries)
      const lowMoodCount = recentScores.filter(score => score <= 2).length
      if (lowMoodCount >= 3) return 'concerning'
      
      // Check for positive trend
      if (averageRecent >= 4) return 'positive'
      
      return 'stable'
      
    } catch (err) {
      console.error('Failed to get mood trend:', err)
      return 'stable'
    }
  }, [])

  // Get mood analytics
  const getMoodAnalytics = useCallback(async () => {
    try {
      const [overview, patterns] = await Promise.all([
        apiService.getAnalyticsOverview(),
        apiService.getWeeklyPatterns()
      ])

      return {
        averageMood: overview.average_mood,
        moodTrend: overview.mood_trend,
        totalEntries: overview.total_entries,
        streak: overview.streak,
        weeklyPattern: overview.weekly_pattern,
        patterns: patterns.patterns || []
      }
    } catch (err) {
      console.error('Failed to get mood analytics:', err)
      throw err
    }
  }, [])

  // Get recent mood entries for display
  const getRecentMoods = useCallback(async (limit: number = 10) => {
    try {
      setLoading(true)
      const entries = await apiService.getMoodEntries(limit)
      
      const formattedMoods = entries.map(entry => ({
        id: entry.id,
        mood: numberToMood(entry.mood_score),
        mood_level: entry.mood_score,
        timestamp: new Date(entry.created_at).getTime(),
        note: entry.notes,
        triggers: entry.context_tags,
        created_at: entry.created_at
      })) as MoodEntry[]

      setMoods(formattedMoods)
      return formattedMoods
      
    } catch (err) {
      console.error('Failed to get recent moods:', err)
      setError('Failed to load mood history')
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  // Load moods on mount with error handling
  useEffect(() => {
    getRecentMoods().catch(err => {
      // Silently handle the error - the hook will work with empty state
      console.log('Backend not available, using local state only')
    })
  }, [getRecentMoods])

  return {
    moods,
    addMood,
    getMoodTrend,
    getMoodAnalytics,
    getRecentMoods,
    loading,
    error
  }
}