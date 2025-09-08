import { useState, useEffect } from 'react'
import { apiService } from '@/services/api'

interface CrisisAnalysisHook {
  riskLevel: 'minimal' | 'low' | 'moderate' | 'high' | 'critical'
  riskScore: number
  crisisIndicators: any[]
  recommendations: string[]
  loading: boolean
  error: string | null
  refresh: () => Promise<void>
}

export function useCrisisAnalysis(): CrisisAnalysisHook {
  const [riskLevel, setRiskLevel] = useState<'minimal' | 'low' | 'moderate' | 'high' | 'critical'>('minimal')
  const [riskScore, setRiskScore] = useState(0)
  const [crisisIndicators, setCrisisIndicators] = useState<any[]>([])
  const [recommendations, setRecommendations] = useState<string[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const analyzeCrisisRisk = async () => {
    try {
      setLoading(true)
      setError(null)

      // This would call the ML service crisis prediction endpoint
      // For now, we'll use local analysis based on available data
      
      // Simulated analysis - in production this would call:
      // const response = await apiService.get('/crisis/analyze')
      
      // For now, return safe defaults
      setRiskLevel('minimal')
      setRiskScore(10)
      setCrisisIndicators([])
      setRecommendations([
        'Continue your regular wellness tracking',
        'Maintain healthy sleep patterns',
        'Stay connected with supportive people'
      ])
      
    } catch (err: any) {
      console.error('Crisis analysis failed:', err)
      setError('Unable to analyze crisis risk')
    } finally {
      setLoading(false)
    }
  }

  const refresh = async () => {
    await analyzeCrisisRisk()
  }

  useEffect(() => {
    analyzeCrisisRisk()
  }, [])

  return {
    riskLevel,
    riskScore,
    crisisIndicators,
    recommendations,
    loading,
    error,
    refresh
  }
}
