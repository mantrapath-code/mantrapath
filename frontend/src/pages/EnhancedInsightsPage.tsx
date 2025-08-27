/**
 * Enhanced Insights Page - Uses real unified data from all services
 */

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Skeleton } from '@/components/ui/skeleton'
import { motion } from 'framer-motion'
import { 
  Brain,
  ChartLine,
  Target,
  TrendUp,
  TrendDown,
  ArrowLeft,
  ArrowClockwise,
  Lightbulb,
  Heart,
  Trophy,
  Calendar,
  Shield,
  Warning
} from '@phosphor-icons/react'
import { enhancedUnifiedInsightsService, UnifiedInsightsData } from '@/services/enhancedUnifiedInsights'
import { EmotionalWeatherWidget } from '@/components/mood/EmotionalWeatherWidget'

interface EnhancedInsightsPageProps {
  onBack?: () => void
}

export function EnhancedInsightsPage({ onBack }: EnhancedInsightsPageProps) {
  const [insights, setInsights] = useState<UnifiedInsightsData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [refreshing, setRefreshing] = useState(false)

  const fetchInsights = async () => {
    try {
      setError(null)
      const data = await enhancedUnifiedInsightsService.getUnifiedInsights()
      setInsights(data)
    } catch (err) {
      console.error('Failed to fetch unified insights:', err)
      setError('Unable to load insights. Please try again.')
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  useEffect(() => {
    fetchInsights()
  }, [])

  const handleRefresh = async () => {
    setRefreshing(true)
    enhancedUnifiedInsightsService.clearCache() // Force fresh data
    await fetchInsights()
  }

  if (loading && !insights) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          {onBack && (
            <Button variant="ghost" onClick={onBack}>
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back
            </Button>
          )}
          <div className="flex items-center gap-2">
            <Skeleton className="h-4 w-32" />
          </div>
        </div>
        
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <Card key={i}>
              <CardHeader>
                <Skeleton className="h-6 w-24" />
              </CardHeader>
              <CardContent>
                <Skeleton className="h-4 w-full mb-2" />
                <Skeleton className="h-4 w-3/4" />
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    )
  }

  if (error && !insights) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center space-y-4">
          <Warning className="h-12 w-12 text-orange-500 mx-auto" />
          <p className="text-muted-foreground">{error}</p>
          <Button onClick={handleRefresh} disabled={refreshing}>
            <ArrowClockwise className={`mr-2 h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
            Try Again
          </Button>
        </div>
      </div>
    )
  }

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'improving': return <TrendUp className="h-4 w-4 text-green-600" />
      case 'declining': return <TrendDown className="h-4 w-4 text-red-600" />
      default: return <Target className="h-4 w-4 text-gray-600" />
    }
  }

  const getDataFreshnessColor = (freshness: string) => {
    switch (freshness) {
      case 'fresh': return 'text-green-600'
      case 'cached': return 'text-blue-600'
      case 'stale': return 'text-orange-600'
      default: return 'text-gray-600'
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        {onBack && (
          <Button variant="ghost" onClick={onBack}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back
          </Button>
        )}
        
        <div className="flex items-center gap-2">
          {insights && (
            <>
              <Badge 
                variant="outline" 
                className={getDataFreshnessColor(insights.metadata.dataFreshness)}
              >
                {insights.metadata.dataFreshness} • {insights.metadata.servicesOnline}/{insights.metadata.totalServices} services
              </Badge>
              <Button
                variant="ghost"
                size="sm"
                onClick={handleRefresh}
                disabled={refreshing}
              >
                <ArrowClockwise className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
              </Button>
            </>
          )}
        </div>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="space-y-6"
      >
        <div>
          <h1 className="text-3xl font-bold">Insights & Analytics</h1>
          <p className="text-muted-foreground mt-2">
            Real-time insights from your wellness journey powered by unified data analysis
            {insights && ` • Confidence: ${Math.round(insights.metadata.confidenceScore)}%`}
          </p>
        </div>

        {insights && (
          <>
            {/* Key Metrics Overview */}
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-base flex items-center gap-2">
                    <Heart className="text-red-500" size={18} />
                    Weekly Score
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="text-2xl font-bold">{insights.mood.currentScore}</div>
                      <div className="flex items-center gap-1 text-sm text-muted-foreground">
                        {getTrendIcon(insights.mood.weeklyTrend)}
                        {insights.mood.weeklyTrend}
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-sm text-muted-foreground">This Week</div>
                      <Progress value={insights.mood.currentScore} className="h-2 w-16" />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-base flex items-center gap-2">
                    <Calendar className="text-blue-500" size={18} />
                    Days Tracked
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="text-2xl font-bold">{insights.mood.totalEntries}</div>
                      <div className="text-sm text-muted-foreground">Total entries</div>
                    </div>
                    <div className="text-right">
                      <div className="text-sm text-muted-foreground">Streak</div>
                      <div className="text-lg font-semibold">{insights.mood.moodStreak}</div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-base flex items-center gap-2">
                    <Brain className="text-purple-500" size={18} />
                    AI Confidence
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="text-2xl font-bold">{Math.round(insights.emotionalWeather.confidence * 100)}%</div>
                      <div className="text-sm text-muted-foreground">Weather forecast</div>
                    </div>
                    <div className="text-2xl">
                      {insights.emotionalWeather.current}
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-base flex items-center gap-2">
                    <Trophy className="text-yellow-500" size={18} />
                    Engagement
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="text-2xl font-bold">{Math.round(insights.activity.engagementLevel * 100)}%</div>
                      <div className="text-sm text-muted-foreground">Activity level</div>
                    </div>
                    <div className="text-right">
                      <div className="text-sm text-muted-foreground">Achievements</div>
                      <div className="text-lg font-semibold">{insights.activity.achievementsUnlocked}</div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Emotional Weather Section */}
            <div className="grid gap-6 lg:grid-cols-3">
              <div className="lg:col-span-2">
                <EmotionalWeatherWidget 
                  showDetails={true}
                  autoRefresh={false}
                  className="h-full"
                />
              </div>
              
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Shield className="text-green-500" size={18} />
                    Protective Factors
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {insights.emotionalWeather.protectiveFactors.map((factor, index) => (
                      <div key={index} className="flex items-center gap-2">
                        <div className="w-2 h-2 bg-green-500 rounded-full" />
                        <span className="text-sm">{factor}</span>
                      </div>
                    ))}
                    {insights.emotionalWeather.protectiveFactors.length === 0 && (
                      <p className="text-sm text-muted-foreground">Continue tracking to identify protective factors</p>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* AI Recommendations */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Lightbulb className="text-amber-500" size={18} />
                  Personalized Recommendations
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4 md:grid-cols-2">
                  {insights.aiInsights.recommendations.map((rec, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className="p-4 border rounded-lg"
                    >
                      <div className="flex items-start gap-3">
                        <Badge 
                          variant={rec.priority === 'high' ? 'destructive' : rec.priority === 'medium' ? 'default' : 'secondary'}
                          className="text-xs"
                        >
                          {rec.priority}
                        </Badge>
                        <div className="flex-1">
                          <h4 className="font-medium">{rec.title}</h4>
                          <p className="text-sm text-muted-foreground mt-1">{rec.description}</p>
                        </div>
                      </div>
                    </motion.div>
                  ))}
                  {insights.aiInsights.recommendations.length === 0 && (
                    <div className="col-span-full text-center py-8">
                      <p className="text-muted-foreground">
                        Continue your wellness journey to receive personalized recommendations
                      </p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Cultural Adaptations */}
            {insights.cultural.adaptations.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <ChartLine className="text-indigo-500" size={18} />
                    Cultural Wellness Insights
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid gap-4 md:grid-cols-2">
                    <div>
                      <h4 className="font-medium mb-2">Regional Adaptations</h4>
                      <div className="space-y-2">
                        {insights.cultural.adaptations.map((adaptation, index) => (
                          <Badge key={index} variant="outline">
                            {adaptation.replace('_', ' ')}
                          </Badge>
                        ))}
                      </div>
                    </div>
                    <div>
                      <h4 className="font-medium mb-2">Cultural Recommendations</h4>
                      <div className="space-y-2">
                        {insights.cultural.culturalRecommendations.map((rec, index) => (
                          <p key={index} className="text-sm text-muted-foreground">• {rec}</p>
                        ))}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}
          </>
        )}
      </motion.div>
    </div>
  )
}
