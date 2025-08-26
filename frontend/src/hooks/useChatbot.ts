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
      
      // Add comprehensive welcome message
      const welcomeMessage: ChatMessage = {
        id: 'welcome',
        sender: 'assistant',
        content: `Hello! 💜 I'm Mantra-Mitra, your AI wellness companion. I'm here to provide emotional support, listen to your feelings, and help you on your wellness journey.

🌟 **What I can help you with:**
• **Emotional Support** - Share how you're feeling and I'll listen with empathy
• **Mood Tracking** - I automatically analyze your emotions and update your mood
• **Voice Conversations** - Speak to me naturally, I understand multiple languages
• **Breathing Exercises** - Get guided breathing exercises when you need to relax
• **Wellness Insights** - Access personalized insights about your mental health patterns
• **Crisis Support** - Get immediate help if you're in distress

🗣️ **Voice Features:**
• Speak in any language - I'll detect and respond appropriately
• I can speak back to you with natural voice synthesis
• Your conversations help me understand your emotional state better

💭 **Privacy & Care:**
• Everything you share is confidential and secure
• I analyze sentiment to better understand your needs
• Your mood patterns help provide personalized support

How are you feeling today? You can speak to me or type - whatever feels most comfortable! 🌸`,
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
      const sessionsData = await apiService.getChatSessions()
      setSessions(sessionsData)
    } catch (err) {
      console.error('Failed to load sessions:', err)
    }
  }, [])

  // Load chat history for a session
  const loadChatHistory = useCallback(async (sessionId: string) => {
    try {
      setLoading(true)
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
      
    } catch (err) {
      console.error('Failed to load chat history:', err)
      toast.error('Failed to load chat history')
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
      // Load sessions first
      await loadSessions()
      
      // Try to restore last session from localStorage
      const lastSessionId = localStorage.getItem('mantrapath_last_chat_session')
      
      if (lastSessionId) {
        // Try to load history for the last session
        try {
          await loadChatHistory(lastSessionId)
          console.log('Restored chat session:', lastSessionId)
        } catch (err) {
          console.log('Could not restore last session, starting new one')
          // If we can't restore, start fresh but don't show error to user
          localStorage.removeItem('mantrapath_last_chat_session')
          await startNewSession()
        }
      } else {
        // No previous session, start a new one
        await startNewSession()
      }
    } catch (err) {
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