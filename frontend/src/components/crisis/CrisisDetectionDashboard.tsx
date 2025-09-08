/**
 * Crisis Detection Dashboard Component
 * 
 * Analyzes user activity and interactions to detect potential crises
 * and provide personalized recommendations and justifications.
 * Uses REAL backend services only - NO MOCK DATA
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
import { useAuth } from "@/hooks/useAuth"
import { apiService } from "@/services/api"
import { format } from "date-fns"

export function CrisisDetectionDashboard() {
  // Log to verify the new component is loading
  console.log('🚨 NEW CrisisDetectionDashboard component loaded!', new Date().toISOString())
  
  const [analysisResult, setAnalysisResult] = useState<CrisisAnalysisResult | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [systemMetrics, setSystemMetrics] = useState<any>(null)
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date())

  // Get authenticated user for real data analysis
  const { user, isAuthenticated } = useAuth()
  
  // Get wellness and journal data for analysis context
  const { moodEntries, analytics } = useWellness()
  const { entries } = useJournal()

  const analyzeCrisisRisk = async () => {
    // Ensure user is authenticated before analysis
    if (!isAuthenticated || !user) {
      setError('Authentication required for crisis analysis')
      setLoading(false)
      return
    }

    try {
      setLoading(true)
      setError(null)
      
      console.log(`🔍 Starting REAL crisis analysis for user ${user.id}...`)
      
      // Use the REAL crisis detection service with authenticated user ID
      const analysisData = await crisisDetectionService.analyzeCrisisRisk(user.id)
      
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

  // Initialize analysis on component mount
  useEffect(() => {
    if (isAuthenticated && user) {
      analyzeCrisisRisk()
    }
  }, [isAuthenticated, user])

  // Auto-refresh every 2 minutes
  useEffect(() => {
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
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Brain className="h-5 w-5" />
              Analyzing Crisis Risk...
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="animate-pulse">
                <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                <div className="h-4 bg-gray-200 rounded w-1/2 mt-2"></div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (error) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold">Crisis Detection</h1>
          <Button onClick={analyzeCrisisRisk} variant="outline" size="sm">
            <RefreshCw className="h-4 w-4 mr-2" />
            Retry
          </Button>
        </div>
        <Alert>
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            {error}
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

  // Check authentication
  if (!isAuthenticated || !user) {
    return (
      <div className="space-y-6">
        <Alert>
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            Authentication required for crisis analysis. Please log in to access your personalized crisis detection dashboard.
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
        <Card className={`${getRiskLevelColor(analysisResult.riskLevel)} border-2`}>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                {getRiskIcon(analysisResult.riskLevel)}
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
                  {analysisResult.riskLevel} Risk
                </Badge>
              </div>
            </div>
            <div className="text-sm text-gray-600">
              Real-time analysis using actual user data • Last updated: {format(lastUpdated, 'MMM d, h:mm a')}
            </div>
          </CardHeader>
        </Card>
      </motion.div>

      {/* Crisis Hotline Alert */}
      {(analysisResult.urgencyLevel === 'immediate' || analysisResult.urgencyLevel === 'urgent') && (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
        >
          <Alert className="border-red-200 bg-red-50">
            <Phone className="h-4 w-4" />
            <AlertDescription className="font-medium">
              <div className="flex items-center justify-between">
                <span>Crisis support recommended. Call 988 (Suicide & Crisis Lifeline) for immediate help.</span>
                <Button size="sm" className="bg-red-600 hover:bg-red-700">
                  <Phone className="h-4 w-4 mr-2" />
                  Call Now
                </Button>
              </div>
            </AlertDescription>
          </Alert>
        </motion.div>
      )}

      <Tabs defaultValue="overview" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="analysis">Analysis</TabsTrigger>
          <TabsTrigger value="indicators">Indicators</TabsTrigger>
          <TabsTrigger value="actions">Actions</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Risk Level</CardTitle>
                <BarChart3 className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <Badge className={getRiskLevelColor(analysisResult.riskLevel)}>
                    {analysisResult.riskLevel}
                  </Badge>
                  <div className="text-2xl font-bold">
                    <span>{(analysisResult.confidence * 100).toFixed(0)}/100</span>
                  </div>
                  <Progress value={analysisResult.confidence * 100} className="h-3" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Crisis Indicators</CardTitle>
                <AlertTriangle className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  <span>{analysisResult.crisisIndicators?.length || 0}</span>
                </div>
                <p className="text-xs text-muted-foreground">
                  Active concerns detected
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Immediate Actions</CardTitle>
                <Zap className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  <span>{analysisResult.recommendations?.length || 0}</span>
                </div>
                <p className="text-xs text-muted-foreground">
                  Recommended steps
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Professional Help</CardTitle>
                <Users className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  <span>{analysisResult.urgencyLevel === 'immediate' || analysisResult.urgencyLevel === 'urgent' ? 'Recommended' : 'Monitor'}</span>
                </div>
                <p className="text-xs text-muted-foreground">
                  Current guidance
                </p>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="analysis" className="space-y-4">
          <div className="grid gap-6 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingDown className="h-5 w-5" />
                  Crisis Indicators
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {analysisResult.crisisIndicators && analysisResult.crisisIndicators.length > 0 ? (
                  analysisResult.crisisIndicators.map((indicator, index) => (
                    <div key={index} className="flex items-center justify-between">
                      <span className="text-sm font-medium">{indicator.type.charAt(0).toUpperCase() + indicator.type.slice(1)}</span>
                      <Badge className={indicator.severity === 'critical' ? 'bg-red-100 text-red-800' : 
                                       indicator.severity === 'high' ? 'bg-orange-100 text-orange-800' : 
                                       'bg-yellow-100 text-yellow-800'}>
                        {indicator.severity.charAt(0).toUpperCase() + indicator.severity.slice(1)}
                      </Badge>
                    </div>
                  ))
                ) : (
                  <div className="text-sm text-gray-600">
                    <p>No crisis indicators detected at this time.</p>
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Users className="h-5 w-5" />
                  Risk Factors
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {analysisResult.riskFactors && analysisResult.riskFactors.length > 0 ? (
                  analysisResult.riskFactors.map((factor, index) => (
                    <div key={index} className="flex items-center gap-2">
                      <AlertTriangle className="h-4 w-4 text-orange-500" />
                      <span className="text-sm">{factor}</span>
                    </div>
                  ))
                ) : (
                  <div className="text-sm text-gray-600">
                    <p>No significant risk factors detected.</p>
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Activity className="h-5 w-5" />
                  Stress Indicators
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {analysisResult.protectiveFactors && analysisResult.protectiveFactors.length > 0 ? (
                  analysisResult.protectiveFactors.map((factor, index) => (
                    <div key={index} className="flex items-center gap-2">
                      <Shield className="h-4 w-4 text-green-500" />
                      <span className="text-sm">{factor}</span>
                    </div>
                  ))
                ) : (
                  <div className="text-sm text-gray-600">
                    <p>Building protective factors is recommended.</p>
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Brain className="h-5 w-5" />
                  Recommendations
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {analysisResult.recommendations && analysisResult.recommendations.length > 0 ? (
                  analysisResult.recommendations.map((recommendation, index) => (
                    <div key={index} className="flex items-center gap-2">
                      <Lightbulb className="h-4 w-4 text-blue-500" />
                      <span className="text-sm">{recommendation}</span>
                    </div>
                  ))
                ) : (
                  <div className="text-sm text-gray-600">
                    <p>Continue monitoring. No specific recommendations at this time.</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="indicators" className="space-y-4">
          <div className="space-y-4">
            {analysisResult.crisisIndicators && analysisResult.crisisIndicators.length > 0 ? 
              analysisResult.crisisIndicators.map((indicator, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <Card>
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <CardTitle className="flex items-center gap-2">
                          <AlertTriangle className={`h-4 w-4 ${
                          indicator.severity === 'critical' ? 'text-red-600' :
                          indicator.severity === 'high' ? 'text-red-500' :
                          indicator.severity === 'medium' ? 'text-orange-500' :
                          'text-yellow-500'
                        }`} />
                        {indicator.description}
                      </CardTitle>
                      <Badge variant={
                        indicator.severity === 'critical' ? 'destructive' :
                        indicator.severity === 'high' ? 'destructive' :
                        indicator.severity === 'medium' ? 'default' :
                        'secondary'
                      }>
                        {indicator.severity}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <h4 className="font-medium text-sm mb-2">Description</h4>
                      <p className="text-sm text-gray-600">{indicator.description}</p>
                    </div>
                    
                    <div className="flex items-center justify-between pt-2 border-t">
                      <span className="text-xs text-gray-500">
                        Confidence: {((indicator.confidence || 0.5) * 100).toFixed(0)}%
                      </span>
                      <span className="text-xs text-gray-500 capitalize">
                        Type: {indicator.type.replace('_', ' ')}
                      </span>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-gray-500 capitalize">
                        Trend: {indicator.trend}
                      </span>
                      <span className="text-xs text-gray-500">
                        {new Date(indicator.timestamp).toLocaleString()}
                      </span>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            )) : (
              <Card>
                <CardContent className="text-center py-8">
                  <Shield className="h-12 w-12 text-green-500 mx-auto mb-4" />
                  <p className="text-gray-600">No crisis indicators detected at this time.</p>
                  <p className="text-sm text-gray-500 mt-2">Your mental health appears stable based on current analysis.</p>
                </CardContent>
              </Card>
            )}
          </div>
        </TabsContent>

        <TabsContent value="actions" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="h-5 w-5" />
                Immediate Actions
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {analysisResult.recommendations && analysisResult.recommendations.length > 0 ? 
                  analysisResult.recommendations.map((action, index) => (
                    <div key={index} className="flex items-start gap-3 p-3 bg-blue-50 rounded-lg">
                      <div className="bg-blue-100 rounded-full p-1 mt-0.5">
                        <span className="text-blue-600 text-xs font-bold">{index + 1}</span>
                      </div>
                      <div className="flex-1">
                        <p className="text-sm font-medium text-blue-900">{action}</p>
                      </div>
                    </div>
                  )) : (
                    <div className="text-center py-4">
                      <p className="text-gray-600">Continue with your current wellness routine.</p>
                      <p className="text-sm text-gray-500 mt-2">No immediate actions required at this time.</p>
                    </div>
                  )
                }
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
