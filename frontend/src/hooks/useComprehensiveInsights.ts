/**
 * Hook for comprehensive insights
 * 
 * This hook provides a React interface to the unified insight service,
 * managing loading states, caching, and error handling.
 * 
 * Now enhanced to use the new unified insights endpoint from the ML service
 * with fallback to the legacy comprehensive insights aggregation.
 * 
 * E4: Enhanced with real-time insight deltas for immediate UI updates
 */

import { useState, useEffect, useCallback } from 'react'
import { 
  unifiedInsightService, 
  ComprehensiveInsights,
  UnifiedInsightsResponse
} from '@/services/unifiedInsightService'
import { useRealtimeInsights } from './useRealtimeInsights'

export interface UseComprehensiveInsightsResult {
  insights: ComprehensiveInsights | null
  unifiedData: UnifiedInsightsResponse | null
  loading: boolean
  error: string | null
  refresh: () => Promise<void>
  refreshUnified: () => Promise<void>
  lastUpdated: Date | null
  isUsingUnifiedEndpoint: boolean
  // E4: Real-time features
  realtimeInsights: ReturnType<typeof useRealtimeInsights>['insights']
  isRealtimeConnected: boolean
  realtimeError: string | null
}

export function useComprehensiveInsights(): UseComprehensiveInsightsResult {
  const [insights, setInsights] = useState<ComprehensiveInsights | null>(null)
  const [unifiedData, setUnifiedData] = useState<UnifiedInsightsResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)
  const [isUsingUnifiedEndpoint, setIsUsingUnifiedEndpoint] = useState(false)

  // E4: Real-time insights integration
  const { 
    insights: realtimeInsights, 
    isConnected: isRealtimeConnected, 
    connectionError: realtimeError,
    resetInsights 
  } = useRealtimeInsights()

  const loadUnifiedInsights = useCallback(async (forceRefresh = false) => {
    setLoading(true)
    setError(null)
    
    try {
      // Try to load from the new unified insights endpoint first
      console.log('🔄 Loading unified insights from ML service...')
      const unifiedResponse = await unifiedInsightService.getUnifiedInsights(forceRefresh)
      setUnifiedData(unifiedResponse)
      
      // Transform to legacy format for compatibility
      const transformedInsights = unifiedInsightService.transformToLegacyFormat(unifiedResponse)
      setInsights(transformedInsights)
      setIsUsingUnifiedEndpoint(true)
      setLastUpdated(new Date())
      
      // E4: Initialize real-time insights with current data
      resetInsights({
        daysTracked: unifiedResponse.aggregated_insights?.mood?.weekly_summary?.days_tracked || 0,
        moodStreak: unifiedResponse.aggregated_insights?.mood?.total_entries || 0,
        journalEntries: 0, // Will be updated from backend when available
        engagementLevel: 0, // Will be updated from backend when available
        latestMood: unifiedResponse.aggregated_insights?.mood?.current_score || null,
        latestSentiment: null, // Will be updated from backend when available
        challengeStreak: 0 // Will be updated from backend when available
      })
      
      console.log('✅ Successfully loaded unified insights')
    } catch (err) {
      console.warn('⚠️ Failed to load unified insights, falling back to legacy method:', err)
      setIsUsingUnifiedEndpoint(false)
      
      try {
        // Fallback to the legacy comprehensive insights method
        const comprehensiveInsights = await unifiedInsightService.getComprehensiveInsights(!forceRefresh)
        setInsights(comprehensiveInsights)
        setLastUpdated(new Date())
        
        // E4: Initialize real-time insights with legacy data
        resetInsights({
          daysTracked: comprehensiveInsights.dashboard?.weeklySummary?.daysTracked || 0,
          latestMood: comprehensiveInsights.dashboard?.currentStatus?.moodScore || null
        })
        
        console.log('✅ Successfully loaded legacy insights')
      } catch (fallbackErr) {
        console.error('❌ Both unified and legacy insights failed:', fallbackErr)
        setError(fallbackErr instanceof Error ? fallbackErr.message : 'Failed to load insights')
      }
    } finally {
      setLoading(false)
    }
  }, [resetInsights])

  const refresh = useCallback(async () => {
    await loadUnifiedInsights(true) // Force refresh
  }, [loadUnifiedInsights])

  const refreshUnified = useCallback(async () => {
    if (!isUsingUnifiedEndpoint) {
      await loadUnifiedInsights(true)
      return
    }
    
    setLoading(true)
    try {
      const unifiedResponse = await unifiedInsightService.getUnifiedInsights(true)
      setUnifiedData(unifiedResponse)
      const transformedInsights = unifiedInsightService.transformToLegacyFormat(unifiedResponse)
      setInsights(transformedInsights)
      setLastUpdated(new Date())
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to refresh unified insights')
    } finally {
      setLoading(false)
    }
  }, [isUsingUnifiedEndpoint])

  useEffect(() => {
    loadUnifiedInsights()
  }, [loadUnifiedInsights])

  return {
    insights,
    unifiedData,
    loading,
    error,
    refresh,
    refreshUnified,
    lastUpdated,
    isUsingUnifiedEndpoint,
    // E4: Real-time insights
    realtimeInsights,
    isRealtimeConnected,
    realtimeError
  }
}

export default useComprehensiveInsights
