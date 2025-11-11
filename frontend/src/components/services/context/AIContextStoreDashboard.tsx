import { useState, useEffect } from "react"
import { motion } from "framer-motion"
import { 
  Brain, 
  Activity, 
  Users, 
  RefreshCw,
  TrendingUp,
  MessageSquare,
  Heart,
  BookOpen,
  Clock,
  Lightbulb
} from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { useAuth } from "@/hooks/useAuth"
import { toast } from "sonner"

interface UserContext {
  user_id: string
  context: {
    mood_context: {
      recent_moods: any[]
      patterns: string
      average_intensity: number
    }
    journal_context: {
      recent_themes: string[]
      sentiment: string
      entry_frequency: string
    }
    community_context: {
      activity_level: string
      engagement: number
      recent_interactions: number
    }
    last_updated: string
  }
  refresh_requested: boolean
  timestamp: string
}

interface ContextInsight {
  id: string
  type: string
  message: string
  confidence: number
  generated_at: string
}

export function AIContextStoreDashboard() {
  const { user } = useAuth()
  const [userContext, setUserContext] = useState<UserContext | null>(null)
  const [insights, setInsights] = useState<ContextInsight[]>([])
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)

  const API_BASE = import.meta.env.VITE_API_BASE_URL
  const token = localStorage.getItem('mantrapath_token')

  useEffect(() => {
    if (user?.id) {
      fetchUserContext()
      fetchInsights()
    }
  }, [user])

  const fetchUserContext = async () => {
    if (!user?.id) return
    
    try {
      const response = await fetch(`${API_BASE}/ai-context-store/api/v1/context/user/${user.id}`, {
        headers: token ? { 'Authorization': `Bearer ${token}` } : {}
      })
      
      if (response.ok) {
        const data = await response.json()
        setUserContext(data)
      } else {
        throw new Error('Failed to fetch context')
      }
    } catch (error) {
      console.error('Error fetching user context:', error)
      toast.error('Failed to load user context')
    } finally {
      setLoading(false)
    }
  }

  const fetchInsights = async () => {
    if (!user?.id) return
    
    try {
      const response = await fetch(`${API_BASE}/ai-context-store/api/v1/intelligence/insights/${user.id}`, {
        headers: token ? { 'Authorization': `Bearer ${token}` } : {}
      })
      
      if (response.ok) {
        const data = await response.json()
        setInsights(data.insights || [])
      }
    } catch (error) {
      console.error('Error fetching insights:', error)
    }
  }

  const refreshContext = async () => {
    if (!user?.id) return
    
    setRefreshing(true)
    try {
      const response = await fetch(`${API_BASE}/ai-context-store/api/v1/context/user/${user.id}/refresh`, {
        method: 'POST',
        headers: token ? { 'Authorization': `Bearer ${token}` } : {}
      })
      
      if (response.ok) {
        toast.success('Context refresh initiated')
        // Wait a moment then fetch updated context
        setTimeout(() => {
          fetchUserContext()
          fetchInsights()
        }, 2000)
      }
    } catch (error) {
      console.error('Error refreshing context:', error)
      toast.error('Failed to refresh context')
    } finally {
      setRefreshing(false)
    }
  }

  const getMoodColor = (intensity: number) => {
    if (intensity >= 7) return "text-green-600"
    if (intensity >= 4) return "text-yellow-600"
    return "text-red-600"
  }

  const getEngagementColor = (engagement: number) => {
    if (engagement >= 0.7) return "text-green-600"
    if (engagement >= 0.4) return "text-yellow-600"
    return "text-red-600"
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-accent-6"></div>
      </div>
    )
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">AI Context Intelligence</h1>
          <p className="text-neutral-11 mt-1">
            Cross-service user context and intelligent insights
          </p>
        </div>
        <Button onClick={refreshContext} disabled={refreshing} size="sm">
          <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
          Refresh Context
        </Button>
      </div>

      {/* Context Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium">Mood Score</p>
                <p className={`text-2xl font-bold ${getMoodColor(userContext?.context?.mood_context?.average_intensity || 0)}`}>
                  {userContext?.context?.mood_context?.average_intensity?.toFixed(1) || '0.0'}
                </p>
              </div>
              <Heart className="h-8 w-8 text-red-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium">Journal Activity</p>
                <p className="text-2xl font-bold text-blue-600">
                  {userContext?.context?.journal_context?.entry_frequency || 'Unknown'}
                </p>
              </div>
              <BookOpen className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium">Community Engagement</p>
                <p className={`text-2xl font-bold ${getEngagementColor(userContext?.context?.community_context?.engagement || 0)}`}>
                  {((userContext?.context?.community_context?.engagement || 0) * 100).toFixed(0)}%
                </p>
              </div>
              <Users className="h-8 w-8 text-purple-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium">AI Insights</p>
                <p className="text-2xl font-bold text-green-600">
                  {insights.length}
                </p>
              </div>
              <Lightbulb className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="context" className="space-y-4">
        <TabsList>
          <TabsTrigger value="context">User Context</TabsTrigger>
          <TabsTrigger value="insights">AI Insights</TabsTrigger>
          <TabsTrigger value="patterns">Behavior Patterns</TabsTrigger>
        </TabsList>

        <TabsContent value="context" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Mood Context */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
            >
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Heart className="h-5 w-5 text-red-500" />
                    Mood Context
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium">Average Intensity</span>
                      <Badge variant="outline" className={getMoodColor(userContext?.context?.mood_context?.average_intensity || 0)}>
                        {userContext?.context?.mood_context?.average_intensity?.toFixed(1) || '0.0'}/10
                      </Badge>
                    </div>
                    <Progress 
                      value={(userContext?.context?.mood_context?.average_intensity || 0) * 10} 
                      className="h-2"
                    />
                  </div>
                  
                  <div>
                    <p className="text-sm font-medium mb-2">Recent Patterns</p>
                    <p className="text-sm text-neutral-11">
                      {userContext?.context?.mood_context?.patterns || 'No patterns available'}
                    </p>
                  </div>

                  {userContext?.context?.mood_context?.recent_moods && 
                   userContext.context.mood_context.recent_moods.length > 0 && (
                    <div>
                      <p className="text-sm font-medium mb-2">Recent Moods</p>
                      <div className="space-y-1">
                        {userContext.context.mood_context.recent_moods.map((mood, index) => (
                          <div key={index} className="flex justify-between text-xs">
                            <span>{mood.date}</span>
                            <Badge variant="outline">
                              {mood.score}/10
                            </Badge>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            </motion.div>

            {/* Journal Context */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
            >
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <BookOpen className="h-5 w-5 text-blue-500" />
                    Journal Context
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Entry Frequency</span>
                    <Badge variant="outline">
                      {userContext?.context?.journal_context?.entry_frequency || 'Unknown'}
                    </Badge>
                  </div>

                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Overall Sentiment</span>
                    <Badge 
                      variant="outline" 
                      className={
                        userContext?.context?.journal_context?.sentiment === 'positive' ? 'text-green-600' :
                        userContext?.context?.journal_context?.sentiment === 'negative' ? 'text-red-600' :
                        'text-yellow-600'
                      }
                    >
                      {userContext?.context?.journal_context?.sentiment || 'Unknown'}
                    </Badge>
                  </div>

                  {userContext?.context?.journal_context?.recent_themes && 
                   userContext.context.journal_context.recent_themes.length > 0 && (
                    <div>
                      <p className="text-sm font-medium mb-2">Recent Themes</p>
                      <div className="flex flex-wrap gap-1">
                        {userContext.context.journal_context.recent_themes.map((theme, index) => (
                          <Badge key={index} variant="secondary" className="text-xs">
                            {theme}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            </motion.div>

            {/* Community Context */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
            >
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Users className="h-5 w-5 text-purple-500" />
                    Community Context
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Activity Level</span>
                    <Badge variant="outline">
                      {userContext?.context?.community_context?.activity_level || 'Unknown'}
                    </Badge>
                  </div>

                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium">Engagement Score</span>
                      <Badge variant="outline" className={getEngagementColor(userContext?.context?.community_context?.engagement || 0)}>
                        {((userContext?.context?.community_context?.engagement || 0) * 100).toFixed(0)}%
                      </Badge>
                    </div>
                    <Progress 
                      value={(userContext?.context?.community_context?.engagement || 0) * 100} 
                      className="h-2"
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Recent Interactions</span>
                    <Badge variant="outline">
                      {userContext?.context?.community_context?.recent_interactions || 0}
                    </Badge>
                  </div>
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
                        Generated {new Date(insight.generated_at).toLocaleString()}
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
                No AI insights available yet. More insights will be generated as you use the platform.
              </AlertDescription>
            </Alert>
          )}
        </TabsContent>

        <TabsContent value="patterns" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5" />
                Behavioral Patterns
              </CardTitle>
              <CardDescription>
                AI-detected patterns in your wellness journey
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-neutral-11">
                Pattern analysis is being enhanced. Check back soon for detailed behavioral insights.
              </p>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Last Updated Info */}
      {userContext?.context?.last_updated && (
        <Alert>
          <Activity className="h-4 w-4" />
          <AlertDescription>
            Context last updated: {new Date(userContext.context.last_updated).toLocaleString()}
            {userContext.refresh_requested && " • Refresh was requested"}
          </AlertDescription>
        </Alert>
      )}
    </div>
  )
}