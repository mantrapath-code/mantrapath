/**
 * Enhanced Insights Page - Unified insight experience
 * 
 * This component consolidates all insight sources into a single,
 * comprehensive dashboard that provides actionable intelligence
 * for user wellness optimization.
 */

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  Brain,
  TrendUp,
  TrendDown,
  Target,
  Star,
  Clock,
  CheckCircle,
  ArrowLeft,
  Lightbulb,
  ChartLine,
  Calendar,
  Sparkle,
  Trophy,
  Heart,
  Lightning,
  Users,
  Gear,
  Warning
} from '@phosphor-icons/react'
import { motion, AnimatePresence } from 'framer-motion'
import { toast } from 'sonner'
import { 
  unifiedInsightService, 
  ComprehensiveInsights,
  RecommendedAction 
} from '@/services/unifiedInsightService'

interface EnhancedInsightsPageProps {
  onBack?: () => void
}

export function EnhancedInsightsPage({ onBack }: EnhancedInsightsPageProps) {
  const [insights, setInsights] = useState<ComprehensiveInsights | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState('dashboard')
  const [actionFeedback, setActionFeedback] = useState<Record<string, { attempted: boolean; rating?: number }>>({})

  useEffect(() => {
    loadInsights()
  }, [])

  const loadInsights = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const comprehensiveInsights = await unifiedInsightService.getComprehensiveInsights()
      setInsights(comprehensiveInsights)
    } catch (err) {
      console.error('Failed to load comprehensive insights:', err)
      setError('Unable to load insights. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleActionAttempt = async (action: RecommendedAction) => {
    try {
      await unifiedInsightService.trackActionAttempt(action.id, true)
      setActionFeedback(prev => ({
        ...prev,
        [action.id]: { attempted: true }
      }))
      toast.success('Action tracked! Great job taking initiative.')
    } catch (error) {
      console.error('Failed to track action:', error)
    }
  }

  const handleActionRating = async (action: RecommendedAction, rating: number, helpful: boolean) => {
    try {
      await unifiedInsightService.rateAction(action.id, rating, helpful)
      setActionFeedback(prev => ({
        ...prev,
        [action.id]: { ...prev[action.id], rating }
      }))
      toast.success('Thank you for your feedback!')
    } catch (error) {
      console.error('Failed to rate action:', error)
    }
  }

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'improving': return <TrendUp className="text-green-500" size={20} />
      case 'declining': return <TrendDown className="text-red-500" size={20} />
      default: return <div className="w-5 h-5 bg-yellow-400 rounded-full" />
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'destructive'
      case 'medium': return 'default'
      case 'low': return 'secondary'
      default: return 'outline'
    }
  }

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'mood_boost': return <Heart className="text-pink-500" size={16} />
      case 'energy_management': return <Lightning className="text-yellow-500" size={16} />
      case 'stress_reduction': return <Sparkle className="text-purple-500" size={16} />
      case 'pattern_optimization': return <Target className="text-blue-500" size={16} />
      default: return <Lightbulb className="text-primary" size={16} />
    }
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <Card>
          <CardContent className="p-8 text-center">
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
            >
              <Brain className="mx-auto text-primary mb-4" size={48} />
            </motion.div>
            <h3 className="text-lg font-semibold mb-2">Analyzing Your Patterns</h3>
            <p className="text-muted-foreground">
              Processing your mood data to generate personalized insights...
            </p>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (error || !insights) {
    return (
      <div className="space-y-6">
        <Card className="border-red-200 bg-red-50">
          <CardContent className="p-6 text-center">
            <Warning className="mx-auto text-red-500 mb-4" size={48} />
            <h3 className="text-lg font-semibold text-red-700 mb-2">Unable to Load Insights</h3>
            <p className="text-red-600 mb-4">{error}</p>
            <Button onClick={loadInsights} variant="outline">
              Try Again
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div className="flex items-center gap-3">
          {onBack && (
            <Button variant="ghost" size="sm" onClick={onBack}>
              <ArrowLeft size={16} />
            </Button>
          )}
          <div>
            <h1 className="text-2xl font-bold flex items-center gap-2">
              <Brain className="text-primary" size={28} />
              Your Comprehensive Insights
            </h1>
            <p className="text-muted-foreground">
              AI-powered analysis of your wellness patterns with actionable recommendations
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="outline" className="text-xs">
            Data Quality: {Math.round(insights.metadata.dataQuality * 100)}%
          </Badge>
          <Badge variant="secondary" className="text-xs">
            {insights.metadata.insightCount} insights
          </Badge>
        </div>
      </motion.div>

      {/* Main Dashboard */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <Card className="bg-gradient-to-r from-primary/5 to-purple-500/5 border-2 border-primary/20">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Target className="text-primary" size={24} />
              This Week's Story
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {/* Current Status */}
              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  {getTrendIcon(insights.dashboard.weeklySummary.trend)}
                  <span className="font-medium capitalize">
                    {insights.dashboard.weeklySummary.trend} Trend
                  </span>
                </div>
                <div className="text-2xl font-bold text-primary">
                  {insights.dashboard.weeklySummary.currentWeekScore}/10
                </div>
                <div className="text-sm text-muted-foreground">
                  {insights.dashboard.weeklySummary.daysTracked}/7 days tracked
                </div>
              </div>

              {/* Highlights */}
              <div className="space-y-2">
                <h4 className="font-medium text-sm">Best Moments</h4>
                <div className="text-sm">
                  <p>🌟 Best day: {insights.dashboard.topHighlights.bestDay}</p>
                  <p>⚡ Energy peak: {insights.dashboard.topHighlights.energyPeak}</p>
                  <p>🔥 Mood streak: {insights.dashboard.topHighlights.moodStreak} days</p>
                </div>
              </div>

              {/* Current Status */}
              <div className="space-y-2">
                <h4 className="font-medium text-sm">Current Status</h4>
                <div className="space-y-1">
                  <div className="flex items-center justify-between text-sm">
                    <span>Mood</span>
                    <span className="font-medium">{insights.dashboard.currentStatus.moodScore}/10</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span>Energy</span>
                    <span className="font-medium">{insights.dashboard.currentStatus.energyLevel}/10</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span>Stress</span>
                    <span className="font-medium">{insights.dashboard.currentStatus.stressLevel}/10</span>
                  </div>
                </div>
              </div>

              {/* Achievements */}
              <div className="space-y-2">
                <h4 className="font-medium text-sm">Achievements</h4>
                <div className="space-y-1">
                  {insights.dashboard.weeklySummary.achievements.length > 0 ? (
                    insights.dashboard.weeklySummary.achievements.map((achievement, index) => (
                      <div key={index} className="flex items-center gap-2 text-sm">
                        <Trophy className="text-yellow-500" size={14} />
                        <span>{achievement}</span>
                      </div>
                    ))
                  ) : (
                    <p className="text-sm text-muted-foreground">Keep tracking to unlock achievements!</p>
                  )}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Top Priority Actions */}
      {insights.recommendedActions.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="text-primary" size={20} />
                Top Actions for You Right Now
              </CardTitle>
              <p className="text-sm text-muted-foreground">
                Personalized recommendations based on your patterns and current needs
              </p>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-2">
                {insights.recommendedActions.slice(0, 4).map((action, index) => (
                  <motion.div
                    key={action.id}
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: index * 0.1 }}
                  >
                    <Card className="p-4 h-full hover:shadow-md transition-shadow">
                      <div className="space-y-3">
                        <div className="flex items-start justify-between">
                          <div className="flex items-center gap-2">
                            {getCategoryIcon(action.category)}
                            <h4 className="font-semibold text-sm">{action.title}</h4>
                          </div>
                          <Badge variant={getPriorityColor(action.priority)} className="text-xs">
                            {action.priority}
                          </Badge>
                        </div>
                        
                        <p className="text-sm text-muted-foreground">{action.description}</p>
                        
                        <div className="space-y-2">
                          <div className="flex items-center justify-between text-xs text-muted-foreground">
                            <div className="flex items-center gap-1">
                              <Clock size={12} />
                              {action.estimatedTime}
                            </div>
                            <div className="flex items-center gap-1">
                              <Star size={12} />
                              {Math.round(action.confidence * 100)}% confidence
                            </div>
                          </div>
                          <div className="text-xs text-green-600 bg-green-50 p-2 rounded">
                            💡 Expected: {action.expectedBenefit}
                          </div>
                        </div>

                        <div className="flex items-center gap-2">
                          {!actionFeedback[action.id]?.attempted ? (
                            <Button 
                              size="sm" 
                              className="flex-1"
                              onClick={() => handleActionAttempt(action)}
                            >
                              <CheckCircle size={14} className="mr-1" />
                              I'll Try This
                            </Button>
                          ) : (
                            <div className="flex items-center gap-2 text-xs text-green-600">
                              <CheckCircle size={14} />
                              Tracked!
                            </div>
                          )}
                          
                          <div className="flex items-center gap-1">
                            {[1, 2, 3, 4, 5].map(rating => (
                              <Button
                                key={rating}
                                size="sm"
                                variant={actionFeedback[action.id]?.rating === rating ? "default" : "ghost"}
                                className="w-6 h-6 p-0"
                                onClick={() => handleActionRating(action, rating, rating >= 3)}
                              >
                                <Star size={12} />
                              </Button>
                            ))}
                          </div>
                        </div>
                      </div>
                    </Card>
                  </motion.div>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Detailed Analysis Tabs */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="dashboard" className="flex items-center gap-2">
              <ChartLine size={16} />
              Overview
            </TabsTrigger>
            <TabsTrigger value="patterns" className="flex items-center gap-2">
              <TrendUp size={16} />
              Patterns
            </TabsTrigger>
            <TabsTrigger value="progress" className="flex items-center gap-2">
              <Trophy size={16} />
              Progress
            </TabsTrigger>
            <TabsTrigger value="community" className="flex items-center gap-2">
              <Users size={16} />
              Community
            </TabsTrigger>
          </TabsList>

          <TabsContent value="dashboard" className="space-y-6 mt-6">
            <div className="grid gap-6 md:grid-cols-2">
              {/* Trend Analysis */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Trend Analysis</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {Object.entries(insights.progressTracking.trends).map(([key, trend]) => (
                      <div key={key} className="flex items-center justify-between">
                        <span className="capitalize font-medium">{key}</span>
                        <div className="flex items-center gap-2">
                          <span className="text-lg font-bold">{trend.current}</span>
                          <div className={`flex items-center gap-1 text-sm ${
                            trend.direction === 'up' ? 'text-green-600' :
                            trend.direction === 'down' ? 'text-red-600' : 'text-yellow-600'
                          }`}>
                            {trend.direction === 'up' ? <TrendUp size={14} /> :
                             trend.direction === 'down' ? <TrendDown size={14} /> :
                             <div className="w-3 h-3 bg-yellow-400 rounded-full" />}
                            {trend.change > 0 ? '+' : ''}{trend.change}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Week Comparison */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Week Comparison</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <h4 className="font-medium mb-2">This Week</h4>
                        <p>Avg Mood: {insights.progressTracking.comparisons.thisWeek.averageMood}</p>
                        <p>Best: {insights.progressTracking.comparisons.thisWeek.bestDay}</p>
                        <p>Challenging: {insights.progressTracking.comparisons.thisWeek.challengingDay}</p>
                      </div>
                      <div>
                        <h4 className="font-medium mb-2">Last Week</h4>
                        <p>Avg Mood: {insights.progressTracking.comparisons.lastWeek.averageMood}</p>
                        <p>Best: {insights.progressTracking.comparisons.lastWeek.bestDay}</p>
                        <p>Challenging: {insights.progressTracking.comparisons.lastWeek.challengingDay}</p>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="patterns" className="space-y-6 mt-6">
            <Card>
              <CardHeader>
                <CardTitle>Pattern Analysis</CardTitle>
                <p className="text-sm text-muted-foreground">
                  Deep insights into your mood patterns and correlations
                </p>
              </CardHeader>
              <CardContent>
                <div className="text-center py-8 text-muted-foreground">
                  <Gear className="mx-auto mb-4 opacity-50" size={48} />
                  <h4 className="font-medium mb-2">Advanced Pattern Analysis</h4>
                  <p className="text-sm mb-4">
                    Detailed pattern analysis will be available here, including time-of-day patterns,
                    activity correlations, and trigger analysis.
                  </p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="progress" className="space-y-6 mt-6">
            <Card>
              <CardHeader>
                <CardTitle>Progress Tracking</CardTitle>
                <p className="text-sm text-muted-foreground">
                  Track your wellness journey and celebrate improvements
                </p>
              </CardHeader>
              <CardContent>
                <div className="text-center py-8 text-muted-foreground">
                  <Trophy className="mx-auto mb-4 opacity-50" size={48} />
                  <h4 className="font-medium mb-2">Goal Progress & Achievements</h4>
                  <p className="text-sm mb-4">
                    Your wellness goals, progress tracking, and achievement system will be displayed here.
                  </p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="community" className="space-y-6 mt-6">
            <Card>
              <CardHeader>
                <CardTitle>Community Insights</CardTitle>
                <p className="text-sm text-muted-foreground">
                  Learn from community patterns and share anonymous insights
                </p>
              </CardHeader>
              <CardContent>
                <div className="text-center py-8 text-muted-foreground">
                  <Users className="mx-auto mb-4 opacity-50" size={48} />
                  <h4 className="font-medium mb-2">Community Wisdom</h4>
                  <p className="text-sm mb-4">
                    Community-informed insights and anonymous pattern sharing will be available here.
                  </p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </motion.div>
    </div>
  )
}

export default EnhancedInsightsPage
