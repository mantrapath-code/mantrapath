import { useState, useMemo } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Progress } from '@/components/ui/progress'
import { CalendarBlank, TrendUp, TrendDown, ArrowsLeftRight, ChartLine } from '@phosphor-icons/react'
import { useMoods } from '@/hooks/useWellness'
import { motion } from 'framer-motion'

type TimePeriod = '7d' | '14d' | '30d' | '90d'

interface PeriodStats {
  averageMood: number
  moodVariability: number
  dominantMood: string
  totalEntries: number
  positivePercentage: number
  streakLength: number
  commonTriggers: string[]
  startDate: number
  endDate: number
}

export function MoodComparisonView() {
  const { moods } = useMoods()
  const [primaryPeriod, setPrimaryPeriod] = useState<TimePeriod>('7d')
  const [secondaryPeriod, setSecondaryPeriod] = useState<TimePeriod>('14d')

  const periodLabels = {
    '7d': 'Last 7 days',
    '14d': 'Last 14 days', 
    '30d': 'Last 30 days',
    '90d': 'Last 90 days'
  }

  const getPeriodData = (period: TimePeriod): PeriodStats => {
    const days = { '7d': 7, '14d': 14, '30d': 30, '90d': 90 }[period]
    const cutoffTime = Date.now() - (days * 24 * 60 * 60 * 1000)
    const periodMoods = moods.filter(mood => mood.timestamp >= cutoffTime)
    
    if (periodMoods.length === 0) {
      return {
        averageMood: 0,
        moodVariability: 0,
        dominantMood: 'neutral',
        totalEntries: 0,
        positivePercentage: 0,
        streakLength: 0,
        commonTriggers: [],
        startDate: cutoffTime,
        endDate: Date.now()
      }
    }

    const moodValues = { 'very-low': 1, 'low': 2, 'neutral': 3, 'good': 4, 'excellent': 5 }
    const values = periodMoods.map(m => moodValues[m.mood])
    
    const averageMood = values.reduce((a, b) => a + b, 0) / values.length
    const variance = values.reduce((acc, val) => acc + Math.pow(val - averageMood, 2), 0) / values.length
    const moodVariability = Math.sqrt(variance)
    
    const moodCounts = periodMoods.reduce((acc, mood) => {
      acc[mood.mood] = (acc[mood.mood] || 0) + 1
      return acc
    }, {} as Record<string, number>)
    
    const dominantMood = Object.entries(moodCounts).reduce((a, b) => 
      moodCounts[a[0]] > moodCounts[b[0]] ? a : b
    )[0]

    const positiveCount = periodMoods.filter(m => ['good', 'excellent'].includes(m.mood)).length
    const positivePercentage = (positiveCount / periodMoods.length) * 100

    // Calculate current streak within this period
    let streakLength = 0
    for (const mood of periodMoods) {
      if (moodValues[mood.mood] >= 3) {
        streakLength++
      } else {
        break
      }
    }

    // Get common triggers
    const allTriggers = periodMoods.flatMap(m => m.triggers || [])
    const triggerCounts = allTriggers.reduce((acc, trigger) => {
      acc[trigger] = (acc[trigger] || 0) + 1
      return acc
    }, {} as Record<string, number>)
    
    const commonTriggers = Object.entries(triggerCounts)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 3)
      .map(([trigger]) => trigger)

    return {
      averageMood,
      moodVariability,
      dominantMood,
      totalEntries: periodMoods.length,
      positivePercentage,
      streakLength,
      commonTriggers,
      startDate: cutoffTime,
      endDate: Date.now()
    }
  }

  const primaryData = useMemo(() => getPeriodData(primaryPeriod), [primaryPeriod, moods])
  const secondaryData = useMemo(() => getPeriodData(secondaryPeriod), [secondaryPeriod, moods])

  const getComparisonInsight = (primary: PeriodStats, secondary: PeriodStats) => {
    const moodDiff = primary.averageMood - secondary.averageMood
    const variabilityDiff = primary.moodVariability - secondary.moodVariability
    const positiveDiff = primary.positivePercentage - secondary.positivePercentage

    if (Math.abs(moodDiff) < 0.2) {
      return {
        type: 'stable',
        message: 'Your mood has been relatively stable between these periods',
        icon: <ChartLine className="text-blue-500" size={20} />
      }
    } else if (moodDiff > 0) {
      return {
        type: 'improving',
        message: `Your mood improved by ${Math.abs(moodDiff).toFixed(1)} points`,
        icon: <TrendUp className="text-green-500" size={20} />
      }
    } else {
      return {
        type: 'declining',
        message: `Your mood decreased by ${Math.abs(moodDiff).toFixed(1)} points`,
        icon: <TrendDown className="text-orange-500" size={20} />
      }
    }
  }

  const insight = getComparisonInsight(primaryData, secondaryData)

  const getStatComparison = (primary: number, secondary: number, higherIsBetter = true) => {
    const diff = primary - secondary
    const isImproved = higherIsBetter ? diff > 0 : diff < 0
    
    if (Math.abs(diff) < 0.1) return { trend: 'stable', color: 'text-gray-600' }
    return {
      trend: isImproved ? 'improved' : 'declined',
      color: isImproved ? 'text-green-600' : 'text-red-600',
      percentage: Math.abs((diff / secondary) * 100).toFixed(1)
    }
  }

  if (moods.length < 3) {
    return (
      <Card>
        <CardContent className="p-6 text-center">
          <CalendarBlank className="mx-auto text-muted-foreground mb-4" size={48} />
          <h3 className="text-lg font-semibold mb-2">Comparison View Coming Soon</h3>
          <p className="text-muted-foreground">
            Log a few more moods to unlock period comparisons and trend analysis.
          </p>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <ArrowsLeftRight className="text-primary" size={24} />
            Mood Pattern Comparison
          </CardTitle>
          <p className="text-sm text-muted-foreground">
            Compare your mood patterns across different time periods to identify trends
          </p>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Period Selection */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium text-primary">Primary Period</label>
              <Select value={primaryPeriod} onValueChange={(value: TimePeriod) => setPrimaryPeriod(value)}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {Object.entries(periodLabels).map(([key, label]) => (
                    <SelectItem key={key} value={key}>{label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-muted-foreground">Compare With</label>
              <Select value={secondaryPeriod} onValueChange={(value: TimePeriod) => setSecondaryPeriod(value)}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {Object.entries(periodLabels).map(([key, label]) => (
                    <SelectItem key={key} value={key}>{label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Overall Insight */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-gradient-to-r from-blue-50 to-indigo-50 p-4 rounded-lg"
          >
            <div className="flex items-center gap-3">
              {insight.icon}
              <div>
                <h4 className="font-medium capitalize">{insight.type} Trend</h4>
                <p className="text-sm text-muted-foreground">{insight.message}</p>
              </div>
            </div>
          </motion.div>

          {/* Detailed Comparison */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Primary Period */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="space-y-4"
            >
              <div className="border-l-4 border-l-primary pl-4">
                <h4 className="font-semibold text-primary">{periodLabels[primaryPeriod]}</h4>
                <p className="text-xs text-muted-foreground">
                  {new Date(primaryData.startDate).toLocaleDateString()} - {new Date(primaryData.endDate).toLocaleDateString()}
                </p>
              </div>
              
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm">Average Mood</span>
                  <div className="flex items-center gap-2">
                    <span className="font-medium">{primaryData.averageMood.toFixed(1)}/5</span>
                    <Badge variant="outline" className="text-xs">
                      {Math.round(primaryData.averageMood * 20)}%
                    </Badge>
                  </div>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-sm">Dominant Mood</span>
                  <Badge className="capitalize">{primaryData.dominantMood}</Badge>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-sm">Total Entries</span>
                  <span className="font-medium">{primaryData.totalEntries}</span>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-sm">Positive Days</span>
                  <span className="font-medium">{primaryData.positivePercentage.toFixed(0)}%</span>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-sm">Mood Stability</span>
                  <div className="flex items-center gap-2">
                    <Progress 
                      value={Math.max(0, 100 - (primaryData.moodVariability * 50))} 
                      className="w-16 h-2" 
                    />
                    <span className="text-xs text-muted-foreground">
                      {primaryData.moodVariability < 1 ? 'Stable' : 'Variable'}
                    </span>
                  </div>
                </div>
              </div>
            </motion.div>

            {/* Secondary Period */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className="space-y-4"
            >
              <div className="border-l-4 border-l-muted-foreground pl-4">
                <h4 className="font-semibold text-muted-foreground">{periodLabels[secondaryPeriod]}</h4>
                <p className="text-xs text-muted-foreground">
                  {new Date(secondaryData.startDate).toLocaleDateString()} - {new Date(secondaryData.endDate).toLocaleDateString()}
                </p>
              </div>
              
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm">Average Mood</span>
                  <div className="flex items-center gap-2">
                    <span className="font-medium">{secondaryData.averageMood.toFixed(1)}/5</span>
                    <Badge variant="outline" className="text-xs">
                      {Math.round(secondaryData.averageMood * 20)}%
                    </Badge>
                    {(() => {
                      const comp = getStatComparison(primaryData.averageMood, secondaryData.averageMood)
                      return comp.trend !== 'stable' && (
                        <Badge variant="outline" className={`text-xs ${comp.color}`}>
                          {comp.trend === 'improved' ? '↗' : '↘'} {comp.percentage}%
                        </Badge>
                      )
                    })()}
                  </div>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-sm">Dominant Mood</span>
                  <Badge variant="outline" className="capitalize">{secondaryData.dominantMood}</Badge>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-sm">Total Entries</span>
                  <span className="font-medium text-muted-foreground">{secondaryData.totalEntries}</span>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-sm">Positive Days</span>
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-muted-foreground">{secondaryData.positivePercentage.toFixed(0)}%</span>
                    {(() => {
                      const comp = getStatComparison(primaryData.positivePercentage, secondaryData.positivePercentage)
                      return comp.trend !== 'stable' && (
                        <Badge variant="outline" className={`text-xs ${comp.color}`}>
                          {comp.trend === 'improved' ? '↗' : '↘'} {comp.percentage}%
                        </Badge>
                      )
                    })()}
                  </div>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-sm">Mood Stability</span>
                  <div className="flex items-center gap-2">
                    <Progress 
                      value={Math.max(0, 100 - (secondaryData.moodVariability * 50))} 
                      className="w-16 h-2" 
                    />
                    <span className="text-xs text-muted-foreground">
                      {secondaryData.moodVariability < 1 ? 'Stable' : 'Variable'}
                    </span>
                  </div>
                </div>
              </div>
            </motion.div>
          </div>

          {/* Common Triggers Comparison */}
          {(primaryData.commonTriggers.length > 0 || secondaryData.commonTriggers.length > 0) && (
            <div className="pt-4 border-t">
              <h4 className="font-medium mb-3">Common Triggers</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-primary font-medium mb-2">{periodLabels[primaryPeriod]}</p>
                  <div className="flex flex-wrap gap-1">
                    {primaryData.commonTriggers.length > 0 ? (
                      primaryData.commonTriggers.map((trigger, index) => (
                        <Badge key={index} variant="secondary" className="text-xs">
                          {trigger}
                        </Badge>
                      ))
                    ) : (
                      <span className="text-xs text-muted-foreground">No triggers logged</span>
                    )}
                  </div>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground font-medium mb-2">{periodLabels[secondaryPeriod]}</p>
                  <div className="flex flex-wrap gap-1">
                    {secondaryData.commonTriggers.length > 0 ? (
                      secondaryData.commonTriggers.map((trigger, index) => (
                        <Badge key={index} variant="outline" className="text-xs">
                          {trigger}
                        </Badge>
                      ))
                    ) : (
                      <span className="text-xs text-muted-foreground">No triggers logged</span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}