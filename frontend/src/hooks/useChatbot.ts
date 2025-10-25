import { useState, useCallback, useRef, useEffect } from 'react'
import { apiService } from '@/services/api'
import { chatbotApi, ChatHistoryResponse } from '@/services/chatbotApi'
import { toast } from 'sonner'

interface ChatMessage {
  id: string
  sender: 'user' | 'assistant'
  content: string
  timestamp: string
  messageType?: string
  breathingExercise?: BreathingExercise
  // Enhanced fields from Action Orchestrator
  intent?: {
    intent_type: string
    confidence: number
    entities: any[]
  }
  orchestration_metadata?: {
    workflow_id: string
    execution_time_ms: number
    services_involved: string[]
    success_rate: number
  }
  suggested_actions?: Array<{
    action: string
    label: string
    description: string
    confidence: number
  }>
  mood_insights?: any
  cultural_adaptations?: any
  confidence_score?: number
  source?: string
}

interface BreathingExercise {
  name: string
  description: string
  steps: Array<{
    action: string
    duration: number
    instruction: string
  }>
  cycles: number
}

interface ChatSession {
  id: string
  title: string
  session_type: string
  is_active: boolean
  created_at: string
}

export function useChatbot() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [sessions, setSessions] = useState<ChatSession[]>([])
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [isTyping, setIsTyping] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const abortControllerRef = useRef<AbortController | null>(null)

  // Send message to chatbot
  const sendMessage = useCallback(async (content: string, includeContext: boolean = true) => {
    if (!content.trim()) return

    // Cancel any ongoing request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
    }

    // Create new abort controller
    abortControllerRef.current = new AbortController()

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      sender: 'user',
      content: content.trim(),
      timestamp: new Date().toISOString()
    }

    setMessages(prev => [...prev, userMessage])
    setIsTyping(true)
    setError(null)

    try {
      // Enhanced message with context about available services
      let enhancedContent = content.trim()
      
      if (includeContext) {
        enhancedContent = `${content.trim()}

SYSTEM_CONTEXT: You are Mantra-Mitra, an empathetic AI wellness companion. You have access to:
- Mood tracking service (can analyze sentiment and update user mood)
- Voice service (TTS/STT with emotion analysis)
- Translation service (multi-language support)
- Breathing exercises and wellness techniques
- Community features and peer support
- Crisis intervention protocols

Respond with empathy, understanding, and practical wellness guidance. If user seems distressed, offer immediate support options. Mention relevant features when appropriate.`
      }

      // Check if this is a mood/wellness related query and request context refresh
      const isMoodQuery = /mood|feeling|emotion|journal|community|track|pattern|trend|wellbeing|wellness|mental health|how have i been|how am i doing/i.test(content)
      
      // Replace enhanced chat with basic send + maintain session; TODO: implement enhanced endpoint bridging
      if (!currentSessionId) {
        const sessionResp = await chatbotApi.createSession()
        const sid = (sessionResp as any).session_id
        setCurrentSessionId(sid)
      }
      const sid = currentSessionId || (localStorage.getItem('chat_session_id') || '')
      const sendResp = await chatbotApi.sendMessage(sid, enhancedContent)
      
      // Handle different response formats from the API
      let responseContent = ''
      let messageType = 'standard'
      
      if (typeof sendResp === 'string') {
        // Response is a simple string
        responseContent = sendResp
      } else if (sendResp.response) {
        if (typeof sendResp.response === 'string') {
          // Response has a 'response' field that's a string
          responseContent = sendResp.response
          messageType = (sendResp as any).message_type || 'standard'
        } else if (sendResp.response.content) {
          // Response has a 'response' field that's an object with 'content'
          responseContent = sendResp.response.content
          messageType = sendResp.response.message_type || 'standard'
        }
      } else if (sendResp.content) {
        // Response is a ChatMessage object
        responseContent = sendResp.content
      }

      const botMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        sender: 'assistant',
        content: responseContent,
        timestamp: new Date().toISOString(),
        messageType: messageType,
        breathingExercise: undefined,
        intent: undefined,
        orchestration_metadata: undefined,
        suggested_actions: undefined,
        mood_insights: undefined,
        cultural_adaptations: undefined,
        confidence_score: undefined,
        source: 'chatbot'
      }

      setMessages(prev => [...prev, botMessage])

    } catch (err) {
      if ((err as any).name !== 'AbortError') {
        console.error('Failed to send message:', err)
        setError('Failed to send message')
        
        // Provide a helpful fallback response instead of just an error
        const fallbackResponses = [
          "I'm sorry, I'm having some connection issues right now. In the meantime, here are some wellness tips: Take a few deep breaths, drink some water, and remember that you're not alone. 💙",
          "I can't connect to the server at the moment, but I want you to know that your wellness matters. Try stepping outside for some fresh air or listening to calming music. 🌱",
          "While I work on reconnecting, here's a gentle reminder: it's okay to take things one moment at a time. Consider doing a brief mindfulness exercise or reaching out to someone you trust. ✨",
          "I'm experiencing technical difficulties, but your mental health journey is important. Take a moment to check in with yourself - how are you feeling right now? Remember to be kind to yourself. 🌸"
        ]
        
        const randomResponse = fallbackResponses[Math.floor(Math.random() * fallbackResponses.length)]
        
        const fallbackMessage: ChatMessage = {
          id: (Date.now() + 1).toString(),
          sender: 'assistant',
          content: randomResponse,
          timestamp: new Date().toISOString(),
          messageType: 'fallback',
          source: 'fallback',
          confidence_score: 0.5
        }
        
        setMessages(prev => [...prev, fallbackMessage])
        toast.warning('Using offline mode - limited functionality available')
      }
    } finally {
      setIsTyping(false)
    }
  }, [currentSessionId])

  // Start new chat session
  const startNewSession = useCallback(async () => {
    try {
      const newSession = await chatbotApi.createSession()
      const newId = (newSession as any).session_id || (newSession as any).id
      if (newId) {
        setCurrentSessionId(newId)
        localStorage.setItem('chat_session_id', newId)
      }
      setMessages([])
      
      // Add personalized welcome message
      const getPersonalizedWelcome = () => {
        const hour = new Date().getHours()
        let timeGreeting = ''
        
        if (hour < 12) timeGreeting = 'Good morning'
        else if (hour < 17) timeGreeting = 'Good afternoon'
        else timeGreeting = 'Good evening'
        
        // Get user name from context if available (you can enhance this)
        const userName = 'there' // TODO: Get from user profile
        
        return `${timeGreeting} ${userName}! 👋 I'm Mantra-Mitra, your wellness companion.

I'm here to listen, support, and help you on your wellness journey. 

💬 **How can I help you today?**
• Share how you're feeling
• Get breathing exercises
• Practice mindfulness
• Track your mood
• Or just chat about anything

You can type or speak to me in any language - I'll understand and respond appropriately. 🌸`
      }
      
      const welcomeMessage: ChatMessage = {
        id: 'welcome',
        sender: 'assistant',
        content: getPersonalizedWelcome(),
        timestamp: new Date().toISOString(),
        messageType: 'greeting'
      }
      
      setMessages([welcomeMessage])
      
    } catch (err) {
      console.error('Failed to start new session:', err)
      toast.error('Failed to start new chat session')
    }
  }, [])

  // Load chat sessions
  const loadSessions = useCallback(async () => {
    try {
      // Refresh token before making the request
      apiService.refreshToken()
      
      const sessionsData = await chatbotApi.getSessions()
      // Adapt minimal session objects if needed
      const adapted = Array.isArray(sessionsData) ? sessionsData.map((s: any) => ({
        id: s.session_id || s.id || s.sessionId || Math.random().toString(),
        title: s.title || 'Session',
        session_type: s.session_type || 'standard',
        is_active: s.is_active ?? true,
        created_at: s.created_at || new Date().toISOString()
      })) : []
      setSessions(adapted as any)
    } catch (err: any) {
      console.error('Failed to load sessions:', err)
      
      // Handle authentication errors gracefully
      if (err.status === 401) {
        console.log('User not authenticated, skipping session load')
      } else if (err.status === 0) {
        console.log('Chat service unavailable, skipping session load')
      }
    }
  }, [])

  // Load chat history for a session
  const loadChatHistory = useCallback(async (sessionId: string) => {
    try {
      setLoading(true)
      setError(null)
      
      // Refresh token before making the request
      apiService.refreshToken()
      
      const historyResp = await chatbotApi.getHistory(sessionId) as ChatHistoryResponse
      const items = historyResp?.messages || []
      const formattedMessages: ChatMessage[] = items.map((msg: any) => ({
        id: msg.id || Math.random().toString(),
        sender: (msg.role === 'assistant' ? 'assistant' : 'user'),
        content: msg.content,
        timestamp: msg.created_at || new Date().toISOString(),
        messageType: msg.message_type
      }))
      
      setMessages(formattedMessages)
      setCurrentSessionId(sessionId)
      
    } catch (err: any) {
      console.error('Failed to load chat history:', err)
      
      // Handle specific error cases
      if (err.status === 401) {
        setError('Authentication required. Please log in again.')
        toast.error('Please log in to access chat history')
      } else if (err.status === 404) {
        setError('Chat session not found.')
        toast.error('Chat session not found')
      } else if (err.status === 0) {
        setError('Unable to connect to chat service.')
        toast.error('Chat service is unavailable')
      } else {
        setError('Failed to load chat history.')
        toast.error('Failed to load chat history')
      }
    } finally {
      setLoading(false)
    }
  }, [])

  // Get breathing exercises
  // Placeholder until breathing exercises endpoint standardized
  const getBreathingExercises = useCallback(async () => ({ exercises: [] }), [])

  // Quick actions for common scenarios
  const quickActions = {
    requestBreathingExercise: () => sendMessage("I need help with breathing exercises"),
    expressAnxiety: () => sendMessage("I'm feeling anxious and need support"),
    expressSadness: () => sendMessage("I'm feeling really sad today"),
    askForHelp: () => sendMessage("I need help and don't know what to do"),
    checkIn: () => sendMessage("I just want to check in and share how I'm feeling")
  }

  // Clear current conversation
  const clearConversation = useCallback(() => {
    setMessages([])
    setCurrentSessionId(null)
    setError(null)
  }, [])

  // Stop any ongoing request
  const stopGeneration = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
      setIsTyping(false)
    }
  }, [])

  // Initialize chatbot - restore session and load history
  const initializeChatbot = useCallback(async () => {
    try {
      // First check if user is authenticated
      const token = localStorage.getItem('mantrapath_token')
      if (!token) {
        console.log('No auth token found, starting with welcome message')
        const welcomeMessage: ChatMessage = {
          id: 'welcome',
          sender: 'assistant',
          content: 'Hello! I\'m Mantra-Mitra, your AI wellness companion. Please log in to access full chat features.',
          timestamp: new Date().toISOString(),
          messageType: 'greeting'
        }
        setMessages([welcomeMessage])
        return
      }
      
      // Load sessions first (this will fail gracefully if service is down)
      await loadSessions()
      
      // Try to restore last session from localStorage
      const lastSessionId = localStorage.getItem('mantrapath_last_chat_session')
      
      if (lastSessionId) {
        // Try to load history for the last session
        try {
          await loadChatHistory(lastSessionId)
          console.log('Restored chat session:', lastSessionId)
        } catch (err: any) {
          console.log('Could not restore last session:', err.message)
          // If we can't restore, clear the invalid session and start new
          localStorage.removeItem('mantrapath_last_chat_session')
          await startNewSession()
        }
      } else {
        // No previous session, start a new one
        await startNewSession()
      }
    } catch (err: any) {
      console.error('Failed to initialize chatbot:', err)
      // Fallback: start with welcome message without session
      const welcomeMessage: ChatMessage = {
        id: 'welcome',
        sender: 'assistant',
        content: 'Hello! I\'m Mantra-Mitra, your AI wellness companion. How are you feeling today?',
        timestamp: new Date().toISOString(),
        messageType: 'greeting'
      }
      setMessages([welcomeMessage])
    }
  }, [loadSessions, loadChatHistory, startNewSession])

  // Save session ID to localStorage when it changes
  useEffect(() => {
    if (currentSessionId) {
      localStorage.setItem('mantrapath_last_chat_session', currentSessionId)
    }
  }, [currentSessionId])

  // Initialize on mount
  useEffect(() => {
    initializeChatbot()
  }, []) // Empty dependency array - only run once on mount

  return {
    messages,
    sessions,
    currentSessionId,
    loading,
    isTyping,
    error,
    actions: {
      sendMessage,
      startNewSession,
      loadSessions,
      loadChatHistory,
      getBreathingExercises,
      clearConversation,
      stopGeneration,
      initializeChatbot,
      quickActions
    }
  }
}