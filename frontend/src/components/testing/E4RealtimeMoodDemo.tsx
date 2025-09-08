import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Textarea } from '@/components/ui/textarea'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  Heart, 
  BookOpen, 
  ChatCircle, 
  Users, 
  Target, 
  Broadcast,
  ChartLine,
  Lightbulb
} from '@phosphor-icons/react'
import { motion, AnimatePresence } from 'framer-motion'
import { toast } from 'sonner'
import { useRealtimeInsights } from '@/hooks/useRealtimeInsights'
import { useRobustWebSocket } from '@/hooks/useRobustWebSocket'
import { MoodQuickEntry } from '@/components/mood/MoodQuickEntry'

interface CrossPlatformMoodState {
  overall_mood: number
  primary_sources: string[]
  confidence: number
  last_updated: string
  mood_breakdown: {
    direct_entries: number
    journal_sentiment: number
    chat_analysis: number
    community_engagement: number
    challenge_progress: number
  }
  recent_signals: Array<{
    source: string
    mood_score: number
    timestamp: string
    context: string
  }>
}

export function E4RealtimeMoodDemo() {
  const [crossPlatformMood, setCrossPlatformMood] = useState<CrossPlatformMoodState | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [demoJournalContent, setDemoJournalContent] = useState('')
  const [demoChatMessage, setDemoChatMessage] = useState('')
  
  // E4: Real-time insights and WebSocket integration
  const { insights, isConnected, connectionError } = useRealtimeInsights()
  const { lastMessage } = useRobustWebSocket()

  // Load cross-platform mood state
  const loadCrossPlatformMood = async () => {
    try {
      setIsLoading(true)
      const token = localStorage.getItem('authToken') || localStorage.getItem('mantrapath_token')
      
      const response = await fetch('/api/v1/mood/cross-platform-state', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        setCrossPlatformMood(data)
      }
    } catch (error) {
      console.error('Failed to load cross-platform mood:', error)
    } finally {
      setIsLoading(false)
    }
  }

  // Simulate platform interactions for demo
  const simulateJournalEntry = async () => {
    if (!demoJournalContent.trim()) return

    try {
      const token = localStorage.getItem('authToken') || localStorage.getItem('mantrapath_token')
      
      // Create journal entry (this will trigger mood inference)
      const response = await fetch('/api/v1/journal/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          content: demoJournalContent,
          is_private: true
        })
      })

      if (response.ok) {
        toast.success('Journal entry created! 📝', {
          description: 'Mood inference processing in real-time...'
        })
        setDemoJournalContent('')
        
        // Refresh cross-platform mood state
        setTimeout(() => loadCrossPlatformMood(), 1000)
      }
    } catch (error) {
      toast.error('Failed to create journal entry')
    }
  }

  const simulateChatInteraction = async () => {
    if (!demoChatMessage.trim()) return

    try {
      const token = localStorage.getItem('authToken') || localStorage.getItem('mantrapath_token')
      
      // Process chat message for mood inference
      const response = await fetch('/api/v1/mood/process-platform-interaction', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          type: 'chat_message',
          user_message: demoChatMessage,
          conversation_type: 'general'
        })
      })

      if (response.ok) {
        const result = await response.json()
        toast.success('Chat interaction processed! 💬', {
          description: `Mood score: ${result.mood_signal?.mood_score?.toFixed(2) || 'N/A'}`
        })
        setDemoChatMessage('')
        
        // Refresh cross-platform mood state
        setTimeout(() => loadCrossPlatformMood(), 1000)
      }
    } catch (error) {
      toast.error('Failed to process chat interaction')
    }
  }

  const simulateCommunityInteraction = async () => {
    try {
      const token = localStorage.getItem('authToken') || localStorage.getItem('mantrapath_token')
      
      // Simulate joining an event
      const response = await fetch('/api/v1/mood/process-platform-interaction', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          type: 'community_interaction',
          interaction_type: 'event_joined',
          content: 'Joined mindfulness workshop'
        })
      })

      if (response.ok) {
        const result = await response.json()
        toast.success('Community interaction processed! 👥', {
          description: `Mood boost from positive engagement`
        })
        
        // Refresh cross-platform mood state
        setTimeout(() => loadCrossPlatformMood(), 1000)
      }
    } catch (error) {
      toast.error('Failed to process community interaction')
    }
  }

  useEffect(() => {
    loadCrossPlatformMood()
  }, [])

  // React to real-time WebSocket messages
  useEffect(() => {
    if (lastMessage?.type === 'insight_delta') {
      loadCrossPlatformMood() // Refresh when real-time updates arrive
    }
  }, [lastMessage])

  const getMoodColor = (score: number) => {
    if (score > 0.3) return 'text-green-600'
    if (score > 0) return 'text-blue-600'
    if (score > -0.3) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getMoodLabel = (score: number) => {
    if (score > 0.5) return 'Very Positive'
    if (score > 0.2) return 'Positive'
    if (score > -0.2) return 'Neutral'
    if (score > -0.5) return 'Negative'
    return 'Very Negative'
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">E4 Real-Time Mood Intelligence</h2>
          <p className="text-muted-foreground">Cross-platform mood tracking from all your interactions</p>
        </div>
        
        <div className="flex items-center gap-2">
          <Badge variant={isConnected ? "default" : "destructive"}>
            <Broadcast className={`h-3 w-3 mr-1 ${isConnected ? 'animate-pulse' : ''}`} />
            {isConnected ? 'Live' : 'Offline'}
          </Badge>
          <Button onClick={loadCrossPlatformMood} disabled={isLoading} size="sm">
            {isLoading ? 'Loading...' : 'Refresh'}
          </Button>
        </div>
      </div>

      {/* Real-time Insights Summary */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <ChartLine className="text-blue-500" size={20} />
            Real-Time Insights Summary
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold">{insights.daysTracked}</div>
              <div className="text-xs text-muted-foreground">Days Tracked</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold">{insights.moodStreak}</div>
              <div className="text-xs text-muted-foreground">Mood Streak</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold">{insights.journalEntries}</div>
              <div className="text-xs text-muted-foreground">Journal Entries</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold">{insights.engagementLevel}</div>
              <div className="text-xs text-muted-foreground">Engagement</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Cross-Platform Mood State */}
      {crossPlatformMood && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Lightbulb className="text-yellow-500" size={20} />
              Cross-Platform Mood Intelligence
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Overall Mood */}
            <div className="flex items-center justify-between p-4 bg-muted/50 rounded-lg">
              <div>
                <div className="font-medium">Overall Mood</div>
                <div className="text-sm text-muted-foreground">
                  Confidence: {Math.round(crossPlatformMood.confidence * 100)}%
                </div>
              </div>
              <div className="text-right">
                <div className={`text-2xl font-bold ${getMoodColor(crossPlatformMood.overall_mood)}`}>
                  {getMoodLabel(crossPlatformMood.overall_mood)}
                </div>
                <div className="text-sm text-muted-foreground">
                  {crossPlatformMood.overall_mood > 0 ? '+' : ''}{crossPlatformMood.overall_mood.toFixed(2)}
                </div>
              </div>
            </div>

            {/* Mood Sources Breakdown */}
            <div>
              <h4 className="font-medium mb-2">Mood Sources</h4>
              <div className="space-y-2">
                {Object.entries(crossPlatformMood.mood_breakdown).map(([source, value]) => (
                  <div key={source} className="flex items-center justify-between">
                    <span className="text-sm capitalize">{source.replace('_', ' ')}</span>
                    <div className="flex items-center gap-2">
                      <div className="w-20 h-2 bg-muted rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-primary transition-all"
                          style={{ width: `${Math.abs(value) * 100}%` }}
                        />
                      </div>
                      <span className="text-xs w-12 text-right">
                        {value > 0 ? '+' : ''}{value.toFixed(2)}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Recent Signals */}
            <div>
              <h4 className="font-medium mb-2">Recent Signals</h4>
              <div className="space-y-2">
                {crossPlatformMood.recent_signals.map((signal, index) => (
                  <div key={index} className="flex items-center justify-between text-sm p-2 bg-muted/30 rounded">
                    <div>
                      <span className="font-medium capitalize">{signal.source.replace('_', ' ')}</span>
                      <div className="text-xs text-muted-foreground">{signal.context}</div>
                    </div>
                    <div className="text-right">
                      <div className={getMoodColor(signal.mood_score)}>
                        {signal.mood_score > 0 ? '+' : ''}{signal.mood_score.toFixed(2)}
                      </div>
                      <div className="text-xs text-muted-foreground">
                        {new Date(signal.timestamp).toLocaleTimeString()}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Interactive Demo */}
      <Tabs defaultValue="mood" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="mood">Direct Mood</TabsTrigger>
          <TabsTrigger value="journal">Journal</TabsTrigger>
          <TabsTrigger value="chat">Chat</TabsTrigger>
          <TabsTrigger value="community">Community</TabsTrigger>
        </TabsList>
        
        <TabsContent value="mood" className="space-y-4">
          <MoodQuickEntry onEntryAdded={() => loadCrossPlatformMood()} />
        </TabsContent>
        
        <TabsContent value="journal" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BookOpen className="text-blue-500" size={20} />
                Journal Entry Demo
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <Textarea
                value={demoJournalContent}
                onChange={(e) => setDemoJournalContent(e.target.value)}
                placeholder="Write about your day... The system will analyze sentiment and update your mood state in real-time."
                className="min-h-[100px]"
              />
              <Button onClick={simulateJournalEntry} disabled={!demoJournalContent.trim()}>
                Create Journal Entry & Analyze Mood
              </Button>
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="chat" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <ChatCircle className="text-green-500" size={20} />
                Chat Interaction Demo
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <Textarea
                value={demoChatMessage}
                onChange={(e) => setDemoChatMessage(e.target.value)}
                placeholder="Type a message to the chatbot... The system will analyze emotional indicators."
                className="min-h-[80px]"
              />
              <Button onClick={simulateChatInteraction} disabled={!demoChatMessage.trim()}>
                Process Chat Message
              </Button>
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="community" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="text-purple-500" size={20} />
                Community Interaction Demo
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-muted-foreground">
                Simulate positive community engagement (joining events, commenting, etc.)
              </p>
              <Button onClick={simulateCommunityInteraction}>
                Simulate Community Engagement
              </Button>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Connection Status */}
      {connectionError && (
        <Card className="border-amber-200 bg-amber-50">
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 text-amber-700">
              <span>⚠️</span>
              <span className="text-sm">Real-time features: {connectionError}</span>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
