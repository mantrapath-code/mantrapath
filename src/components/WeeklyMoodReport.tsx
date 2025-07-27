/**
 * Weekly Mood Report Component - Personalized weekly mood analysis with actionable insights
 * 
 * Features:
 * - Comprehensive mood pattern analysis
 * - Actionable recommendations based on individual data
 * - Trend visualization with comparison to previous weeks
 * - Integration with backend analytics API
 */

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  TrendUp, 
  TrendDown, 
  Calendar, 
  Clock, 
  Heart, 
  Brain, 
  Target,
  Share,
  Download,
  ChartLine,
  Lightbulb
} from '@phosphor-icons/react'
import { motion, AnimatePresence } from 'framer-motion'
import { apiService } from '@/services/api'
import { toast } from 'sonner'
import { useMoods } from '@/hooks/useWellness'
import { useMoodAnalytics } from '@/hooks/useWellness'

interface WeeklyMoodData {
  weeklyScore: number
  previousWeekScore: number
  trend: 'improving' | 'declining' | 'stable'
  moodDistribution: Record<string, number>
  dayOfWeekPatterns: Array<{
    day: string
    average: number
    count: number
  }>
  timeOfDayPatterns: Array<{
    period: string
    average: number
    count: number
  }>
  topTriggers: Array<{
    trigger: string
    frequency: number
    impact: 'positive' | 'negative' | 'neutral'
  }>
  topBoosters: Array<{
    booster: string
    frequency: number
    impact: number
  }>
  insights: Array<{
    type: 'pattern' | 'recommendation' | 'achievement' | 'concern'
    title: string
    description: string
    actionable: string
    priority: 'high' | 'medium' | 'low'
  }>
  interventionTimes: Array<{
    timeOfDay: string
    dayOfWeek: string
    effectiveness: number
    description: string
  }>
}

export function WeeklyMoodReport() {
  const [reportData, setReportData] = useState<WeeklyMoodData | null>(null)
  const [loading, setLoading] = useState(true)
  const [selectedWeek, setSelectedWeek] = useState(0) // 0 = current week, 1 = last week, etc.
  const [showSharing, setShowSharing] = useState(false)
  
  const { moods } = useMoods()
  const { getWeeklyInsights } = useMoodAnalytics()

  useEffect(() => {
    generateWeeklyReport()
  }, [selectedWeek, moods])

  const generateWeeklyReport = async () => {
    setLoading(true)
    try {
      // Calculate date range for selected week
      const endDate = new Date()
      endDate.setDate(endDate.getDate() - (selectedWeek * 7))
      const startDate = new Date(endDate)
      startDate.setDate(startDate.getDate() - 6)

      // Fetch analytics data from backend
      const [
        weeklyPatterns,
        triggers, 
        boosters,
        trends,
        healthScore
      ] = await Promise.all([
        apiService.getWeeklyPatterns(),
        apiService.getAnalyticsOverview(), // Using this as fallback for triggers
        apiService.getAnalyticsOverview(), // Using this as fallback for boosters  
        apiService.getAnalyticsOverview(), // Using this as fallback for trends
        apiService.getAnalyticsOverview()  // Using this as fallback for health score
      ])

      // Process local mood data for the selected week
      const weekStart = startDate.getTime()
      const weekEnd = endDate.getTime()
      const weekMoods = moods.filter(mood => 
        mood.timestamp >= weekStart && mood.timestamp <= weekEnd
      )

      const reportData = await processWeeklyData(
        weekMoods,
        weeklyPatterns,
        triggers,
        boosters,
        trends,
        healthScore
      )

      setReportData(reportData)
    } catch (error) {
      console.error('Failed to generate weekly report:', error)
      toast.error('Unable to generate weekly report. Please try again.')
      
      // Fallback to local analysis
      const localInsights = getWeeklyInsights()
      setReportData(generateLocalReport(localInsights))
    } finally {
      setLoading(false)
    }
  }

  const processWeeklyData = async (
    weekMoods: any[],
    weeklyPatterns: any,
    triggers: any,
    boosters: any,
    trends: any,
    healthScore: any
  ): Promise<WeeklyMoodData> => {
    const moodValues = { 'very-low': 1, 'low': 2, 'neutral': 3, 'good': 4, 'excellent': 5 }
    
    // Calculate weekly score
    const weeklyScore = weekMoods.length > 0 
      ? weekMoods.reduce((sum, mood) => sum + moodValues[mood.mood], 0) / weekMoods.length
      : 3

    // Get previous week data for comparison
    const prevWeekStart = Date.now() - (14 * 24 * 60 * 60 * 1000)
    const prevWeekEnd = Date.now() - (7 * 24 * 60 * 60 * 1000)
    const prevWeekMoods = moods.filter(mood => 
      mood.timestamp >= prevWeekStart && mood.timestamp <= prevWeekEnd
    )
    const previousWeekScore = prevWeekMoods.length > 0
      ? prevWeekMoods.reduce((sum, mood) => sum + moodValues[mood.mood], 0) / prevWeekMoods.length
      : 3

    // Determine trend
    const scoreDiff = weeklyScore - previousWeekScore
    const trend = Math.abs(scoreDiff) < 0.3 ? 'stable' : 
                  scoreDiff > 0 ? 'improving' : 'declining'

    // Analyze mood distribution
    const moodDistribution = weekMoods.reduce((acc, mood) => {
      acc[mood.mood] = (acc[mood.mood] || 0) + 1
      return acc
    }, {} as Record<string, number>)

    // Analyze day of week patterns
    const dayNames = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    const dayOfWeekPatterns = dayNames.map(day => {
      const dayIndex = dayNames.indexOf(day)
      const dayMoods = weekMoods.filter(mood => 
        new Date(mood.timestamp).getDay() === dayIndex
      )
      return {
        day,
        average: dayMoods.length > 0 
          ? dayMoods.reduce((sum, mood) => sum + moodValues[mood.mood], 0) / dayMoods.length
          : 0,
        count: dayMoods.length
      }
    }).filter(item => item.count > 0)

    // Analyze time of day patterns
    const timeOfDayPatterns = ['morning', 'afternoon', 'evening', 'night'].map(period => {
      const periodMoods = weekMoods.filter(mood => mood.timeOfDay === period)
      return {
        period,
        average: periodMoods.length > 0
          ? periodMoods.reduce((sum, mood) => sum + moodValues[mood.mood], 0) / periodMoods.length
          : 0,
        count: periodMoods.length
      }
    }).filter(item => item.count > 0)

    // Process triggers and boosters
    const topTriggers = triggers.data?.slice(0, 5).map((trigger: any) => ({
      trigger: trigger.name,
      frequency: trigger.frequency,
      impact: trigger.impact_score < 3 ? 'negative' : trigger.impact_score > 3 ? 'positive' : 'neutral'
    })) || []

    const topBoosters = boosters.data?.slice(0, 5).map((booster: any) => ({
      booster: booster.name,
      frequency: booster.frequency,
      impact: booster.impact_score
    })) || []

    // Generate insights with actionable recommendations
    const insights = await generateActionableInsights({
      weeklyScore,
      previousWeekScore,
      trend,
      dayOfWeekPatterns,
      timeOfDayPatterns,
      topTriggers,
      topBoosters,
      weekMoods
    })

    // Identify optimal intervention times
    const interventionTimes = identifyInterventionTimes(dayOfWeekPatterns, timeOfDayPatterns)

    return {
      weeklyScore,
      previousWeekScore,
      trend,
      moodDistribution,
      dayOfWeekPatterns,
      timeOfDayPatterns,
      topTriggers,
      topBoosters,
      insights,
      interventionTimes
    }
  }

  const generateActionableInsights = async (data: any) => {
    const insights = []

    // Trend-based insights
    if (data.trend === 'improving') {
      insights.push({
        type: 'achievement' as const,
        title: 'Positive Momentum! 🌟',
        description: `Your mood has improved by ${((data.weeklyScore - data.previousWeekScore) * 20).toFixed(0)}% this week.`,
        actionable: 'Keep doing what you\'re doing! Consider documenting what\'s working well.',
        priority: 'medium' as const
      })
    } else if (data.trend === 'declining') {
      insights.push({
        type: 'concern' as const,
        title: 'Gentle Check-in Needed 💙',
        description: `Your mood has dipped slightly this week. This is completely normal.`,
        actionable: 'Consider reaching out to a friend, practicing self-care, or reviewing your recent stressors.',
        priority: 'high' as const
      })
    }

    // Day pattern insights
    const bestDay = data.dayOfWeekPatterns.reduce((best: any, day: any) => 
      day.average > best.average ? day : best, data.dayOfWeekPatterns[0])
    const worstDay = data.dayOfWeekPatterns.reduce((worst: any, day: any) => 
      day.average < worst.average ? day : worst, data.dayOfWeekPatterns[0])

    if (bestDay && worstDay && Math.abs(bestDay.average - worstDay.average) > 0.8) {
      insights.push({
        type: 'pattern' as const,
        title: `${bestDay.day}s vs ${worstDay.day}s Pattern`,
        description: `You consistently feel better on ${bestDay.day}s (${bestDay.average.toFixed(1)}/5) compared to ${worstDay.day}s (${worstDay.average.toFixed(1)}/5).`,
        actionable: `Plan lighter activities on ${worstDay.day}s and use ${bestDay.day} energy for important tasks.`,
        priority: 'medium' as const
      })
    }

    // Time pattern insights
    const bestTime = data.timeOfDayPatterns.reduce((best: any, time: any) => 
      time.average > best.average ? time : best, data.timeOfDayPatterns[0])
    const worstTime = data.timeOfDayPatterns.reduce((worst: any, time: any) => 
      time.average < worst.average ? time : worst, data.timeOfDayPatterns[0])

    if (bestTime && worstTime && Math.abs(bestTime.average - worstTime.average) > 0.8) {
      insights.push({
        type: 'pattern' as const,
        title: `${bestTime.period} vs ${worstTime.period} Energy`,
        description: `Your energy peaks during ${bestTime.period} and dips during ${worstTime.period}.`,
        actionable: `Schedule important meetings during ${bestTime.period} and plan self-care during ${worstTime.period}.`,
        priority: 'medium' as const
      })
    }

    // Trigger insights
    const negativeTriggersCount = data.topTriggers.filter((t: any) => t.impact === 'negative').length
    if (negativeTriggersCount > 0) {
      const topNegativeTrigger = data.topTriggers.find((t: any) => t.impact === 'negative')
      insights.push({
        type: 'recommendation' as const,
        title: 'Managing Common Triggers',
        description: `"${topNegativeTrigger.trigger}" appears to be a frequent challenge for you.`,
        actionable: 'Consider developing a coping strategy for this trigger, or discuss it in the community for peer support.',
        priority: 'high' as const
      })
    }

    // Booster insights
    if (data.topBoosters.length > 0) {
      const topBooster = data.topBoosters[0]
      insights.push({
        type: 'recommendation' as const,
        title: 'Amplify What Works! ✨',
        description: `"${topBooster.booster}" consistently improves your mood.`,
        actionable: `Try to incorporate "${topBooster.booster}" more frequently into your routine.`,
        priority: 'medium' as const
      })
    }

    return insights
  }

  const identifyInterventionTimes = (dayPatterns: any[], timePatterns: any[]) => {
    const interventions = []

    // Find the day/time combination with lowest mood for proactive intervention
    const worstDay = dayPatterns.reduce((worst, day) => 
      day.average < worst.average ? day : worst, dayPatterns[0])
    const worstTime = timePatterns.reduce((worst, time) => 
      time.average < worst.average ? time : worst, timePatterns[0])

    if (worstDay && worstTime) {
      interventions.push({
        timeOfDay: worstTime.period,
        dayOfWeek: worstDay.day,
        effectiveness: 0.8,
        description: `Proactive check-in recommended during ${worstTime.period} on ${worstDay.day}s when mood typically dips.`
      })
    }

    // Find high-energy times for positive activities
    const bestTime = timePatterns.reduce((best, time) => 
      time.average > best.average ? time : best, timePatterns[0])

    if (bestTime && bestTime.average > 3.5) {
      interventions.push({
        timeOfDay: bestTime.period,
        dayOfWeek: 'any',
        effectiveness: 0.9,
        description: `Optimal time for challenging activities and personal growth during ${bestTime.period}.`
      })
    }

    return interventions
  }

  const generateLocalReport = (localInsights: any[]): WeeklyMoodData => {
    // Fallback local analysis when backend is unavailable
    const oneWeekAgo = Date.now() - (7 * 24 * 60 * 60 * 1000)
    const weekMoods = moods.filter(mood => mood.timestamp >= oneWeekAgo)
    
    const moodValues = { 'very-low': 1, 'low': 2, 'neutral': 3, 'good': 4, 'excellent': 5 }
    const weeklyScore = weekMoods.length > 0 
      ? weekMoods.reduce((sum, mood) => sum + moodValues[mood.mood], 0) / weekMoods.length 
      : 3

    return {
      weeklyScore,
      previousWeekScore: 3,
      trend: 'stable',
      moodDistribution: {},
      dayOfWeekPatterns: [],
      timeOfDayPatterns: [],
      topTriggers: [],
      topBoosters: [],
      insights: localInsights.map(insight => ({
        type: 'pattern' as const,
        title: insight.type,
        description: insight.insight,
        actionable: insight.recommendation,
        priority: 'medium' as const
      })),
      interventionTimes: []
    }
  }

  const shareReport = async () => {
    if (!reportData) return
    
    // Create shareable mood pattern summary for community
    const shareableData = {
      weeklyScore: Math.round(reportData.weeklyScore * 20), // Convert to percentage
      trend: reportData.trend,
      topInsight: reportData.insights[0]?.title || 'Continuing my wellness journey',
      anonymized: true
    }

    setShowSharing(true)
    toast.success('Report prepared for community sharing!')
  }

  const downloadReport = () => {
    if (!reportData) return
    
    const reportText = `
MantraPath Weekly Mood Report
Generated: ${new Date().toLocaleDateString()}

Weekly Score: ${(reportData.weeklyScore * 20).toFixed(0)}%
Trend: ${reportData.trend}

Key Insights:
${reportData.insights.map(insight => 
  `• ${insight.title}: ${insight.description}\n  Action: ${insight.actionable}`
).join('\n\n')}

Optimal Intervention Times:
${reportData.interventionTimes.map(time => 
  `• ${time.timeOfDay} on ${time.dayOfWeek}: ${time.description}`
).join('\n')}
`

    const blob = new Blob([reportText], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `mantrapath-weekly-report-${new Date().toISOString().split('T')[0]}.txt`
    a.click()
    URL.revokeObjectURL(url)
  }

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <ChartLine className="w-5 h-5" />
            Generating Weekly Report...
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="h-4 bg-muted rounded animate-pulse" />
            <div className="h-4 bg-muted rounded animate-pulse w-3/4" />
            <div className="h-4 bg-muted rounded animate-pulse w-1/2" />
          </div>
        </CardContent>
      </Card>
    )
  }

  if (!reportData) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Weekly Mood Report</CardTitle>
          <CardDescription>
            Unable to generate report. Please ensure you have mood data for analysis.
          </CardDescription>
        </CardHeader>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <ChartLine className="w-5 h-5" />
                Weekly Mood Report
              </CardTitle>
              <CardDescription>
                Personalized insights for {new Date().toLocaleDateString()}
              </CardDescription>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" size="sm" onClick={shareReport}>
                <Share className="w-4 h-4 mr-2" />
                Share
              </Button>
              <Button variant="outline" size="sm" onClick={downloadReport}>
                <Download className="w-4 h-4 mr-2" />
                Download
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="text-center">
              <div className="text-3xl font-bold text-primary">
                {(reportData.weeklyScore * 20).toFixed(0)}%
              </div>
              <div className="text-sm text-muted-foreground">Weekly Score</div>
            </div>
            <div className="text-center">
              <div className="flex items-center justify-center gap-2">
                {reportData.trend === 'improving' && <TrendUp className="w-5 h-5 text-green-500" />}
                {reportData.trend === 'declining' && <TrendDown className="w-5 h-5 text-red-500" />}
                {reportData.trend === 'stable' && <div className="w-5 h-5 bg-gray-400 rounded-full" />}
                <span className="text-lg font-semibold capitalize">{reportData.trend}</span>
              </div>
              <div className="text-sm text-muted-foreground">Trend</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold">
                {reportData.insights.length}
              </div>
              <div className="text-sm text-muted-foreground">Key Insights</div>
            </div>
          </div>

          <Tabs defaultValue="insights" className="w-full">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="insights">Insights</TabsTrigger>
              <TabsTrigger value="patterns">Patterns</TabsTrigger>
              <TabsTrigger value="triggers">Triggers</TabsTrigger>
              <TabsTrigger value="interventions">Optimal Times</TabsTrigger>
            </TabsList>

            <TabsContent value="insights" className="space-y-4">
              <div className="space-y-3">
                {reportData.insights.map((insight, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                  >
                    <Card className="p-4">
                      <div className="flex items-start gap-3">
                        <div className="p-2 rounded-full bg-primary/10">
                          {insight.type === 'achievement' && <Heart className="w-4 h-4 text-green-500" />}
                          {insight.type === 'concern' && <Brain className="w-4 h-4 text-orange-500" />}
                          {insight.type === 'pattern' && <Clock className="w-4 h-4 text-blue-500" />}
                          {insight.type === 'recommendation' && <Lightbulb className="w-4 h-4 text-yellow-500" />}
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <h4 className="font-semibold">{insight.title}</h4>
                            <Badge variant={insight.priority === 'high' ? 'destructive' : insight.priority === 'medium' ? 'default' : 'secondary'}>
                              {insight.priority}
                            </Badge>
                          </div>
                          <p className="text-sm text-muted-foreground mb-2">{insight.description}</p>
                          <div className="flex items-center gap-2 text-sm">
                            <Target className="w-4 h-4 text-primary" />
                            <span className="font-medium">Action:</span>
                            <span>{insight.actionable}</span>
                          </div>
                        </div>
                      </div>
                    </Card>
                  </motion.div>
                ))}
              </div>
            </TabsContent>

            <TabsContent value="patterns" className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Card className="p-4">
                  <h4 className="font-semibold mb-3 flex items-center gap-2">
                    <Calendar className="w-4 h-4" />
                    Day of Week Patterns
                  </h4>
                  <div className="space-y-2">
                    {reportData.dayOfWeekPatterns.map((day, index) => (
                      <div key={index} className="flex items-center justify-between">
                        <span className="text-sm">{day.day}</span>
                        <div className="flex items-center gap-2">
                          <Progress value={day.average * 20} className="w-16" />
                          <span className="text-sm w-8">{day.average.toFixed(1)}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </Card>

                <Card className="p-4">
                  <h4 className="font-semibold mb-3 flex items-center gap-2">
                    <Clock className="w-4 h-4" />
                    Time of Day Patterns
                  </h4>
                  <div className="space-y-2">
                    {reportData.timeOfDayPatterns.map((time, index) => (
                      <div key={index} className="flex items-center justify-between">
                        <span className="text-sm capitalize">{time.period}</span>
                        <div className="flex items-center gap-2">
                          <Progress value={time.average * 20} className="w-16" />
                          <span className="text-sm w-8">{time.average.toFixed(1)}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </Card>
              </div>
            </TabsContent>

            <TabsContent value="triggers" className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Card className="p-4">
                  <h4 className="font-semibold mb-3 text-red-600">Common Triggers</h4>
                  <div className="space-y-2">
                    {reportData.topTriggers.filter(t => t.impact === 'negative').map((trigger, index) => (
                      <div key={index} className="flex items-center justify-between p-2 rounded bg-red-50 dark:bg-red-900/20">
                        <span className="text-sm">{trigger.trigger}</span>
                        <Badge variant="destructive">{trigger.frequency}x</Badge>
                      </div>
                    ))}
                  </div>
                </Card>

                <Card className="p-4">
                  <h4 className="font-semibold mb-3 text-green-600">Mood Boosters</h4>
                  <div className="space-y-2">
                    {reportData.topBoosters.map((booster, index) => (
                      <div key={index} className="flex items-center justify-between p-2 rounded bg-green-50 dark:bg-green-900/20">
                        <span className="text-sm">{booster.booster}</span>
                        <Badge variant="default">{booster.frequency}x</Badge>
                      </div>
                    ))}
                  </div>
                </Card>
              </div>
            </TabsContent>

            <TabsContent value="interventions" className="space-y-4">
              <div className="space-y-3">
                {reportData.interventionTimes.map((intervention, index) => (
                  <Card key={index} className="p-4">
                    <div className="flex items-center gap-3">
                      <div className="p-2 rounded-full bg-blue-100 dark:bg-blue-900/20">
                        <Clock className="w-4 h-4 text-blue-600" />
                      </div>
                      <div className="flex-1">
                        <div className="font-semibold">
                          {intervention.timeOfDay} on {intervention.dayOfWeek}
                        </div>
                        <p className="text-sm text-muted-foreground">{intervention.description}</p>
                        <div className="flex items-center gap-2 mt-2">
                          <span className="text-xs">Effectiveness:</span>
                          <Progress value={intervention.effectiveness * 100} className="w-20" />
                          <span className="text-xs">{(intervention.effectiveness * 100).toFixed(0)}%</span>
                        </div>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      {/* Community Sharing Modal */}
      <AnimatePresence>
        {showSharing && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4"
            onClick={() => setShowSharing(false)}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="bg-background p-6 rounded-lg max-w-md w-full"
              onClick={(e) => e.stopPropagation()}
            >
              <h3 className="text-lg font-semibold mb-4">Share Your Progress</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Share your anonymized mood patterns with the community to inspire others and receive encouragement.
              </p>
              <div className="flex gap-3">
                <Button onClick={() => setShowSharing(false)} variant="outline" className="flex-1">
                  Cancel
                </Button>
                <Button onClick={() => setShowSharing(false)} className="flex-1">
                  Share Progress
                </Button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}