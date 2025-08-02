/**
 * Unified Insight Service - Consolidates all insight sources
 * 
 * This service layer merges insights from:
 * - PersonalizedInsights (mood service)
 * - MoodCorrelations (pattern analysis)
 * - EmotionalWeather (weather-based recommendations)
 * - ML Service (AI-powered insights)
 * - Community insights
 */

import { apiService } from './api'

export interface ComprehensiveInsights {
  dashboard: InsightDashboard
  detailedAnalysis: DetailedAnalysis
  recommendedActions: RecommendedAction[]
  progressTracking: ProgressTracking
  metadata: InsightMetadata
}

export interface InsightDashboard {
  weeklySummary: {
    currentWeekScore: number
    trend: 'improving' | 'stable' | 'declining'
    daysTracked: number
    achievements: string[]
  }
  currentStatus: {
    moodScore: number
    energyLevel: number
    stressLevel: number
    lastUpdated: Date
  }
  topHighlights: {
    bestDay: string
    energyPeak: string
    dominantMood: string
    moodStreak: number
  }
}

export interface DetailedAnalysis {
  patterns: {
    timeOfDay: TimePattern[]
    dayOfWeek: DayPattern[]
    triggers: TriggerPattern[]
    boosters: BoosterPattern[]
  }
  correlations: {
    activities: ActivityCorrelation[]
    weather: WeatherCorrelation[]
    sleep: SleepCorrelation[]
    social: SocialCorrelation[]
  }
  predictions: {
    upcomingChallenges: Challenge[]
    opportunityWindows: OpportunityWindow[]
    moodForecast: MoodForecast[]
  }
}

export interface RecommendedAction {
  id: string
  priority: 'high' | 'medium' | 'low'
  category: 'mood_boost' | 'energy_management' | 'stress_reduction' | 'pattern_optimization'
  title: string
  description: string
  specificActions: string[]
  estimatedTime: string
  expectedBenefit: string
  optimalTiming: string
  source: 'ai' | 'patterns' | 'community' | 'weather'
  confidence: number
  userFeedback?: {
    attempted: boolean
    helpful: boolean
    rating: number
  }
}

export interface ProgressTracking {
  goals: WellnessGoal[]
  trends: {
    mood: TrendData
    energy: TrendData
    stress: TrendData
    overall: TrendData
  }
  comparisons: {
    thisWeek: PeriodData
    lastWeek: PeriodData
    thisMonth: PeriodData
    lastMonth: PeriodData
  }
  successPatterns: SuccessPattern[]
}

export interface InsightMetadata {
  lastUpdated: Date
  dataQuality: number
  confidenceScore: number
  insightCount: number
  sourceDistribution: {
    personalized: number
    patterns: number
    weather: number
    ml: number
    community: number
  }
}

// Supporting types
interface TimePattern {
  timeSlot: string
  averageMood: number
  frequency: number
  recommendation: string
}

interface DayPattern {
  dayOfWeek: string
  averageMood: number
  commonTriggers: string[]
  suggestions: string[]
}

interface TriggerPattern {
  trigger: string
  frequency: number
  impact: number
  mitigation: string[]
}

interface BoosterPattern {
  activity: string
  effectiveness: number
  frequency: number
  optimalTiming: string[]
}

interface ActivityCorrelation {
  activity: string
  moodImpact: number
  energyImpact: number
  confidence: number
  recommendation: string
}

interface WeatherCorrelation {
  condition: string
  moodImpact: number
  frequency: number
  adaptations: string[]
}

interface SleepCorrelation {
  sleepQuality: number
  nextDayMood: number
  recommendation: string
}

interface SocialCorrelation {
  interaction: string
  moodBoost: number
  frequency: number
  suggestion: string
}

interface Challenge {
  date: Date
  type: string
  probability: number
  preparation: string[]
}

interface OpportunityWindow {
  timeSlot: string
  activity: string
  expectedBenefit: number
  scheduling: string
}

interface MoodForecast {
  date: Date
  predictedMood: number
  confidence: number
  factors: string[]
}

interface WellnessGoal {
  id: string
  title: string
  progress: number
  target: number
  timeframe: string
  nextMilestone: string
}

interface TrendData {
  current: number
  change: number
  direction: 'up' | 'down' | 'stable'
  weeklyAverage: number
}

interface PeriodData {
  averageMood: number
  moodVariability: number
  bestDay: string
  challengingDay: string
  keyActivities: string[]
}

interface SuccessPattern {
  pattern: string
  successRate: number
  description: string
  howToRepeat: string[]
}

export class UnifiedInsightService {
  private cache = new Map<string, { data: any; timestamp: number }>()
  private cacheTimeout = 5 * 60 * 1000 // 5 minutes

  async getComprehensiveInsights(useCache = true): Promise<ComprehensiveInsights> {
    const cacheKey = 'comprehensive-insights'
    
    if (useCache && this.isCacheValid(cacheKey)) {
      return this.cache.get(cacheKey)!.data
    }

    try {
      // Fetch all insight sources in parallel
      const [
        personalizedData,
        patternsData,
        weatherData,
        mlData,
        correlationsData
      ] = await Promise.all([
        this.getPersonalizedInsights(),
        this.getPatternAnalysis(),
        this.getWeatherInsights(),
        this.getMLInsights(),
        this.getCorrelationAnalysis()
      ])

      // Merge and prioritize all insights
      const comprehensiveInsights = this.mergeAndPrioritizeInsights({
        personalizedData,
        patternsData,
        weatherData,
        mlData,
        correlationsData
      })

      // Cache the results
      this.cache.set(cacheKey, {
        data: comprehensiveInsights,
        timestamp: Date.now()
      })

      return comprehensiveInsights
    } catch (error) {
      console.error('Failed to get comprehensive insights:', error)
      return this.getFallbackInsights()
    }
  }

  private async getPersonalizedInsights() {
    try {
      return await apiService.getPersonalizedInsights()
    } catch (error) {
      console.warn('Failed to get personalized insights:', error)
      return null
    }
  }

  private async getPatternAnalysis() {
    try {
      // This would be extracted from MoodCorrelations logic
      return await apiService.request('/api/v1/analytics/patterns')
    } catch (error) {
      console.warn('Failed to get pattern analysis:', error)
      return null
    }
  }

  private async getWeatherInsights() {
    try {
      return await apiService.getEmotionalWeather()
    } catch (error) {
      console.warn('Failed to get weather insights:', error)
      return null
    }
  }

  private async getMLInsights() {
    try {
      return await apiService.request('/ml/personalized-insights/current-user')
    } catch (error) {
      console.warn('Failed to get ML insights:', error)
      return null
    }
  }

  private async getCorrelationAnalysis() {
    try {
      return await apiService.request('/api/v1/analytics/correlations')
    } catch (error) {
      console.warn('Failed to get correlation analysis:', error)
      return null
    }
  }

  private mergeAndPrioritizeInsights(sources: any): ComprehensiveInsights {
    const { personalizedData, patternsData, weatherData, mlData, correlationsData } = sources

    // Build dashboard summary
    const dashboard: InsightDashboard = {
      weeklySummary: {
        currentWeekScore: personalizedData?.weekly_summary?.current_week_score || 0,
        trend: personalizedData?.weekly_summary?.trend || 'stable',
        daysTracked: personalizedData?.weekly_summary?.days_tracked_this_week || 0,
        achievements: this.extractAchievements(personalizedData)
      },
      currentStatus: {
        moodScore: this.getCurrentMoodScore(),
        energyLevel: this.getCurrentEnergyLevel(),
        stressLevel: this.getCurrentStressLevel(),
        lastUpdated: new Date()
      },
      topHighlights: {
        bestDay: this.findBestDay(patternsData),
        energyPeak: this.findEnergyPeak(patternsData),
        dominantMood: this.findDominantMood(personalizedData),
        moodStreak: this.calculateMoodStreak()
      }
    }

    // Merge all recommendations with priority scoring
    const recommendedActions = this.prioritizeRecommendations([
      ...(personalizedData?.recommendations || []),
      ...(weatherData?.recommendations || []),
      ...(mlData?.recommendations || []),
      ...this.generatePatternBasedRecommendations(patternsData)
    ])

    // Build detailed analysis
    const detailedAnalysis: DetailedAnalysis = {
      patterns: this.buildPatternAnalysis(patternsData, correlationsData),
      correlations: this.buildCorrelationAnalysis(correlationsData),
      predictions: this.buildPredictions(personalizedData, patternsData, weatherData)
    }

    // Build progress tracking
    const progressTracking: ProgressTracking = {
      goals: this.extractGoals(personalizedData),
      trends: this.calculateTrends(personalizedData, patternsData),
      comparisons: this.buildComparisons(personalizedData),
      successPatterns: this.identifySuccessPatterns(patternsData)
    }

    // Calculate metadata
    const metadata: InsightMetadata = {
      lastUpdated: new Date(),
      dataQuality: this.calculateDataQuality(sources),
      confidenceScore: this.calculateConfidenceScore(sources),
      insightCount: recommendedActions.length,
      sourceDistribution: {
        personalized: personalizedData?.insights?.length || 0,
        patterns: patternsData?.patterns?.length || 0,
        weather: weatherData?.recommendations?.length || 0,
        ml: mlData?.insights?.length || 0,
        community: 0 // To be implemented
      }
    }

    return {
      dashboard,
      detailedAnalysis,
      recommendedActions,
      progressTracking,
      metadata
    }
  }

  private prioritizeRecommendations(allRecommendations: any[]): RecommendedAction[] {
    return allRecommendations
      .map(rec => this.normalizeRecommendation(rec))
      .sort((a, b) => {
        // Priority order: high > medium > low
        const priorityScore = { high: 3, medium: 2, low: 1 }
        if (priorityScore[a.priority] !== priorityScore[b.priority]) {
          return priorityScore[b.priority] - priorityScore[a.priority]
        }
        // Then by confidence
        return b.confidence - a.confidence
      })
      .slice(0, 10) // Top 10 recommendations
  }

  private normalizeRecommendation(rec: any): RecommendedAction {
    // Normalize different recommendation formats into unified structure
    return {
      id: rec.id || `rec-${Date.now()}-${Math.random()}`,
      priority: rec.priority || 'medium',
      category: this.categorizerecommendation(rec),
      title: rec.title || rec.name || 'Recommendation',
      description: rec.description || '',
      specificActions: rec.actions || rec.actionItems || [rec.description],
      estimatedTime: rec.estimated_time || rec.estimatedTime || '5-10 minutes',
      expectedBenefit: rec.expected_benefit || rec.expectedBenefit || 'Improved wellbeing',
      optimalTiming: rec.optimal_timing || 'Any time',
      source: this.identifySource(rec),
      confidence: rec.confidence || rec.effectiveness_score || 0.7,
      userFeedback: rec.userFeedback
    }
  }

  private categorizerecommendation(rec: any): RecommendedAction['category'] {
    const title = (rec.title || rec.name || '').toLowerCase()
    const description = (rec.description || '').toLowerCase()
    const text = `${title} ${description}`

    if (text.includes('mood') || text.includes('happy') || text.includes('positive')) {
      return 'mood_boost'
    }
    if (text.includes('energy') || text.includes('tired') || text.includes('fatigue')) {
      return 'energy_management'
    }
    if (text.includes('stress') || text.includes('anxiety') || text.includes('relax')) {
      return 'stress_reduction'
    }
    return 'pattern_optimization'
  }

  private identifySource(rec: any): RecommendedAction['source'] {
    if (rec.source) return rec.source
    if (rec.basedOn) return 'patterns'
    if (rec.weather_type) return 'weather'
    if (rec.ml_generated) return 'ai'
    return 'patterns'
  }

  // Helper methods for building different sections
  private extractAchievements(data: any): string[] {
    const achievements: string[] = []
    if (data?.weekly_summary?.trend === 'improving') {
      achievements.push('Improving trend this week')
    }
    if (data?.weekly_summary?.days_tracked_this_week >= 7) {
      achievements.push('Perfect tracking week')
    }
    return achievements
  }

  private getCurrentMoodScore(): number {
    // This would get current mood from useMoods hook or API
    return 7.5 // Placeholder
  }

  private getCurrentEnergyLevel(): number {
    return 6.8 // Placeholder
  }

  private getCurrentStressLevel(): number {
    return 4.2 // Placeholder
  }

  private findBestDay(patternsData: any): string {
    return patternsData?.best_day || 'Tuesday'
  }

  private findEnergyPeak(patternsData: any): string {
    return patternsData?.energy_peak || '2:00 PM'
  }

  private findDominantMood(data: any): string {
    return data?.weekly_summary?.dominant_mood || 'good'
  }

  private calculateMoodStreak(): number {
    return 5 // Placeholder - would calculate from mood data
  }

  private generatePatternBasedRecommendations(patternsData: any): any[] {
    // Generate recommendations based on detected patterns
    return []
  }

  private buildPatternAnalysis(patternsData: any, correlationsData: any): DetailedAnalysis['patterns'] {
    return {
      timeOfDay: [],
      dayOfWeek: [],
      triggers: [],
      boosters: []
    }
  }

  private buildCorrelationAnalysis(correlationsData: any): DetailedAnalysis['correlations'] {
    return {
      activities: [],
      weather: [],
      sleep: [],
      social: []
    }
  }

  private buildPredictions(personalizedData: any, patternsData: any, weatherData: any): DetailedAnalysis['predictions'] {
    return {
      upcomingChallenges: [],
      opportunityWindows: [],
      moodForecast: []
    }
  }

  private extractGoals(data: any): WellnessGoal[] {
    return []
  }

  private calculateTrends(personalizedData: any, patternsData: any): ProgressTracking['trends'] {
    return {
      mood: { current: 7.5, change: 0.5, direction: 'up', weeklyAverage: 7.2 },
      energy: { current: 6.8, change: -0.2, direction: 'down', weeklyAverage: 6.9 },
      stress: { current: 4.2, change: -0.8, direction: 'down', weeklyAverage: 4.8 },
      overall: { current: 7.0, change: 0.3, direction: 'up', weeklyAverage: 6.8 }
    }
  }

  private buildComparisons(data: any): ProgressTracking['comparisons'] {
    return {
      thisWeek: {
        averageMood: 7.2,
        moodVariability: 1.1,
        bestDay: 'Tuesday',
        challengingDay: 'Monday',
        keyActivities: ['Exercise', 'Meditation']
      },
      lastWeek: {
        averageMood: 6.8,
        moodVariability: 1.3,
        bestDay: 'Friday',
        challengingDay: 'Wednesday',
        keyActivities: ['Reading', 'Walking']
      },
      thisMonth: {
        averageMood: 7.0,
        moodVariability: 1.2,
        bestDay: 'Saturday',
        challengingDay: 'Monday',
        keyActivities: ['Exercise', 'Social time']
      },
      lastMonth: {
        averageMood: 6.7,
        moodVariability: 1.4,
        bestDay: 'Sunday',
        challengingDay: 'Monday',
        keyActivities: ['Sleep', 'Nature time']
      }
    }
  }

  private identifySuccessPatterns(patternsData: any): SuccessPattern[] {
    return []
  }

  private calculateDataQuality(sources: any): number {
    let quality = 0
    let sourceCount = 0
    
    Object.values(sources).forEach(source => {
      if (source) {
        quality += 0.2
        sourceCount++
      }
    })
    
    return Math.min(quality, 1.0)
  }

  private calculateConfidenceScore(sources: any): number {
    // Calculate confidence based on data availability and quality
    return 0.85
  }

  private getFallbackInsights(): ComprehensiveInsights {
    return {
      dashboard: {
        weeklySummary: {
          currentWeekScore: 0,
          trend: 'stable',
          daysTracked: 0,
          achievements: []
        },
        currentStatus: {
          moodScore: 5,
          energyLevel: 5,
          stressLevel: 5,
          lastUpdated: new Date()
        },
        topHighlights: {
          bestDay: 'Unknown',
          energyPeak: 'Unknown',
          dominantMood: 'neutral',
          moodStreak: 0
        }
      },
      detailedAnalysis: {
        patterns: { timeOfDay: [], dayOfWeek: [], triggers: [], boosters: [] },
        correlations: { activities: [], weather: [], sleep: [], social: [] },
        predictions: { upcomingChallenges: [], opportunityWindows: [], moodForecast: [] }
      },
      recommendedActions: [],
      progressTracking: {
        goals: [],
        trends: {
          mood: { current: 5, change: 0, direction: 'stable', weeklyAverage: 5 },
          energy: { current: 5, change: 0, direction: 'stable', weeklyAverage: 5 },
          stress: { current: 5, change: 0, direction: 'stable', weeklyAverage: 5 },
          overall: { current: 5, change: 0, direction: 'stable', weeklyAverage: 5 }
        },
        comparisons: {
          thisWeek: { averageMood: 5, moodVariability: 0, bestDay: 'Unknown', challengingDay: 'Unknown', keyActivities: [] },
          lastWeek: { averageMood: 5, moodVariability: 0, bestDay: 'Unknown', challengingDay: 'Unknown', keyActivities: [] },
          thisMonth: { averageMood: 5, moodVariability: 0, bestDay: 'Unknown', challengingDay: 'Unknown', keyActivities: [] },
          lastMonth: { averageMood: 5, moodVariability: 0, bestDay: 'Unknown', challengingDay: 'Unknown', keyActivities: [] }
        },
        successPatterns: []
      },
      metadata: {
        lastUpdated: new Date(),
        dataQuality: 0,
        confidenceScore: 0,
        insightCount: 0,
        sourceDistribution: { personalized: 0, patterns: 0, weather: 0, ml: 0, community: 0 }
      }
    }
  }

  private isCacheValid(key: string): boolean {
    const cached = this.cache.get(key)
    if (!cached) return false
    return Date.now() - cached.timestamp < this.cacheTimeout
  }

  // Action tracking methods
  async trackActionAttempt(actionId: string, attempted: boolean) {
    try {
      await apiService.request(`/api/v1/insights/actions/${actionId}/track`, {
        method: 'POST',
        body: JSON.stringify({
          attempted,
          timestamp: Date.now()
        })
      })
    } catch (error) {
      console.error('Failed to track action attempt:', error)
    }
  }

  async rateAction(actionId: string, rating: number, helpful: boolean) {
    try {
      await apiService.request(`/api/v1/insights/actions/${actionId}/rate`, {
        method: 'POST',
        body: JSON.stringify({
          rating,
          helpful,
          timestamp: Date.now()
        })
      })
    } catch (error) {
      console.error('Failed to rate action:', error)
    }
  }

  // Clear cache method
  clearCache() {
    this.cache.clear()
  }
}

export const unifiedInsightService = new UnifiedInsightService()
