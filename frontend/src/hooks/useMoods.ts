import { useState, useCallback, useEffect, useMemo, useRef } from 'react'
import { toast } from 'sonner'
import { apiService } from '@/services/api'
import { MoodEntry } from '@/types/index'

// Debounce utility
function debounce<T extends (...args: any[]) => void>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null
  return (...args: Parameters<T>) => {
    if (timeout) clearTimeout(timeout)
    timeout = setTimeout(() => func(...args), wait)
  }
}

/**
 * Enhanced Mood-specific hook for tracking and managing mood entries
 * Phase 2 Optimizations: Memoization, debouncing, caching
 * Connects to the backend API for real-time data
 */
export function useMoods() {
  const [moods, setMoods] = useState<MoodEntry[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  // Cache for API responses
  const cacheRef = useRef<{ [key: string]: { data: any; timestamp: number } }>({})
  const CACHE_DURATION = 5 * 60 * 1000 // 5 minutes

  // Memoized calculations to avoid recalculating on every render
  const moodAnalytics = useMemo(() => {
    if (moods.length === 0) return null

    const moodValues = {
      'very-low': 1,
      'low': 2,
      'neutral': 3,
      'good': 4,
      'excellent': 5
    }

    const recentMoods = moods.slice(0, 7) // Last 7 entries
    const averageMood = recentMoods.reduce((sum, mood) => sum + moodValues[mood.mood], 0) / recentMoods.length
    
    // Calculate trend
    const firstHalf = recentMoods.slice(0, Math.ceil(recentMoods.length / 2))
    const secondHalf = recentMoods.slice(Math.ceil(recentMoods.length / 2))
    
    const firstAvg = firstHalf.reduce((sum, mood) => sum + moodValues[mood.mood], 0) / firstHalf.length
    const secondAvg = secondHalf.reduce((sum, mood) => sum + moodValues[mood.mood], 0) / secondHalf.length
    
    const trend = secondAvg > firstAvg ? 'improving' : secondAvg < firstAvg ? 'declining' : 'stable'
    
    return {
      averageMood,
      trend,
      recentCount: recentMoods.length,
      totalEntries: moods.length
    }
  }, [moods])

  // Cached API call helper
  const getCachedOrFetch = useCallback(async <T>(
    key: string,
    fetchFn: () => Promise<T>
  ): Promise<T> => {
    const cached = cacheRef.current[key]
    const now = Date.now()
    
    if (cached && (now - cached.timestamp) < CACHE_DURATION) {
      return cached.data
    }
    
    const data = await fetchFn()
    cacheRef.current[key] = { data, timestamp: now }
    return data
  }, [])

  // Convert mood string to numeric scale for backend
  const moodToNumber = (mood: MoodEntry['mood']): number => {
    const moodMap = {
      'very-low': 1,
      'low': 3,
      'neutral': 5,
      'good': 7,
      'excellent': 9
    }
    return moodMap[mood] || 5
  }

  // Convert mood number back to string for frontend
  const numberToMood = (score: number): MoodEntry['mood'] => {
    // Handle 1-10 scale from backend
    if (score <= 2) return 'very-low'
    if (score <= 4) return 'low'
    if (score <= 6) return 'neutral'
    if (score <= 8) return 'good'
    return 'excellent'
  }

  // Convert energy string to number for backend
  const energyToNumber = (energy: 'high' | 'medium' | 'low'): number => {
    const energyMap = { 'low': 2, 'medium': 5, 'high': 8 }
    return energyMap[energy] || 5
  }

  // Convert energy number back to string for frontend
  const numberToEnergy = (level: number): 'high' | 'medium' | 'low' => {
    if (level <= 3) return 'low'
    if (level <= 6) return 'medium'
    return 'high'
  }

  // Optimized add mood entry with debouncing and error handling
  const addMoodEntry = async (
    mood: MoodEntry['mood'],
    note?: string,
    triggers?: string[],
    enhancedData?: {
      energy?: 'high' | 'medium' | 'low'
      stress?: number
      sleep?: number
      emotions?: string[]
      reflection?: string
      emotional_granularity?: number
      mood_confidence?: number
      adaptive_responses?: any[]
    }
  ): Promise<MoodEntry> => {
    try {
      setLoading(true)
      setError(null)

      // Create enhanced mood entry in backend
      const backendEntry = await apiService.createMoodEntry({
        mood_score: moodToNumber(mood),
        energy_level: enhancedData?.energy ? energyToNumber(enhancedData.energy) : undefined,
        stress_level: enhancedData?.stress,
        sleep_quality: enhancedData?.sleep,
        notes: note || enhancedData?.reflection,
        context_tags: triggers || [],
        emotional_granularity: enhancedData?.emotional_granularity,
        mood_confidence: enhancedData?.mood_confidence,
        adaptive_responses: enhancedData?.adaptive_responses,
        environmental_context: {
          timestamp: Date.now(),
          source: 'web_app'
        }
      })

      // Convert backend response to frontend format
      const moodEntry: MoodEntry = {
        id: (backendEntry as any)?.id || Date.now().toString(),
        mood,
        mood_level: moodToNumber(mood),
        timestamp: Date.now(),
        note: note || enhancedData?.reflection,
        triggers: triggers,
        energy: enhancedData?.energy,
        energy_level: enhancedData?.energy ? energyToNumber(enhancedData.energy) : undefined,
        stress_level: enhancedData?.stress,
        sleep_quality: enhancedData?.sleep,
        context_tags: triggers
      }

      // Update local state optimistically
      setMoods(prev => [moodEntry, ...prev])
      
      // Clear relevant caches
      cacheRef.current = {}

      toast.success(`Enhanced mood logged as ${mood}!`)
      return moodEntry
      
    } catch (err) {
      console.error('Failed to add mood entry:', err)
      setError('Failed to save mood entry')
      toast.error('Failed to save mood entry')
      throw err
    } finally {
      setLoading(false)
    }
  }

  // Debounced version of addMood for rapid-fire prevention
  const debouncedAddMood = useCallback(
    debounce(addMoodEntry, 1000), // 1 second debounce
    []
  )

  // Public addMood function (backwards compatibility)
  const addMood = useCallback(async (
    mood: MoodEntry['mood'],
    note?: string,
    triggers?: string[],
    enhancedData?: {
      energy?: 'high' | 'medium' | 'low'
      stress?: number
      sleep?: number
      emotions?: string[]
      reflection?: string
      emotional_granularity?: number
      mood_confidence?: number
      adaptive_responses?: any[]
    }
  ): Promise<MoodEntry> => {
    try {
      setLoading(true)
      setError(null)

      // Create enhanced mood entry in backend
      const backendEntry = await apiService.createMoodEntry({
        mood_score: moodToNumber(mood),
        energy_level: enhancedData?.energy ? energyToNumber(enhancedData.energy) : undefined,
        stress_level: enhancedData?.stress,
        sleep_quality: enhancedData?.sleep,
        notes: note || enhancedData?.reflection,
        context_tags: triggers || [],
        emotional_granularity: enhancedData?.emotional_granularity,
        mood_confidence: enhancedData?.mood_confidence,
        adaptive_responses: enhancedData?.adaptive_responses,
        environmental_context: {
          emotions: enhancedData?.emotions || [],
          activities: triggers || []
        }
      }) as any

      // Convert backend response to frontend format
      const moodEntry: MoodEntry = {
        id: backendEntry.id || `mood_${Date.now()}`,
        mood,
        mood_level: moodToNumber(mood),
        timestamp: Date.now(),
        note: note || enhancedData?.reflection,
        triggers,
        created_at: backendEntry.created_at || new Date().toISOString(),
        energy: enhancedData?.energy,
        energy_level: enhancedData?.energy ? energyToNumber(enhancedData.energy) : undefined,
        context_tags: triggers || []
      }

      // Update local state
      setMoods(prev => [moodEntry, ...prev])

      toast.success(`Enhanced mood logged as ${mood}!`)
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

  // Get mood analytics with enhanced insights
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
        notes: entry.notes, // Backend compatibility
        triggers: entry.context_tags,
        context_tags: entry.context_tags, // Backend compatibility
        created_at: entry.created_at,
        energy: entry.energy_level ? numberToEnergy(entry.energy_level) : undefined,
        energy_level: entry.energy_level,
        user_id: entry.id // Assuming user context from backend
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

  // Get mood insights for timeline display
  const getMoodInsights = useCallback(async (timeRange: 'week' | 'month' | 'quarter' = 'week') => {
    try {
      const limit = timeRange === 'week' ? 50 : timeRange === 'month' ? 150 : 500
      const entries = await getRecentMoods(limit)
      
      // Calculate insights from the data
      const totalEntries = entries.length
      const averageMood = entries.reduce((sum, entry) => sum + entry.mood_level, 0) / totalEntries
      const energyData = entries.filter(e => e.energy).map(e => e.energy)
      const moodCounts = entries.reduce((acc, entry) => {
        acc[entry.mood] = (acc[entry.mood] || 0) + 1
        return acc
      }, {} as Record<string, number>)

      return {
        totalEntries,
        averageMood,
        moodDistribution: moodCounts,
        energyDistribution: energyData.reduce((acc, energy) => {
          acc[energy!] = (acc[energy!] || 0) + 1
          return acc
        }, {} as Record<string, number>),
        timeRange,
        lastEntry: entries[0],
        entries
      }
    } catch (err) {
      console.error('Failed to get mood insights:', err)
      throw err
    }
  }, [getRecentMoods])

  // Load moods on mount with error handling
  useEffect(() => {
    // Only try to load moods if there's a token (user is authenticated)
    const token = localStorage.getItem('mantrapath_token')
    if (token) {
      getRecentMoods().catch(err => {
        // Silently handle the error - the hook will work with empty state
        console.log('Backend not available or unauthorized, using local state only')
      })
    }
  }, [getRecentMoods])

  return {
    moods,
    addMood,
    getMoodTrend,
    getMoodAnalytics,
    getMoodInsights,
    getRecentMoods,
    loading,
    error
  }
}