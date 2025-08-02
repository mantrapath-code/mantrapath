/**
 * Enhanced Notification Scheduler Test Component
 * 
 * Tests smart notification functionality with ML integration
 * Includes pattern analysis, optimal timing, and personalized insights
 */

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Bell, Clock, CheckCircle, Play, Brain, Target, Sparkle, TrendUp, Lightning } from '@phosphor-icons/react'
import { toast } from 'sonner'

interface NotificationTiming {
  hour: number
  day_of_week: number | null
  effectiveness_score: number
  notification_type: string
  reason?: string
  confidence_level?: number
}

interface ScheduleResult {
  message: string
  optimal_times: NotificationTiming[]
  next_notification?: string
  ml_prediction?: boolean
}

interface MLAnalysisResult {
  user_id: string
  patterns: any
  analysis_timestamp: string
  data_points_analyzed: any
}

interface PersonalizedInsight {
  insight_type: string
  title: string
  content: string
  action_suggestions: string[]
  confidence_score: number
  priority: string
}

export function NotificationSchedulerTest() {
  const [isScheduling, setIsScheduling] = useState(false)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [isGeneratingInsights, setIsGeneratingInsights] = useState(false)
  const [isCalculatingTiming, setIsCalculatingTiming] = useState(false)
  
  const [scheduledNotifications, setScheduledNotifications] = useState<NotificationTiming[]>([])
  const [lastScheduleResult, setLastScheduleResult] = useState<ScheduleResult | null>(null)
  const [mlAnalysisResult, setMlAnalysisResult] = useState<MLAnalysisResult | null>(null)
  const [personalizedInsights, setPersonalizedInsights] = useState<PersonalizedInsight[]>([])

  const testSmartNotifications = async () => {
    setIsScheduling(true)
    
    try {
      // Test the smart notification scheduling
      const response = await fetch('/api/notify/schedule-smart-notifications', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('mantrapath_token')}`
        }
      })
      
      if (response.ok) {
        const result = await response.json()
        setLastScheduleResult(result)
        setScheduledNotifications(result.optimal_times || [])
        
        toast.success('Smart notifications scheduled! 🎉', {
          description: result.message
        })
      } else {
        const error = await response.json()
        throw new Error(error.message || 'Failed to schedule notifications')
      }
    } catch (error) {
      console.error('Error testing smart notifications:', error)
      toast.error('Failed to schedule notifications', {
        description: error.message
      })
    } finally {
      setIsScheduling(false)
    }
  }

  const testMLPatternAnalysis = async () => {
    setIsAnalyzing(true)
    
    try {
      const response = await fetch('/api/ml/analyze-patterns', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('mantrapath_token')}`
        },
        body: JSON.stringify({
          user_id: 'current_user',
          mood_entries: [],
          journal_entries: [],
          notification_responses: [],
          app_usage_patterns: [],
          contextual_data: {}
        })
      })
      
      if (response.ok) {
        const result = await response.json()
        setMlAnalysisResult(result)
        toast.success('ML Pattern Analysis Complete! 🧠', {
          description: 'AI has analyzed your behavior patterns'
        })
        console.log('ML Analysis Result:', result)
      } else {
        throw new Error('ML analysis failed')
      }
    } catch (error) {
      console.error('Error testing ML analysis:', error)
      toast.error('ML Analysis Failed', {
        description: error.message
      })
    } finally {
      setIsAnalyzing(false)
    }
  }

  const testPersonalizedInsights = async () => {
    setIsGeneratingInsights(true)
    
    try {
      const response = await fetch('/api/ml/personalized-insights/current_user', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('mantrapath_token')}`
        }
      })
      
      if (response.ok) {
        const result = await response.json()
        setPersonalizedInsights(result.insights || [])
        toast.success('AI Insights Generated! ✨', {
          description: 'Personalized wellness insights ready'
        })
        console.log('Personalized Insights:', result)
      } else {
        throw new Error('Insights generation failed')
      }
    } catch (error) {
      console.error('Error testing personalized insights:', error)
      toast.error('Insights Generation Failed', {
        description: error.message
      })
    } finally {
      setIsGeneratingInsights(false)
    }
  }

  const testOptimalTiming = async () => {
    setIsCalculatingTiming(true)
    
    try {
      const response = await fetch('/api/ml/optimal-times/current_user', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('mantrapath_token')}`
        }
      })
      
      if (response.ok) {
        const result = await response.json()
        setScheduledNotifications(result.optimal_times || [])
        toast.success('Optimal Times Calculated! ⏰', {
          description: `Found ${result.optimal_times?.length || 0} optimal notification windows`
        })
        console.log('Optimal Times:', result)
      } else {
        throw new Error('Optimal timing calculation failed')
      }
    } catch (error) {
      console.error('Error testing optimal timing:', error)
      toast.error('Optimal Timing Failed', {
        description: error.message
      })
    } finally {
      setIsCalculatingTiming(false)
    }
  }

  const testPatternNotification = async () => {
    try {
      const response = await fetch('/api/notify/mood-pattern', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('mantrapath_token')}`
        },
        body: JSON.stringify({
          user_id: 'test_user',
          pattern_type: 'positive_streak',
          pattern_data: {
            streak_days: 3
          }
        })
      })
      
      if (response.ok) {
        const result = await response.json()
        toast.success('Pattern notification sent! 📱', {
          description: 'Check your notifications panel'
        })
      } else {
        throw new Error('Failed to send pattern notification')
      }
    } catch (error) {
      console.error('Error sending pattern notification:', error)
      toast.error('Failed to send notification', {
        description: error.message
      })
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

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'bg-red-100 text-red-800 border-red-200'
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      case 'low': return 'bg-green-100 text-green-800 border-green-200'
      default: return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  return (
    <Card className="border-dashed border-2 border-blue-200 bg-blue-50/30">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Brain className="text-blue-500" size={20} />
          Smart Notification System with ML
        </CardTitle>
        <CardDescription>
          Test AI-powered notification scheduling, pattern analysis, and personalized insights
        </CardDescription>
      </CardHeader>
      
      <CardContent>
        <Tabs defaultValue="scheduling" className="w-full">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="scheduling">Scheduling</TabsTrigger>
            <TabsTrigger value="analysis">ML Analysis</TabsTrigger>
            <TabsTrigger value="insights">Insights</TabsTrigger>
            <TabsTrigger value="results">Results</TabsTrigger>
          </TabsList>
          
          <TabsContent value="scheduling" className="space-y-4 mt-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <Button 
                onClick={testSmartNotifications}
                disabled={isScheduling}
                className="flex items-center gap-2"
              >
                <Clock size={16} />
                {isScheduling ? 'Scheduling...' : 'Schedule Smart Notifications'}
              </Button>
              
              <Button 
                onClick={testOptimalTiming}
                disabled={isCalculatingTiming}
                variant="outline"
                className="flex items-center gap-2"
              >
                <Target size={16} />
                {isCalculatingTiming ? 'Calculating...' : 'Calculate Optimal Times'}
              </Button>
              
              <Button 
                onClick={testPatternNotification}
                variant="outline"
                className="flex items-center gap-2"
              >
                <Play size={16} />
                Test Pattern Alert
              </Button>
              
              <Button 
                onClick={testMLPatternAnalysis}
                disabled={isAnalyzing}
                variant="outline"
                className="flex items-center gap-2"
              >
                <Brain size={16} />
                {isAnalyzing ? 'Analyzing...' : 'ML Pattern Analysis'}
              </Button>
            </div>

            {lastScheduleResult && (
              <div className="space-y-3 mt-4">
                <div className="flex items-center gap-2 text-green-700">
                  <CheckCircle size={20} />
                  <span className="font-medium">Scheduling Complete</span>
                  {lastScheduleResult.ml_prediction && (
                    <Badge variant="secondary" className="text-xs">
                      <Brain size={12} className="mr-1" />
                      ML-Powered
                    </Badge>
                  )}
                </div>
                
                <div className="text-sm text-muted-foreground">
                  {lastScheduleResult.message}
                </div>
                
                {lastScheduleResult.next_notification && (
                  <div className="text-sm">
                    <strong>Next notification:</strong> {lastScheduleResult.next_notification}
                  </div>
                )}
              </div>
            )}
          </TabsContent>
          
          <TabsContent value="analysis" className="space-y-4 mt-4">
            <div className="flex gap-3">
              <Button 
                onClick={testMLPatternAnalysis}
                disabled={isAnalyzing}
                className="flex items-center gap-2"
              >
                <Brain size={16} />
                {isAnalyzing ? 'Analyzing Patterns...' : 'Run ML Analysis'}
              </Button>
            </div>

            {mlAnalysisResult && (
              <div className="space-y-3">
                <div className="flex items-center gap-2 text-blue-700">
                  <Brain size={20} />
                  <span className="font-medium">ML Analysis Complete</span>
                </div>
                
                <div className="bg-white/60 p-3 rounded border">
                  <div className="text-sm">
                    <strong>Analysis Timestamp:</strong> {new Date(mlAnalysisResult.analysis_timestamp).toLocaleString()}
                  </div>
                  <div className="text-sm mt-1">
                    <strong>Data Points:</strong> {mlAnalysisResult.data_points_analyzed?.mood_entries || 0} mood entries, 
                    {mlAnalysisResult.data_points_analyzed?.journal_entries || 0} journal entries
                  </div>
                  <div className="text-xs text-muted-foreground mt-2">
                    AI has analyzed your behavior patterns to optimize notification timing and content.
                  </div>
                </div>
              </div>
            )}
          </TabsContent>
          
          <TabsContent value="insights" className="space-y-4 mt-4">
            <div className="flex gap-3">
              <Button 
                onClick={testPersonalizedInsights}
                disabled={isGeneratingInsights}
                className="flex items-center gap-2"
              >
                <Sparkle size={16} />
                {isGeneratingInsights ? 'Generating...' : 'Generate AI Insights'}
              </Button>
            </div>

            {personalizedInsights.length > 0 && (
              <div className="space-y-3">
                <div className="flex items-center gap-2 text-purple-700">
                  <Sparkle size={20} />
                  <span className="font-medium">Personalized Insights</span>
                </div>
                
                {personalizedInsights.map((insight, index) => (
                  <div key={index} className="bg-white/60 p-3 rounded border-l-4 border-purple-300">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium text-sm">{insight.title}</h4>
                      <Badge className={`text-xs ${getPriorityColor(insight.priority)}`}>
                        {insight.priority}
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground mb-2">{insight.content}</p>
                    {insight.action_suggestions.length > 0 && (
                      <div className="text-xs">
                        <strong>Suggestions:</strong>
                        <ul className="list-disc list-inside mt-1">
                          {insight.action_suggestions.slice(0, 2).map((suggestion, idx) => (
                            <li key={idx}>{suggestion}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    <div className="flex items-center gap-2 mt-2">
                      <div className="text-xs text-muted-foreground">
                        Confidence: {Math.round(insight.confidence_score * 100)}%
                      </div>
                      <Badge variant="outline" className="text-xs capitalize">
                        {insight.insight_type.replace('_', ' ')}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </TabsContent>
          
          <TabsContent value="results" className="space-y-4 mt-4">
            {scheduledNotifications.length > 0 && (
              <div className="space-y-2">
                <h4 className="font-medium text-sm flex items-center gap-2">
                  <TrendUp size={16} className="text-blue-500" />
                  Scheduled Notifications:
                </h4>
                <div className="space-y-2">
                  {scheduledNotifications.slice(0, 5).map((notification, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-white/60 rounded border">
                      <div className="flex items-center gap-3">
                        <div className="p-1.5 rounded-md bg-blue-100 dark:bg-blue-900/20">
                          <Clock size={16} className="text-blue-600 dark:text-blue-400" />
                        </div>
                        <div>
                          <div className="text-sm font-medium">
                            {formatTime(notification.hour)}
                            {notification.day_of_week !== null && (
                              <span className="text-muted-foreground ml-1">
                                on {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][notification.day_of_week]}s
                              </span>
                            )}
                          </div>
                          {notification.reason && (
                            <div className="text-xs text-muted-foreground">{notification.reason}</div>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge variant="outline" className="text-xs">
                          {notification.effectiveness_score?.toFixed(1)}/10
                        </Badge>
                        <Badge variant="secondary" className="text-xs capitalize">
                          {notification.notification_type?.replace('_', ' ')}
                        </Badge>
                        {notification.confidence_level && (
                          <div className="flex items-center gap-1">
                            <Lightning size={12} className="text-yellow-500" />
                            <span className="text-xs">{Math.round(notification.confidence_level * 100)}%</span>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="text-xs text-muted-foreground bg-white/60 p-3 rounded border-l-4 border-blue-300">
              <strong>How the ML System Works:</strong> The AI analyzes your mood patterns, app usage, and 
              engagement history to find optimal times for wellness reminders. The system learns from your 
              responses to continuously improve notification effectiveness and personalization.
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  )
}
