import { MoodAnalytics } from '@/services/moodService'

export interface WellnessMetrics {
  overall_score: number
  mood_stability: number
  stress_level: number
  energy_level: number
  improvement_trend: number
}

export function calculateWellness(analytics: MoodAnalytics | null): WellnessMetrics {
  if (!analytics || analytics.total_entries === 0) {
    return { overall_score: 0, mood_stability: 0, stress_level: 10, energy_level: 0, improvement_trend: 0 }
  }
  const variationBuckets = Object.keys(analytics.mood_distribution).length
  const moodStability = Math.max(0, 100 - variationBuckets * 10)
  const stressLevel = analytics.stress_average ?? 5
  const stressWellness = Math.max(0, 100 - stressLevel * 10)
  const energyLevel = (analytics.energy_average ?? 5) * 10
  const moodContribution = (analytics.average_mood / 10) * 100
  let multiplier = 1
  if (analytics.mood_trend === 'improving') multiplier = 1.1
  else if (analytics.mood_trend === 'declining') multiplier = 0.9
  const overall = Math.min(100, Math.max(0, (moodContribution * 0.4 + stressWellness * 0.3 + energyLevel * 0.2 + moodStability * 0.1) * multiplier))
  return {
    overall_score: Math.round(overall),
    mood_stability: Math.round(moodStability),
    stress_level: Math.round(stressLevel),
    energy_level: Math.round(energyLevel),
    improvement_trend: analytics.improvement_trend || 0
  }
}
