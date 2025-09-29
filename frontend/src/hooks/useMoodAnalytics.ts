import { useCallback, useEffect, useState } from 'react'
import { moodService, MoodAnalytics, EmotionAnalysisResult } from '@/services/moodService'
import { isDevMode, setDevToken, getAuthToken } from '@/utils/auth'

export interface UseMoodAnalyticsOptions {
  days?: number
  autoFetch?: boolean
}

export function useMoodAnalytics(options: UseMoodAnalyticsOptions = {}) {
  const { days = 30, autoFetch = true } = options
  const [analytics, setAnalytics] = useState<MoodAnalytics | null>(null)
  const [loading, setLoading] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)
  const [lastUpdated, setLastUpdated] = useState<number | null>(null)

  const fetchAnalytics = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      if (isDevMode() && !getAuthToken()) {
        setDevToken()
      }
      const data = await moodService.getMoodAnalytics(days)
      setAnalytics(data)
      setLastUpdated(Date.now())
    } catch (e: any) {
      setError(e?.message || 'Failed to load mood analytics')
    } finally {
      setLoading(false)
    }
  }, [days])

  useEffect(() => {
    if (autoFetch) fetchAnalytics()
  }, [autoFetch, fetchAnalytics])

  return { analytics, loading, error, refresh: fetchAnalytics, lastUpdated }
}

export function useEmotionAnalysis() {
  const [result, setResult] = useState<EmotionAnalysisResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const analyze = useCallback(async (text: string, attach: boolean = false, moodScore?: number) => {
    if (!text.trim()) {
      setError('Text required')
      return null
    }
    try {
      setLoading(true)
      setError(null)
      const res = await moodService.analyzeEmotion(text, attach, moodScore)
      setResult(res)
      return res
    } catch (e: any) {
      setError(e?.message || 'Emotion analysis failed')
      return null
    } finally {
      setLoading(false)
    }
  }, [])

  return { result, loading, error, analyze }
}
