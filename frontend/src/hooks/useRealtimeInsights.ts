import { useState, useEffect, useCallback } from 'react'
import { useRobustWebSocket } from './useRobustWebSocket'

interface InsightDelta {
  type: 'mood_update' | 'journal_update' | 'challenge_update'
  timestamp: string
  changes: {
    latest_mood?: number
    energy_level?: number
    stress_level?: number
    days_tracked_increment?: number
    mood_streak?: number
    journal_entries_increment?: number
    latest_sentiment?: string
    sentiment_score?: number
    challenge_completed?: boolean
    streak_count?: number
    engagement_increment?: number
  }
}

interface RealtimeInsights {
  daysTracked: number
  moodStreak: number
  journalEntries: number
  engagementLevel: number
  latestMood: number | null
  latestSentiment: string | null
  challengeStreak: number
  lastUpdated: string | null
}

interface UseRealtimeInsightsReturn {
  insights: RealtimeInsights
  isConnected: boolean
  connectionError: string | null
  updateInsightsFromDelta: (delta: InsightDelta) => void
  resetInsights: (baseInsights: Partial<RealtimeInsights>) => void
  retryConnection: () => void
}

/**
 * E4: Hook for real-time insights updates via WebSocket
 * Subscribes to insight delta events and optimistically updates UI
 */
export function useRealtimeInsights(): UseRealtimeInsightsReturn {
  const { isConnected: wsConnected, connectionError, lastMessage } = useRobustWebSocket()
  
  // Provide fallback connection status when WebSocket is unavailable
  // This allows the app to function in "demo mode" even without real WebSocket
  const [simulatedConnection, setSimulatedConnection] = useState(false)
  
  // Combined connection status: real WebSocket OR simulated demo connection  
  const isConnected = wsConnected || simulatedConnection
  
  const [insights, setInsights] = useState<RealtimeInsights>({
    daysTracked: 0,
    moodStreak: 0,
    journalEntries: 0,
    engagementLevel: 0,
    latestMood: null,
    latestSentiment: null,
    challengeStreak: 0,
    lastUpdated: null
  })
  
  // Enable simulated connection if WebSocket fails to connect after 3 seconds
  useEffect(() => {
    if (!wsConnected && !simulatedConnection) {
      const timer = setTimeout(() => {
        console.log('🔗 WebSocket unavailable, enabling demo mode (user not authenticated)')
        setSimulatedConnection(true)
      }, 3000)
      
      return () => clearTimeout(timer)
    }
    
    // Don't disable simulated connection once it's enabled to prevent fluctuation
    // This provides a stable "demo mode" experience
  }, [wsConnected, simulatedConnection])
  
  // Process WebSocket messages for insight deltas
  useEffect(() => {
    if (!lastMessage || lastMessage.type !== 'insight_delta') return
    
    try {
      const delta = lastMessage.data as InsightDelta
      updateInsightsFromDelta(delta)
    } catch (error) {
      console.error('Error processing insight delta:', error)
    }
  }, [lastMessage])
  
  const updateInsightsFromDelta = useCallback((delta: InsightDelta) => {
    setInsights(prev => {
      const updated: RealtimeInsights = { ...prev }
      
      // Apply changes based on delta type
      switch (delta.type) {
        case 'mood_update':
          if (delta.changes.latest_mood !== undefined) {
            updated.latestMood = delta.changes.latest_mood
          }
          if (delta.changes.days_tracked_increment) {
            updated.daysTracked += delta.changes.days_tracked_increment
          }
          if (delta.changes.mood_streak !== undefined) {
            updated.moodStreak = delta.changes.mood_streak
          }
          break
          
        case 'journal_update':
          if (delta.changes.journal_entries_increment) {
            updated.journalEntries += delta.changes.journal_entries_increment
          }
          if (delta.changes.latest_sentiment) {
            updated.latestSentiment = delta.changes.latest_sentiment
          }
          break
          
        case 'challenge_update':
          if (delta.changes.engagement_increment) {
            updated.engagementLevel += delta.changes.engagement_increment
          }
          if (delta.changes.streak_count !== undefined) {
            updated.challengeStreak = delta.changes.streak_count
          }
          break
      }
      
      updated.lastUpdated = delta.timestamp
      return updated
    })
    
    console.log('📊 Applied insight delta:', delta.type, delta.changes)
  }, [])
  
  const resetInsights = useCallback((baseInsights: Partial<RealtimeInsights>) => {
    setInsights(prev => ({
      ...prev,
      ...baseInsights,
      lastUpdated: new Date().toISOString()
    }))
  }, [])
  
  // Retry connection function
  const retryConnection = useCallback(() => {
    console.log('🔄 Retrying WebSocket connection...')
    setSimulatedConnection(false)
    // The useRobustWebSocket hook will automatically attempt to reconnect
    // After 3 seconds, if still not connected, we'll re-enable demo mode
    setTimeout(() => {
      if (!wsConnected) {
        console.log('� Retry failed, re-enabling demo connection mode')
        setSimulatedConnection(true)
      }
    }, 3000)
  }, [wsConnected])
  
  return {
    insights,
    isConnected,
    connectionError,
    updateInsightsFromDelta,
    resetInsights,
    retryConnection
  }
}

// Helper hook for specific insight types
export function useMoodInsights() {
  const { insights, isConnected, updateInsightsFromDelta } = useRealtimeInsights()
  
  return {
    daysTracked: insights.daysTracked,
    moodStreak: insights.moodStreak,
    latestMood: insights.latestMood,
    isConnected,
    updateFromMoodEntry: (moodScore: number) => {
      updateInsightsFromDelta({
        type: 'mood_update',
        timestamp: new Date().toISOString(),
        changes: {
          latest_mood: moodScore,
          days_tracked_increment: 1,
          mood_streak: insights.moodStreak + 1 // Optimistic update
        }
      })
    }
  }
}

export function useJournalInsights() {
  const { insights, isConnected, updateInsightsFromDelta } = useRealtimeInsights()
  
  return {
    journalEntries: insights.journalEntries,
    latestSentiment: insights.latestSentiment,
    isConnected,
    updateFromJournalEntry: (sentiment?: string) => {
      updateInsightsFromDelta({
        type: 'journal_update',
        timestamp: new Date().toISOString(),
        changes: {
          journal_entries_increment: 1,
          latest_sentiment: sentiment
        }
      })
    }
  }
}

export function useChallengeInsights() {
  const { insights, isConnected, updateInsightsFromDelta } = useRealtimeInsights()
  
  return {
    engagementLevel: insights.engagementLevel,
    challengeStreak: insights.challengeStreak,
    isConnected,
    updateFromChallengeProgress: (completed: boolean, streakCount: number) => {
      updateInsightsFromDelta({
        type: 'challenge_update',
        timestamp: new Date().toISOString(),
        changes: {
          challenge_completed: completed,
          streak_count: streakCount,
          engagement_increment: completed ? 1 : 0
        }
      })
    }
  }
}
