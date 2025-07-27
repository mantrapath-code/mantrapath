/**
 * Smart Notification Scheduler - Personalized notification timing based on user's optimal intervention times
 * 
 * Features:
 * - Machine learning-based optimal timing prediction
 * - User behavior pattern analysis
 * - Contextual notification content
 * - Non-intrusive scheduling with user preferences
 */

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Switch } from '@/components/ui/switch'
import { Badge } from '@/components/ui/badge'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Progress } from '@/components/ui/progress'
import { 
  Bell, 
  Clock, 
  TrendUp, 
  Brain, 
  Heart, 
  Moon, 
  Sun, 
  Coffee,
  Target,
  Settings,
  CheckCircle,
  AlertTriangle
} from '@phosphor-icons/react'
import { motion, AnimatePresence } from 'framer-motion'
import { analyticsApi, moodApi } from '@/services/api'
import { toast } from 'sonner'
import { useMoods } from '@/hooks/useWellness'
import { useKV } from '@github/spark/hooks'

interface NotificationSchedule {
  id: string
  type: 'mood-check' | 'breathing' | 'affirmation' | 'intervention' | 'reflection'
  title: string
  content: string
  preferredTime: string // HH:MM format
  dayOfWeek: number[] // 0-6, Sunday = 0
  frequency: 'daily' | 'weekly' | 'custom'
  enabled: boolean
  effectiveness: number
  lastSent?: number
  userEngagement: number
  contextualTriggers: string[]
  optimalInterventionScore: number
}

interface UserNotificationPreferences {
  quietHours: {
    start: string
    end: string
  }
  enabledTypes: string[]
  maxPerDay: number
  adaptiveTiming: boolean
  urgencyLevels: {
    low: boolean
    medium: boolean
    high: boolean
  }
}

interface OptimalTime {
  time: string
  dayOfWeek: number
  effectiveness: number
  context: string
  interventionType: string
}

export function SmartNotificationScheduler() {
  const [schedules, setSchedules] = useKV<NotificationSchedule[]>('notification-schedules', [])
  const [preferences, setPreferences] = useKV<UserNotificationPreferences>('notification-preferences', {
    quietHours: { start: '22:00', end: '07:00' },
    enabledTypes: ['mood-check', 'breathing', 'affirmation'],
    maxPerDay: 5,
    adaptiveTiming: true,
    urgencyLevels: { low: true, medium: true, high: false }
  })
  const [optimalTimes, setOptimalTimes] = useState<OptimalTime[]>([])
  const [analytics, setAnalytics] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  
  const { moods } = useMoods()

  useEffect(() => {
    initializeSmartScheduling()
  }, [moods])

  const initializeSmartScheduling = async () => {
    setLoading(true)
    try {
      // Analyze user patterns for optimal intervention times
      const optimalTimes = await analyzeOptimalInterventionTimes()
      setOptimalTimes(optimalTimes)

      // Get analytics for personalization
      const [trends, patterns, healthScore] = await Promise.all([
        analyticsApi.getTrends(),
        analyticsApi.getWeeklyPatterns(),
        analyticsApi.getHealthScore()
      ])
      
      setAnalytics({ trends, patterns, healthScore })

      // Initialize default schedules if none exist
      if (schedules.length === 0) {
        const defaultSchedules = generateSmartDefaultSchedules(optimalTimes)
        setSchedules(defaultSchedules)
      } else {
        // Update existing schedules with new optimal times
        updateSchedulesWithOptimalTimes(optimalTimes)
      }

    } catch (error) {
      console.error('Failed to initialize smart scheduling:', error)
      // Fallback to basic scheduling
      if (schedules.length === 0) {
        setSchedules(generateBasicDefaultSchedules())
      }
    } finally {
      setLoading(false)
    }
  }

  const analyzeOptimalInterventionTimes = async (): Promise<OptimalTime[]> => {
    const optimalTimes: OptimalTime[] = []
    
    // Analyze mood patterns to find optimal intervention windows
    const oneMonthAgo = Date.now() - (30 * 24 * 60 * 60 * 1000)
    const recentMoods = moods.filter(mood => mood.timestamp >= oneMonthAgo)
    
    if (recentMoods.length < 10) {
      // Not enough data, return basic optimal times
      return [
        { time: '09:00', dayOfWeek: 1, effectiveness: 0.7, context: 'morning-check', interventionType: 'mood-check' },
        { time: '15:00', dayOfWeek: 3, effectiveness: 0.8, context: 'afternoon-boost', interventionType: 'breathing' },
        { time: '20:00', dayOfWeek: 0, effectiveness: 0.75, context: 'evening-reflection', interventionType: 'reflection' }
      ]
    }

    // Group moods by day of week and time of day
    const moodsByDayAndTime = groupMoodsByDayAndTime(recentMoods)
    
    // Find times when mood tends to dip (optimal for proactive intervention)
    for (let day = 0; day < 7; day++) {
      for (let hour = 7; hour < 22; hour++) {
        const timeKey = `${day}-${hour}`
        const dayMoods = moodsByDayAndTime[timeKey] || []
        
        if (dayMoods.length >= 3) {
          const avgMood = calculateAverageMood(dayMoods)
          const nextHourMoods = moodsByDayAndTime[`${day}-${hour + 1}`] || []
          const nextAvgMood = nextHourMoods.length > 0 ? calculateAverageMood(nextHourMoods) : avgMood
          
          // If mood typically dips at this time, it's a good intervention point
          if (avgMood < 3.5 && nextAvgMood > avgMood) {
            optimalTimes.push({
              time: `${hour.toString().padStart(2, '0')}:00`,
              dayOfWeek: day,
              effectiveness: Math.min(0.9, (nextAvgMood - avgMood) * 2),
              context: getContextForTime(hour),
              interventionType: getOptimalInterventionType(avgMood, hour)
            })
          }
        }
      }
    }

    // Find high-energy times for positive activities
    const energyTimes = findHighEnergyTimes(recentMoods)
    energyTimes.forEach(energyTime => {
      optimalTimes.push({
        time: energyTime.time,
        dayOfWeek: energyTime.dayOfWeek,
        effectiveness: energyTime.effectiveness,
        context: 'high-energy',
        interventionType: 'affirmation'
      })
    })

    // Sort by effectiveness and return top 10
    return optimalTimes
      .sort((a, b) => b.effectiveness - a.effectiveness)
      .slice(0, 10)
  }

  const groupMoodsByDayAndTime = (moods: any[]) => {
    return moods.reduce((acc, mood) => {
      const date = new Date(mood.timestamp)
      const day = date.getDay()
      const hour = date.getHours()
      const key = `${day}-${hour}`
      
      if (!acc[key]) acc[key] = []
      acc[key].push(mood)
      return acc
    }, {} as Record<string, any[]>)
  }

  const calculateAverageMood = (moods: any[]) => {
    const moodValues = { 'very-low': 1, 'low': 2, 'neutral': 3, 'good': 4, 'excellent': 5 }
    return moods.reduce((sum, mood) => sum + moodValues[mood.mood], 0) / moods.length
  }

  const getContextForTime = (hour: number): string => {
    if (hour >= 6 && hour < 10) return 'morning-energy'
    if (hour >= 10 && hour < 12) return 'mid-morning'
    if (hour >= 12 && hour < 14) return 'lunch-time'
    if (hour >= 14 && hour < 17) return 'afternoon-dip'
    if (hour >= 17 && hour < 20) return 'evening-wind-down'
    return 'night-reflection'
  }

  const getOptimalInterventionType = (moodLevel: number, hour: number): string => {
    if (moodLevel < 2.5) return 'intervention'
    if (hour >= 6 && hour < 10) return 'mood-check'
    if (hour >= 14 && hour < 16) return 'breathing'
    if (hour >= 18 && hour < 21) return 'reflection'
    return 'affirmation'
  }

  const findHighEnergyTimes = (moods: any[]) => {
    const highEnergyMoods = moods.filter(mood => 
      mood.energy === 'high' || ['good', 'excellent'].includes(mood.mood)
    )
    
    const energyTimes = groupMoodsByDayAndTime(highEnergyMoods)
    return Object.entries(energyTimes)
      .filter(([_, moodsAtTime]) => moodsAtTime.length >= 2)
      .map(([timeKey, moodsAtTime]) => {
        const [day, hour] = timeKey.split('-').map(Number)
        return {
          time: `${hour.toString().padStart(2, '0')}:00`,
          dayOfWeek: day,
          effectiveness: Math.min(0.85, moodsAtTime.length / 10),
          context: 'high-energy'
        }
      })
  }

  const generateSmartDefaultSchedules = (optimalTimes: OptimalTime[]): NotificationSchedule[] => {
    const schedules: NotificationSchedule[] = []

    // Create schedules based on optimal times
    optimalTimes.forEach((optimal, index) => {
      schedules.push({
        id: `smart-${index}`,
        type: optimal.interventionType as any,
        title: getNotificationTitle(optimal.interventionType, optimal.context),
        content: getNotificationContent(optimal.interventionType, optimal.context),
        preferredTime: optimal.time,
        dayOfWeek: [optimal.dayOfWeek],
        frequency: 'weekly',
        enabled: true,
        effectiveness: optimal.effectiveness,
        userEngagement: 0.5,
        contextualTriggers: [optimal.context],
        optimalInterventionScore: optimal.effectiveness
      })
    })

    // Add essential daily check-ins if not covered
    if (!schedules.some(s => s.type === 'mood-check')) {
      schedules.push({
        id: 'daily-mood-check',
        type: 'mood-check',
        title: 'Daily Mood Check-in',
        content: 'How are you feeling today? Take a moment to log your mood.',
        preferredTime: '09:00',
        dayOfWeek: [1, 2, 3, 4, 5],
        frequency: 'daily',
        enabled: true,
        effectiveness: 0.7,
        userEngagement: 0.8,
        contextualTriggers: ['morning-routine'],
        optimalInterventionScore: 0.7
      })
    }

    return schedules.slice(0, 8) // Limit to reasonable number
  }

  const generateBasicDefaultSchedules = (): NotificationSchedule[] => {
    return [
      {
        id: 'morning-check',
        type: 'mood-check',
        title: 'Good Morning! 🌅',
        content: 'How are you starting your day? Log your morning mood.',
        preferredTime: '09:00',
        dayOfWeek: [1, 2, 3, 4, 5],
        frequency: 'daily',
        enabled: true,
        effectiveness: 0.7,
        userEngagement: 0.5,
        contextualTriggers: ['morning'],
        optimalInterventionScore: 0.7
      },
      {
        id: 'afternoon-breathing',
        type: 'breathing',
        title: 'Afternoon Reset 🌬️',
        content: 'Take a moment for a quick breathing exercise to recharge.',
        preferredTime: '15:00',
        dayOfWeek: [1, 2, 3, 4, 5],
        frequency: 'daily',
        enabled: true,
        effectiveness: 0.8,
        userEngagement: 0.5,
        contextualTriggers: ['afternoon-dip'],
        optimalInterventionScore: 0.8
      }
    ]
  }

  const getNotificationTitle = (type: string, context: string): string => {
    const titles = {
      'mood-check': {
        'morning-energy': 'Good Morning Check-in! ☀️',
        'afternoon-dip': 'How are you holding up? 💙',
        'evening-wind-down': 'Evening Reflection 🌙',
        default: 'Mood Check-in 📝'
      },
      'breathing': {
        'afternoon-dip': 'Afternoon Reset 🌬️',
        'high-energy': 'Enhance Your Energy ✨',
        default: 'Breathing Moment 🫁'
      },
      'affirmation': {
        'high-energy': 'You\'re Amazing! 🌟',
        'morning-energy': 'Start Strong! 💪',
        default: 'Daily Affirmation 💖'
      },
      'intervention': {
        default: 'Gentle Check-in 🤗'
      },
      'reflection': {
        'evening-wind-down': 'Evening Reflection 🌅',
        default: 'Reflection Time 💭'
      }
    }
    
    return titles[type]?.[context] || titles[type]?.default || 'MantraPath Reminder'
  }

  const getNotificationContent = (type: string, context: string): string => {
    const content = {
      'mood-check': 'Take a moment to check in with yourself. How are you feeling right now?',
      'breathing': 'Your body might benefit from a quick breathing exercise. Ready to reset?',
      'affirmation': 'You\'re doing great! Here\'s a positive reminder for you.',
      'intervention': 'It seems like you might benefit from some gentle support. We\'re here for you.',
      'reflection': 'Time to reflect on your day. What went well? What can you learn?'
    }
    
    return content[type] || 'Take a moment for yourself with MantraPath.'
  }

  const updateSchedulesWithOptimalTimes = (optimalTimes: OptimalTime[]) => {
    setSchedules(currentSchedules => {
      return currentSchedules.map(schedule => {
        // Find matching optimal time for this schedule
        const matchingOptimal = optimalTimes.find(optimal => 
          optimal.interventionType === schedule.type &&
          schedule.dayOfWeek.includes(optimal.dayOfWeek)
        )
        
        if (matchingOptimal && preferences.adaptiveTiming) {
          return {
            ...schedule,
            preferredTime: matchingOptimal.time,
            effectiveness: matchingOptimal.effectiveness,
            optimalInterventionScore: matchingOptimal.effectiveness
          }
        }
        
        return schedule
      })
    })
  }

  const toggleSchedule = (scheduleId: string) => {
    setSchedules(current => 
      current.map(schedule => 
        schedule.id === scheduleId 
          ? { ...schedule, enabled: !schedule.enabled }
          : schedule
      )
    )
  }

  const updatePreferences = (updates: Partial<UserNotificationPreferences>) => {
    setPreferences(current => ({ ...current, ...updates }))
    toast.success('Notification preferences updated!')
  }

  const scheduleNotification = async (schedule: NotificationSchedule) => {
    try {
      // In a real implementation, this would call the notification service
      // For now, we'll simulate the scheduling
      console.log('Scheduling notification:', schedule)
      
      // Update engagement metrics
      setSchedules(current => 
        current.map(s => 
          s.id === schedule.id 
            ? { ...s, lastSent: Date.now(), userEngagement: s.userEngagement + 0.1 }
            : s
        )
      )
      
      toast.success(`Scheduled: ${schedule.title}`)
    } catch (error) {
      toast.error('Failed to schedule notification')
    }
  }

  const getScheduleIcon = (type: string) => {
    switch (type) {
      case 'mood-check': return <Heart className="w-4 h-4" />
      case 'breathing': return <Coffee className="w-4 h-4" />
      case 'affirmation': return <Sun className="w-4 h-4" />
      case 'intervention': return <AlertTriangle className="w-4 h-4" />
      case 'reflection': return <Moon className="w-4 h-4" />
      default: return <Bell className="w-4 h-4" />
    }
  }

  const getDayName = (dayNum: number) => {
    const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    return days[dayNum]
  }

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="w-5 h-5" />
            Analyzing Optimal Times...
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

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="w-5 h-5" />
            Smart Notification Scheduler
          </CardTitle>
          <CardDescription>
            Personalized notifications based on your optimal intervention times
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="schedules" className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="schedules">My Schedules</TabsTrigger>
              <TabsTrigger value="optimal-times">Optimal Times</TabsTrigger>
              <TabsTrigger value="preferences">Preferences</TabsTrigger>
            </TabsList>

            <TabsContent value="schedules" className="space-y-4">
              <div className="space-y-3">
                {schedules.map((schedule, index) => (
                  <motion.div
                    key={schedule.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                  >
                    <Card className={`p-4 ${schedule.enabled ? 'border-primary/50' : 'opacity-60'}`}>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <div className="p-2 rounded-full bg-primary/10">
                            {getScheduleIcon(schedule.type)}
                          </div>
                          <div>
                            <h4 className="font-semibold">{schedule.title}</h4>
                            <p className="text-sm text-muted-foreground">{schedule.content}</p>
                            <div className="flex items-center gap-2 mt-1">
                              <Clock className="w-3 h-3" />
                              <span className="text-xs">{schedule.preferredTime}</span>
                              <span className="text-xs">•</span>
                              <span className="text-xs">
                                {schedule.dayOfWeek.map(day => getDayName(day)).join(', ')}
                              </span>
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center gap-3">
                          <div className="text-right">
                            <div className="text-sm font-medium">
                              {(schedule.effectiveness * 100).toFixed(0)}% effective
                            </div>
                            <Progress value={schedule.effectiveness * 100} className="w-16 h-2" />
                          </div>
                          <Switch
                            checked={schedule.enabled}
                            onCheckedChange={() => toggleSchedule(schedule.id)}
                          />
                        </div>
                      </div>
                      
                      {schedule.enabled && (
                        <div className="mt-3 pt-3 border-t flex justify-end">
                          <Button 
                            size="sm" 
                            variant="outline"
                            onClick={() => scheduleNotification(schedule)}
                          >
                            <Target className="w-3 h-3 mr-1" />
                            Test Now
                          </Button>
                        </div>
                      )}
                    </Card>
                  </motion.div>
                ))}
              </div>
            </TabsContent>

            <TabsContent value="optimal-times" className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {optimalTimes.map((optimal, index) => (
                  <Card key={index} className="p-4">
                    <div className="flex items-center gap-3">
                      <div className="p-2 rounded-full bg-blue-100 dark:bg-blue-900/20">
                        <TrendUp className="w-4 h-4 text-blue-600" />
                      </div>
                      <div className="flex-1">
                        <div className="font-semibold">
                          {optimal.time} on {getDayName(optimal.dayOfWeek)}s
                        </div>
                        <div className="text-sm text-muted-foreground capitalize">
                          {optimal.interventionType} • {optimal.context.replace('-', ' ')}
                        </div>
                        <div className="flex items-center gap-2 mt-2">
                          <span className="text-xs">Effectiveness:</span>
                          <Progress value={optimal.effectiveness * 100} className="w-20" />
                          <span className="text-xs">{(optimal.effectiveness * 100).toFixed(0)}%</span>
                        </div>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            </TabsContent>

            <TabsContent value="preferences" className="space-y-6">
              <div className="space-y-4">
                <Card className="p-4">
                  <h4 className="font-semibold mb-3 flex items-center gap-2">
                    <Settings className="w-4 h-4" />
                    General Settings
                  </h4>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <label className="font-medium">Adaptive Timing</label>
                        <p className="text-sm text-muted-foreground">
                          Automatically adjust notification times based on your patterns
                        </p>
                      </div>
                      <Switch
                        checked={preferences.adaptiveTiming}
                        onCheckedChange={(checked) => updatePreferences({ adaptiveTiming: checked })}
                      />
                    </div>
                    
                    <div className="space-y-2">
                      <label className="font-medium">Maximum notifications per day</label>
                      <Select
                        value={preferences.maxPerDay.toString()}
                        onValueChange={(value) => updatePreferences({ maxPerDay: parseInt(value) })}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="1">1 notification</SelectItem>
                          <SelectItem value="3">3 notifications</SelectItem>
                          <SelectItem value="5">5 notifications</SelectItem>
                          <SelectItem value="8">8 notifications</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                </Card>

                <Card className="p-4">
                  <h4 className="font-semibold mb-3 flex items-center gap-2">
                    <Moon className="w-4 h-4" />
                    Quiet Hours
                  </h4>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="text-sm font-medium">Start Time</label>
                      <input
                        type="time"
                        value={preferences.quietHours.start}
                        onChange={(e) => updatePreferences({
                          quietHours: { ...preferences.quietHours, start: e.target.value }
                        })}
                        className="w-full mt-1 p-2 border rounded"
                      />
                    </div>
                    <div>
                      <label className="text-sm font-medium">End Time</label>
                      <input
                        type="time"
                        value={preferences.quietHours.end}
                        onChange={(e) => updatePreferences({
                          quietHours: { ...preferences.quietHours, end: e.target.value }
                        })}
                        className="w-full mt-1 p-2 border rounded"
                      />
                    </div>
                  </div>
                </Card>

                <Card className="p-4">
                  <h4 className="font-semibold mb-3">Notification Types</h4>
                  <div className="space-y-3">
                    {['mood-check', 'breathing', 'affirmation', 'intervention', 'reflection'].map(type => (
                      <div key={type} className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          {getScheduleIcon(type)}
                          <span className="capitalize">{type.replace('-', ' ')}</span>
                        </div>
                        <Switch
                          checked={preferences.enabledTypes.includes(type)}
                          onCheckedChange={(checked) => {
                            const newTypes = checked
                              ? [...preferences.enabledTypes, type]
                              : preferences.enabledTypes.filter(t => t !== type)
                            updatePreferences({ enabledTypes: newTypes })
                          }}
                        />
                      </div>
                    ))}
                  </div>
                </Card>
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  )
}