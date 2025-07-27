import { useState, useCallback, useRef } from 'react'
import { apiService } from '@/services/api'
import { toast } from 'sonner'

interface ChatMessage {
  id: string
  sender: 'user' | 'assistant'
  content: string
  timestamp: string
  messageType?: string
  breathingExercise?: BreathingExercise
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
  const sendMessage = useCallback(async (content: string) => {
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
      const response = await apiService.chatWithBot(content, currentSessionId || undefined)
      
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
        breathingExercise: response.breathing_exercise
      }

      setMessages(prev => [...prev, botMessage])

    } catch (err) {
      if ((err as any).name !== 'AbortError') {
        console.error('Failed to send message:', err)
        setError('Failed to send message')
        toast.error('Failed to send message to chatbot')
      }
    } finally {
      setIsTyping(false)
    }
  }, [currentSessionId])

  // Start new chat session
  const startNewSession = useCallback(async () => {
    try {
      const newSession = await apiService.createChatSession()
      setCurrentSessionId(newSession.id)
      setMessages([])
      
      // Add welcome message
      const welcomeMessage: ChatMessage = {
        id: 'welcome',
        sender: 'assistant',
        content: "Hello! I'm Mantra-Mitra, your wellness companion. I'm here to listen, support you, and help you through difficult moments. How are you feeling today?",
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
      quickActions
    }
  }
}