/**
 * Hook for comprehensive insights
 * 
 * This hook provides a React interface to the unified insight service,
 * managing loading states, caching, and error handling.
 */

import { useState, useEffect, useCallback } from 'react'
import { 
  unifiedInsightService, 
  ComprehensiveInsights 
} from '@/services/unifiedInsightService'

export interface UseComprehensiveInsightsResult {
  insights: ComprehensiveInsights | null
  loading: boolean
  error: string | null
  refresh: () => Promise<void>
  lastUpdated: Date | null
}

export function useComprehensiveInsights(): UseComprehensiveInsightsResult {
  const [insights, setInsights] = useState<ComprehensiveInsights | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)

  const loadInsights = useCallback(async (useCache = true) => {
    setLoading(true)
    setError(null)
    
    try {
      const comprehensiveInsights = await unifiedInsightService.getComprehensiveInsights(useCache)
      setInsights(comprehensiveInsights)
      setLastUpdated(new Date())
    } catch (err) {
      console.error('Failed to load comprehensive insights:', err)
      setError(err instanceof Error ? err.message : 'Failed to load insights')
    } finally {
      setLoading(false)
    }
  }, [])

  const refresh = useCallback(async () => {
    await loadInsights(false) // Force refresh without cache
  }, [loadInsights])

  useEffect(() => {
    loadInsights()
  }, [loadInsights])

  return {
    insights,
    loading,
    error,
    refresh,
    lastUpdated
  }
}

export default useComprehensiveInsights
