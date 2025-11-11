import { useState, useEffect, useRef } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { 
  Send, 
  MessageCircle, 
  Bot,
  User,
  Mic,
  MicOff,
  Volume2,
  VolumeX,
  RotateCcw,
  Sparkles,
  Brain,
  Heart,
  Lightbulb,
  Coffee
} from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"
import { useAuth } from "@/hooks/useAuth"
import { toast } from "sonner"

interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: string
  confidence?: number
  emotions_detected?: Array<{
    emotion: string
    confidence: number
  }>
  mood_impact?: {
    predicted_mood_change: number
    suggested_follow_up: string
  }
  conversation_metrics?: {
    engagement_score: number
    empathy_level: number
    supportiveness: number
  }
}

interface ConversationSession {
  session_id: string
  user_id: string
  created_at: string
  updated_at: string
  message_count: number
  session_mood_progression: Array<{
    message_index: number
    mood_score: number
    emotional_state: string
  }>
  topics_discussed: string[]
  session_summary: string
}

interface ChatbotStats {
  total_conversations: number
  total_messages: number
  avg_session_length: number
  most_common_topics: Array<{
    topic: string
    frequency: number
  }>
  mood_improvement_rate: number
  user_satisfaction_score: number
}

export function ChatServiceDashboard() {
  const { user } = useAuth()
  const [currentSession, setCurrentSession] = useState<ConversationSession | null>(null)
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [recentSessions, setRecentSessions] = useState<ConversationSession[]>([])
  const [stats, setStats] = useState<ChatbotStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [sending, setSending] = useState(false)
  const [message, setMessage] = useState('')
  const [isListening, setIsListening] = useState(false)
  const [voiceEnabled, setVoiceEnabled] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const API_BASE = import.meta.env.VITE_API_BASE_URL
  const token = localStorage.getItem('mantrapath_token')

  useEffect(() => {
    if (user?.id) {
      fetchChatData()
      createNewSession()
    }
  }, [user])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  const fetchChatData = async () => {
    if (!user?.id) return

    try {
      // Fetch recent sessions
      const sessionsResponse = await fetch(`${API_BASE}/chatbot-service/api/v1/chat/sessions?limit=5`, {
        headers: token ? { 'Authorization': `Bearer ${token}` } : {}
      })
      
      if (sessionsResponse.ok) {
        const sessionsData = await sessionsResponse.json()
        setRecentSessions(sessionsData.sessions || [])
      }

      // Fetch stats
      const statsResponse = await fetch(`${API_BASE}/chatbot-service/api/v1/analytics/user-stats`, {
        headers: token ? { 'Authorization': `Bearer ${token}` } : {}
      })
      
      if (statsResponse.ok) {
        const statsData = await statsResponse.json()
        setStats(statsData)
      }

    } catch (error) {
      console.error('Error fetching chat data:', error)
      toast.error('Failed to load chat data')
    } finally {
      setLoading(false)
    }
  }

  const createNewSession = async () => {
    if (!user?.id) return

    try {
      const response = await fetch(`${API_BASE}/chatbot-service/api/v1/chat/sessions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        }
      })
      
      if (response.ok) {
        const sessionData = await response.json()
        setCurrentSession(sessionData)
        setMessages([])
      }
    } catch (error) {
      console.error('Error creating session:', error)
    }
  }

  const sendMessage = async () => {
    if (!message.trim() || !currentSession || sending) return

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: message.trim(),
      timestamp: new Date().toISOString()
    }

    setMessages(prev => [...prev, userMessage])
    setMessage('')
    setSending(true)

    try {
      const response = await fetch(`${API_BASE}/chatbot-service/api/v1/chat/messages`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        },
        body: JSON.stringify({
          session_id: currentSession.session_id,
          message: userMessage.content,
          enable_emotion_detection: true,
          enable_mood_tracking: true
        })
      })
      
      if (response.ok) {
        const responseData = await response.json()
        
        const assistantMessage: ChatMessage = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: responseData.response,
          timestamp: new Date().toISOString(),
          confidence: responseData.confidence,
          emotions_detected: responseData.emotions_detected,
          mood_impact: responseData.mood_impact,
          conversation_metrics: responseData.conversation_metrics
        }

        setMessages(prev => [...prev, assistantMessage])

        // Read response aloud if voice is enabled
        if (voiceEnabled && 'speechSynthesis' in window) {
          const utterance = new SpeechSynthesisUtterance(responseData.response)
          utterance.rate = 0.9
          utterance.pitch = 1.0
          speechSynthesis.speak(utterance)
        }

      } else {
        throw new Error('Failed to send message')
      }
    } catch (error) {
      console.error('Error sending message:', error)
      toast.error('Failed to send message')
    } finally {
      setSending(false)
    }
  }

  const startVoiceRecognition = () => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      toast.error('Speech recognition not supported in this browser')
      return
    }

    const SpeechRecognition = window.webkitSpeechRecognition || window.SpeechRecognition
    const recognition = new SpeechRecognition()

    recognition.continuous = false
    recognition.interimResults = false
    recognition.lang = 'en-US'

    recognition.onstart = () => {
      setIsListening(true)
    }

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript
      setMessage(transcript)
    }

    recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error)
      toast.error('Speech recognition failed')
    }

    recognition.onend = () => {
      setIsListening(false)
    }

    recognition.start()
  }

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    })
  }

  const getEmotionIcon = (emotion: string) => {
    switch (emotion.toLowerCase()) {
      case 'joy':
      case 'happiness':
        return <Heart className="h-4 w-4 text-pink-500" />
      case 'sadness':
        return <Heart className="h-4 w-4 text-blue-500" />
      case 'anger':
        return <Heart className="h-4 w-4 text-red-500" />
      case 'fear':
        return <Heart className="h-4 w-4 text-purple-500" />
      case 'surprise':
        return <Sparkles className="h-4 w-4 text-yellow-500" />
      default:
        return <Brain className="h-4 w-4 text-gray-500" />
    }
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
          <h1 className="text-3xl font-bold">AI Chat Assistant</h1>
          <p className="text-neutral-11 mt-1">
            Intelligent conversations with mood tracking and emotional support
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button onClick={createNewSession} variant="outline" size="sm">
            <RotateCcw className="h-4 w-4 mr-2" />
            New Chat
          </Button>
        </div>
      </div>

      {/* Stats Overview */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium">Conversations</p>
                  <p className="text-2xl font-bold text-blue-600">{stats.total_conversations}</p>
                </div>
                <MessageCircle className="h-8 w-8 text-blue-600" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium">Messages</p>
                  <p className="text-2xl font-bold text-green-600">{stats.total_messages}</p>
                </div>
                <Send className="h-8 w-8 text-green-600" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium">Mood Improvement</p>
                  <p className="text-2xl font-bold text-pink-600">
                    {(stats.mood_improvement_rate * 100).toFixed(1)}%
                  </p>
                </div>
                <Heart className="h-8 w-8 text-pink-600" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium">Satisfaction</p>
                  <p className="text-2xl font-bold text-purple-600">
                    {(stats.user_satisfaction_score * 10).toFixed(1)}/10
                  </p>
                </div>
                <Sparkles className="h-8 w-8 text-purple-600" />
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      <Tabs defaultValue="chat" className="space-y-4">
        <TabsList>
          <TabsTrigger value="chat">Active Chat</TabsTrigger>
          <TabsTrigger value="history">Chat History</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
        </TabsList>

        <TabsContent value="chat" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
            {/* Chat Interface */}
            <div className="lg:col-span-3">
              <Card className="h-[600px] flex flex-col">
                <CardHeader className="flex-shrink-0 border-b">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Bot className="h-5 w-5 text-blue-600" />
                      <CardTitle>MantraPath AI Assistant</CardTitle>
                      <Badge variant="secondary" className="bg-green-100 text-green-700">
                        Online
                      </Badge>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="flex items-center gap-2">
                        <Label htmlFor="voice-mode" className="text-sm">Voice</Label>
                        <Switch
                          id="voice-mode"
                          checked={voiceEnabled}
                          onCheckedChange={setVoiceEnabled}
                        />
                        {voiceEnabled ? 
                          <Volume2 className="h-4 w-4 text-blue-600" /> : 
                          <VolumeX className="h-4 w-4 text-gray-400" />
                        }
                      </div>
                    </div>
                  </div>
                </CardHeader>

                {/* Messages */}
                <CardContent className="flex-1 overflow-hidden p-0">
                  <ScrollArea className="h-full p-4">
                    <AnimatePresence>
                      {messages.length === 0 ? (
                        <motion.div
                          initial={{ opacity: 0 }}
                          animate={{ opacity: 1 }}
                          className="text-center py-8"
                        >
                          <Bot className="h-12 w-12 text-blue-600 mx-auto mb-4" />
                          <p className="text-lg font-medium mb-2">Welcome to MantraPath AI</p>
                          <p className="text-neutral-11">
                            I'm here to support your emotional wellbeing. Share what's on your mind!
                          </p>
                        </motion.div>
                      ) : (
                        <div className="space-y-4">
                          {messages.map((msg) => (
                            <motion.div
                              key={msg.id}
                              initial={{ opacity: 0, y: 20 }}
                              animate={{ opacity: 1, y: 0 }}
                              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                            >
                              <div className={`max-w-[80%] ${
                                msg.role === 'user' 
                                  ? 'bg-blue-600 text-white' 
                                  : 'bg-gray-100 text-gray-900'
                              } rounded-lg px-4 py-3 space-y-2`}>
                                <div className="flex items-center gap-2 mb-1">
                                  {msg.role === 'user' ? (
                                    <User className="h-4 w-4" />
                                  ) : (
                                    <Bot className="h-4 w-4" />
                                  )}
                                  <span className="text-xs opacity-70">
                                    {formatTimestamp(msg.timestamp)}
                                  </span>
                                </div>
                                
                                <p className="text-sm">{msg.content}</p>

                                {/* Emotion Detection */}
                                {msg.emotions_detected && msg.emotions_detected.length > 0 && (
                                  <div className="flex items-center gap-2 text-xs">
                                    <span className="opacity-70">Emotions:</span>
                                    <div className="flex gap-1">
                                      {msg.emotions_detected.slice(0, 2).map((emotion, index) => (
                                        <div key={index} className="flex items-center gap-1">
                                          {getEmotionIcon(emotion.emotion)}
                                          <span>{emotion.emotion}</span>
                                        </div>
                                      ))}
                                    </div>
                                  </div>
                                )}

                                {/* Conversation Metrics */}
                                {msg.conversation_metrics && msg.role === 'assistant' && (
                                  <div className="flex gap-3 text-xs opacity-70">
                                    <span>Engagement: {(msg.conversation_metrics.engagement_score * 100).toFixed(0)}%</span>
                                    <span>Empathy: {(msg.conversation_metrics.empathy_level * 100).toFixed(0)}%</span>
                                  </div>
                                )}
                              </div>
                            </motion.div>
                          ))}
                          {sending && (
                            <motion.div
                              initial={{ opacity: 0 }}
                              animate={{ opacity: 1 }}
                              className="flex justify-start"
                            >
                              <div className="bg-gray-100 rounded-lg px-4 py-3">
                                <div className="flex items-center gap-2">
                                  <Bot className="h-4 w-4" />
                                  <div className="flex gap-1">
                                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                                  </div>
                                </div>
                              </div>
                            </motion.div>
                          )}
                        </div>
                      )}
                    </AnimatePresence>
                    <div ref={messagesEndRef} />
                  </ScrollArea>
                </CardContent>

                {/* Input Area */}
                <div className="flex-shrink-0 border-t p-4">
                  <div className="flex gap-2">
                    <Input
                      value={message}
                      onChange={(e) => setMessage(e.target.value)}
                      placeholder="Type your message..."
                      className="flex-1"
                      onKeyPress={(e) => {
                        if (e.key === 'Enter' && !e.shiftKey) {
                          e.preventDefault()
                          sendMessage()
                        }
                      }}
                    />
                    <Button
                      variant="outline"
                      size="icon"
                      onClick={startVoiceRecognition}
                      disabled={isListening}
                      className={isListening ? 'bg-red-100 text-red-600' : ''}
                    >
                      {isListening ? (
                        <MicOff className="h-4 w-4" />
                      ) : (
                        <Mic className="h-4 w-4" />
                      )}
                    </Button>
                    <Button 
                      onClick={sendMessage} 
                      disabled={sending || !message.trim()}
                      className="bg-blue-600 hover:bg-blue-700"
                    >
                      <Send className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </Card>
            </div>

            {/* Session Info */}
            <div className="space-y-4">
              {currentSession && (
                <Card>
                  <CardHeader>
                    <CardTitle className="text-sm">Current Session</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div>
                      <p className="text-xs text-neutral-11">Messages</p>
                      <p className="font-semibold">{messages.length}</p>
                    </div>
                    <div>
                      <p className="text-xs text-neutral-11">Started</p>
                      <p className="font-semibold">
                        {new Date(currentSession.created_at).toLocaleTimeString()}
                      </p>
                    </div>
                    {currentSession.topics_discussed && currentSession.topics_discussed.length > 0 && (
                      <div>
                        <p className="text-xs text-neutral-11 mb-1">Topics</p>
                        <div className="flex flex-wrap gap-1">
                          {currentSession.topics_discussed.slice(0, 3).map((topic, index) => (
                            <Badge key={index} variant="secondary" className="text-xs">
                              {topic}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>
              )}

              {stats?.most_common_topics && (
                <Card>
                  <CardHeader>
                    <CardTitle className="text-sm">Popular Topics</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      {stats.most_common_topics.slice(0, 5).map((topic, index) => (
                        <div key={index} className="flex items-center justify-between text-sm">
                          <span>{topic.topic}</span>
                          <Badge variant="outline">{topic.frequency}</Badge>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          </div>
        </TabsContent>

        <TabsContent value="history" className="space-y-4">
          {recentSessions.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {recentSessions.map((session) => (
                <Card key={session.session_id} className="hover:shadow-lg transition-shadow">
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <p className="font-semibold">
                          {new Date(session.created_at).toLocaleDateString()}
                        </p>
                        <p className="text-sm text-neutral-11">
                          {new Date(session.created_at).toLocaleTimeString()}
                        </p>
                      </div>
                      <Badge variant="outline">
                        {session.message_count} messages
                      </Badge>
                    </div>

                    {session.session_summary && (
                      <p className="text-sm text-neutral-11 mb-3">
                        {session.session_summary}
                      </p>
                    )}

                    {session.topics_discussed && session.topics_discussed.length > 0 && (
                      <div className="flex flex-wrap gap-1">
                        {session.topics_discussed.slice(0, 3).map((topic, index) => (
                          <Badge key={index} variant="secondary" className="text-xs">
                            {topic}
                          </Badge>
                        ))}
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <Alert>
              <MessageCircle className="h-4 w-4" />
              <AlertDescription>
                No chat history available. Start a conversation to see your session history.
              </AlertDescription>
            </Alert>
          )}
        </TabsContent>

        <TabsContent value="analytics" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Brain className="h-5 w-5" />
                Conversation Analytics
              </CardTitle>
              <CardDescription>
                Insights into your chat patterns and emotional support effectiveness
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-neutral-11">
                Detailed analytics and insights are being developed. Check back soon for conversation trends and mood impact analysis.
              </p>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}