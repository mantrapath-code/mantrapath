import { useState, useEffect } from "react"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Bell, TrendDown, TrendUp, X, Warning, Target, Calendar, Clock, Activity, Brain } from "@phosphor-icons/react"
import { useMoods, useMoodAnalytics } from "@/hooks/useWellness"
import { useJournal } from "@/hooks/useJournal"
import { motion, AnimatePresence } from "framer-motion"
import { useKV } from '@github/spark/hooks'
import { toast } from "sonner"

interface SmartNotification {
  id: string
  type: 'declining-trend' | 'negative-streak' | 'positive-pattern' | 'preventive-action' | 'pattern-alert' | 'wellness-reminder'
  category: 'urgent' | 'preventive' | 'supportive' | 'insight'
  message: string
  recommendation: string
  actionItems?: string[]
  severity: 'low' | 'medium' | 'high'
  timestamp: number
  confidence: number
  basedOn: string[]
  preventiveAction?: {
    type: 'breathing' | 'social' | 'activity' | 'mindfulness' | 'routine'
    estimatedTime: string
    benefits: string[]
  }
}

export function MoodPatternNotifications() {
  const { moods } = useMoods()
  const { getWeeklyInsights, getMoodPredictions } = useMoodAnalytics()
  const { entries } = useJournal()
  const [dismissedPatterns, setDismissedPatterns] = useKV<string[]>('dismissed-patterns', [])
  const [activeNotifications, setActiveNotifications] = useState<SmartNotification[]>([])
  const [lastCheckTimestamp, setLastCheckTimestamp] = useKV<number>('last-pattern-check', 0)

  useEffect(() => {
    // Check for patterns every hour or when moods change
    const now = Date.now()
    const oneHour = 60 * 60 * 1000
    
    if (now - lastCheckTimestamp > oneHour || moods.length > 0) {
      checkForSmartPatterns()
      setLastCheckTimestamp(now)
    }
  }, [moods, entries])

  const checkForSmartPatterns = () => {
    const notifications: SmartNotification[] = []
    const now = Date.now()
    const currentHour = new Date().getHours()
    const currentDay = new Date().getDay()
    
    // Weekly trend analysis
    const weeklyAnalysis = analyzeWeeklyTrends()
    if (weeklyAnalysis) {
      weeklyAnalysis.forEach(pattern => {
        const patternId = `weekly-${pattern.type}-${Math.floor(now / (24 * 60 * 60 * 1000))}`
        if (!dismissedPatterns.includes(patternId)) {
          notifications.push({
            id: patternId,
            type: 'pattern-alert',
            category: pattern.severity === 'high' ? 'urgent' : 'preventive',
            message: pattern.message,
            recommendation: pattern.recommendation,
            actionItems: pattern.actionItems,
            severity: pattern.severity,
            timestamp: now,
            confidence: pattern.confidence,
            basedOn: pattern.basedOn,
            preventiveAction: pattern.preventiveAction
          })
        }
      })
    }
    
    // Enhanced declining trend detection
    const recentMoods = moods.slice(0, 5) // Look at last 5 entries
    if (recentMoods.length >= 3) {
      const moodValues = { 'very-low': 1, 'low': 2, 'neutral': 3, 'good': 4, 'excellent': 5 }
      const trend = recentMoods.map(m => moodValues[m.mood])
      
      // Check for consistent decline
      const isDecline = trend.every((mood, i) => i === 0 || mood <= trend[i - 1])
      const avgDecline = trend.length > 1 ? trend[0] - trend[trend.length - 1] : 0
      
      if (isDecline && avgDecline >= 1) {
        const patternId = `smart-decline-${Math.floor(now / (12 * 60 * 60 * 1000))}`
        if (!dismissedPatterns.includes(patternId)) {
          notifications.push({
            id: patternId,
            type: 'declining-trend',
            category: trend[0] <= 2 ? 'urgent' : 'preventive',
            message: `Your mood has declined over ${trend.length} recent entries`,
            recommendation: 'Consider proactive self-care before things get harder',
            actionItems: [
              'Try a 5-minute breathing exercise',
              'Reach out to a supportive friend',
              'Take a short walk or do gentle movement',
              'Practice a grounding technique'
            ],
            severity: trend[0] <= 2 ? 'high' : 'medium',
            timestamp: now,
            confidence: Math.min(0.9, avgDecline / 2),
            basedOn: [`${trend.length} consecutive mood entries`, `${avgDecline.toFixed(1)} point decline`],
            preventiveAction: {
              type: 'breathing',
              estimatedTime: '5-10 minutes',
              benefits: ['Reduces stress', 'Improves focus', 'Calms nervous system']
            }
          })
        }
      }
    }
    
    // Weekly comparison and trend insights
    const weeklyComparison = analyzeWeeklyComparison()
    if (weeklyComparison) {
      const patternId = `weekly-comparison-${Math.floor(now / (7 * 24 * 60 * 60 * 1000))}`
      if (!dismissedPatterns.includes(patternId)) {
        notifications.push({
          id: patternId,
          type: 'pattern-alert',
          category: weeklyComparison.trend === 'declining' ? 'preventive' : 'supportive',
          message: weeklyComparison.message,
          recommendation: weeklyComparison.recommendation,
          actionItems: weeklyComparison.actionItems,
          severity: weeklyComparison.trend === 'declining' ? 'medium' : 'low',
          timestamp: now,
          confidence: weeklyComparison.confidence,
          basedOn: weeklyComparison.basedOn,
          preventiveAction: weeklyComparison.preventiveAction
        })
      }
    }

    // Predictive pattern alerts based on historical data
    const historicalPatterns = analyzeHistoricalPatterns()
    historicalPatterns.forEach(pattern => {
      if (pattern.confidence > 0.6) {
        const patternId = `predictive-${pattern.type}-${Math.floor(now / (24 * 60 * 60 * 1000))}`
        if (!dismissedPatterns.includes(patternId)) {
          notifications.push({
            id: patternId,
            type: 'pattern-alert',
            category: 'preventive',
            message: pattern.message,
            recommendation: pattern.recommendation,
            actionItems: pattern.actionItems,
            severity: 'medium',
            timestamp: now,
            confidence: pattern.confidence,
            basedOn: pattern.basedOn,
            preventiveAction: pattern.preventiveAction
          })
        }
      }
    })

    // Wellness reminders based on successful patterns
    const successfulPatterns = detectSuccessfulPatterns()
    successfulPatterns.forEach(pattern => {
      const patternId = `wellness-reminder-${pattern.type}-${Math.floor(now / (7 * 24 * 60 * 60 * 1000))}`
      if (!dismissedPatterns.includes(patternId)) {
        notifications.push({
          id: patternId,
          type: 'wellness-reminder',
          category: 'supportive',
          message: pattern.message,
          recommendation: pattern.recommendation,
          severity: 'low',
          timestamp: now,
          confidence: pattern.confidence,
          basedOn: pattern.basedOn,
          preventiveAction: pattern.preventiveAction
        })
      }
    })

    // Positive reinforcement
    const positiveStreak = getPositiveStreak()
    if (positiveStreak >= 3) {
      const patternId = `positive-streak-${Math.floor(now / (7 * 24 * 60 * 60 * 1000))}`
      if (!dismissedPatterns.includes(patternId)) {
        notifications.push({
          id: patternId,
          type: 'positive-pattern',
          category: 'supportive',
          message: `Amazing! You've maintained positive mood for ${positiveStreak} days 🌟`,
          recommendation: 'Keep up the great work and consider what\'s been helping you thrive',
          actionItems: [
            'Reflect on what\'s been working well',
            'Share your positive energy with others',
            'Consider setting a new wellness goal'
          ],
          severity: 'low',
          timestamp: now,
          confidence: 0.9,
          basedOn: [`${positiveStreak} consecutive positive mood days`],
          preventiveAction: {
            type: 'mindfulness',
            estimatedTime: '5 minutes',
            benefits: ['Reinforces positive patterns', 'Builds self-awareness', 'Maintains momentum']
          }
        })
      }
    }

    setActiveNotifications(notifications)
  }

  const analyzeWeeklyTrends = () => {
    const patterns: any[] = []
    const now = Date.now()
    const oneWeek = 7 * 24 * 60 * 60 * 1000
    const twoWeeks = 2 * oneWeek
    const threeWeeks = 3 * oneWeek
    
    // Get mood data for different time periods
    const thisWeek = moods.filter(m => m.timestamp >= now - oneWeek)
    const lastWeek = moods.filter(m => m.timestamp >= now - twoWeeks && m.timestamp < now - oneWeek)
    const twoWeeksAgo = moods.filter(m => m.timestamp >= now - threeWeeks && m.timestamp < now - twoWeeks)
    
    if (thisWeek.length < 2 || lastWeek.length < 2) return patterns
    
    const moodValues = { 'very-low': 1, 'low': 2, 'neutral': 3, 'good': 4, 'excellent': 5 }
    
    // Calculate weekly averages
    const thisWeekAvg = thisWeek.reduce((sum, m) => sum + moodValues[m.mood], 0) / thisWeek.length
    const lastWeekAvg = lastWeek.reduce((sum, m) => sum + moodValues[m.mood], 0) / lastWeek.length
    const twoWeeksAvg = twoWeeksAgo.length > 1 ? 
      twoWeeksAgo.reduce((sum, m) => sum + moodValues[m.mood], 0) / twoWeeksAgo.length : null
    
    // Analyze weekly progression
    const weeklyChange = thisWeekAvg - lastWeekAvg
    const isConsistentTrend = twoWeeksAvg ? 
      (lastWeekAvg - twoWeeksAvg > 0) === (thisWeekAvg - lastWeekAvg > 0) : false
    
    // Declining trend over multiple weeks
    if (weeklyChange < -0.5 && Math.abs(weeklyChange) > 0.3) {
      patterns.push({
        type: 'weekly-decline',
        message: `Your weekly mood average has declined from ${lastWeekAvg.toFixed(1)} to ${thisWeekAvg.toFixed(1)}`,
        recommendation: 'Let\'s identify what changed and create a support plan',
        actionItems: [
          'Review recent life changes or stressors',
          'Increase self-care activities that worked before',
          'Consider reaching out to friends or family',
          'Explore relaxation techniques and stress management'
        ],
        severity: weeklyChange < -1 ? 'high' : 'medium' as const,
        confidence: Math.min(0.9, Math.abs(weeklyChange) / 2),
        basedOn: [`${thisWeek.length} entries this week`, `${lastWeek.length} entries last week`, `${weeklyChange.toFixed(2)} point decline`],
        preventiveAction: {
          type: 'mindfulness',
          estimatedTime: '10-15 minutes',
          benefits: ['Reduces anxiety', 'Improves self-awareness', 'Breaks negative thought cycles']
        }
      })
    }
    
    // Improving trend recognition
    if (weeklyChange > 0.5 && Math.abs(weeklyChange) > 0.3) {
      patterns.push({
        type: 'weekly-improvement',
        message: `Great progress! Your weekly mood average improved from ${lastWeekAvg.toFixed(1)} to ${thisWeekAvg.toFixed(1)}`,
        recommendation: 'Reflect on what\'s working well and build on it',
        actionItems: [
          'Identify the positive changes you\'ve made',
          'Celebrate your progress with something meaningful',
          'Share your success with supportive people',
          'Plan to maintain these positive habits'
        ],
        severity: 'low' as const,
        confidence: Math.min(0.9, Math.abs(weeklyChange) / 2),
        basedOn: [`${thisWeek.length} entries this week`, `${lastWeek.length} entries last week`, `+${weeklyChange.toFixed(2)} point improvement`],
        preventiveAction: {
          type: 'social',
          estimatedTime: '5-10 minutes',
          benefits: ['Reinforces positive changes', 'Builds support network', 'Increases motivation']
        }
      })
    }
    
    // Weekly pattern consistency analysis
    if (isConsistentTrend && twoWeeksAvg) {
      const overallTrend = thisWeekAvg - twoWeeksAvg
      if (Math.abs(overallTrend) > 0.8) {
        patterns.push({
          type: 'consistent-trend',
          message: `Your mood has been ${overallTrend > 0 ? 'consistently improving' : 'consistently declining'} over the past 3 weeks`,
          recommendation: overallTrend > 0 ? 
            'Keep up the momentum with what\'s working' : 
            'This trend suggests you might benefit from additional support',
          actionItems: overallTrend > 0 ? [
            'Document what strategies are working',
            'Share your success story to help others',
            'Set new wellness goals to maintain progress'
          ] : [
            'Consider speaking with a counselor or therapist',
            'Reach out to trusted friends or family',
            'Review and adjust your self-care routine',
            'Explore community support resources'
          ],
          severity: overallTrend > 0 ? 'low' : 'high' as const,
          confidence: 0.8,
          basedOn: [`3-week trend analysis`, `${overallTrend.toFixed(2)} point ${overallTrend > 0 ? 'improvement' : 'decline'}`],
          preventiveAction: {
            type: overallTrend > 0 ? 'mindfulness' : 'social',
            estimatedTime: '10-20 minutes',
            benefits: overallTrend > 0 ? 
              ['Maintains positive momentum', 'Builds resilience', 'Enhances self-awareness'] :
              ['Provides emotional support', 'Reduces isolation', 'Offers new perspectives']
          }
        })
      }
    }
    
    // Weekly volatility analysis
    const thisWeekVolatility = calculateMoodVolatility(thisWeek)
    const lastWeekVolatility = calculateMoodVolatility(lastWeek)
    
    if (thisWeekVolatility > 1.5 && thisWeekVolatility > lastWeekVolatility * 1.3) {
      patterns.push({
        type: 'mood-volatility',
        message: 'Your mood has been more variable this week than usual',
        recommendation: 'Focus on stability and routine to help smooth out mood swings',
        actionItems: [
          'Establish a consistent daily routine',
          'Practice grounding techniques during mood swings',
          'Identify triggers for mood changes',
          'Consider mood tracking at specific times of day'
        ],
        severity: 'medium' as const,
        confidence: 0.7,
        basedOn: [`Mood volatility: ${thisWeekVolatility.toFixed(2)} this week vs ${lastWeekVolatility.toFixed(2)} last week`],
        preventiveAction: {
          type: 'routine',
          estimatedTime: '20-30 minutes',
          benefits: ['Stabilizes mood', 'Reduces anxiety', 'Improves predictability']
        }
      })
    }
    
    return patterns
  }
  
  const calculateMoodVolatility = (moodEntries: any[]) => {
    if (moodEntries.length < 2) return 0
    
    const moodValues = { 'very-low': 1, 'low': 2, 'neutral': 3, 'good': 4, 'excellent': 5 }
    const values = moodEntries.map(m => moodValues[m.mood])
    const avg = values.reduce((sum, val) => sum + val, 0) / values.length
    const variance = values.reduce((sum, val) => sum + Math.pow(val - avg, 2), 0) / values.length
    
    return Math.sqrt(variance)
  }
  
  const analyzeWeeklyComparison = () => {
    const now = Date.now()
    const oneWeek = 7 * 24 * 60 * 60 * 1000
    const twoWeeks = 2 * oneWeek
    
    const thisWeek = moods.filter(m => m.timestamp >= now - oneWeek)
    const lastWeek = moods.filter(m => m.timestamp >= now - twoWeeks && m.timestamp < now - oneWeek)
    
    if (thisWeek.length < 2 || lastWeek.length < 2) return null
    
    const moodValues = { 'very-low': 1, 'low': 2, 'neutral': 3, 'good': 4, 'excellent': 5 }
    
    // Compare daily patterns
    const thisWeekByDay = groupMoodsByDay(thisWeek)
    const lastWeekByDay = groupMoodsByDay(lastWeek)
    
    const dayNames = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    const insights: string[] = []
    
    Object.keys(thisWeekByDay).forEach(day => {
      const dayNum = parseInt(day)
      const thisWeekDayAvg = thisWeekByDay[dayNum]?.reduce((sum, m) => sum + moodValues[m.mood], 0) / thisWeekByDay[dayNum].length || 0
      const lastWeekDayAvg = lastWeekByDay[dayNum]?.reduce((sum, m) => sum + moodValues[m.mood], 0) / lastWeekByDay[dayNum].length || 0
      
      if (thisWeekDayAvg && lastWeekDayAvg && Math.abs(thisWeekDayAvg - lastWeekDayAvg) > 0.8) {
        const change = thisWeekDayAvg > lastWeekDayAvg ? 'improved' : 'declined'
        insights.push(`${dayNames[dayNum]}s have ${change} significantly`)
      }
    })
    
    // Overall weekly comparison
    const thisWeekAvg = thisWeek.reduce((sum, m) => sum + moodValues[m.mood], 0) / thisWeek.length
    const lastWeekAvg = lastWeek.reduce((sum, m) => sum + moodValues[m.mood], 0) / lastWeek.length
    const weeklyDiff = thisWeekAvg - lastWeekAvg
    
    if (Math.abs(weeklyDiff) < 0.3 && insights.length === 0) return null
    
    const trend = weeklyDiff > 0.3 ? 'improving' : weeklyDiff < -0.3 ? 'declining' : 'stable'
    
    let message = `Weekly comparison: ${trend} trend`
    if (insights.length > 0) {
      message += ` (${insights.slice(0, 2).join(', ')})`
    }
    
    const actionItems = trend === 'declining' ? [
      'Review what changed from last week',
      'Return to strategies that worked before',
      'Increase social connection and support',
      'Consider professional guidance if needed'
    ] : trend === 'improving' ? [
      'Identify the positive changes you\'ve made',
      'Continue with strategies that are working',
      'Build on this momentum with new goals',
      'Share your success with others'
    ] : [
      'Maintain current positive habits',
      'Look for small improvements to make',
      'Stay consistent with your wellness routine'
    ]
    
    return {
      trend,
      message,
      recommendation: trend === 'declining' ? 
        'Focus on returning to what worked before' : 
        trend === 'improving' ? 'Build on your positive momentum' : 'Consistency is key - keep going',
      actionItems,
      confidence: Math.min(0.8, Math.abs(weeklyDiff) + 0.3),
      basedOn: [`${thisWeek.length} entries this week`, `${lastWeek.length} entries last week`, insights.length > 0 ? `Day-specific changes: ${insights.join(', ')}` : 'Overall weekly patterns'],
      preventiveAction: {
        type: trend === 'declining' ? 'social' : 'mindfulness',
        estimatedTime: '10-15 minutes',
        benefits: trend === 'declining' ? 
          ['Provides support', 'Offers perspective', 'Reduces isolation'] :
          ['Maintains awareness', 'Reinforces positive patterns', 'Builds resilience']
      }
    }
  }
  
  const groupMoodsByDay = (moodEntries: any[]) => {
    return moodEntries.reduce((acc, mood) => {
      const day = new Date(mood.timestamp).getDay()
      if (!acc[day]) acc[day] = []
      acc[day].push(mood)
      return acc
    }, {} as Record<number, any[]>)
  }

  const analyzeHistoricalPatterns = () => {
    const patterns: any[] = []
    const currentHour = new Date().getHours()
    const currentDay = new Date().getDay()
    
    // Analyze time-based patterns
    const afternoonSlumps = moods.filter(m => {
      const hour = new Date(m.timestamp).getHours()
      return hour >= 14 && hour <= 16 && ['low', 'very-low'].includes(m.mood)
    })
    
    if (afternoonSlumps.length >= 3 && currentHour >= 13 && currentHour <= 15) {
      patterns.push({
        type: 'afternoon-slump',
        message: 'You often experience afternoon energy dips around this time',
        recommendation: 'Try a quick energy boost before your mood drops',
        actionItems: [
          'Take a 5-minute walk',
          'Do some light stretching',
          'Have a healthy snack',
          'Practice energizing breathing'
        ],
        confidence: Math.min(0.8, afternoonSlumps.length / 10),
        basedOn: [`${afternoonSlumps.length} historical afternoon low moods`],
        preventiveAction: {
          type: 'activity',
          estimatedTime: '5-10 minutes',
          benefits: ['Boosts energy', 'Prevents mood dip', 'Improves focus']
        }
      })
    }

    // Analyze day-of-week patterns
    const mondayBlues = moods.filter(m => {
      const day = new Date(m.timestamp).getDay()
      return day === 1 && ['low', 'very-low'].includes(m.mood)
    })
    
    if (mondayBlues.length >= 2 && currentDay === 1) {
      patterns.push({
        type: 'monday-blues',
        message: 'Mondays tend to be challenging for you',
        recommendation: 'Start your Monday with extra self-care',
        actionItems: [
          'Plan something enjoyable for Monday evening',
          'Prepare Sunday night to reduce Monday stress',
          'Start with a gentle morning routine',
          'Connect with supportive people'
        ],
        confidence: Math.min(0.9, mondayBlues.length / 5),
        basedOn: [`${mondayBlues.length} challenging Mondays`],
        preventiveAction: {
          type: 'routine',
          estimatedTime: '10-15 minutes',
          benefits: ['Reduces Monday stress', 'Improves week start', 'Builds resilience']
        }
      })
    }

    return patterns
  }

  const detectSuccessfulPatterns = () => {
    const patterns: any[] = []
    
    // Analyze what activities correlate with mood improvements
    const exerciseMentions = entries.filter(entry => 
      entry.content.toLowerCase().includes('exercise') || 
      entry.content.toLowerCase().includes('workout') ||
      entry.keywords.includes('exercise')
    )
    
    if (exerciseMentions.length >= 3) {
      const exerciseImpact = analyzeActivityImpact('exercise')
      if (exerciseImpact && exerciseImpact.improvement > 0.5) {
        patterns.push({
          type: 'exercise-reminder',
          message: 'Exercise has been consistently boosting your mood',
          recommendation: 'Consider incorporating movement into your routine today',
          confidence: 0.8,
          basedOn: [`${exerciseMentions.length} exercise entries`, `+${exerciseImpact.improvement.toFixed(1)} mood improvement`],
          preventiveAction: {
            type: 'activity',
            estimatedTime: '15-30 minutes',
            benefits: ['Improves mood', 'Increases energy', 'Reduces stress']
          }
        })
      }
    }

    return patterns
  }

  const analyzeActivityImpact = (activity: string) => {
    const relevantEntries = entries.filter(entry => 
      entry.content.toLowerCase().includes(activity.toLowerCase()) || 
      entry.keywords.includes(activity.toLowerCase())
    )
    
    if (relevantEntries.length < 2) return null

    const moodValues = { 'very-low': 1, 'low': 2, 'neutral': 3, 'good': 4, 'excellent': 5 }
    let beforeMoods: number[] = []
    let afterMoods: number[] = []

    relevantEntries.forEach(entry => {
      const entryTime = entry.timestamp
      const beforeMood = moods.find(m => m.timestamp <= entryTime && (entryTime - m.timestamp) <= 4 * 60 * 60 * 1000)
      const afterMood = moods.find(m => m.timestamp >= entryTime && (m.timestamp - entryTime) <= 4 * 60 * 60 * 1000)
      
      if (beforeMood && afterMood) {
        beforeMoods.push(moodValues[beforeMood.mood])
        afterMoods.push(moodValues[afterMood.mood])
      }
    })

    if (beforeMoods.length < 2) return null

    const avgBefore = beforeMoods.reduce((a, b) => a + b, 0) / beforeMoods.length
    const avgAfter = afterMoods.reduce((a, b) => a + b, 0) / afterMoods.length

    return {
      improvement: avgAfter - avgBefore,
      frequency: relevantEntries.length
    }
  }

  const getPositiveStreak = () => {
    let streak = 0
    const moodValues = { 'very-low': 1, 'low': 2, 'neutral': 3, 'good': 4, 'excellent': 5 }
    
    for (const mood of moods) {
      if (moodValues[mood.mood] >= 4) {
        streak++
      } else {
        break
      }
    }
    return streak
  }

  const dismissNotification = (notificationId: string) => {
    setDismissedPatterns(current => [...current, notificationId])
    setActiveNotifications(current => current.filter(n => n.id !== notificationId))
    
    // Show a supportive message when dismissing
    toast.success("We're here when you need us", {
      description: "You can always access wellness tools in the chatbot.",
      duration: 3000,
    })
  }

  const executePreventiveAction = (notification: SmartNotification) => {
    if (notification.preventiveAction) {
      const action = notification.preventiveAction
      toast.success(`Starting ${action.type} exercise`, {
        description: `This should take about ${action.estimatedTime}`,
        duration: 5000,
      })
      
      // Here you could trigger specific actions like opening breathing exercises
      // For now, we'll just dismiss the notification and show encouragement
      dismissNotification(notification.id)
    }
  }

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'urgent': return 'border-l-destructive bg-destructive/5'
      case 'preventive': return 'border-l-orange-500 bg-orange-50'
      case 'supportive': return 'border-l-green-500 bg-green-50'
      case 'insight': return 'border-l-blue-500 bg-blue-50'
      default: return 'border-l-primary bg-primary/5'
    }
  }

  const getCategoryIcon = (category: string, type: string) => {
    switch (category) {
      case 'urgent': return <Warning className="text-destructive" size={16} />
      case 'preventive': return <Target className="text-orange-600" size={16} />
      case 'supportive': return <TrendUp className="text-green-600" size={16} />
      case 'insight': return <Brain className="text-blue-600" size={16} />
      default: return <Bell size={16} />
    }
  }

  const getSeverityBadge = (severity: string) => {
    switch (severity) {
      case 'high': return { variant: 'destructive' as const, label: 'High Priority' }
      case 'medium': return { variant: 'default' as const, label: 'Medium Priority' }
      case 'low': return { variant: 'secondary' as const, label: 'Low Priority' }
      default: return { variant: 'outline' as const, label: 'Info' }
    }
  }

  if (activeNotifications.length === 0) return null

  return (
    <div className="space-y-3">
      <AnimatePresence>
        {activeNotifications.map((notification) => {
          const severityBadge = getSeverityBadge(notification.severity)
          
          return (
            <motion.div
              key={notification.id}
              initial={{ opacity: 0, y: -20, height: 0 }}
              animate={{ opacity: 1, y: 0, height: 'auto' }}
              exit={{ opacity: 0, y: -20, height: 0 }}
              transition={{ duration: 0.3 }}
            >
              <Alert className={`border-l-4 ${getCategoryColor(notification.category)}`}>
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-2 flex-1">
                    {getCategoryIcon(notification.category, notification.type)}
                    <div className="flex-1 space-y-3">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="font-medium">{notification.message}</span>
                        <Badge variant={severityBadge.variant} className="text-xs">
                          {severityBadge.label}
                        </Badge>
                        <Badge variant="outline" className="text-xs">
                          {Math.round(notification.confidence * 100)}% confidence
                        </Badge>
                      </div>
                      
                      <AlertDescription className="space-y-3">
                        <p className="text-sm text-muted-foreground">
                          {notification.recommendation}
                        </p>
                        
                        {notification.actionItems && notification.actionItems.length > 0 && (
                          <div className="space-y-2">
                            <span className="text-sm font-medium">Suggested actions:</span>
                            <ul className="text-sm space-y-1">
                              {notification.actionItems.map((item, index) => (
                                <li key={index} className="flex items-start gap-2">
                                  <span className="text-primary text-xs">•</span>
                                  <span>{item}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                        
                        {notification.preventiveAction && (
                          <div className="bg-accent/10 p-3 rounded-lg space-y-2">
                            <div className="flex items-center justify-between">
                              <span className="text-sm font-medium">Quick Action Available</span>
                              <Button
                                size="sm"
                                onClick={() => executePreventiveAction(notification)}
                                className="text-xs"
                              >
                                Start {notification.preventiveAction.type}
                              </Button>
                            </div>
                            <div className="text-xs text-muted-foreground">
                              {notification.preventiveAction.estimatedTime} • {notification.preventiveAction.benefits.join(', ')}
                            </div>
                          </div>
                        )}
                        
                        <div className="text-xs text-muted-foreground">
                          <span className="font-medium">Based on: </span>
                          {notification.basedOn.join(', ')}
                        </div>
                      </AlertDescription>
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => dismissNotification(notification.id)}
                    className="shrink-0 ml-2"
                  >
                    <X size={14} />
                  </Button>
                </div>
              </Alert>
            </motion.div>
          )
        })}
      </AnimatePresence>
    </div>
  )
}