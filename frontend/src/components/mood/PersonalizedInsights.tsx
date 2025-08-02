/**
 * Personalized Insights Component - Enhanced weekly mood insights and smart notifications
 * 
 * Features:
 * - Personalized weekly mood insights with actionable recommendations
 * - Smart notification scheduling based on optimal intervention times
 * - Community-informed recommendations
 * - Adaptive notifications that learn from user patterns
 */

import { useState, useEffect, useCallback } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Switch } from '@/components/ui/switch'
import { 
  Brain,
  Bell,
  TrendUp,
  TrendDown,
  Target,
  Clock,
  Star,
  CheckCircle,
  Warning,
  Calendar,
  Lightning,
  Heart,
  Users,
  Gear,
  Sparkle
} from '@phosphor-icons/react'
import { motion, AnimatePresence } from 'framer-motion'
import { toast } from 'sonner'
import { apiService } from '@/services/api'
import { formatRelativeTime } from '@/utils/timeFormat'

interface PersonalizedInsight {
  id: string
  type: string
  title: string
  description: string
  actionable: string
  priority: string
  category: string
}

interface Recommendation {
  id: string
  title: string
  description: string
  actions: string[]
  estimated_time: string
  expected_benefit: string
}

interface OptimalTime {
  time_of_day: string
  average_mood: number
  recommendation: string
  effectiveness_score: number
}

interface WeeklySummary {
  current_week_score: number
  previous_weeks_score: number
  trend: string
  improvement_areas: string[]
  total_entries: number
  days_tracked_this_week: number
}

interface NotificationTime {
  hour: number
  day_of_week: number | null
  effectiveness_score: number
  notification_type: string
  reason: string
  average_mood_at_time?: number
  sample_size?: number
}

export function PersonalizedInsights() {
  const [insights, setInsights] = useState<PersonalizedInsight[]>([])
  const [recommendations, setRecommendations] = useState<Recommendation[]>([])
  const [optimalTimes, setOptimalTimes] = useState<OptimalTime[]>([])
  const [weeklySummary, setWeeklySummary] = useState<WeeklySummary | null>(null)
  const [notificationTimes, setNotificationTimes] = useState<NotificationTime[]>([])
  const [notificationsEnabled, setNotificationsEnabled] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)

  const loadPersonalizedInsights = useCallback(async () => {
    setLoading(true)
    setError(null)
    
    try {
      const insightsData = await apiService.getPersonalizedInsights()
      
      setInsights(insightsData.insights || [])
      setRecommendations(insightsData.recommendations || [])
      setOptimalTimes(insightsData.optimal_times || [])
      setWeeklySummary(insightsData.weekly_summary || null)
      setLastUpdated(new Date())
      
    } catch (err) {
      console.error('Failed to load personalized insights:', err)
      setError('Unable to load personalized insights. Using local analysis.')
      
      // Fallback to basic insights
      setInsights([
        {
          id: 'welcome',
          type: 'info',
          title: 'Building Your Insights',
          description: 'Continue logging your moods to unlock personalized recommendations.',
          actionable: 'Log your mood daily to see patterns and get tailored advice.',
          priority: 'medium',
          category: 'onboarding'
        }
      ])
    } finally {
      setLoading(false)
    }
  }, [])

  const loadOptimalNotificationTimes = useCallback(async () => {
    try {
      const timingData = await apiService.getOptimalNotificationTimes()
      setNotificationTimes(timingData.optimal_times || [])
      
      // Check if user has notifications enabled
      const hasScheduledNotifications = timingData.optimal_times.length > 0
      setNotificationsEnabled(hasScheduledNotifications)
      
    } catch (err) {
      console.error('Failed to load optimal notification times:', err)
      // Set default notification times
      setNotificationTimes([
        {
          hour: 9,
          day_of_week: null,
          effectiveness_score: 7.5,
          notification_type: 'morning_check',
          reason: 'Morning check-ins help set a positive tone for the day'
        },
        {
          hour: 15,
          day_of_week: null,
          effectiveness_score: 8.0,
          notification_type: 'afternoon_support',
          reason: 'Afternoon energy dips are common - perfect for gentle reminders'
        }
      ])
    }
  }, [])

  const scheduleSmartNotifications = useCallback(async () => {
    try {
      const response = await fetch('/api/notify/schedule-smart-notifications', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('mantrapath_token')}`
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        setNotificationsEnabled(true)
        toast.success('Smart notifications scheduled! 🔔', {
          description: data.message
        })
        return data
      } else {
        throw new Error('Failed to schedule notifications')
      }
    } catch (error) {
      console.error('Error scheduling smart notifications:', error)
      toast.error('Unable to schedule notifications. Please try again.')
      return null
    }
  }, [])

  const toggleNotifications = useCallback(async (enabled: boolean) => {
    if (enabled) {
      await scheduleSmartNotifications()
    } else {
      setNotificationsEnabled(false)
      toast.success('Notifications disabled')
    }
  }, [scheduleSmartNotifications])

  useEffect(() => {
    loadPersonalizedInsights()
    loadOptimalNotificationTimes()
  }, [loadPersonalizedInsights, loadOptimalNotificationTimes])

  const getInsightIcon = (type: string) => {
    switch (type) {
      case 'achievement': return <Star className="w-5 h-5 text-yellow-500" />
      case 'support': return <Heart className="w-5 h-5 text-blue-500" />
      case 'pattern': return <Brain className="w-5 h-5 text-purple-500" />
      case 'warning': return <Warning className="w-5 h-5 text-red-500" />
      default: return <Sparkle className="w-5 h-5 text-green-500" />
    }
  }

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'improving': return <TrendUp className="w-5 h-5 text-green-500" />
      case 'declining': return <TrendDown className="w-5 h-5 text-red-500" />
      default: return <div className="w-5 h-5 bg-gray-400 rounded-full" />
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

  const formatTime = (hour: number) => {
    const time = new Date()
    time.setHours(hour, 0, 0, 0)
    return time.toLocaleTimeString('en-US', { 
      hour: 'numeric', 
      minute: '2-digit',
      hour12: true 
    })
  }

  if (loading && !insights.length) {
    return (
      <div className="space-y-6">
        <Card>
          <CardContent className="p-6 text-center">
            <Brain className="mx-auto text-muted-foreground mb-4 animate-pulse" size={48} />
            <h3 className="text-lg font-semibold mb-2">Generating Your Insights</h3>
            <p className="text-muted-foreground">
              Analyzing your mood patterns to create personalized recommendations...
            </p>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Weekly Summary */}
      {weeklySummary && (
        <Card className="border-2 border-primary/20">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="flex items-center gap-2">
                  {getTrendIcon(weeklySummary.trend)}
                  Weekly Summary
                </CardTitle>
                <CardDescription>
                  Your personalized mood insights for this week
                </CardDescription>
              </div>
              {lastUpdated && (
                <div className="text-sm text-muted-foreground">
                  Updated {formatRelativeTime(lastUpdated.getTime())}
                </div>
              )}
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-primary">
                  {weeklySummary.current_week_score}/10
                </div>
                <div className="text-sm text-muted-foreground">Current Week</div>
              </div>
              <div className="text-center">
                <div className={`text-2xl font-bold ${
                  weeklySummary.trend === 'improving' ? 'text-green-500' :
                  weeklySummary.trend === 'declining' ? 'text-red-500' : 'text-yellow-500'
                }`}>
                  {weeklySummary.trend === 'improving' ? '+' : weeklySummary.trend === 'declining' ? '-' : ''}
                  {Math.abs(weeklySummary.current_week_score - weeklySummary.previous_weeks_score).toFixed(1)}
                </div>
                <div className="text-sm text-muted-foreground capitalize">{weeklySummary.trend}</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-500">
                  {weeklySummary.days_tracked_this_week}
                </div>
                <div className="text-sm text-muted-foreground">Days Tracked</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-500">
                  {weeklySummary.total_entries}
                </div>
                <div className="text-sm text-muted-foreground">Total Entries</div>
              </div>
            </div>
            
            {weeklySummary.improvement_areas.length > 0 && (
              <div className="mt-4">
                <h4 className="font-medium text-sm mb-2">Focus Areas</h4>
                <div className="flex flex-wrap gap-2">
                  {weeklySummary.improvement_areas.map((area) => (
                    <Badge key={area} variant="outline">
                      {area}s need extra care
                    </Badge>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Personalized Insights */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="text-primary" size={20} />
            Personalized Insights
          </CardTitle>
          <CardDescription>
            AI-powered insights based on your unique patterns and community data
          </CardDescription>
        </CardHeader>
        <CardContent>
          {insights.length > 0 ? (
            <div className="space-y-4">
              {insights.map((insight, index) => (
                <motion.div
                  key={insight.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <Card className={`p-4 ${
                    insight.priority === 'high' ? 'border-red-200 bg-red-50/50' :
                    insight.priority === 'medium' ? 'border-yellow-200 bg-yellow-50/50' :
                    'border-green-200 bg-green-50/50'
                  }`}>
                    <div className="flex items-start gap-3">
                      {getInsightIcon(insight.type)}
                      <div className="flex-1">
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-semibold">{insight.title}</h4>
                          <Badge variant={getPriorityColor(insight.priority)}>
                            {insight.priority}
                          </Badge>
                        </div>
                        <p className="text-sm text-muted-foreground mb-2">
                          {insight.description}
                        </p>
                        <div className="p-3 bg-white/60 rounded border-l-4 border-primary">
                          <p className="text-sm font-medium">💡 Action: {insight.actionable}</p>
                        </div>
                      </div>
                    </div>
                  </Card>
                </motion.div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-muted-foreground">
              <Brain size={48} className="mx-auto mb-4 opacity-50" />
              <h4 className="font-medium mb-2">No Insights Yet</h4>
              <p className="text-sm">
                Keep logging your moods to unlock personalized insights and recommendations.
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Smart Notifications */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Bell className="text-primary" size={20} />
                Smart Notifications
              </CardTitle>
              <CardDescription>
                Personalized reminders at optimal times based on your patterns
              </CardDescription>
            </div>
            <Switch
              checked={notificationsEnabled}
              onCheckedChange={toggleNotifications}
            />
          </div>
        </CardHeader>
        <CardContent>
          {notificationTimes.length > 0 ? (
            <div className="space-y-4">
              <div className="grid gap-3">
                {notificationTimes.slice(0, 3).map((time, index) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
                    <div className="flex items-center gap-3">
                      <Clock size={20} className="text-primary" />
                      <div>
                        <div className="font-medium">
                          {formatTime(time.hour)}
                          {time.day_of_week !== null && (
                            <span className="text-sm text-muted-foreground ml-2">
                              on {['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][time.day_of_week]}s
                            </span>
                          )}
                        </div>
                        <div className="text-sm text-muted-foreground">
                          {time.reason}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant="outline">
                        {(time.effectiveness_score || 0).toFixed(1)}/10 effectiveness
                      </Badge>
                      <Badge variant="secondary" className="capitalize">
                        {(time.notification_type || 'general').replace('_', ' ')}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
              
              {!notificationsEnabled && (
                <div className="text-center p-4 bg-blue-50 rounded-lg border border-blue-200">
                  <Bell size={32} className="mx-auto mb-2 text-blue-500" />
                  <p className="text-sm font-medium text-blue-700 mb-2">
                    Enable Smart Notifications
                  </p>
                  <p className="text-sm text-blue-600 mb-3">
                    Get personalized wellness reminders at times when you're most likely to benefit from them.
                  </p>
                  <Button onClick={() => toggleNotifications(true)} size="sm">
                    Enable Now
                  </Button>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-8 text-muted-foreground">
              <Bell size={48} className="mx-auto mb-4 opacity-50" />
              <h4 className="font-medium mb-2">Learning Your Patterns</h4>
              <p className="text-sm mb-4">
                We need a few more mood entries to find your optimal notification times.
              </p>
              <Button onClick={loadOptimalNotificationTimes} variant="outline">
                Check Again
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Actionable Recommendations */}
      {recommendations.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Target className="text-primary" size={20} />
              Personalized Recommendations
            </CardTitle>
            <CardDescription>
              Tailored actions based on your patterns and community insights
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-2">
              {recommendations.map((rec, index) => (
                <motion.div
                  key={rec.id}
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <Card className="p-4 h-full">
                    <div className="space-y-3">
                      <div>
                        <h4 className="font-semibold mb-1">{rec.title}</h4>
                        <p className="text-sm text-muted-foreground">{rec.description}</p>
                      </div>
                      
                      <div className="space-y-2">
                        <h5 className="text-sm font-medium">Action Steps:</h5>
                        <ul className="space-y-1">
                          {rec.actions.map((action, actionIndex) => (
                            <li key={actionIndex} className="flex items-start gap-2 text-sm">
                              <CheckCircle size={16} className="text-green-500 mt-0.5 flex-shrink-0" />
                              {action}
                            </li>
                          ))}
                        </ul>
                      </div>
                      
                      <div className="flex items-center justify-between text-sm">
                        <div className="flex items-center gap-1 text-muted-foreground">
                          <Clock size={14} />
                          {rec.estimated_time}
                        </div>
                        <div className="flex items-center gap-1 text-green-600">
                          <Lightning size={14} />
                          {rec.expected_benefit}
                        </div>
                      </div>
                    </div>
                  </Card>
                </motion.div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Optimal Times for Activities */}
      {optimalTimes.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calendar className="text-primary" size={20} />
              Your Optimal Times
            </CardTitle>
            <CardDescription>
              When to focus on wellness activities for maximum impact
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-3 md:grid-cols-2">
              {optimalTimes.map((time, index) => (
                <div key={index} className="p-3 bg-gradient-to-r from-primary/10 to-purple-500/10 rounded-lg border">
                  <div className="flex items-center justify-between mb-2">
                    <div className="font-medium capitalize">{time.time_of_day}</div>
                    <Progress value={time.effectiveness_score * 10} className="w-20" />
                  </div>
                  <p className="text-sm text-muted-foreground mb-1">
                    Avg mood: {time.average_mood.toFixed(1)}/10
                  </p>
                  <p className="text-sm">{time.recommendation}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {error && (
        <Card className="border-yellow-200 bg-yellow-50">
          <CardContent className="p-4">
            <div className="flex items-center gap-2 text-yellow-700">
              <Warning size={20} />
              <span className="font-medium">Limited Connectivity</span>
            </div>
            <p className="text-sm text-yellow-600 mt-1">
              {error} Some features may be limited.
            </p>
          </CardContent>
        </Card>
      )}

    </div>
  )
}
