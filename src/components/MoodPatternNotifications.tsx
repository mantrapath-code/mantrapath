import { useState, useEffect } from "react"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Bell, TrendDown, TrendUp, X } from "@phosphor-icons/react"
import { useMoods, useMoodAnalytics } from "@/hooks/useWellness"
import { motion, AnimatePresence } from "framer-motion"
import { useKV } from '@github/spark/hooks'

interface MoodPattern {
  id: string
  type: 'declining-trend' | 'negative-streak' | 'positive-pattern'
  message: string
  recommendation: string
  severity: 'low' | 'medium' | 'high'
  timestamp: number
}

export function MoodPatternNotifications() {
  const { moods } = useMoods()
  const { getWeeklyInsights } = useMoodAnalytics()
  const [dismissedPatterns, setDismissedPatterns] = useKV<string[]>('dismissed-patterns', [])
  const [activePatterns, setActivePatterns] = useState<MoodPattern[]>([])

  useEffect(() => {
    checkForPatterns()
  }, [moods])

  const checkForPatterns = () => {
    const patterns: MoodPattern[] = []
    
    // Check for declining trend (last 3 days)
    const recentMoods = moods.slice(0, 3)
    if (recentMoods.length >= 3) {
      const moodValues = { 'very-low': 1, 'low': 2, 'neutral': 3, 'good': 4, 'excellent': 5 }
      const trend = recentMoods.map(m => moodValues[m.mood])
      
      if (trend[0] < trend[1] && trend[1] < trend[2]) {
        const patternId = `declining-${Date.now()}`
        if (!dismissedPatterns.includes(patternId)) {
          patterns.push({
            id: patternId,
            type: 'declining-trend',
            message: 'Your mood has been declining over the past 3 days',
            recommendation: 'Consider reaching out to support or practicing self-care activities',
            severity: trend[0] <= 2 ? 'high' : 'medium',
            timestamp: Date.now()
          })
        }
      }
    }

    // Check for negative streak (4+ consecutive low moods)
    const consecutiveLowMoods = getConsecutiveLowMoods()
    if (consecutiveLowMoods >= 4) {
      const patternId = `negative-streak-${Math.floor(Date.now() / (24 * 60 * 60 * 1000))}`
      if (!dismissedPatterns.includes(patternId)) {
        patterns.push({
          id: patternId,
          type: 'negative-streak',
          message: `You've logged ${consecutiveLowMoods} consecutive low mood entries`,
          recommendation: 'This might be a good time to connect with your support network or try a breathing exercise',
          severity: consecutiveLowMoods >= 7 ? 'high' : 'medium',
          timestamp: Date.now()
        })
      }
    }

    // Check for positive patterns to reinforce
    const recentPositive = moods.slice(0, 5).filter(m => ['good', 'excellent'].includes(m.mood))
    if (recentPositive.length >= 4) {
      const patternId = `positive-pattern-${Math.floor(Date.now() / (7 * 24 * 60 * 60 * 1000))}`
      if (!dismissedPatterns.includes(patternId)) {
        patterns.push({
          id: patternId,
          type: 'positive-pattern',
          message: 'You\'ve been in a great mood lately! 🌟',
          recommendation: 'Keep up the great work! Consider noting what\'s been helping you feel good',
          severity: 'low',
          timestamp: Date.now()
        })
      }
    }

    setActivePatterns(patterns)
  }

  const getConsecutiveLowMoods = () => {
    let count = 0
    for (const mood of moods) {
      if (['very-low', 'low'].includes(mood.mood)) {
        count++
      } else {
        break
      }
    }
    return count
  }

  const dismissPattern = (patternId: string) => {
    setDismissedPatterns(current => [...current, patternId])
    setActivePatterns(current => current.filter(p => p.id !== patternId))
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high': return 'destructive'
      case 'medium': return 'default'
      case 'low': return 'secondary'
      default: return 'default'
    }
  }

  const getPatternIcon = (type: string) => {
    switch (type) {
      case 'declining-trend': return <TrendDown className="text-destructive" size={16} />
      case 'negative-streak': return <Bell className="text-destructive" size={16} />
      case 'positive-pattern': return <TrendUp className="text-accent" size={16} />
      default: return <Bell size={16} />
    }
  }

  if (activePatterns.length === 0) return null

  return (
    <div className="space-y-3">
      <AnimatePresence>
        {activePatterns.map((pattern) => (
          <motion.div
            key={pattern.id}
            initial={{ opacity: 0, y: -20, height: 0 }}
            animate={{ opacity: 1, y: 0, height: 'auto' }}
            exit={{ opacity: 0, y: -20, height: 0 }}
            transition={{ duration: 0.3 }}
          >
            <Alert className={`border-l-4 ${
              pattern.severity === 'high' ? 'border-l-destructive' : 
              pattern.severity === 'medium' ? 'border-l-primary' : 
              'border-l-accent'
            }`}>
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-2 flex-1">
                  {getPatternIcon(pattern.type)}
                  <div className="flex-1">
                    <AlertDescription className="space-y-2">
                      <div className="flex items-center gap-2">
                        <span className="font-medium">{pattern.message}</span>
                        <Badge variant={getSeverityColor(pattern.severity)} className="text-xs">
                          {pattern.severity}
                        </Badge>
                      </div>
                      <p className="text-sm text-muted-foreground">
                        {pattern.recommendation}
                      </p>
                    </AlertDescription>
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => dismissPattern(pattern.id)}
                  className="shrink-0 ml-2"
                >
                  <X size={14} />
                </Button>
              </div>
            </Alert>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  )
}