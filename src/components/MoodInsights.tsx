import { useMemo } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  TrendUp, 
  TrendDown, 
  Calendar, 
  Clock, 
  Target, 
  Lightbulb,
  Heart,
  Brain,
  Users,
  Activity,
  ArrowsLeftRight,
  BarChart3
} from '@phosphor-icons/react'
import { motion } from 'framer-motion'
import { useMoods } from '@/hooks/useWellness'
import { useJournal } from '@/hooks/useJournal'
import { MoodPattern, PersonalizedInsight, WeeklyAnalysis, RecommendationCard } from '@/types'
import { DemoDataSeeder } from './DemoDataSeeder'
import { MoodCorrelations } from './MoodCorrelations'
import { MoodComparisonView } from './MoodComparisonView'
import { EnhancedMoodChart } from './EnhancedMoodChart'

export function MoodInsights() {
  const { moods } = useMoods()
  const { entries } = useJournal()

  const weeklyAnalysis = useMemo(() => {
    return analyzeWeeklyPatterns(moods, entries)
  }, [moods, entries])

  const patterns = useMemo(() => {
    return detectMoodPatterns(moods)
  }, [moods])

  const recommendations = useMemo(() => {
    return generateRecommendations(weeklyAnalysis, patterns)
  }, [weeklyAnalysis, patterns])

  if (moods.length < 7) {
    return (
      <div className="space-y-6">
        <Card>
          <CardContent className="p-6 text-center">
            <Brain className="mx-auto text-muted-foreground mb-4" size={48} />
            <h3 className="text-lg font-semibold mb-2">Building Your Insights</h3>
            <p className="text-muted-foreground mb-4">
              Log moods for a few more days to unlock personalized patterns and recommendations.
            </p>
            <div className="flex items-center justify-center gap-2">
              <Progress value={(moods.length / 7) * 100} className="w-32" />
              <span className="text-sm text-muted-foreground">{moods.length}/7 days</span>
            </div>
          </CardContent>
        </Card>
        
        <DemoDataSeeder />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <Tabs defaultValue="overview" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview" className="flex items-center gap-2">
            <Calendar size={16} />
            Overview
          </TabsTrigger>
          <TabsTrigger value="comparison" className="flex items-center gap-2">
            <ArrowsLeftRight size={16} />
            Compare
          </TabsTrigger>
          <TabsTrigger value="correlations" className="flex items-center gap-2">
            <BarChart3 size={16} />
            Correlations
          </TabsTrigger>
          <TabsTrigger value="recommendations" className="flex items-center gap-2">
            <Target size={16} />
            Actions
          </TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6 mt-6">
          {/* Enhanced Mood Chart */}
          <EnhancedMoodChart />
          
          {/* Weekly Overview */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <Card className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-950/20 dark:to-indigo-950/20">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Calendar className="text-blue-600" size={24} />
                  This Week's Analysis
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="text-center">
                    <div className="text-3xl font-bold text-blue-600 mb-1">
                      {Math.round(weeklyAnalysis.averageMood * 20)}%
                    </div>
                    <div className="text-sm text-muted-foreground">Average Wellness</div>
                  </div>
                  <div className="text-center">
                    <div className="text-3xl font-bold text-green-600 mb-1 capitalize">
                      {weeklyAnalysis.dominantMood}
                    </div>
                    <div className="text-sm text-muted-foreground">Dominant Mood</div>
                  </div>
                  <div className="text-center">
                    <div className="text-3xl font-bold text-purple-600 mb-1">
                      {weeklyAnalysis.streaks.current}
                    </div>
                    <div className="text-sm text-muted-foreground">Current Streak</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* Detected Patterns */}
          {patterns.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
            >
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <TrendUp className="text-green-600" size={24} />
                    Detected Patterns
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {patterns.slice(0, 3).map((pattern, index) => (
                    <PatternCard key={index} pattern={pattern} />
                  ))}
                </CardContent>
              </Card>
            </motion.div>
          )}

          {/* Personalized Insights */}
          {weeklyAnalysis.insights.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
            >
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Lightbulb className="text-yellow-600" size={24} />
                    Personal Insights
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {weeklyAnalysis.insights.map((insight) => (
                    <InsightCard key={insight.id} insight={insight} />
                  ))}
                </CardContent>
              </Card>
            </motion.div>
          )}
        </TabsContent>

        <TabsContent value="comparison" className="space-y-6 mt-6">
          <MoodComparisonView />
        </TabsContent>

        <TabsContent value="correlations" className="space-y-6 mt-6">
          <MoodCorrelations />
        </TabsContent>

        <TabsContent value="recommendations" className="space-y-6 mt-6">
          {/* Recommendations */}
          {recommendations.length > 0 ? (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Target className="text-primary" size={24} />
                    Personalized Recommendations
                  </CardTitle>
                  <p className="text-sm text-muted-foreground">
                    Based on your mood patterns and insights, here are actions that could help improve your well-being
                  </p>
                </CardHeader>
                <CardContent className="space-y-4">
                  {recommendations.map((rec) => (
                    <RecommendationCardComponent key={rec.id} recommendation={rec} />
                  ))}
                </CardContent>
              </Card>
            </motion.div>
          ) : (
            <Card>
              <CardContent className="p-6 text-center">
                <Target className="mx-auto text-muted-foreground mb-4" size={48} />
                <h3 className="text-lg font-semibold mb-2">Personalized Recommendations Coming Soon</h3>
                <p className="text-muted-foreground">
                  Continue logging your moods and activities to receive tailored wellness recommendations.
                </p>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  )
}

function PatternCard({ pattern }: { pattern: MoodPattern }) {
  const getPatternIcon = () => {
    switch (pattern.type) {
      case 'daily': return <Clock size={20} />
      case 'weekly': return <Calendar size={20} />
      case 'trigger-based': return <Activity size={20} />
      case 'context-based': return <Users size={20} />
      default: return <TrendUp size={20} />
    }
  }

  const getImpactColor = () => {
    switch (pattern.impact) {
      case 'positive': return 'text-green-600 bg-green-50'
      case 'negative': return 'text-red-600 bg-red-50'
      default: return 'text-blue-600 bg-blue-50'
    }
  }

  return (
    <div className="border rounded-lg p-4 space-y-3">
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-2">
          {getPatternIcon()}
          <span className="font-medium capitalize">{pattern.type.replace('-', ' ')} Pattern</span>
        </div>
        <Badge variant="outline" className={getImpactColor()}>
          {pattern.impact}
        </Badge>
      </div>
      
      <p className="text-sm text-muted-foreground">{pattern.pattern}</p>
      
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="text-xs">
            <span className="text-muted-foreground">Confidence: </span>
            <span className="font-medium">{Math.round(pattern.confidence * 100)}%</span>
          </div>
          <div className="text-xs">
            <span className="text-muted-foreground">Frequency: </span>
            <span className="font-medium">{pattern.frequency}x/week</span>
          </div>
        </div>
      </div>
      
      <div className="bg-accent/10 p-3 rounded text-sm">
        <span className="font-medium text-accent-foreground">💡 Suggestion: </span>
        {pattern.suggestion}
      </div>
    </div>
  )
}

function InsightCard({ insight }: { insight: PersonalizedInsight }) {
  const getInsightIcon = () => {
    switch (insight.type) {
      case 'pattern': return <TrendUp size={20} />
      case 'achievement': return <Heart size={20} />
      case 'recommendation': return <Target size={20} />
      case 'warning': return <TrendDown size={20} />
      default: return <Lightbulb size={20} />
    }
  }

  const getPriorityColor = () => {
    switch (insight.priority) {
      case 'high': return 'border-red-200 bg-red-50'
      case 'medium': return 'border-yellow-200 bg-yellow-50'
      default: return 'border-blue-200 bg-blue-50'
    }
  }

  return (
    <div className={`border rounded-lg p-4 space-y-3 ${getPriorityColor()}`}>
      <div className="flex items-start gap-3">
        {getInsightIcon()}
        <div className="flex-1">
          <h4 className="font-medium">{insight.title}</h4>
          <p className="text-sm text-muted-foreground mt-1">{insight.description}</p>
        </div>
        <Badge variant="outline" className="text-xs">
          {insight.category}
        </Badge>
      </div>
      
      {insight.actionItems.length > 0 && (
        <div className="space-y-2">
          <span className="text-sm font-medium">Action Items:</span>
          <ul className="text-sm space-y-1">
            {insight.actionItems.map((item, index) => (
              <li key={index} className="flex items-start gap-2">
                <span className="text-primary">•</span>
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

function RecommendationCardComponent({ recommendation }: { recommendation: RecommendationCard }) {
  const getTypeIcon = () => {
    switch (recommendation.type) {
      case 'exercise': return <Activity size={20} />
      case 'mindfulness': return <Brain size={20} />
      case 'social': return <Users size={20} />
      case 'routine': return <Clock size={20} />
      case 'professional': return <Target size={20} />
      default: return <Heart size={20} />
    }
  }

  const getUrgencyColor = () => {
    switch (recommendation.urgency) {
      case 'high': return 'border-red-200 bg-red-50'
      case 'medium': return 'border-yellow-200 bg-yellow-50'
      default: return 'border-green-200 bg-green-50'
    }
  }

  return (
    <div className={`border rounded-lg p-4 space-y-3 ${getUrgencyColor()}`}>
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3">
          {getTypeIcon()}
          <div>
            <h4 className="font-medium">{recommendation.title}</h4>
            <p className="text-sm text-muted-foreground">{recommendation.description}</p>
          </div>
        </div>
        <Badge variant="outline" className="text-xs">
          {recommendation.estimatedTime}
        </Badge>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <span className="text-sm font-medium">Benefits:</span>
          <ul className="text-sm text-muted-foreground mt-1">
            {recommendation.benefits.slice(0, 2).map((benefit, index) => (
              <li key={index} className="flex items-start gap-1">
                <span className="text-green-600">✓</span>
                <span>{benefit}</span>
              </li>
            ))}
          </ul>
        </div>
        <div>
          <span className="text-sm font-medium">Based on:</span>
          <ul className="text-sm text-muted-foreground mt-1">
            {recommendation.basedOn.slice(0, 2).map((basis, index) => (
              <li key={index} className="flex items-start gap-1">
                <span className="text-blue-600">•</span>
                <span>{basis}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
      
      <Button size="sm" className="w-full mt-3">
        Try This Recommendation
      </Button>
    </div>
  )
}

// Analysis Functions
function analyzeWeeklyPatterns(moods: any[], entries: any[]): WeeklyAnalysis {
  const oneWeekAgo = Date.now() - (7 * 24 * 60 * 60 * 1000)
  const weekMoods = moods.filter(mood => mood.timestamp >= oneWeekAgo)
  
  if (weekMoods.length === 0) {
    return {
      week: { start: oneWeekAgo, end: Date.now() },
      averageMood: 3,
      moodVariability: 0,
      dominantMood: 'neutral',
      patterns: [],
      insights: [],
      recommendations: [],
      streaks: { current: 0, longest: 0 }
    }
  }

  const moodValues = { 'very-low': 1, 'low': 2, 'neutral': 3, 'good': 4, 'excellent': 5 }
  const weekMoodValues = weekMoods.map(m => moodValues[m.mood])
  
  const averageMood = weekMoodValues.reduce((a, b) => a + b, 0) / weekMoodValues.length
  const moodVariability = Math.sqrt(weekMoodValues.reduce((acc, val) => acc + Math.pow(val - averageMood, 2), 0) / weekMoodValues.length)
  
  const moodCounts = weekMoods.reduce((acc, mood) => {
    acc[mood.mood] = (acc[mood.mood] || 0) + 1
    return acc
  }, {} as Record<string, number>)
  
  const dominantMood = Object.entries(moodCounts).reduce((a, b) => moodCounts[a[0]] > moodCounts[b[0]] ? a : b)[0] as any

  const insights = generateWeeklyInsights(weekMoods, entries, averageMood, moodVariability)

  return {
    week: { start: oneWeekAgo, end: Date.now() },
    averageMood,
    moodVariability,
    dominantMood,
    patterns: [],
    insights,
    recommendations: [],
    streaks: calculateStreaks(moods)
  }
}

function detectMoodPatterns(moods: any[]): MoodPattern[] {
  const patterns: MoodPattern[] = []
  
  // Day of week pattern
  const dayOfWeekPattern = analyzeDayOfWeekPattern(moods)
  if (dayOfWeekPattern) patterns.push(dayOfWeekPattern)
  
  // Time of day pattern
  const timePattern = analyzeTimePattern(moods)
  if (timePattern) patterns.push(timePattern)
  
  // Trigger-based pattern
  const triggerPattern = analyzeTriggerPattern(moods)
  if (triggerPattern) patterns.push(triggerPattern)
  
  return patterns
}

function analyzeDayOfWeekPattern(moods: any[]): MoodPattern | null {
  const dayMoods = moods.reduce((acc, mood) => {
    const day = new Date(mood.timestamp).getDay()
    if (!acc[day]) acc[day] = []
    acc[day].push(mood.mood)
    return acc
  }, {} as Record<number, string[]>)

  const dayNames = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
  const moodValues = { 'very-low': 1, 'low': 2, 'neutral': 3, 'good': 4, 'excellent': 5 }
  
  let bestDay = -1
  let worstDay = -1
  let bestAvg = 0
  let worstAvg = 6
  
  Object.entries(dayMoods).forEach(([day, dayMoodList]) => {
    if (dayMoodList.length < 2) return
    const avg = dayMoodList.reduce((sum, mood) => sum + moodValues[mood], 0) / dayMoodList.length
    if (avg > bestAvg) {
      bestAvg = avg
      bestDay = parseInt(day)
    }
    if (avg < worstAvg) {
      worstAvg = avg
      worstDay = parseInt(day)
    }
  })

  if (bestDay === -1 || Math.abs(bestAvg - worstAvg) < 1) return null

  return {
    type: 'weekly',
    pattern: `Your mood tends to be ${bestAvg > 3.5 ? 'higher' : 'lower'} on ${dayNames[bestDay]}s compared to ${dayNames[worstDay]}s`,
    confidence: Math.min(0.9, Math.abs(bestAvg - worstAvg) / 2),
    frequency: 1,
    suggestion: bestDay < worstDay 
      ? `Plan self-care activities for ${dayNames[worstDay]}s to boost your mood`
      : `Use the positive energy from ${dayNames[bestDay]}s to prepare for challenging days`,
    impact: bestAvg > worstAvg ? 'positive' : 'negative'
  }
}

function analyzeTimePattern(moods: any[]): MoodPattern | null {
  // Simplified time analysis - you could expand this
  const morningMoods = moods.filter(m => {
    const hour = new Date(m.timestamp).getHours()
    return hour >= 6 && hour < 12
  })
  
  const eveningMoods = moods.filter(m => {
    const hour = new Date(m.timestamp).getHours()
    return hour >= 18 && hour < 24
  })

  if (morningMoods.length < 3 || eveningMoods.length < 3) return null

  const moodValues = { 'very-low': 1, 'low': 2, 'neutral': 3, 'good': 4, 'excellent': 5 }
  const morningAvg = morningMoods.reduce((sum, m) => sum + moodValues[m.mood], 0) / morningMoods.length
  const eveningAvg = eveningMoods.reduce((sum, m) => sum + moodValues[m.mood], 0) / eveningMoods.length

  if (Math.abs(morningAvg - eveningAvg) < 0.5) return null

  return {
    type: 'daily',
    pattern: morningAvg > eveningAvg 
      ? 'Your mood tends to be higher in the morning and decline throughout the day'
      : 'Your mood tends to improve as the day progresses',
    confidence: Math.min(0.8, Math.abs(morningAvg - eveningAvg) / 2),
    frequency: 5,
    suggestion: morningAvg > eveningAvg
      ? 'Consider an evening routine to maintain your morning energy'
      : 'Try energizing morning activities to start your day stronger',
    impact: morningAvg > 3 && eveningAvg > 3 ? 'positive' : 'negative'
  }
}

function analyzeTriggerPattern(moods: any[]): MoodPattern | null {
  const triggeredMoods = moods.filter(m => m.triggers && m.triggers.length > 0)
  if (triggeredMoods.length < 5) return null

  const triggerCounts = triggeredMoods.reduce((acc, mood) => {
    mood.triggers.forEach((trigger: string) => {
      if (!acc[trigger]) acc[trigger] = { count: 0, totalMood: 0 }
      acc[trigger].count++
      acc[trigger].totalMood += { 'very-low': 1, 'low': 2, 'neutral': 3, 'good': 4, 'excellent': 5 }[mood.mood]
    })
    return acc
  }, {} as Record<string, { count: number, totalMood: number }>)

  const commonTrigger = Object.entries(triggerCounts)
    .sort(([,a], [,b]) => b.count - a.count)[0]

  if (!commonTrigger || commonTrigger[1].count < 3) return null

  const avgMoodForTrigger = commonTrigger[1].totalMood / commonTrigger[1].count

  return {
    type: 'trigger-based',
    pattern: `"${commonTrigger[0]}" appears to be a recurring influence on your mood`,
    confidence: Math.min(0.9, commonTrigger[1].count / triggeredMoods.length * 2),
    frequency: commonTrigger[1].count,
    suggestion: avgMoodForTrigger < 3 
      ? `Consider strategies to manage "${commonTrigger[0]}" triggers`
      : `"${commonTrigger[0]}" seems positive - try to incorporate it more often`,
    impact: avgMoodForTrigger > 3 ? 'positive' : 'negative'
  }
}

function generateWeeklyInsights(moods: any[], entries: any[], avgMood: number, variability: number): PersonalizedInsight[] {
  const insights: PersonalizedInsight[] = []

  if (avgMood >= 4) {
    insights.push({
      id: 'positive-week',
      type: 'achievement',
      title: 'Great Week!',
      description: 'Your mood has been consistently positive this week.',
      actionItems: ['Keep doing what\'s working', 'Share your positive energy with others'],
      priority: 'low',
      timestamp: Date.now(),
      category: 'mood'
    })
  }

  if (avgMood <= 2.5) {
    insights.push({
      id: 'concerning-week',
      type: 'warning',
      title: 'Challenging Week Detected',
      description: 'Your mood has been lower than usual. This is completely normal, and support is available.',
      actionItems: [
        'Consider reaching out to a friend or counselor',
        'Try gentle self-care activities',
        'Review what might be contributing to stress'
      ],
      priority: 'high',
      timestamp: Date.now(),
      category: 'mood'
    })
  }

  if (variability > 1.5) {
    insights.push({
      id: 'mood-variability',
      type: 'pattern',
      title: 'Mood Variability Notice',
      description: 'Your mood has fluctuated quite a bit this week.',
      actionItems: [
        'Look for patterns in what triggers ups and downs',
        'Consider stress management techniques',
        'Maintain consistent sleep and eating schedules'
      ],
      priority: 'medium',
      timestamp: Date.now(),
      category: 'wellness'
    })
  }

  return insights
}

function generateRecommendations(analysis: WeeklyAnalysis, patterns: MoodPattern[]): RecommendationCard[] {
  const recommendations: RecommendationCard[] = []

  if (analysis.averageMood < 3) {
    recommendations.push({
      id: 'mood-boost',
      title: 'Mood Boosting Activities',
      description: 'Simple activities proven to improve mood and energy',
      type: 'exercise',
      urgency: 'medium',
      estimatedTime: '10-20 min',
      benefits: ['Releases endorphins', 'Improves energy', 'Better sleep'],
      basedOn: ['Recent low mood trend', 'Research on exercise benefits']
    })
  }

  if (analysis.moodVariability > 1.5) {
    recommendations.push({
      id: 'stabilizing-routine',
      title: 'Stabilizing Daily Routine',
      description: 'Build consistency to help stabilize mood fluctuations',
      type: 'routine',
      urgency: 'medium',
      estimatedTime: '5-10 min',
      benefits: ['More predictable energy', 'Better emotional regulation', 'Improved focus'],
      basedOn: ['High mood variability', 'Benefits of routine structure']
    })
  }

  const negativePatterns = patterns.filter(p => p.impact === 'negative')
  if (negativePatterns.length > 0) {
    recommendations.push({
      id: 'mindfulness-practice',
      title: 'Mindfulness & Awareness',
      description: 'Develop awareness of mood patterns and triggers',
      type: 'mindfulness',
      urgency: 'low',
      estimatedTime: '5-15 min',
      benefits: ['Better self-awareness', 'Improved emotional regulation', 'Stress reduction'],
      basedOn: ['Detected negative patterns', 'Mindfulness research']
    })
  }

  return recommendations
}

function calculateStreaks(moods: any[]): { current: number, longest: number } {
  if (moods.length === 0) return { current: 0, longest: 0 }

  let current = 0
  let longest = 0
  let currentStreak = 0

  const sortedMoods = [...moods].sort((a, b) => b.timestamp - a.timestamp)
  
  for (let i = 0; i < sortedMoods.length; i++) {
    const mood = sortedMoods[i]
    const moodValue = { 'very-low': 1, 'low': 2, 'neutral': 3, 'good': 4, 'excellent': 5 }[mood.mood]
    
    if (moodValue >= 3) {
      currentStreak++
      if (i === 0) current = currentStreak
    } else {
      longest = Math.max(longest, currentStreak)
      currentStreak = 0
    }
  }
  
  longest = Math.max(longest, currentStreak)
  
  return { current, longest }
}