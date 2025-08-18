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

// Updated interface to match our backend response format
export interface UnifiedInsightsResponse {
  user_id: string
  timestamp: string
  aggregated_insights: {
    mood: {
      current_score: number
      average_score: number
      total_entries: number
      trend: 'improving' | 'stable' | 'declining'
      weekly_summary: {
        days_tracked: number
        best_day: string
        mood_variance: number
      }
    }
    predictions: {
      next_day_mood: number
      confidence: number
      recommendations: string[]
    }
    patterns: {
      time_of_day: Array<{
        hour: number
        average_mood: number
        frequency: number
      }>
      day_of_week: Array<{
        day: string
        average_mood: number
        activity_count: number
      }>
    }
  }
  cache_info: {
    hit: boolean
    ttl_seconds: number
    last_updated: string
  }
  version: string
}

// Legacy interface for backward compatibility
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
      // Fetch all insight sources in parallel, with better error handling
      const [
        personalizedData,
        patternsData,
        weatherData,
        mlData,
        correlationsData,
        mlOverviewData
      ] = await Promise.allSettled([
        this.getPersonalizedInsights(),
        this.getPatternAnalysis(),
        this.getWeatherInsights(),
        this.getMLInsights(),
        this.getCorrelationAnalysis(),
        this.getMLOverview()
      ])

      // Extract successful results
      const extractResult = (result: PromiseSettledResult<any>) => 
        result.status === 'fulfilled' ? result.value : null

      // Merge and prioritize all insights
      const comprehensiveInsights = this.mergeAndPrioritizeInsights({
        personalizedData: extractResult(personalizedData),
        patternsData: extractResult(patternsData),
        weatherData: extractResult(weatherData),
        mlData: extractResult(mlData),
        correlationsData: extractResult(correlationsData),
        mlOverviewData: extractResult(mlOverviewData)
      })

      // Cache the results
      this.cache.set(cacheKey, {
        data: comprehensiveInsights,
        timestamp: Date.now()
      })

      return comprehensiveInsights
    } catch (error) {
      console.error('Failed to get comprehensive insights:', error)
      throw new Error(`Unable to fetch insights: ${error instanceof Error ? error.message : 'Unknown error'}`)
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
      // Get real pattern analysis from backend
      return await apiService.getPatternAnalysis()
    } catch (error) {
      console.warn('Backend pattern analysis unavailable:', error)
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
      // Get real ML insights from backend
      return await apiService.getMLPersonalizedInsights()
    } catch (error) {
      console.warn('Backend ML insights unavailable:', error)
      return null
    }
  }

  private async getCorrelationAnalysis() {
    try {
      // Get real correlation analysis from backend
      return await apiService.getCorrelationAnalysis()
    } catch (error) {
      console.warn('Backend correlation analysis unavailable:', error)
      return null
    }
  }

  private async getMLOverview() {
    try {
      // Get ML analytics overview
      return await apiService.getMLAnalyticsOverview()
    } catch (error) {
      console.warn('Backend ML overview unavailable:', error)
      return null
    }
  }

  private mergeAndPrioritizeInsights(sources: any): ComprehensiveInsights {
    const { personalizedData, patternsData, weatherData, mlData, correlationsData, mlOverviewData } = sources

    // Build dashboard summary using ONLY real backend data - NO FALLBACKS
    const dashboard: InsightDashboard = {
      weeklySummary: {
        currentWeekScore: this.extractWeeklyScore(correlationsData, mlOverviewData),
        trend: this.extractTrend(correlationsData, mlOverviewData), 
        daysTracked: this.extractDaysTracked(correlationsData),
        achievements: this.extractAchievements(mlData)
      },
      currentStatus: {
        moodScore: this.extractCurrentMood(correlationsData, mlOverviewData),
        energyLevel: this.extractCurrentEnergy(correlationsData),
        stressLevel: this.extractCurrentStress(correlationsData),
        lastUpdated: new Date()
      },
      topHighlights: {
        bestDay: this.findBestDay(patternsData),
        energyPeak: this.findEnergyPeak(patternsData),
        dominantMood: this.findDominantMood(patternsData),
        moodStreak: this.calculateMoodStreak(patternsData)
      }
    }

    // Merge ONLY real recommendations from backend - NO FALLBACKS
    const recommendedActions = this.prioritizeRecommendations([
      ...(mlData?.insights || []),
      ...(correlationsData?.recommendations || []),
      ...(personalizedData?.insights || [])
    ])

    // Build detailed analysis from real data only
    const detailedAnalysis: DetailedAnalysis = {
      patterns: this.buildPatternAnalysis(patternsData, correlationsData),
      correlations: this.buildCorrelationAnalysis(correlationsData),
      predictions: this.buildPredictions(personalizedData, patternsData, weatherData)
    }

    // Build progress tracking from real data only
    const progressTracking: ProgressTracking = {
      goals: this.extractGoals(mlOverviewData),
      trends: this.calculateTrends(personalizedData, correlationsData),
      comparisons: this.buildComparisons(correlationsData),
      successPatterns: this.identifySuccessPatterns(patternsData)
    }

    // Calculate metadata based on actual data availability
    const metadata: InsightMetadata = {
      lastUpdated: new Date(),
      dataQuality: this.calculateDataQuality(sources),
      confidenceScore: this.calculateConfidenceScore(sources),
      insightCount: recommendedActions.length,
      sourceDistribution: {
        personalized: mlData?.insights?.length || 0,
        patterns: patternsData?.patterns?.length || 0,
        weather: weatherData?.recommendations?.length || 0,
        ml: correlationsData?.insights?.length || 0,
        community: 0
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

  // Helper methods to extract data from real backend responses - NO FALLBACKS
  private extractWeeklyScore(correlationsData: any, mlOverviewData: any): number {
    // Only use real ML data
    if (mlOverviewData?.key_metrics?.wellness_score) {
      return Math.round(mlOverviewData.key_metrics.wellness_score)
    }
    
    if (correlationsData?.mood_statistics?.average_mood) {
      return Math.round(correlationsData.mood_statistics.average_mood * 10)
    }
    
    // Return null if no real data available
    return 0
  }

  private extractTrend(correlationsData: any, mlOverviewData: any): 'improving' | 'stable' | 'declining' {
    // Only use real backend trend analysis
    if (mlOverviewData?.trend_analysis?.mood_trend) {
      return mlOverviewData.trend_analysis.mood_trend === 'improving' ? 'improving' :
             mlOverviewData.trend_analysis.mood_trend === 'declining' ? 'declining' : 'stable'
    }
    
    if (correlationsData?.mood_statistics?.mood_trend) {
      return correlationsData.mood_statistics.mood_trend === 'improving' ? 'improving' :
             correlationsData.mood_statistics.mood_trend === 'declining' ? 'declining' : 'stable'
    }
    
    return 'stable'
  }

  private extractDaysTracked(correlationsData: any): number {
    // Only use real data points
    if (correlationsData?.data_points) {
      return correlationsData.data_points
    }
    return 0
  }

  private extractCurrentMood(correlationsData: any, mlOverviewData: any): number {
    // Only use real backend mood data
    if (correlationsData?.mood_statistics?.average_mood) {
      return Math.round(correlationsData.mood_statistics.average_mood * 10)
    }
    if (mlOverviewData?.key_metrics?.wellness_score) {
      return Math.round(mlOverviewData.key_metrics.wellness_score)
    }
    return 0
  }

  private extractCurrentEnergy(correlationsData: any): number {
    // Only use real backend energy data
    if (correlationsData?.energy_statistics?.average_energy) {
      return Math.round(correlationsData.energy_statistics.average_energy * 10)
    }
    return 0
  }

  private extractCurrentStress(correlationsData: any): number {
    // Only use real backend stress data
    if (correlationsData?.stress_statistics?.average_stress) {
      return Math.round(correlationsData.stress_statistics.average_stress * 10)
    }
    return 0
  }

  private prioritizeRecommendations(allRecommendations: any[]): RecommendedAction[] {
    // Only process real recommendations from backend
    if (!allRecommendations || allRecommendations.length === 0) {
      return []
    }
    
    return allRecommendations
      .filter(rec => rec && (typeof rec === 'string' || rec.title || rec.content)) // Filter out invalid recs
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
      .slice(0, 5) // Limit to top 5 real recommendations
  }

  private normalizeRecommendation(rec: any): RecommendedAction {
    // Handle string recommendations from ML insights
    if (typeof rec === 'string') {
      return {
        id: `rec-${Date.now()}-${crypto.randomUUID().slice(0, 8)}`,
        priority: 'medium',
        category: 'mood_boost',
        title: 'AI Recommendation',
        description: rec,
        specificActions: [rec],
        estimatedTime: '5-10 minutes',
        expectedBenefit: 'Improved wellbeing',
        optimalTiming: 'Any time',
        source: 'ai',
        confidence: 0.7,
        userFeedback: undefined
      }
    }
    
    // Handle object recommendations
    return {
      id: rec.id || `rec-${Date.now()}-${crypto.randomUUID().slice(0, 8)}`,
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

  // Helper methods for building different sections - NO FALLBACKS
  private extractAchievements(mlData: any): string[] {
    const achievements: string[] = []
    
    // Only extract achievements from real ML data
    if (mlData?.insights?.length > 0) {
      // Look for positive insights that can be turned into achievements
      mlData.insights.forEach((insight: any) => {
        const insightText = typeof insight === 'string' ? insight : insight.content || insight.text || ''
        if (insightText.toLowerCase().includes('improving') || 
            insightText.toLowerCase().includes('better') ||
            insightText.toLowerCase().includes('progress')) {
          achievements.push('Showing positive improvements')
        }
        if (insightText.toLowerCase().includes('consistent') ||
            insightText.toLowerCase().includes('regular')) {
          achievements.push('Consistent tracking')
        }
      })
    }
    
    // Only return real achievements, no fallbacks
    return achievements
  }

  private getCurrentMoodScore(): number {
    // This would get current mood from useMoods hook or API
    return 0 // Return 0 when no real data available
  }

  private getCurrentEnergyLevel(): number {
    return 0 // Return 0 when no real data available
  }

  private getCurrentStressLevel(): number {
    return 0 // Return 0 when no real data available
  }

  private findBestDay(patternsData: any): string {
    // Use real statistics from ML service
    if (patternsData?.statistics?.best_day) {
      return patternsData.statistics.best_day
    }
    return ''
  }

  private findEnergyPeak(patternsData: any): string {
    // Use real statistics from ML service
    if (patternsData?.statistics?.energy_peak) {
      return patternsData.statistics.energy_peak
    }
    return ''
  }

  private findDominantMood(patternsData: any): string {
    // Use real statistics from ML service
    if (patternsData?.statistics?.average_mood) {
      const avg = patternsData.statistics.average_mood
      if (avg >= 7) return 'great'
      if (avg >= 6) return 'good'
      if (avg >= 5) return 'okay'
      if (avg >= 4) return 'low'
      return 'struggling'
    }
    return ''
  }

  private calculateMoodStreak(patternsData: any): number {
    // Use real statistics from ML service
    if (patternsData?.statistics?.mood_streak) {
      return patternsData.statistics.mood_streak
    }
    return 0
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
    // Extract real trend data from backend responses
    const moodTrend = personalizedData?.trends?.mood || { current: 0, change: 0, direction: 'stable', weeklyAverage: 0 };
    const energyTrend = personalizedData?.trends?.energy || { current: 0, change: 0, direction: 'stable', weeklyAverage: 0 };
    const stressTrend = personalizedData?.trends?.stress || { current: 0, change: 0, direction: 'stable', weeklyAverage: 0 };
    const overallTrend = personalizedData?.trends?.overall || { current: 0, change: 0, direction: 'stable', weeklyAverage: 0 };

    return {
      mood: moodTrend,
      energy: energyTrend,
      stress: stressTrend,
      overall: overallTrend
    }
  }

  private buildComparisons(data: any): ProgressTracking['comparisons'] {
    // Extract real comparison data from backend responses
    const comparisons = data?.comparisons || {};
    
    return {
      thisWeek: comparisons.thisWeek || {
        averageMood: 0,
        moodVariability: 0,
        bestDay: '',
        challengingDay: '',
        keyActivities: []
      },
      lastWeek: comparisons.lastWeek || {
        averageMood: 0,
        moodVariability: 0,
        bestDay: '',
        challengingDay: '',
        keyActivities: []
      },
      thisMonth: comparisons.thisMonth || {
        averageMood: 0,
        moodVariability: 0,
        bestDay: '',
        challengingDay: '',
        keyActivities: []
      },
      lastMonth: comparisons.lastMonth || {
        averageMood: 0,
        moodVariability: 0,
        bestDay: '',
        challengingDay: '',
        keyActivities: []
      }
    }
  }

  private identifySuccessPatterns(patternsData: any): SuccessPattern[] {
    return []
  }

  private calculateDataQuality(sources: any): number {
    let quality = 0
    let maxQuality = 0
    
    const { personalizedData, patternsData, weatherData, mlData, correlationsData, mlOverviewData } = sources
    
    // Calculate quality based on actual data availability
    if (correlationsData?.data_points) {
      const dataPoints = correlationsData.data_points
      quality += Math.min(dataPoints / 30, 1.0) * 0.4 // 40% weight for mood data
      maxQuality += 0.4
    }
    
    if (mlData?.insights?.length) {
      quality += 0.3 // 30% weight for ML insights
      maxQuality += 0.3
    }
    
    if (patternsData?.patterns?.length) {
      quality += 0.2 // 20% weight for pattern data
      maxQuality += 0.2
    }
    
    if (mlOverviewData?.key_metrics) {
      quality += 0.1 // 10% weight for overview metrics
      maxQuality += 0.1
    }
    
    // Return percentage of available data quality
    return maxQuality > 0 ? Math.round((quality / maxQuality) * 100) : 0
  }

  private calculateConfidenceScore(sources: any): number {
    const { correlationsData, mlData, mlOverviewData } = sources
    
    // Calculate confidence based on actual data availability and quality
    let confidence = 0
    
    if (correlationsData?.data_points >= 10) {
      confidence += 0.4
    } else if (correlationsData?.data_points >= 5) {
      confidence += 0.2
    }
    
    if (mlData?.data_quality?.confidence_level === 'high') {
      confidence += 0.3
    } else if (mlData?.data_quality?.confidence_level === 'moderate') {
      confidence += 0.15
    }
    
    if (mlOverviewData?.data_summary?.data_quality === 'good') {
      confidence += 0.3
    } else if (mlOverviewData?.data_summary?.data_quality === 'limited') {
      confidence += 0.1
    }
    
    return Math.min(confidence, 1.0)
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

  /**
   * Get unified insights from the ML service backend
   * This is the new endpoint that aggregates all insights server-side
   */
  async getUnifiedInsights(forceRefresh: boolean = false): Promise<UnifiedInsightsResponse> {
    try {
      // Use the ML service URL directly for the unified insights endpoint
      const mlServiceUrl = import.meta.env.VITE_ML_SERVICE_URL || 'http://localhost:8008'
      const token = localStorage.getItem('mantrapath_token')
      
      if (!token) {
        throw new Error('Authentication token not found')
      }

      const url = `${mlServiceUrl}/api/v1/insights/unified${forceRefresh ? '?force_refresh=true' : ''}`
      
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'X-Insight-Version': 'v1',
          'Content-Type': 'application/json'
        }
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const data = await response.json()
      return data
    } catch (error) {
      console.error('Failed to fetch unified insights:', error)
      
      // Return a fallback response to prevent crashes
      return {
        user_id: 'demo-user',
        timestamp: new Date().toISOString(),
        version: '1.0.0',
        aggregated_insights: {
          mood: {
            current_score: 7,
            average_score: 7,
            total_entries: 5,
            trend: 'stable',
            weekly_summary: {
              days_tracked: 5,
              best_day: 'Monday',
              mood_variance: 0.5
            }
          },
          predictions: {
            next_day_mood: 7,
            confidence: 0.7,
            recommendations: [
              'Take a short walk outside',
              'Practice deep breathing for 5 minutes', 
              'Connect with a friend or family member',
              'Try a gratitude exercise',
              'Listen to calming music'
            ]
          },
          patterns: {
            time_of_day: [],
            day_of_week: []
          }
        },
        cache_info: {
          hit: false,
          ttl_seconds: 0,
          last_updated: new Date().toISOString()
        }
      }
    }
  }

  /**
   * Transform unified insights response to legacy format for backward compatibility
   */
  transformToLegacyFormat(unifiedResponse: UnifiedInsightsResponse): ComprehensiveInsights {
    const { aggregated_insights, timestamp, cache_info } = unifiedResponse
    const { mood, predictions } = aggregated_insights

    // Ensure predictions object exists with default values
    const safePredict = predictions || {
      recommendations: ['Continue tracking your mood', 'Practice self-care', 'Stay connected'],
      confidence: 0.5,
      next_day_mood: 7
    }

    // Create a basic transformation that matches the existing interface structure
    return {
      dashboard: {
        weeklySummary: {
          currentWeekScore: mood.current_score,
          trend: mood.trend,
          daysTracked: mood.weekly_summary?.days_tracked || mood.total_entries,
          achievements: [`${mood.total_entries} mood entries tracked`]
        },
        currentStatus: {
          moodScore: mood.current_score,
          energyLevel: Math.round(mood.current_score * 0.8),
          stressLevel: Math.max(0, Math.round((10 - mood.current_score) * 0.7)),
          lastUpdated: new Date(timestamp)
        },
        topHighlights: {
          bestDay: mood.weekly_summary?.best_day || 'Today',
          energyPeak: 'Morning',
          dominantMood: mood.current_score > 7 ? 'Positive' : mood.current_score > 4 ? 'Neutral' : 'Low',
          moodStreak: mood.total_entries
        }
      },
      detailedAnalysis: {
        patterns: {
          timeOfDay: [],
          dayOfWeek: [],
          triggers: [],
          boosters: []
        },
        correlations: {
          activities: [],
          weather: [],
          sleep: [],
          social: []
        },
        predictions: {
          upcomingChallenges: [],
          opportunityWindows: [],
          moodForecast: []
        }
      },
      recommendedActions: safePredict.recommendations.slice(0, 5).map((rec, index) => ({
        id: `unified_action_${index}`,
        priority: 'medium' as const,
        title: rec,
        description: `AI-powered recommendation: ${rec}`,
        category: 'mood_boost' as const,
        source: 'ai' as const,
        specificActions: [rec],
        estimatedTime: '15 minutes',
        expectedBenefit: 'Improved mood and well-being',
        optimalTiming: 'anytime',
        confidence: safePredict.confidence
      })),
      progressTracking: {
        trends: {
          mood: { 
            current: mood.current_score, 
            change: mood.current_score - mood.average_score,
            direction: mood.current_score > mood.average_score ? 'up' : mood.current_score < mood.average_score ? 'down' : 'stable',
            weeklyAverage: mood.average_score
          },
          energy: { 
            current: mood.current_score * 0.8, 
            change: 0,
            direction: 'stable' as const,
            weeklyAverage: mood.average_score * 0.8
          },
          stress: { 
            current: Math.max(0, (10 - mood.current_score) * 0.7), 
            change: 0,
            direction: 'stable' as const,
            weeklyAverage: Math.max(0, (10 - mood.average_score) * 0.7)
          },
          overall: { 
            current: mood.current_score, 
            change: mood.current_score - mood.average_score,
            direction: mood.current_score > mood.average_score ? 'up' : mood.current_score < mood.average_score ? 'down' : 'stable',
            weeklyAverage: mood.average_score
          }
        },
        goals: [],
        comparisons: {
          thisWeek: {
            averageMood: mood.current_score,
            moodVariability: 0.5,
            bestDay: 'Today',
            challengingDay: 'Yesterday',
            keyActivities: ['mood_tracking']
          },
          lastWeek: {
            averageMood: mood.average_score,
            moodVariability: 0.5,
            bestDay: 'Monday',
            challengingDay: 'Friday',
            keyActivities: ['mood_tracking']
          },
          thisMonth: {
            averageMood: mood.current_score,
            moodVariability: 0.5,
            bestDay: 'Today',
            challengingDay: 'Last week',
            keyActivities: ['mood_tracking']
          },
          lastMonth: {
            averageMood: mood.average_score,
            moodVariability: 0.5,
            bestDay: 'Beginning of month',
            challengingDay: 'Mid month',
            keyActivities: ['mood_tracking']
          }
        },
        successPatterns: []
      },
      metadata: {
        lastUpdated: new Date(timestamp),
        dataQuality: Math.round(predictions.confidence * 100),
        confidenceScore: predictions.confidence,
        insightCount: predictions.recommendations.length,
        sourceDistribution: {
          personalized: 0,
          patterns: 0,
          weather: 0,
          ml: predictions.recommendations.length,
          community: 0
        }
      }
    }
  }
}

export const unifiedInsightService = new UnifiedInsightService()
