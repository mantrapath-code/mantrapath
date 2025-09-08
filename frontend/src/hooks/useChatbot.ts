import { useState, useCallback, useRef, useEffect } from 'react'
import { apiService } from '@/services/api'
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
      
      const response = await apiService.chatWithBotEnhanced(enhancedContent, currentSessionId || undefined, isMoodQuery)
      
      // Update session ID if this is a new conversation
      if (!currentSessionId) {
        setCurrentSessionId(response.session_id)
      }

      const botMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        sender: 'assistant',
        content: response.response,
        timestamp: new Date().toISOString(),
        messageType: response.message_type,
        breathingExercise: response.breathing_exercise,
        // Enhanced fields from Action Orchestrator
        intent: response.intent,
        orchestration_metadata: response.orchestration_metadata,
        suggested_actions: response.suggested_actions,
        mood_insights: response.mood_insights,
        cultural_adaptations: response.cultural_adaptations,
        confidence_score: response.confidence_score,
        source: response.source
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
      const newSession = await apiService.createChatSession() as { id: string }
      setCurrentSessionId(newSession.id)
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
      
      const sessionsData = await apiService.getChatSessions()
      setSessions(sessionsData)
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
      
      const history = await apiService.getChatHistory(sessionId)
      
      const formattedMessages: ChatMessage[] = history.map(msg => ({
        id: msg.id,
        sender: msg.sender as 'user' | 'assistant',
        content: msg.content,
        timestamp: msg.created_at,
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
  const getBreathingExercises = useCallback(async () => {
    try {
      const exercisesData = await apiService.getBreathingExercises()
      return exercisesData.exercises
    } catch (err) {
      console.error('Failed to load breathing exercises:', err)
      return {}
    }
  }, [])

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