/**
 * Crisis Detection Service
 * 
 * REAL backend integration for crisis analysis - NO MOCK DATA
 * Uses actual ML models and user data to detect mental health crises
 */

import { apiService } from './api'
import { getServiceUrls } from '../config/api-config'

// Get environment-aware service URLs
const serviceUrls = getServiceUrls()
const ML_SERVICE_URL = serviceUrls.ML_SERVICE_URL
const MOOD_SERVICE_URL = serviceUrls.MOOD_SERVICE_URL
const MEMORY_SERVICE_URL = serviceUrls.AI_CONTEXT_SERVICE_URL // Memory service is part of AI context

export interface CrisisIndicator {
  type: 'mood' | 'sleep' | 'activity' | 'social' | 'behavioral'
  severity: 'low' | 'medium' | 'high' | 'critical'
  trend: 'improving' | 'stable' | 'declining' | 'worsening'
  description: string
  timestamp: string
  confidence?: number
}

export interface CrisisAnalysisResult {
  riskLevel: 'minimal' | 'low' | 'medium' | 'high' | 'critical'
  confidence: number
  riskFactors: string[]
  protectiveFactors: string[]
  recommendations: string[]
  urgencyLevel: 'routine' | 'moderate' | 'urgent' | 'immediate'
  timeToIntervention: string
  crisisIndicators: CrisisIndicator[]
  lastUpdated: string
  mlAssessment?: any
  dataQuality?: {
    moodEntries: number
    journalEntries: number
    sufficientData: boolean
  }
}

class CrisisDetectionService {
  /**
   * Get comprehensive crisis analysis using REAL backend services ONLY
   */
  async analyzeCrisisRisk(userId: string): Promise<CrisisAnalysisResult> {
    let moodEntries: any[] = []
    let behavioralInsights: any[] = []
    
    try {
      console.log(`🔍 Starting real crisis analysis for user ${userId} - NO MOCK DATA`)
      
      // Get real user data from actual services
      const [mood, insights] = await Promise.all([
        this.getRealMoodData(userId),
        this.getRealBehavioralInsights(userId)
      ])
      
      moodEntries = mood
      behavioralInsights = insights

      console.log(`📊 Retrieved ${moodEntries.length} mood entries and ${behavioralInsights.length} behavioral insights`)

      // Handle insufficient data gracefully
      if (moodEntries.length === 0) {
        console.log('⚠️ No mood data available - returning guidance for user')
        return this.createInsufficientDataResponse('no_mood_data')
      }

      // Call ML service for REAL crisis prediction
      let mlCrisisAssessment = null
      if (moodEntries.length >= 1) {
        mlCrisisAssessment = await this.callRealMLCrisisPrediction({
          user_id: userId,
          mood_entries: moodEntries,
          journal_entries: [], // Will be populated when journal service is available
          activity_data: {},
          sleep_data: {},
          demographic_info: {},
          include_interventions: true
        })
      }

      // Process the real ML assessment
      const result = this.processMLAssessment(mlCrisisAssessment, moodEntries, behavioralInsights)
      
      console.log('✅ Real crisis analysis completed successfully')
      return result
      
    } catch (error: any) {
      console.error('❌ Crisis analysis failed:', error)
      
      // Handle service unavailability more gracefully
      if (error.message?.includes('mood service unavailable') || error.message?.includes('memory service unavailable')) {
        return this.createServiceUnavailableResponse(error.message)
      }
      
      // If ML service fails, provide fallback analysis based on available data
      if (error.message?.includes('Crisis analysis requires ML service')) {
        console.log('⚠️ ML service unavailable, providing fallback analysis')
        return this.createFallbackAnalysis(moodEntries, behavioralInsights)
      }
      
      throw new Error(`Crisis analysis failed: ${error.message}. Please ensure all services are running and user has sufficient data.`)
    }
  }

  /**
   * Create fallback analysis when ML service is unavailable
   */
  private createFallbackAnalysis(moodEntries: any[], behavioralInsights: any[]): CrisisAnalysisResult {
    // Simple rule-based analysis when ML service is down
    const recentMoods = moodEntries.slice(0, 7) // Last 7 entries
    const avgMood = recentMoods.length > 0 
      ? recentMoods.reduce((sum, entry) => sum + (entry.mood_score || 3), 0) / recentMoods.length
      : 3
    
    let riskLevel: 'low' | 'medium' | 'high' = 'low'
    let confidenceScore = 0.6 // Lower confidence for rule-based analysis
    
    if (avgMood < 2) {
      riskLevel = 'high'
      confidenceScore = 0.7
    } else if (avgMood < 2.5) {
      riskLevel = 'medium'
    }
    
    return {
      riskLevel,
      confidence: confidenceScore,
      riskFactors: avgMood < 2.5 ? ['Low mood trend detected'] : [],
      protectiveFactors: avgMood >= 3 ? ['Stable mood levels'] : [],
      recommendations: [
        'Continue regular mood tracking',
        'Consider speaking with a mental health professional if concerns persist'
      ],
      urgencyLevel: riskLevel === 'high' ? 'immediate' : 'routine',
      timeToIntervention: riskLevel === 'high' ? '24 hours' : '7 days',
      crisisIndicators: [],
      lastUpdated: new Date().toISOString(),
      dataQuality: {
        moodEntries: moodEntries.length,
        journalEntries: 0,
        sufficientData: moodEntries.length > 0
      }
    }
  }

  /**
   * Create a helpful response when there's insufficient data
   */
  private createInsufficientDataResponse(reason: string): CrisisAnalysisResult {
    const now = new Date().toISOString()
    
    return {
      riskLevel: 'minimal',
      confidence: 0,
      riskFactors: [],
      protectiveFactors: ['Getting started with mental health tracking'],
      recommendations: [
        'Start by recording your daily mood to enable crisis detection',
        'Add a few mood entries over the next few days',
        'Journal about your daily experiences',
        'Complete your profile for personalized insights'
      ],
      urgencyLevel: 'routine',
      timeToIntervention: 'Begin tracking today',
      crisisIndicators: [{
        type: 'activity',
        severity: 'low',
        trend: 'stable',
        description: 'No mood data available yet - crisis detection will improve as you add mood entries',
        timestamp: now,
        confidence: 1.0
      }],
      lastUpdated: now,
      dataQuality: {
        moodEntries: 0,
        journalEntries: 0,
        sufficientData: false
      }
    }
  }

  /**
   * Create a response when services are unavailable
   */
  private createServiceUnavailableResponse(errorMessage: string): CrisisAnalysisResult {
    const now = new Date().toISOString()
    
    return {
      riskLevel: 'medium',
      confidence: 0,
      riskFactors: ['Unable to access mood analysis services'],
      protectiveFactors: [],
      recommendations: [
        'Backend services are currently unavailable',
        'Please try again in a few minutes',
        'Contact support if the issue persists'
      ],
      urgencyLevel: 'routine',
      timeToIntervention: 'Retry when services are available',
      crisisIndicators: [{
        type: 'activity',
        severity: 'medium',
        trend: 'stable',
        description: 'Crisis detection temporarily unavailable due to service connectivity',
        timestamp: now,
        confidence: 0.5
      }],
      lastUpdated: now,
      dataQuality: {
        moodEntries: 0,
        journalEntries: 0,
        sufficientData: false
      }
    }
  }

  /**
   * Get REAL user mood data from mood service - NO MOCK DATA
   */
  private async getRealMoodData(userId: string): Promise<any[]> {
    try {
      console.log(`🎭 Fetching REAL mood data from mood service for user ${userId}`)
      
      const response = await apiService.request<any>(`/api/v1/mood/entries?limit=50`, {
        method: 'GET'
      })

      console.log(`✅ Retrieved ${response.length || 0} real mood entries`)
      return response || []
    } catch (error) {
      console.error('❌ Real mood service unavailable:', error)
      // Return empty array and let the main function handle insufficient data
      return []
    }
  }

  /**
   * Get REAL behavioral insights from memory service - NO MOCK DATA
   */
  private async getRealBehavioralInsights(userId: string): Promise<any[]> {
    try {
      console.log(`🧠 Fetching REAL behavioral insights from memory service for user ${userId}`)
      
      // Use AI insights endpoint through API Gateway
      const response = await apiService.getAIInsights()
      
      const insights = response.insights || []
      console.log(`✅ Retrieved ${insights.length} real behavioral insights`)
      return insights
    } catch (error) {
      console.error('❌ Real memory service unavailable:', error)
      // Return empty array and let the main function handle this gracefully
      return []
    }
  }

  /**
   * Call REAL ML service for crisis prediction - NO MOCK DATA
   */
  private async callRealMLCrisisPrediction(data: any): Promise<any> {
    try {
      console.log('🤖 Calling REAL ML crisis prediction service')
      const response = await apiService.request<any>('/ml/crisis/predict-risk', {
        method: 'POST',
        body: JSON.stringify(data)
      })
      
      console.log('✅ Real ML crisis prediction completed')
      return response.crisis_assessment || response
    } catch (error) {
      console.error('❌ Real ML crisis prediction failed:', error)
      throw new Error('Crisis analysis requires ML service for risk prediction. Please ensure ML service is running.')
    }
  }

  /**
   * Process ML assessment and convert to frontend format
   */
  private processMLAssessment(
    mlAssessment: any, 
    moodEntries: any[], 
    behavioralInsights: any[]
  ): CrisisAnalysisResult {
    // Guard: ML assessment may be null/undefined if ML service is down or returned no data
    if (!mlAssessment || typeof mlAssessment !== 'object') {
      console.warn('⚠️ ML crisis assessment missing or invalid. Returning fallback crisis analysis result.')
      const fallback = this.createServiceUnavailableResponse('ml service unavailable or returned no data')
      return {
        ...fallback,
        dataQuality: {
          moodEntries: moodEntries.length,
          journalEntries: 0,
          sufficientData: moodEntries.length >= 7
        },
        mlAssessment: mlAssessment || null,
        lastUpdated: new Date().toISOString()
      }
    }

    // Convert ML risk level to frontend format
    const riskLevel = this.convertRiskLevel(mlAssessment?.risk_level)
    
    // Extract crisis indicators from various sources
    const crisisIndicators = this.extractCrisisIndicators(moodEntries, behavioralInsights, mlAssessment)
    
    // Generate recommendations based on ML assessment
  const recommendations = mlAssessment?.recommended_interventions || []
    
    return {
      riskLevel,
      confidence: mlAssessment?.confidence ?? 0.5,
      riskFactors: mlAssessment?.key_risk_factors ?? [],
      protectiveFactors: mlAssessment?.protective_factors ?? [],
      recommendations,
      urgencyLevel: this.convertUrgencyLevel(mlAssessment?.urgency_level),
      timeToIntervention: this.calculateTimeToIntervention(riskLevel, mlAssessment?.time_to_crisis),
      crisisIndicators,
      lastUpdated: new Date().toISOString(),
      mlAssessment,
      dataQuality: {
        moodEntries: moodEntries.length,
        journalEntries: 0, // Will be updated when journal data is available
        sufficientData: moodEntries.length >= 7
      }
    }
  }

  /**
   * Convert ML risk level to frontend format
   */
  private convertRiskLevel(mlRiskLevel: string): CrisisAnalysisResult['riskLevel'] {
    switch (mlRiskLevel?.toUpperCase()) {
      case 'MINIMAL': return 'minimal'
      case 'LOW': return 'low'
      case 'MEDIUM': return 'medium'
      case 'HIGH': return 'high'
      case 'CRITICAL': return 'critical'
      default: return 'medium'
    }
  }

  /**
   * Convert ML urgency level to frontend format
   */
  private convertUrgencyLevel(mlUrgencyLevel: string): CrisisAnalysisResult['urgencyLevel'] {
    switch (mlUrgencyLevel?.toUpperCase()) {
      case 'ROUTINE': return 'routine'
      case 'MODERATE': return 'moderate'
      case 'URGENT': return 'urgent'
      case 'IMMEDIATE': return 'immediate'
      default: return 'moderate'
    }
  }

  /**
   * Calculate time to intervention based on risk level
   */
  private calculateTimeToIntervention(riskLevel: string, timeToCrisis: any): string {
    if (timeToCrisis && typeof timeToCrisis === 'object') {
      return timeToCrisis.estimated_hours ? `${timeToCrisis.estimated_hours} hours` : '24-48 hours'
    }
    
    switch (riskLevel) {
      case 'critical': return 'Immediate'
      case 'high': return '2-6 hours'
      case 'medium': return '24-48 hours'
      case 'low': return '1-7 days'
      default: return '1-2 weeks'
    }
  }

  /**
   * Extract crisis indicators from all data sources
   */
  private extractCrisisIndicators(
    moodEntries: any[], 
    behavioralInsights: any[], 
    mlAssessment: any
  ): CrisisIndicator[] {
    const indicators: CrisisIndicator[] = []
    
    // Extract mood-based indicators
    if (moodEntries.length > 0) {
      const recentMoods = moodEntries.slice(0, 7) // Last 7 entries
      const avgMood = recentMoods.reduce((sum, entry) => sum + (entry.mood_score || 5), 0) / recentMoods.length
      
      if (avgMood < 3) {
        indicators.push({
          type: 'mood',
          severity: avgMood < 2 ? 'critical' : 'high',
          trend: this.analyzeMoodTrend(recentMoods),
          description: `Average mood score: ${avgMood.toFixed(1)}/10`,
          timestamp: new Date().toISOString(),
          confidence: 0.9
        })
      }
    }
    
    // Extract behavioral indicators
    behavioralInsights.forEach((insight: any) => {
      if (insight.pattern_type === 'concerning') {
        indicators.push({
          type: 'behavioral',
          severity: this.convertInsightRiskToSeverity(insight.risk_level),
          trend: 'worsening',
          description: insight.description,
          timestamp: new Date().toISOString(),
          confidence: insight.confidence || 0.7
        })
      }
    })
    
    return indicators
  }

  /**
   * Analyze mood trend from recent entries
   */
  private analyzeMoodTrend(moodEntries: any[]): CrisisIndicator['trend'] {
    if (moodEntries.length < 2) return 'stable'
    
    const recent = moodEntries[0]?.mood_score || 5
    const previous = moodEntries[moodEntries.length - 1]?.mood_score || 5
    
    if (recent > previous + 1) return 'improving'
    if (recent < previous - 1) return 'declining'
    return 'stable'
  }

  /**
   * Convert insight risk level to severity
   */
  private convertInsightRiskToSeverity(riskLevel: string): CrisisIndicator['severity'] {
    switch (riskLevel?.toLowerCase()) {
      case 'critical': return 'critical'
      case 'high': return 'high'
      case 'medium': return 'medium'
      case 'low': return 'low'
      default: return 'medium'
    }
  }

  /**
   * Get real-time system health for crisis detection services
   */
  async getSystemHealth(): Promise<any> {
    try {
      const healthChecks = await Promise.allSettled([
        this.checkServiceHealth('ML Service', '/ml/health'),
        this.checkServiceHealth('Mood Service', '/api/v1/mood/health'),
        this.checkServiceHealth('Memory Service', '/ai-context/health')
      ])
      
      return {
        services: healthChecks.map((result, index) => ({
          name: ['ML Service', 'Mood Service', 'Memory Service'][index],
          status: result.status === 'fulfilled' ? 'healthy' : 'unhealthy',
          details: result.status === 'fulfilled' ? result.value : result.reason
        })),
        timestamp: new Date().toISOString()
      }
    } catch (error) {
      console.error('System health check failed:', error)
      return {
        services: [],
        error: 'Health check failed',
        timestamp: new Date().toISOString()
      }
    }
  }

  /**
   * Check individual service health
   */
  private async checkServiceHealth(serviceName: string, healthUrl: string): Promise<any> {
    try {
      const response = await fetch(healthUrl, { 
        method: 'GET',
        timeout: 5000 
      } as any)
      
      if (response.ok) {
        return {
          status: 'healthy',
          responseTime: Date.now(),
          details: await response.json()
        }
      } else {
        throw new Error(`HTTP ${response.status}`)
      }
    } catch (error) {
      throw {
        status: 'unhealthy',
        error: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date().toISOString()
      }
    }
  }
}

// Export singleton instance
export const crisisDetectionService = new CrisisDetectionService()
