import { useMemo, useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Progress } from '@/components/ui/progress'
import { ChartBar, TrendUp, TrendDown, Pulse, Clock, Calendar, Lightbulb, Target } from '@phosphor-icons/react'
import { useMoods } from '@/hooks/useMoods'
import { useJournal } from '@/hooks/useJournal'
import { motion, AnimatePresence } from 'framer-motion'

interface MoodCorrelation {
  type: 'day' | 'time' | 'energy' | 'trigger' | 'activity' | 'context'
  label: string
  value: number
  count: number
  trend: 'positive' | 'negative' | 'neutral'
  confidence: number
  impact: 'high' | 'medium' | 'low'
  suggestion?: string
}

interface ActivityInsight {
  activity: string
  averageMoodBefore: number
  averageMoodAfter: number
  improvement: number
  frequency: number
  recommendation: string
}

export function MoodCorrelations() {
  const { moods } = useMoods()
  const { entries } = useJournal()
  const [selectedTab, setSelectedTab] = useState('patterns')

  const { correlations, activityInsights, triggerAnalysis } = useMemo(() => {
    if (moods.length < 7) return { correlations: [], activityInsights: [], triggerAnalysis: [] }

    const moodValues = { 'very-low': 1, 'low': 2, 'neutral': 3, 'good': 4, 'excellent': 5 }
    
    // Enhanced day of week analysis
    const dayCorrelations = Array.from({ length: 7 }, (_, day) => {
      const dayMoods = moods.filter(m => (m.dayOfWeek ?? new Date(m.timestamp).getDay()) === day)
      if (dayMoods.length < 2) return null
      
      const avg = dayMoods.reduce((sum, m) => sum + moodValues[m.mood], 0) / dayMoods.length
      const dayName = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'][day]
      const shortName = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'][day]
      
      const deviation = Math.abs(avg - 3)
      const confidence = Math.min(0.9, (dayMoods.length / 10) * (deviation / 2))
      
      let suggestion = ''
      if (avg < 2.5) {
        suggestion = `Plan self-care activities for ${dayName}s to boost your mood`
      } else if (avg > 4) {
        suggestion = `Leverage your positive ${dayName} energy for challenging tasks`
      }
      
      return {
        type: 'day' as const,
        label: shortName,
        value: avg,
        count: dayMoods.length,
        trend: avg > 3.2 ? 'positive' : avg < 2.8 ? 'negative' : 'neutral',
        confidence,
        impact: deviation > 1 ? 'high' : deviation > 0.5 ? 'medium' : 'low',
        suggestion
      }
    }).filter(Boolean) as MoodCorrelation[]

    // Enhanced time of day analysis
    const timeCorrelations = ['morning', 'afternoon', 'evening', 'night'].map(time => {
      const timeMoods = moods.filter(m => m.timeOfDay === time)
      if (timeMoods.length < 2) return null
      
      const avg = timeMoods.reduce((sum, m) => sum + moodValues[m.mood], 0) / timeMoods.length
      const deviation = Math.abs(avg - 3)
      const confidence = Math.min(0.9, (timeMoods.length / 10) * (deviation / 2))
      
      let suggestion = ''
      if (avg < 2.5) {
        suggestion = `Consider mood-boosting activities during ${time} hours`
      } else if (avg > 4) {
        suggestion = `Schedule important tasks during ${time} when you feel your best`
      }
      
      return {
        type: 'time' as const,
        label: time.charAt(0).toUpperCase() + time.slice(1),
        value: avg,
        count: timeMoods.length,
        trend: avg > 3.2 ? 'positive' : avg < 2.8 ? 'negative' : 'neutral',
        confidence,
        impact: deviation > 1 ? 'high' : deviation > 0.5 ? 'medium' : 'low',
        suggestion
      }
    }).filter(Boolean) as MoodCorrelation[]

    // Enhanced energy level analysis
    const energyCorrelations = ['high', 'medium', 'low'].map(energy => {
      const energyMoods = moods.filter(m => m.energy === energy)
      if (energyMoods.length < 2) return null
      
      const avg = energyMoods.reduce((sum, m) => sum + moodValues[m.mood], 0) / energyMoods.length
      const deviation = Math.abs(avg - 3)
      const confidence = Math.min(0.9, (energyMoods.length / 8) * (deviation / 2))
      
      let suggestion = ''
      if (energy === 'low' && avg < 3) {
        suggestion = 'Rest and gentle activities when energy is low can help maintain mood'
      } else if (energy === 'high' && avg > 3.5) {
        suggestion = 'Maintain your high-energy activities - they clearly boost your mood'
      }
      
      return {
        type: 'energy' as const,
        label: `${energy.charAt(0).toUpperCase() + energy.slice(1)} Energy`,
        value: avg,
        count: energyMoods.length,
        trend: avg > 3.2 ? 'positive' : avg < 2.8 ? 'negative' : 'neutral',
        confidence,
        impact: deviation > 1 ? 'high' : deviation > 0.5 ? 'medium' : 'low',
        suggestion
      }
    }).filter(Boolean) as MoodCorrelation[]

    // Trigger analysis
    const triggerMoods = moods.filter(m => m.triggers && m.triggers.length > 0)
    const triggerAnalysis = Object.entries(
      triggerMoods.reduce((acc, mood) => {
        mood.triggers!.forEach(trigger => {
          if (!acc[trigger]) acc[trigger] = { total: 0, count: 0, moods: [] }
          acc[trigger].total += moodValues[mood.mood]
          acc[trigger].count++
          acc[trigger].moods.push(moodValues[mood.mood])
        })
        return acc
      }, {} as Record<string, { total: number, count: number, moods: number[] }>)
    ).map(([trigger, data]) => {
      const avg = data.total / data.count
      const deviation = Math.abs(avg - 3)
      const confidence = Math.min(0.9, data.count / 5)
      
      let suggestion = ''
      if (avg < 2.5) {
        suggestion = `Consider strategies to manage "${trigger}" as it tends to lower your mood`
      } else if (avg > 3.5) {
        suggestion = `"${trigger}" has a positive impact - try to incorporate it more often`
      }
      
      return {
        type: 'trigger' as const,
        label: trigger,
        value: avg,
        count: data.count,
        trend: avg > 3.2 ? 'positive' : avg < 2.8 ? 'negative' : 'neutral',
        confidence,
        impact: deviation > 1 ? 'high' : deviation > 0.5 ? 'medium' : 'low',
        suggestion
      }
    }).filter(item => item.count >= 2) as MoodCorrelation[]

    // Context/Activity analysis from journal entries
    const contextMoods = moods.filter(m => m.context && m.context.length > 0)
    const contextAnalysis = Object.entries(
      contextMoods.reduce((acc, mood) => {
        mood.context!.forEach(context => {
          if (!acc[context]) acc[context] = { total: 0, count: 0 }
          acc[context].total += moodValues[mood.mood]
          acc[context].count++
        })
        return acc
      }, {} as Record<string, { total: number, count: number }>)
    ).map(([context, data]) => {
      const avg = data.total / data.count
      const deviation = Math.abs(avg - 3)
      const confidence = Math.min(0.9, data.count / 3)
      
      return {
        type: 'context' as const,
        label: context,
        value: avg,
        count: data.count,
        trend: avg > 3.2 ? 'positive' : avg < 2.8 ? 'negative' : 'neutral',
        confidence,
        impact: deviation > 1 ? 'high' : deviation > 0.5 ? 'medium' : 'low'
      }
    }).filter(item => item.count >= 2) as MoodCorrelation[]

    // Activity insights from mood timing and changes
    const activityInsights: ActivityInsight[] = []
    
    // Analyze mood changes after common activities mentioned in journal entries
    const commonActivities = ['exercise', 'meditation', 'social', 'work', 'sleep', 'creative', 'nature', 'reading']
    
    commonActivities.forEach(activity => {
      const relatedEntries = entries.filter(entry => 
        entry.content.toLowerCase().includes(activity) || 
        entry.keywords.includes(activity)
      )
      
      if (relatedEntries.length >= 3) {
        const beforeMoods: number[] = []
        const afterMoods: number[] = []
        
        relatedEntries.forEach(entry => {
          const entryTime = entry.timestamp
          const beforeMood = moods.find(m => m.timestamp <= entryTime && (entryTime - m.timestamp) <= 3 * 60 * 60 * 1000)
          const afterMood = moods.find(m => m.timestamp >= entryTime && (m.timestamp - entryTime) <= 3 * 60 * 60 * 1000)
          
          if (beforeMood && afterMood) {
            beforeMoods.push(moodValues[beforeMood.mood])
            afterMoods.push(moodValues[afterMood.mood])
          }
        })
        
        if (beforeMoods.length >= 2) {
          const avgBefore = beforeMoods.reduce((a, b) => a + b, 0) / beforeMoods.length
          const avgAfter = afterMoods.reduce((a, b) => a + b, 0) / afterMoods.length
          const improvement = avgAfter - avgBefore
          
          let recommendation = ''
          if (improvement > 0.5) {
            recommendation = `${activity} consistently improves your mood - consider making it a regular practice`
          } else if (improvement < -0.5) {
            recommendation = `${activity} might be draining for you - consider modifying your approach or timing`
          } else {
            recommendation = `${activity} has a neutral effect - focus on activities that boost your mood more`
          }
          
          activityInsights.push({
            activity,
            averageMoodBefore: avgBefore,
            averageMoodAfter: avgAfter,
            improvement,
            frequency: relatedEntries.length,
            recommendation
          })
        }
      }
    })

    const allCorrelations = [...dayCorrelations, ...timeCorrelations, ...energyCorrelations, ...triggerAnalysis, ...contextAnalysis]
      .sort((a, b) => {
        // Sort by impact first, then by confidence, then by deviation from neutral
        if (a.impact !== b.impact) {
          const impactOrder = { high: 3, medium: 2, low: 1 }
          return impactOrder[b.impact] - impactOrder[a.impact]
        }
        if (Math.abs(a.confidence - b.confidence) > 0.1) {
          return b.confidence - a.confidence
        }
        return Math.abs(b.value - 3) - Math.abs(a.value - 3)
      })
      .slice(0, 8)

    return { 
      correlations: allCorrelations, 
      activityInsights: activityInsights.sort((a, b) => Math.abs(b.improvement) - Math.abs(a.improvement)).slice(0, 5),
      triggerAnalysis: triggerAnalysis.sort((a, b) => b.confidence - a.confidence).slice(0, 4)
    }
  }, [moods, entries])

  if (correlations.length === 0 && activityInsights.length === 0) {
    return (
      <Card>
        <CardContent className="p-6 text-center">
          <ChartBar className="mx-auto text-muted-foreground mb-4" size={48} />
          <h3 className="text-lg font-semibold mb-2">Building Correlations</h3>
          <p className="text-muted-foreground">
            Log more moods and journal entries to discover patterns and activity correlations.
          </p>
        </CardContent>
      </Card>
    )
  }

  const getValueColor = (value: number) => {
    if (value >= 4) return 'text-green-600 bg-green-50'
    if (value >= 3.5) return 'text-blue-600 bg-blue-50'
    if (value >= 2.5) return 'text-yellow-600 bg-yellow-50'
    return 'text-red-600 bg-red-50'
  }

  const getBarWidth = (value: number) => {
    return `${(value / 5) * 100}%`
  }

  const getImpactBadgeColor = (impact: string) => {
    switch (impact) {
      case 'high': return 'destructive'
      case 'medium': return 'default'
      case 'low': return 'secondary'
      default: return 'outline'
    }
  }

  const getImprovementColor = (improvement: number) => {
    if (improvement > 0.5) return 'text-green-600 bg-green-50'
    if (improvement > 0) return 'text-blue-600 bg-blue-50'
    if (improvement > -0.5) return 'text-yellow-600 bg-yellow-50'
    return 'text-red-600 bg-red-50'
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.4 }}
    >
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <ChartBar className="text-indigo-600" size={24} />
            Mood Correlations & Activity Insights
          </CardTitle>
          <p className="text-sm text-muted-foreground">
            Discover how different factors and activities influence your emotional well-being
          </p>
        </CardHeader>
        <CardContent>
          <Tabs value={selectedTab} onValueChange={setSelectedTab} className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="patterns" className="flex items-center gap-2">
                <ChartBar size={16} />
                Patterns
              </TabsTrigger>
              <TabsTrigger value="activities" className="flex items-center gap-2">
                <Pulse size={16} />
                Activities
              </TabsTrigger>
              <TabsTrigger value="triggers" className="flex items-center gap-2">
                <Target size={16} />
                Triggers
              </TabsTrigger>
            </TabsList>

            <TabsContent value="patterns" className="space-y-4 mt-6">
              {correlations.length > 0 ? (
                correlations.map((correlation, index) => (
                  <motion.div
                    key={`${correlation.type}-${correlation.label}`}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="space-y-3 p-4 border rounded-lg"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        {correlation.type === 'day' && <Calendar size={16} className="text-blue-600" />}
                        {correlation.type === 'time' && <Clock size={16} className="text-purple-600" />}
                        {correlation.type === 'energy' && <Pulse size={16} className="text-orange-600" />}
                        {correlation.type === 'trigger' && <Target size={16} className="text-red-600" />}
                        {correlation.type === 'context' && <Lightbulb size={16} className="text-green-600" />}
                        <span className="text-sm font-medium">{correlation.label}</span>
                        <Badge variant="outline" className="text-xs">
                          {correlation.count} entries
                        </Badge>
                        <Badge variant={getImpactBadgeColor(correlation.impact)} className="text-xs">
                          {correlation.impact} impact
                        </Badge>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge className={`text-xs ${getValueColor(correlation.value)}`}>
                          {correlation.value.toFixed(1)}/5
                        </Badge>
                        {correlation.trend === 'positive' && <TrendUp size={16} className="text-green-600" />}
                        {correlation.trend === 'negative' && <TrendDown size={16} className="text-red-600" />}
                      </div>
                    </div>
                    
                    <div className="relative h-2 bg-gray-100 rounded-full overflow-hidden">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: getBarWidth(correlation.value) }}
                        transition={{ delay: index * 0.1 + 0.2, duration: 0.5 }}
                        className={`h-full rounded-full ${
                          correlation.value >= 4 ? 'bg-green-500' :
                          correlation.value >= 3.5 ? 'bg-blue-500' :
                          correlation.value >= 2.5 ? 'bg-yellow-500' :
                          'bg-red-500'
                        }`}
                      />
                    </div>
                    
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-muted-foreground">
                        Confidence: {Math.round(correlation.confidence * 100)}%
                      </span>
                      <Progress value={correlation.confidence * 100} className="w-16 h-1" />
                    </div>
                    
                    {correlation.suggestion && (
                      <div className="bg-accent/10 p-3 rounded text-sm">
                        <span className="font-medium text-accent-foreground">💡 Insight: </span>
                        {correlation.suggestion}
                      </div>
                    )}
                  </motion.div>
                ))
              ) : (
                <div className="text-center text-muted-foreground py-8">
                  <ChartBar size={48} className="mx-auto mb-4 opacity-50" />
                  <p>Not enough data yet to show meaningful patterns.</p>
                  <p className="text-xs mt-2">Keep logging your moods to unlock insights!</p>
                </div>
              )}
            </TabsContent>

            <TabsContent value="activities" className="space-y-4 mt-6">
              {activityInsights.length > 0 ? (
                activityInsights.map((insight, index) => (
                  <motion.div
                    key={insight.activity}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="space-y-3 p-4 border rounded-lg"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Pulse size={16} className="text-blue-600" />
                        <span className="font-medium capitalize">{insight.activity}</span>
                        <Badge variant="outline" className="text-xs">
                          {insight.frequency} times
                        </Badge>
                      </div>
                      <Badge className={`text-xs ${getImprovementColor(insight.improvement)}`}>
                        {insight.improvement > 0 ? '+' : ''}{insight.improvement.toFixed(1)} mood points
                      </Badge>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div className="space-y-1">
                        <span className="text-muted-foreground">Before Activity</span>
                        <div className="flex items-center gap-2">
                          <Progress value={(insight.averageMoodBefore / 5) * 100} className="flex-1 h-2" />
                          <span className="font-medium">{insight.averageMoodBefore.toFixed(1)}/5</span>
                        </div>
                      </div>
                      <div className="space-y-1">
                        <span className="text-muted-foreground">After Activity</span>
                        <div className="flex items-center gap-2">
                          <Progress value={(insight.averageMoodAfter / 5) * 100} className="flex-1 h-2" />
                          <span className="font-medium">{insight.averageMoodAfter.toFixed(1)}/5</span>
                        </div>
                      </div>
                    </div>
                    
                    <div className="bg-accent/10 p-3 rounded text-sm">
                      <span className="font-medium text-accent-foreground">💡 Recommendation: </span>
                      {insight.recommendation}
                    </div>
                  </motion.div>
                ))
              ) : (
                <div className="text-center text-muted-foreground py-8">
                  <Pulse size={48} className="mx-auto mb-4 opacity-50" />
                  <p>Start journaling about your activities to discover their impact on your mood.</p>
                  <p className="text-xs mt-2">Mention activities like exercise, meditation, social time, etc.</p>
                </div>
              )}
            </TabsContent>

            <TabsContent value="triggers" className="space-y-4 mt-6">
              {triggerAnalysis.length > 0 ? (
                triggerAnalysis.map((trigger, index) => (
                  <motion.div
                    key={trigger.label}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="space-y-3 p-4 border rounded-lg"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Target size={16} className="text-red-600" />
                        <span className="font-medium">{trigger.label}</span>
                        <Badge variant="outline" className="text-xs">
                          {trigger.count} occurrences
                        </Badge>
                        <Badge variant={getImpactBadgeColor(trigger.impact)} className="text-xs">
                          {trigger.impact} impact
                        </Badge>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge className={`text-xs ${getValueColor(trigger.value)}`}>
                          {trigger.value.toFixed(1)}/5
                        </Badge>
                        {trigger.trend === 'positive' && <TrendUp size={16} className="text-green-600" />}
                        {trigger.trend === 'negative' && <TrendDown size={16} className="text-red-600" />}
                      </div>
                    </div>
                    
                    <div className="relative h-2 bg-gray-100 rounded-full overflow-hidden">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: getBarWidth(trigger.value) }}
                        transition={{ delay: index * 0.1 + 0.2, duration: 0.5 }}
                        className={`h-full rounded-full ${
                          trigger.value >= 4 ? 'bg-green-500' :
                          trigger.value >= 3.5 ? 'bg-blue-500' :
                          trigger.value >= 2.5 ? 'bg-yellow-500' :
                          'bg-red-500'
                        }`}
                      />
                    </div>
                    
                    {trigger.suggestion && (
                      <div className="bg-accent/10 p-3 rounded text-sm">
                        <span className="font-medium text-accent-foreground">💡 Strategy: </span>
                        {trigger.suggestion}
                      </div>
                    )}
                  </motion.div>
                ))
              ) : (
                <div className="text-center text-muted-foreground py-8">
                  <Target size={48} className="mx-auto mb-4 opacity-50" />
                  <p>Start logging mood triggers to understand what affects your emotional state.</p>
                  <p className="text-xs mt-2">Add triggers when logging your mood to unlock this analysis.</p>
                </div>
              )}
            </TabsContent>
          </Tabs>
          
          <div className="pt-4 mt-6 border-t text-xs text-muted-foreground">
            <p>💡 These insights help you understand what influences your mood so you can make informed decisions about your daily activities and routines.</p>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}