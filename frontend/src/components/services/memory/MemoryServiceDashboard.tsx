import { useState, useEffect } from "react"
import { motion } from "framer-motion"
import { 
  Brain, 
  Activity, 
  TrendingUp,
  Clock,
  Target,
  Lightbulb,
  Calendar,
  BarChart3,
  Zap,
  ArrowUp,
  ArrowDown,
  Minus
} from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { useAuth } from "@/hooks/useAuth"
import { toast } from "sonner"

interface MoodPattern {
  date: string
  mood_score: number
  confidence: number
}

interface ActivityPattern {
  most_active_hours: number[]
  preferred_interaction_types: string[]
  engagement_trend: string
}

interface MemoryPatterns {
  mood_patterns: MoodPattern[]
  activity_patterns: ActivityPattern
}

interface MemoryInsight {
  id: string
  type: string
  message: string
  confidence: number
  generated_at: string
}

interface UserInteraction {
  id: string
  user_id: string
  type: string
  timestamp: string
  content: string
}

interface MemoryResponse {
  success: boolean
  data: MemoryPatterns | MemoryInsight[] | UserInteraction[]
}

export function MemoryServiceDashboard() {
  const { user } = useAuth()
  const [patterns, setPatterns] = useState<MemoryPatterns | null>(null)
  const [insights, setInsights] = useState<MemoryInsight[]>([])
  const [interactions, setInteractions] = useState<UserInteraction[]>([])
  const [loading, setLoading] = useState(true)

  const API_BASE = import.meta.env.VITE_API_BASE_URL
  const token = localStorage.getItem('mantrapath_token')

  useEffect(() => {
    if (user?.id) {
      fetchMemoryData()
    }
  }, [user])

  const fetchMemoryData = async () => {
    if (!user?.id) return

    try {
      // Fetch patterns
      const patternsResponse = await fetch(`${API_BASE}/memory-service/api/v1/patterns/${user.id}`, {
        headers: token ? { 'Authorization': `Bearer ${token}` } : {}
      })
      
      if (patternsResponse.ok) {
        const patternsData = await patternsResponse.json() as MemoryResponse
        if (patternsData.success) {
          setPatterns(patternsData.data as MemoryPatterns)
        }
      }

      // Fetch insights
      const insightsResponse = await fetch(`${API_BASE}/memory-service/api/v1/insights/${user.id}`, {
        headers: token ? { 'Authorization': `Bearer ${token}` } : {}
      })
      
      if (insightsResponse.ok) {
        const insightsData = await patternsResponse.json() as MemoryResponse
        if (insightsData.success) {
          setInsights((insightsData.data as any).recent_insights || [])
        }
      }

      // Fetch recent interactions
      const interactionsResponse = await fetch(`${API_BASE}/memory-service/api/v1/interactions/${user.id}`, {
        headers: token ? { 'Authorization': `Bearer ${token}` } : {}
      })
      
      if (interactionsResponse.ok) {
        const interactionsData = await interactionsResponse.json() as MemoryResponse
        if (interactionsData.success) {
          setInteractions(interactionsData.data as UserInteraction[])
        }
      }

    } catch (error) {
      console.error('Error fetching memory data:', error)
      toast.error('Failed to load memory data')
    } finally {
      setLoading(false)
    }
  }

  const getEngagementTrendIcon = (trend: string) => {
    switch (trend) {
      case 'increasing':
        return <ArrowUp className="h-4 w-4 text-green-600" />
      case 'decreasing':
        return <ArrowDown className="h-4 w-4 text-red-600" />
      default:
        return <Minus className="h-4 w-4 text-gray-600" />
    }
  }

  const getEngagementTrendColor = (trend: string) => {
    switch (trend) {
      case 'increasing':
        return 'text-green-600'
      case 'decreasing':
        return 'text-red-600'
      default:
        return 'text-gray-600'
    }
  }

  const formatHour = (hour: number) => {
    if (hour === 0) return '12 AM'
    if (hour < 12) return `${hour} AM`
    if (hour === 12) return '12 PM'
    return `${hour - 12} PM`
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-accent-6"></div>
      </div>
    )
  }

  const avgMoodScore = (patterns?.mood_patterns || []).reduce((acc, p) => acc + (p?.mood_score || 0), 0) / Math.max((patterns?.mood_patterns || []).length, 1) || 0
  const avgConfidence = (patterns?.mood_patterns || []).reduce((acc, p) => acc + (p?.confidence || 0), 0) / Math.max((patterns?.mood_patterns || []).length, 1) || 0

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Memory Intelligence</h1>
          <p className="text-neutral-11 mt-1">
            Behavioral patterns and long-term insights from your wellness journey
          </p>
        </div>
        <Badge variant="outline" className="text-purple-600 border-purple-300">
          <Brain className="h-3 w-3 mr-1" />
          Pattern Analysis Active
        </Badge>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium">Avg Mood Score</p>
                <p className="text-2xl font-bold text-blue-600">
                  {avgMoodScore.toFixed(1)}
                </p>
              </div>
              <TrendingUp className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium">Pattern Confidence</p>
                <p className="text-2xl font-bold text-green-600">
                  {(avgConfidence * 100).toFixed(0)}%
                </p>
              </div>
              <Target className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium">Engagement Trend</p>
                <p className={`text-2xl font-bold ${getEngagementTrendColor(patterns?.activity_patterns?.engagement_trend || 'stable')}`}>
                  {patterns?.activity_patterns?.engagement_trend || 'Stable'}
                </p>
              </div>
              {getEngagementTrendIcon(patterns?.activity_patterns?.engagement_trend || 'stable')}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium">Memory Insights</p>
                <p className="text-2xl font-bold text-purple-600">
                  {insights.length}
                </p>
              </div>
              <Lightbulb className="h-8 w-8 text-purple-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="patterns" className="space-y-4">
        <TabsList>
          <TabsTrigger value="patterns">Behavioral Patterns</TabsTrigger>
          <TabsTrigger value="insights">Memory Insights</TabsTrigger>
          <TabsTrigger value="interactions">Recent Interactions</TabsTrigger>
        </TabsList>

        <TabsContent value="patterns" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Mood Patterns */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
            >
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <BarChart3 className="h-5 w-5 text-blue-500" />
                    Mood Patterns
                  </CardTitle>
                  <CardDescription>
                    Recent mood trends and confidence levels
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {patterns?.mood_patterns && patterns.mood_patterns.length > 0 ? (
                    <div className="space-y-3">
                      {patterns.mood_patterns.map((pattern, index) => (
                        <div key={index} className="flex items-center justify-between">
                          <div className="flex items-center gap-3">
                            <div className="text-sm font-medium">
                              {new Date(pattern.date).toLocaleDateString()}
                            </div>
                            <div className="text-sm text-neutral-11">
                              Score: {pattern.mood_score}/10
                            </div>
                          </div>
                          <Badge 
                            variant="outline"
                            className={
                              pattern.confidence >= 0.8 ? 'text-green-600' :
                              pattern.confidence >= 0.6 ? 'text-yellow-600' :
                              'text-red-600'
                            }
                          >
                            {(pattern.confidence * 100).toFixed(0)}%
                          </Badge>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-sm text-neutral-11">No mood patterns available yet.</p>
                  )}
                </CardContent>
              </Card>
            </motion.div>

            {/* Activity Patterns */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
            >
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Activity className="h-5 w-5 text-green-500" />
                    Activity Patterns
                  </CardTitle>
                  <CardDescription>
                    Usage patterns and preferences
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {patterns?.activity_patterns ? (
                    <>
                      <div>
                        <p className="text-sm font-medium mb-2">Most Active Hours</p>
                        <div className="flex flex-wrap gap-2">
                          {patterns.activity_patterns.most_active_hours.map((hour, index) => (
                            <Badge key={index} variant="secondary">
                              {formatHour(hour)}
                            </Badge>
                          ))}
                        </div>
                      </div>

                      <div>
                        <p className="text-sm font-medium mb-2">Preferred Interactions</p>
                        <div className="flex flex-wrap gap-2">
                          {patterns.activity_patterns.preferred_interaction_types.map((type, index) => (
                            <Badge key={index} variant="outline">
                              {type.replace('_', ' ').toUpperCase()}
                            </Badge>
                          ))}
                        </div>
                      </div>

                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">Engagement Trend</span>
                        <div className="flex items-center gap-2">
                          {getEngagementTrendIcon(patterns.activity_patterns.engagement_trend)}
                          <span className={`text-sm font-medium ${getEngagementTrendColor(patterns.activity_patterns.engagement_trend)}`}>
                            {patterns.activity_patterns.engagement_trend}
                          </span>
                        </div>
                      </div>
                    </>
                  ) : (
                    <p className="text-sm text-neutral-11">No activity patterns available yet.</p>
                  )}
                </CardContent>
              </Card>
            </motion.div>
          </div>
        </TabsContent>

        <TabsContent value="insights" className="space-y-4">
          {insights.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {insights.map((insight) => (
                <motion.div
                  key={insight.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                >
                  <Card>
                    <CardHeader className="pb-3">
                      <div className="flex items-center justify-between">
                        <CardTitle className="text-sm">{insight.type.replace('_', ' ').toUpperCase()}</CardTitle>
                        <Badge 
                          variant="outline"
                          className={
                            insight.confidence >= 0.8 ? 'text-green-600' :
                            insight.confidence >= 0.6 ? 'text-yellow-600' :
                            'text-red-600'
                          }
                        >
                          {(insight.confidence * 100).toFixed(0)}% confidence
                        </Badge>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm text-neutral-11 mb-3">{insight.message}</p>
                      <div className="flex items-center gap-2 text-xs text-neutral-10">
                        <Clock className="h-3 w-3" />
                        {new Date(insight.generated_at).toLocaleString()}
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </div>
          ) : (
            <Alert>
              <Lightbulb className="h-4 w-4" />
              <AlertDescription>
                No memory insights available yet. Insights will be generated as you interact with the platform.
              </AlertDescription>
            </Alert>
          )}
        </TabsContent>

        <TabsContent value="interactions" className="space-y-4">
          {interactions.length > 0 ? (
            <div className="space-y-3">
              {interactions.slice(0, 10).map((interaction) => (
                <motion.div
                  key={interaction.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                >
                  <Card>
                    <CardContent className="p-4">
                      <div className="flex items-start justify-between mb-2">
                        <Badge variant="outline">
                          {interaction.type.replace('_', ' ').toUpperCase()}
                        </Badge>
                        <div className="flex items-center gap-2 text-xs text-neutral-10">
                          <Clock className="h-3 w-3" />
                          {new Date(interaction.timestamp).toLocaleString()}
                        </div>
                      </div>
                      <p className="text-sm text-neutral-11 truncate">
                        {interaction.content}
                      </p>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </div>
          ) : (
            <Alert>
              <Calendar className="h-4 w-4" />
              <AlertDescription>
                No recent interactions available. Start using the platform to see your interaction history.
              </AlertDescription>
            </Alert>
          )}
        </TabsContent>
      </Tabs>
    </div>
  )
}