/**
 * Crisis Detection Dashboard Component
 * 
 * Analyzes user activity and interactions to detect potential crises
 * and provide personalized recommendations and justifications.
 * 
 * Features:
 * - Real-time user activity analysis
 * - Crisis pattern detection
 * - Personalized intervention recommendations
 * - User-friendly crisis explanations
 * - Actionable guidance for crisis management
 */

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { 
  AlertTriangle, 
  Heart, 
  Brain, 
  Shield, 
  TrendingDown, 
  TrendingUp,
  MessageCircle,
  Activity,
  Clock,
  CheckCircle,
  XCircle,
  Eye,
  RefreshCw,
  Phone,
  AlertCircle,
  BarChart3,
  Zap,
  Users,
  Calendar,
  Target,
  ArrowRight,
  Lightbulb
} from "lucide-react"
import { motion, AnimatePresence } from "framer-motion"
import { toast } from "sonner"
import { crisisDetectionService, type CrisisAnalysisResult } from "@/services/crisisDetection"
import { useWellness } from "@/hooks/useWellness"
import { useJournal } from "@/hooks/useJournal"
import { apiService } from "@/services/api"
import { format } from "date-fns"

interface CrisisIndicator {
  type: string
  severity: 'low' | 'medium' | 'high' | 'critical'
  description: string
  detected_patterns: string[]
  recommendations: string[]
  confidence: number
  justification: string
}

interface UserActivityAnalysis {
  mood_decline_trend: {
    detected: boolean
    severity: 'low' | 'medium' | 'high'
    duration_days: number
    current_score: number
    recommendation: string
  }
  interaction_changes: {
    reduced_engagement: boolean
    isolation_indicators: string[]
    social_withdrawal_score: number
    recommendation: string
  }
  stress_indicators: {
    elevated_stress: boolean
    stress_triggers: string[]
    coping_effectiveness: number
    recommendation: string
  }
  behavioral_patterns: {
    concerning_patterns: string[]
    protective_factors: string[]
    resilience_score: number
    recommendation: string
  }
}

interface CrisisDetectionData {
  overall_risk_level: 'minimal' | 'low' | 'moderate' | 'high' | 'critical'
  risk_score: number
  crisis_indicators: CrisisIndicator[]
  user_activity_analysis: UserActivityAnalysis
  immediate_actions: string[]
  professional_help_recommended: boolean
  crisis_hotline_needed: boolean
  last_updated: string
}

export function CrisisDetectionDashboard() {
  // Log to verify the new component is loading
  console.log('🚨 NEW CrisisDetectionDashboard component loaded!', new Date().toISOString())
  
  const [analysisResult, setAnalysisResult] = useState<CrisisAnalysisResult | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [systemMetrics, setSystemMetrics] = useState<any>(null)
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date())
  
  const { moodEntries, analytics } = useWellness()
  const { entries } = useJournal()

  const analyzeCrisisRisk = async () => {
    try {
      setLoading(true)
      setError(null)
      
      console.log('🔍 Starting REAL crisis analysis via service...')
      
      // Use the REAL crisis detection service instead of local mock data
      const analysisData = await crisisDetectionService.analyzeCrisisRisk()
      
      console.log('✅ Real crisis analysis completed:', analysisData)
      
      setAnalysisResult(analysisData)
      setLastUpdated(new Date())
      
    } catch (err: any) {
      console.error('❌ Crisis analysis failed:', err)
      setError(`Unable to analyze crisis risk: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }

  const analyzeMoodTrend = () => {
    const recentMoods = moodEntries.slice(0, 14) // Last 14 days
    const currentMood = recentMoods.length > 0 ? recentMoods[0].mood : 5
    
    // Calculate trend
    const moodValues = recentMoods.map(entry => entry.mood)
    const isDecreasing = moodValues.length > 3 && 
      moodValues.slice(0, 3).every((mood, i) => i === 0 || mood < moodValues[i - 1])
    
    const averageMood = moodValues.length > 0 ? moodValues.reduce((a, b) => a + b, 0) / moodValues.length : 5
    
    let severity: 'low' | 'medium' | 'high' = 'low'
    if (currentMood <= 3 && isDecreasing) severity = 'high'
    else if (currentMood <= 4 && isDecreasing) severity = 'medium'
    
    return {
      detected: isDecreasing && currentMood < 5,
      severity,
      duration_days: recentMoods.length,
      current_score: currentMood,
      recommendation: severity === 'high' 
        ? "Your mood has been declining consistently. Consider reaching out to a counselor or trusted friend for support."
        : severity === 'medium'
        ? "Notice the downward trend in your mood. Practice self-care activities and monitor how you're feeling."
        : "Your mood is stable. Keep maintaining your current wellness practices."
    }
  }

  const analyzeInteractionChanges = () => {
    const recentEntries = entries.slice(0, 7) // Last week of journal entries
    const reducedEngagement = recentEntries.length < 3 // Less than 3 entries in a week
    
    const isolationKeywords = ['alone', 'lonely', 'isolated', 'withdrawn', 'nobody', 'disconnected']
    const isolationIndicators = recentEntries
      .filter(entry => isolationKeywords.some(keyword => entry.content.toLowerCase().includes(keyword)))
      .map(entry => `Mentioned feeling ${isolationKeywords.find(k => entry.content.toLowerCase().includes(k))} on ${new Date(entry.timestamp).toLocaleDateString()}`)
    
    const socialWithdrawalScore = reducedEngagement ? 40 : 0 + (isolationIndicators.length * 15)
    
    return {
      reduced_engagement: reducedEngagement,
      isolation_indicators: isolationIndicators,
      social_withdrawal_score: Math.min(socialWithdrawalScore, 100),
      recommendation: socialWithdrawalScore > 50
        ? "You may be withdrawing from social connections. Consider reaching out to someone you trust or joining a supportive community."
        : "Your social engagement looks healthy. Continue nurturing your relationships."
    }
  }

  const analyzeStressIndicators = () => {
    const stressKeywords = ['stress', 'anxious', 'overwhelmed', 'pressure', 'worried', 'panic', 'exhausted']
    const stressEntries = entries.slice(0, 10).filter(entry => 
      stressKeywords.some(keyword => entry.content.toLowerCase().includes(keyword))
    )
    
    const elevatedStress = stressEntries.length > 3
    const stressTriggers = stressKeywords.filter(keyword => 
      stressEntries.some(entry => entry.content.toLowerCase().includes(keyword))
    )
    
    // Calculate coping effectiveness based on positive words following stress mentions
    const copingWords = ['better', 'helped', 'calmer', 'relaxed', 'managed', 'coped']
    const copingMentions = stressEntries.filter(entry =>
      copingWords.some(word => entry.content.toLowerCase().includes(word))
    )
    const copingEffectiveness = stressEntries.length > 0 ? (copingMentions.length / stressEntries.length) * 100 : 75
    
    return {
      elevated_stress: elevatedStress,
      stress_triggers: stressTriggers,
      coping_effectiveness: copingEffectiveness,
      recommendation: elevatedStress && copingEffectiveness < 30
        ? "High stress levels detected with limited coping strategies. Consider learning new stress management techniques or speaking with a counselor."
        : elevatedStress
        ? "Stress detected, but you seem to be managing it well. Continue your current coping strategies."
        : "Your stress levels appear manageable. Keep up your good self-care practices."
    }
  }

  const analyzeBehavioralPatterns = () => {
    const concerningPatterns: string[] = []
    const protectiveFactors: string[] = []
    
    // Analyze patterns from journal entries
    const recentEntries = entries.slice(0, 14)
    
    // Concerning patterns
    if (recentEntries.filter(e => e.content.toLowerCase().includes('sleep')).length > 3) {
      if (recentEntries.some(e => e.content.toLowerCase().includes('insomnia') || e.content.toLowerCase().includes("can't sleep"))) {
        concerningPatterns.push('Sleep disturbances mentioned frequently')
      }
    }
    
    if (recentEntries.some(e => e.content.toLowerCase().includes('hopeless') || e.content.toLowerCase().includes('worthless'))) {
      concerningPatterns.push('Negative self-perception expressed')
    }
    
    // Protective factors
    if (recentEntries.some(e => e.content.toLowerCase().includes('grateful') || e.content.toLowerCase().includes('thankful'))) {
      protectiveFactors.push('Practicing gratitude')
    }
    
    if (recentEntries.some(e => e.content.toLowerCase().includes('exercise') || e.content.toLowerCase().includes('workout'))) {
      protectiveFactors.push('Regular physical activity')
    }
    
    if (recentEntries.some(e => e.content.toLowerCase().includes('friend') || e.content.toLowerCase().includes('family'))) {
      protectiveFactors.push('Social connections maintained')
    }
    
    const resilienceScore = Math.max(0, 70 - (concerningPatterns.length * 15) + (protectiveFactors.length * 10))
    
    return {
      concerning_patterns: concerningPatterns,
      protective_factors: protectiveFactors,
      resilience_score: resilienceScore,
      recommendation: resilienceScore < 40
        ? "Building resilience is important right now. Focus on strengthening your support network and developing healthy coping strategies."
        : resilienceScore < 60
        ? "You have some protective factors in place. Continue building on these strengths while addressing areas of concern."
        : "You show good resilience and protective factors. Keep maintaining these positive patterns."
    }
  }

  const calculateOverallRiskScore = (mood: any, interaction: any, stress: any, behavioral: any) => {
    let score = 0
    
    // Mood contribution (0-30 points)
    if (mood.detected) {
      score += mood.severity === 'high' ? 30 : mood.severity === 'medium' ? 20 : 10
    }
    
    // Social withdrawal contribution (0-25 points)
    score += Math.min(interaction.social_withdrawal_score * 0.25, 25)
    
    // Stress contribution (0-20 points)
    if (stress.elevated_stress) {
      score += 20 - (stress.coping_effectiveness * 0.2)
    }
    
    // Behavioral patterns contribution (0-25 points)
    score += Math.max(0, 25 - (behavioral.resilience_score * 0.25))
    
    return Math.min(Math.round(score), 100)
  }

  const determineRiskLevel = (score: number): 'minimal' | 'low' | 'moderate' | 'high' | 'critical' => {
    if (score >= 90) return 'critical'
    if (score >= 70) return 'high'
    if (score >= 50) return 'moderate'
    if (score >= 25) return 'low'
    return 'minimal'
  }

  const generateCrisisIndicators = (mood: any, interaction: any, stress: any, behavioral: any): CrisisIndicator[] => {
    const indicators: CrisisIndicator[] = []
    
    if (mood.detected && mood.severity === 'high') {
      indicators.push({
        type: 'mood_decline',
        severity: 'high',
        description: 'Significant mood decline detected',
        detected_patterns: [`Mood dropped to ${mood.current_score}/10`, 'Consistent downward trend'],
        recommendations: [
          'Reach out to a mental health professional',
          'Connect with trusted friends or family',
          'Practice gentle self-care activities'
        ],
        confidence: 85,
        justification: 'Your mood has been consistently declining over several days, which is a strong indicator that you may benefit from additional support and intervention.'
      })
    }
    
    if (interaction.social_withdrawal_score > 60) {
      indicators.push({
        type: 'social_withdrawal',
        severity: interaction.social_withdrawal_score > 80 ? 'high' : 'medium',
        description: 'Social withdrawal and isolation patterns',
        detected_patterns: interaction.isolation_indicators,
        recommendations: [
          'Schedule time with a friend or family member',
          'Join a support group or community activity',
          'Consider online communities if in-person feels overwhelming'
        ],
        confidence: 75,
        justification: 'Isolation and withdrawal from social connections can worsen mental health. Reconnecting with others, even in small ways, can provide crucial support.'
      })
    }
    
    if (stress.elevated_stress && stress.coping_effectiveness < 30) {
      indicators.push({
        type: 'stress_overload',
        severity: 'medium',
        description: 'High stress with ineffective coping strategies',
        detected_patterns: stress.stress_triggers.map(trigger => `Frequent mentions of: ${trigger}`),
        recommendations: [
          'Learn new stress management techniques (deep breathing, meditation)',
          'Break large problems into smaller, manageable steps',
          'Consider professional guidance for stress management'
        ],
        confidence: 70,
        justification: 'High stress levels combined with limited effective coping strategies can lead to overwhelming feelings and potential crisis situations.'
      })
    }
    
    return indicators
  }

  const generateImmediateActions = (riskLevel: string, indicators: CrisisIndicator[]): string[] => {
    const actions: string[] = []
    
    if (riskLevel === 'critical' || riskLevel === 'high') {
      actions.push('Contact a crisis hotline: Call 988 (Suicide & Crisis Lifeline)')
      actions.push('Reach out to a trusted friend, family member, or counselor immediately')
      actions.push('Consider going to an emergency room if you feel unsafe')
    }
    
    if (riskLevel === 'moderate' || riskLevel === 'high') {
      actions.push('Schedule an appointment with a mental health professional')
      actions.push('Practice grounding techniques (5-4-3-2-1 sensory method)')
      actions.push('Engage in a comforting, safe activity')
    }
    
    actions.push('Continue tracking your mood to monitor changes')
    actions.push('Maintain your sleep schedule and eat regular meals')
    actions.push('Practice gentle movement or exercise as you feel able')
    
    return actions
  }

  useEffect(() => {
    analyzeCrisisRisk()
    
    // Auto-refresh every 2 minutes
    const interval = setInterval(analyzeCrisisRisk, 2 * 60 * 1000)
    return () => clearInterval(interval)
  }, [moodEntries, entries])

  const getRiskLevelColor = (level: string) => {
    switch (level) {
      case 'critical': return 'bg-red-100 text-red-800 border-red-200'
      case 'high': return 'bg-red-50 text-red-700 border-red-200'
      case 'moderate': return 'bg-orange-50 text-orange-700 border-orange-200'
      case 'low': return 'bg-yellow-50 text-yellow-700 border-yellow-200'
      default: return 'bg-green-50 text-green-700 border-green-200'
    }
  }

  const getRiskIcon = (level: string) => {
    switch (level) {
      case 'critical':
      case 'high': return <AlertTriangle className="h-5 w-5" />
      case 'moderate': return <TrendingDown className="h-5 w-5" />
      case 'low': return <TrendingUp className="h-5 w-5" />
      default: return <Shield className="h-5 w-5" />
    }
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold">Crisis Detection</h1>
          <div className="animate-pulse">
            <div className="h-4 w-32 bg-gray-200 rounded"></div>
          </div>
        </div>
        <div className="grid gap-4">
          {Array.from({ length: 3 }).map((_, i) => (
            <Card key={i}>
              <CardContent className="p-6">
                <div className="animate-pulse space-y-4">
                  <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                  <div className="h-4 bg-gray-200 rounded w-1/2"></div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="space-y-6">
        <Alert className="border-red-200 bg-red-50">
          <AlertTriangle className="h-4 w-4 text-red-600" />
          <AlertDescription className="text-red-800">
            {error}
            <Button
              onClick={analyzeCrisisRisk}
              variant="outline"
              size="sm"
              className="mt-2 ml-2"
            >
              <RefreshCw className="h-4 w-4 mr-2" />
              Try Again
            </Button>
          </AlertDescription>
        </Alert>
      </div>
    )
  }

  if (!analysisResult) {
    return (
      <div className="space-y-6">
        <Alert>
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            No crisis analysis data available. Please ensure you have mood entries and journal data to analyze.
          </AlertDescription>
        </Alert>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <Card className={`${getRiskLevelColor(analysisResult.overall_risk_level)} border-2`}>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                {getRiskIcon(analysisResult.overall_risk_level)}
                Crisis Detection Dashboard
                <Badge className="bg-green-500 text-white text-xs">NEW ✨</Badge>
              </CardTitle>
              <div className="flex items-center gap-3">
                <Button
                  onClick={analyzeCrisisRisk}
                  variant="outline"
                  size="sm"
                  disabled={loading}
                >
                  <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
                  Refresh Analysis
                </Button>
                <Badge variant="outline" className="text-xs capitalize">
                  {analysisResult.overall_risk_level} Risk
                </Badge>
                {lastUpdated && (
                  <div className="text-xs text-muted-foreground">
                    Updated: {lastUpdated.toLocaleTimeString()}
                  </div>
                )}
              </div>
            </div>
            <p className="text-sm opacity-90">
              AI-powered analysis of your activity patterns, interactions, and well-being indicators
            </p>
          </CardHeader>
        </Card>
      </motion.div>

      {/* Crisis Hotline Alert */}
      {analysisResult.crisis_hotline_needed && (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
        >
          <Alert className="border-red-500 bg-red-50 border-2">
            <Phone className="h-4 w-4 text-red-600" />
            <AlertDescription className="text-red-800">
              <div className="space-y-2">
                <p className="font-semibold">Immediate Support Available</p>
                <p>If you're having thoughts of suicide or self-harm, please reach out now:</p>
                <div className="flex gap-2 flex-wrap">
                  <Button
                    size="sm"
                    className="bg-red-600 hover:bg-red-700 text-white"
                    onClick={() => window.open('tel:988', '_self')}
                  >
                    <Phone className="h-4 w-4 mr-2" />
                    Call 988
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => window.open('sms:741741', '_self')}
                  >
                    Text HOME to 741741
                  </Button>
                </div>
              </div>
            </AlertDescription>
          </Alert>
        </motion.div>
      )}

      {/* Risk Score Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-medium">Overall Risk Score</h3>
              <Badge className={getRiskLevelColor(analysisResult.overall_risk_level)}>
                {analysisResult.overall_risk_level}
              </Badge>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Risk Level</span>
                <span>{analysisResult.risk_score}/100</span>
              </div>
              <Progress value={analysisResult.risk_score} className="h-3" />
              <p className="text-xs text-muted-foreground mt-2">
                Based on mood patterns, social interaction, stress levels, and behavioral indicators
              </p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-2 mb-4">
              <Activity className="h-5 w-5 text-blue-500" />
              <h3 className="font-medium">Active Monitoring</h3>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Crisis Indicators</span>
                <span>{analysisResult.crisis_indicators.length}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Data Sources</span>
                <span>Mood, Journal, Activity</span>
              </div>
              <p className="text-xs text-muted-foreground mt-2">
                Continuous analysis of your wellness patterns and behaviors
              </p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-2 mb-4">
              <Target className="h-5 w-5 text-green-500" />
              <h3 className="font-medium">Intervention Ready</h3>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Immediate Actions</span>
                <span>{analysisResult.immediate_actions.length}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Professional Help</span>
                <span>{analysisResult.professional_help_recommended ? 'Recommended' : 'Monitor'}</span>
              </div>
              <p className="text-xs text-muted-foreground mt-2">
                Personalized recommendations based on your current situation
              </p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Content Tabs */}
      <Tabs defaultValue="analysis" className="space-y-4">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="analysis">Activity Analysis</TabsTrigger>
          <TabsTrigger value="indicators">Crisis Indicators</TabsTrigger>
          <TabsTrigger value="actions">Recommended Actions</TabsTrigger>
        </TabsList>

        <TabsContent value="analysis" className="space-y-4">
          <div className="grid gap-4">
            {/* Mood Decline Analysis */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-lg">
                  <Heart className="h-5 w-5 text-pink-500" />
                  Mood Pattern Analysis
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="font-medium">Current Mood Score</span>
                  <Badge variant="outline">{analysisResult.user_activity_analysis.mood_decline_trend.current_score}/10</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="font-medium">Trend Detected</span>
                  <Badge className={analysisResult.user_activity_analysis.mood_decline_trend.detected ? 'bg-orange-100 text-orange-800' : 'bg-green-100 text-green-800'}>
                    {analysisResult.user_activity_analysis.mood_decline_trend.detected ? 'Declining' : 'Stable'}
                  </Badge>
                </div>
                <div className="bg-blue-50 p-4 rounded-lg">
                  <h4 className="font-medium text-blue-800 mb-2">What this means:</h4>
                  <p className="text-sm text-blue-700">{analysisResult.user_activity_analysis.mood_decline_trend.recommendation}</p>
                </div>
              </CardContent>
            </Card>

            {/* Social Interaction Analysis */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-lg">
                  <Users className="h-5 w-5 text-purple-500" />
                  Social Interaction Changes
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="font-medium">Engagement Level</span>
                  <Badge className={analysisResult.user_activity_analysis.interaction_changes.reduced_engagement ? 'bg-orange-100 text-orange-800' : 'bg-green-100 text-green-800'}>
                    {analysisResult.user_activity_analysis.interaction_changes.reduced_engagement ? 'Reduced' : 'Normal'}
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="font-medium">Social Withdrawal Score</span>
                  <span className="text-sm">{analysisResult.user_activity_analysis.interaction_changes.social_withdrawal_score}/100</span>
                </div>
                <Progress value={analysisResult.user_activity_analysis.interaction_changes.social_withdrawal_score} className="h-2" />
                
                {analysisResult.user_activity_analysis.interaction_changes.isolation_indicators.length > 0 && (
                  <div className="space-y-2">
                    <h4 className="font-medium text-sm">Isolation Indicators Detected:</h4>
                    <ul className="text-sm space-y-1">
                      {analysisResult.user_activity_analysis.interaction_changes.isolation_indicators.map((indicator, index) => (
                        <li key={index} className="flex items-start gap-2">
                          <span className="w-1 h-1 bg-orange-500 rounded-full mt-2 flex-shrink-0"></span>
                          <span className="text-orange-700">{indicator}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                
                <div className="bg-purple-50 p-4 rounded-lg">
                  <h4 className="font-medium text-purple-800 mb-2">How to improve:</h4>
                  <p className="text-sm text-purple-700">{analysisResult.user_activity_analysis.interaction_changes.recommendation}</p>
                </div>
              </CardContent>
            </Card>

            {/* Stress Indicators */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-lg">
                  <Brain className="h-5 w-5 text-red-500" />
                  Stress & Coping Analysis
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="font-medium">Elevated Stress</span>
                  <Badge className={analysisResult.user_activity_analysis.stress_indicators.elevated_stress ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'}>
                    {analysisResult.user_activity_analysis.stress_indicators.elevated_stress ? 'Detected' : 'Normal'}
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="font-medium">Coping Effectiveness</span>
                  <span className="text-sm">{Math.round(analysisResult.user_activity_analysis.stress_indicators.coping_effectiveness)}%</span>
                </div>
                <Progress value={analysisResult.user_activity_analysis.stress_indicators.coping_effectiveness} className="h-2" />
                
                {analysisResult.user_activity_analysis.stress_indicators.stress_triggers.length > 0 && (
                  <div className="space-y-2">
                    <h4 className="font-medium text-sm">Stress Triggers Identified:</h4>
                    <div className="flex flex-wrap gap-2">
                      {analysisResult.user_activity_analysis.stress_indicators.stress_triggers.map((trigger, index) => (
                        <Badge key={index} variant="secondary" className="text-xs">
                          {trigger}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
                
                <div className="bg-red-50 p-4 rounded-lg">
                  <h4 className="font-medium text-red-800 mb-2">Stress management guidance:</h4>
                  <p className="text-sm text-red-700">{analysisResult.user_activity_analysis.stress_indicators.recommendation}</p>
                </div>
              </CardContent>
            </Card>

            {/* Behavioral Patterns */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-lg">
                  <Target className="h-5 w-5 text-green-500" />
                  Behavioral Patterns & Resilience
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="font-medium">Resilience Score</span>
                  <span className="text-sm">{analysisResult.user_activity_analysis.behavioral_patterns.resilience_score}/100</span>
                </div>
                <Progress value={analysisResult.user_activity_analysis.behavioral_patterns.resilience_score} className="h-2" />
                
                <div className="grid md:grid-cols-2 gap-4">
                  {analysisResult.user_activity_analysis.behavioral_patterns.protective_factors.length > 0 && (
                    <div className="space-y-2">
                      <h4 className="font-medium text-sm text-green-700">✅ Protective Factors:</h4>
                      <ul className="text-sm space-y-1">
                        {analysisResult.user_activity_analysis.behavioral_patterns.protective_factors.map((factor, index) => (
                          <li key={index} className="flex items-start gap-2">
                            <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                            <span className="text-green-700">{factor}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                  
                  {analysisResult.user_activity_analysis.behavioral_patterns.concerning_patterns.length > 0 && (
                    <div className="space-y-2">
                      <h4 className="font-medium text-sm text-orange-700">⚠️ Areas of Concern:</h4>
                      <ul className="text-sm space-y-1">
                        {analysisResult.user_activity_analysis.behavioral_patterns.concerning_patterns.map((pattern, index) => (
                          <li key={index} className="flex items-start gap-2">
                            <AlertTriangle className="w-4 h-4 text-orange-500 mt-0.5 flex-shrink-0" />
                            <span className="text-orange-700">{pattern}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
                
                <div className="bg-green-50 p-4 rounded-lg">
                  <h4 className="font-medium text-green-800 mb-2">Building resilience:</h4>
                  <p className="text-sm text-green-700">{analysisResult.user_activity_analysis.behavioral_patterns.recommendation}</p>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="indicators" className="space-y-4">
          {analysisResult.crisis_indicators.length > 0 ? (
            <div className="space-y-4">
              {analysisResult.crisis_indicators.map((indicator, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <Card className={`border-l-4 ${
                    indicator.severity === 'high' ? 'border-l-red-500' :
                    indicator.severity === 'medium' ? 'border-l-orange-500' :
                    'border-l-yellow-500'
                  }`}>
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <CardTitle className="flex items-center gap-2 text-lg">
                          <AlertTriangle className={`h-5 w-5 ${
                            indicator.severity === 'high' ? 'text-red-500' :
                            indicator.severity === 'medium' ? 'text-orange-500' :
                            'text-yellow-500'
                          }`} />
                          {indicator.description}
                        </CardTitle>
                        <div className="flex items-center gap-2">
                          <Badge className={
                            indicator.severity === 'high' ? 'bg-red-100 text-red-800' :
                            indicator.severity === 'medium' ? 'bg-orange-100 text-orange-800' :
                            'bg-yellow-100 text-yellow-800'
                          }>
                            {indicator.severity} severity
                          </Badge>
                          <Badge variant="outline">
                            {indicator.confidence}% confidence
                          </Badge>
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="bg-blue-50 p-4 rounded-lg">
                        <h4 className="font-medium text-blue-800 mb-2">Why this matters:</h4>
                        <p className="text-sm text-blue-700">{indicator.justification}</p>
                      </div>
                      
                      {indicator.detected_patterns.length > 0 && (
                        <div className="space-y-2">
                          <h4 className="font-medium text-sm">Detected Patterns:</h4>
                          <ul className="text-sm space-y-1">
                            {indicator.detected_patterns.map((pattern, idx) => (
                              <li key={idx} className="flex items-start gap-2">
                                <span className="w-1 h-1 bg-gray-500 rounded-full mt-2 flex-shrink-0"></span>
                                <span className="text-gray-700">{pattern}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                      
                      <div className="space-y-2">
                        <h4 className="font-medium text-sm">Recommended Actions:</h4>
                        <ul className="text-sm space-y-2">
                          {indicator.recommendations.map((rec, idx) => (
                            <li key={idx} className="flex items-start gap-2">
                              <ArrowRight className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                              <span className="text-gray-700">{rec}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </div>
          ) : (
            <Card>
              <CardContent className="p-8 text-center">
                <Shield className="h-12 w-12 text-green-500 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-green-700 mb-2">No Crisis Indicators Detected</h3>
                <p className="text-sm text-green-600 mb-4">
                  Your current patterns don't show significant crisis indicators. Continue monitoring your wellness.
                </p>
                <Button variant="outline" onClick={analyzeCrisisRisk}>
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Re-analyze
                </Button>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="actions" className="space-y-4">
          <div className="grid gap-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Target className="h-5 w-5 text-blue-500" />
                  Immediate Actions You Can Take
                </CardTitle>
                <p className="text-sm text-muted-foreground">
                  Personalized recommendations based on your current situation and risk level
                </p>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {analysisResult.immediate_actions.map((action, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className="flex items-start gap-3 p-3 bg-blue-50 rounded-lg"
                    >
                      <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center text-blue-600 text-xs font-bold flex-shrink-0 mt-0.5">
                        {index + 1}
                      </div>
                      <div className="flex-1">
                        <p className="text-sm text-blue-800">{action}</p>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {analysisResult.professional_help_recommended && (
              <Card className="border-orange-200 bg-orange-50">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-orange-800">
                    <Lightbulb className="h-5 w-5" />
                    Professional Support Recommended
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-orange-700 mb-4">
                    Based on your current risk level, we recommend reaching out to a mental health professional for additional support.
                  </p>
                  <div className="space-y-2">
                    <Button size="sm" variant="outline" className="w-full">
                      Find Local Mental Health Services
                    </Button>
                    <Button size="sm" variant="outline" className="w-full">
                      Schedule Online Therapy Session
                    </Button>
                    <Button size="sm" variant="outline" className="w-full">
                      Contact Your Healthcare Provider
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )}

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Clock className="h-5 w-5 text-green-500" />
                  Ongoing Wellness Strategies
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-2 gap-4">
                  <div className="space-y-3">
                    <h4 className="font-medium text-sm">Daily Practices:</h4>
                    <ul className="text-sm space-y-2">
                      <li className="flex items-start gap-2">
                        <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                        <span>Continue daily mood tracking</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                        <span>Practice deep breathing exercises</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                        <span>Maintain regular sleep schedule</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                        <span>Gentle physical activity</span>
                      </li>
                    </ul>
                  </div>
                  
                  <div className="space-y-3">
                    <h4 className="font-medium text-sm">Support Network:</h4>
                    <ul className="text-sm space-y-2">
                      <li className="flex items-start gap-2">
                        <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                        <span>Stay connected with friends/family</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                        <span>Consider joining support groups</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                        <span>Use crisis hotlines when needed</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                        <span>Regular check-ins with counselor</span>
                      </li>
                    </ul>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}
