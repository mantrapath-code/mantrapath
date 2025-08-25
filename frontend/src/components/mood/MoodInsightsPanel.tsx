import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { 
  Sparkle, 
  ChatCircle, 
  Heart,
  TrendUp,
  Gift,
  ArrowRight,
  ArrowClockwise
} from '@phosphor-icons/react'
import { motion, AnimatePresence } from 'framer-motion'
import { toast } from 'sonner'
import { apiService } from '@/services/api'

interface FollowUpResponse {
  question: string
  options?: Array<{
    value: string
    label: string
  }>
  type: string
}

interface MoodInsights {
  follow_up_responses: FollowUpResponse[]
  celebration_triggers: string[]
  adaptive_questions?: FollowUpResponse[]
  mood_score: number
  energy_level: number
  stress_level: number
}

interface MoodInsightsPanelProps {
  className?: string
  onResponseSelect?: (response: string, value: string) => void
  showCelebrations?: boolean
  autoRefresh?: boolean
}

export function MoodInsightsPanel({ 
  className = "",
  onResponseSelect,
  showCelebrations = true,
  autoRefresh = false
}: MoodInsightsPanelProps) {
  const [insights, setInsights] = useState<MoodInsights | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)

  const fetchMoodInsights = async () => {
    try {
      setIsLoading(true)
      setError(null)
      
      // Get the latest mood entry with insights using the correct endpoint
      const response = await apiService.getMoodEntries(1) // This should work
      
      if (response && response.length > 0) {
        const latestMood = response[0] as any // Use any to access additional fields
        
        // Debug log to see what we're getting
        console.log('Latest mood entry:', latestMood)
        
        setInsights({
          follow_up_responses: latestMood.follow_up_responses || [],
          celebration_triggers: latestMood.celebration_triggers || [],
          adaptive_questions: latestMood.adaptive_questions || [],
          mood_score: latestMood.mood_score,
          energy_level: latestMood.energy_level || 5,
          stress_level: latestMood.stress_level || 5
        })
        setLastUpdated(new Date())
      } else {
        setInsights(null)
      }
    } catch (err: any) {
      console.error('Failed to fetch mood insights:', err)
      setError('Unable to load mood insights. Please try again.')
      
      // More specific error handling
      if (err.status === 401) {
        setError('Please log in to view your mood insights.')
      } else if (err.status === 404) {
        setError('No mood data found. Track your mood to see insights!')
      } else {
        setError('Unable to load mood insights. Please try again.')
      }
    } finally {
      setIsLoading(false)
    }
  }

  const handleQuestionResponse = (question: string, value: string) => {
    onResponseSelect?.(question, value)
    toast.success('Response recorded!', {
      description: 'Thank you for your additional insight.'
    })
  }

  const handleCelebrationAcknowledge = (trigger: string) => {
    toast.success('🎉 Celebration acknowledged!', {
      description: `Great job on: ${trigger.replace('_', ' ')}`
    })
  }

  useEffect(() => {
    fetchMoodInsights()
    
    // Auto-refresh every 2 minutes if enabled
    let interval: NodeJS.Timeout | null = null
    if (autoRefresh) {
      interval = setInterval(fetchMoodInsights, 2 * 60 * 1000)
    }
    
    return () => {
      if (interval) {
        clearInterval(interval)
      }
    }
  }, [autoRefresh])

  const formatRelativeTime = (date: Date) => {
    const now = new Date()
    const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60))
    
    if (diffInMinutes < 1) return 'Just now'
    if (diffInMinutes < 60) return `${diffInMinutes}m ago`
    const diffInHours = Math.floor(diffInMinutes / 60)
    if (diffInHours < 24) return `${diffInHours}h ago`
    const diffInDays = Math.floor(diffInHours / 24)
    return `${diffInDays}d ago`
  }

  const getCelebrationIcon = (trigger: string) => {
    if (trigger.includes('mood')) return Heart
    if (trigger.includes('stress')) return TrendUp
    if (trigger.includes('energy')) return Sparkle
    return Gift
  }

  const getCelebrationMessage = (trigger: string) => {
    const messages = {
      'high_mood_celebration': 'Your mood is shining bright! 🌟',
      'stress_management_success': 'Great stress management! 🧘‍♀️',
      'energy_boost_achievement': 'Your energy is amazing today! ⚡',
      'consistency_milestone': 'Fantastic tracking consistency! 📊',
      'improvement_streak': 'You\'re on an improvement streak! 🚀',
      'emotional_balance': 'Beautiful emotional balance! ⚖️'
    }
    return messages[trigger as keyof typeof messages] || `Celebrating: ${trigger.replace(/_/g, ' ')}! 🎉`
  }

  if (isLoading) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <ChatCircle className="animate-pulse" size={20} />
            <span>Mood Insights</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <Skeleton className="h-4 w-3/4" />
          <Skeleton className="h-4 w-1/2" />
          <div className="flex gap-2">
            <Skeleton className="h-8 w-24" />
            <Skeleton className="h-8 w-32" />
          </div>
        </CardContent>
      </Card>
    )
  }

  if (error) {
    return (
      <Card className={className}>
        <CardContent className="p-6">
          <Alert>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
          <Button 
            onClick={fetchMoodInsights} 
            className="mt-4 w-full"
            variant="outline"
          >
            <ArrowClockwise size={16} className="mr-2" />
            Try Again
          </Button>
        </CardContent>
      </Card>
    )
  }

  if (!insights || (insights.follow_up_responses.length === 0 && insights.celebration_triggers.length === 0)) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <ChatCircle size={20} />
            <span>Mood Insights</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-gray-500 text-center py-8">
            Track your mood to see personalized insights and celebrations! 🌟
          </p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <ChatCircle size={20} />
            <span>Mood Insights</span>
          </div>
          <div className="flex items-center gap-2">
            {lastUpdated && (
              <Badge variant="outline" className="text-xs">
                {formatRelativeTime(lastUpdated)}
              </Badge>
            )}
            <Button
              variant="ghost"
              size="sm"
              onClick={fetchMoodInsights}
              disabled={isLoading}
            >
              <ArrowClockwise size={14} className={isLoading ? 'animate-spin' : ''} />
            </Button>
          </div>
        </CardTitle>
      </CardHeader>

      <CardContent className="space-y-6">
        <AnimatePresence mode="wait">
          {/* Celebrations */}
          {showCelebrations && insights.celebration_triggers.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="space-y-3"
            >
              <h4 className="flex items-center gap-2 text-sm font-medium text-gray-700">
                <Sparkle size={16} className="text-yellow-500" />
                Celebrations
              </h4>
              <div className="space-y-2">
                {insights.celebration_triggers.map((trigger, index) => {
                  const CelebrationIcon = getCelebrationIcon(trigger)
                  return (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, scale: 0.95 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: index * 0.1 }}
                      className="p-3 bg-gradient-to-r from-yellow-50 to-orange-50 border border-yellow-200 rounded-lg"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <CelebrationIcon size={20} className="text-yellow-600" />
                          <span className="text-sm font-medium text-gray-800">
                            {getCelebrationMessage(trigger)}
                          </span>
                        </div>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => handleCelebrationAcknowledge(trigger)}
                          className="text-yellow-600 hover:text-yellow-700"
                        >
                          <Heart size={16} />
                        </Button>
                      </div>
                    </motion.div>
                  )
                })}
              </div>
            </motion.div>
          )}

          {/* Follow-up Questions */}
          {insights.follow_up_responses.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="space-y-3"
            >
              <h4 className="flex items-center gap-2 text-sm font-medium text-gray-700">
                <ChatCircle size={16} className="text-blue-500" />
                Quick Check-in
              </h4>
              <div className="space-y-3">
                {insights.follow_up_responses.map((response, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.15 }}
                    className="p-4 bg-blue-50 border border-blue-200 rounded-lg"
                  >
                    <p className="text-sm font-medium text-gray-800 mb-3">
                      {response.question}
                    </p>
                    {response.options && response.options.length > 0 ? (
                      <div className="space-y-2">
                        {response.options.map((option, optionIndex) => (
                          <Button
                            key={optionIndex}
                            variant="outline"
                            size="sm"
                            onClick={() => handleQuestionResponse(response.question, option.value)}
                            className="w-full text-left justify-start text-sm"
                          >
                            <span>{option.label}</span>
                            <ArrowRight size={14} className="ml-auto" />
                          </Button>
                        ))}
                      </div>
                    ) : (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleQuestionResponse(response.question, 'acknowledged')}
                        className="text-sm"
                      >
                        Thanks for asking! <ArrowRight size={14} className="ml-2" />
                      </Button>
                    )}
                  </motion.div>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </CardContent>
    </Card>
  )
}
