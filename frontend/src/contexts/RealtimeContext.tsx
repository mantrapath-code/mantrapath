/**
 * Real-time Context Provider for Sprint 2 Backend Integration
 * Manages state from all 8 backend services with real WebSocket connections
 */

import React, { createContext, useContext, useReducer, useEffect, useCallback } from 'react'
import { useRobustWebSocket } from '../hooks/useRobustWebSocket'
import { useAuth } from '../hooks/useAuth'
import type {
  EmotionData,
  RiskData,
  InterventionData,
  ContextData,
  AggregatedData,
  IntelligenceData,
  AssistanceData,
  DeliveryData,
  FeedbackData,
  EvaluationData,
  VoiceData,
  SessionData,
  CommandData,
  NotificationData,
  InteractionData,
  MoodEntryData,
  PatternData,
  QuestionData,
  ChatMessageData,
  CrisisData
} from '../types/backend-events'

// Sprint 2 Real-time State Interface
export interface RealtimeState {
  // Live user context (from AI Context Store Port 8013)
  userContext: ContextData | null
  contextLastUpdated: string | null
  contextIntelligence: IntelligenceData | null
  
  // AI insights (from AI Event Processor Port 8014)
  currentEmotionState: EmotionData | null
  riskScore: RiskData | null
  interventionSuggestions: InterventionData[]
  
  // Assistance state (from Proactive Assistance Engine Port 8018) - Primary Focus
  activeAssistance: AssistanceData | null
  assistanceHistory: AssistanceData[]
  assistanceEvaluations: EvaluationData[]
  assistanceDeliveries: DeliveryData[]
  
  // Voice activity (from Voice Event Processor Port 8015 + API Gateway Port 8000)
  voiceSession: SessionData | null
  voiceCommands: CommandData[]
  voiceActivityLevel: number
  
  // Real-time notifications (from Notification Service Port 3001)
  activeNotifications: NotificationData[]
  notificationHistory: NotificationData[]
  
  // Enhanced mood tracking (from Mood Service Port 8002)
  currentMoodState: MoodEntryData | null
  moodPatterns: PatternData[]
  adaptiveQuestions: QuestionData[]
  
  // Chat intelligence (from Chatbot Service Port 8004)
  chatMessages: ChatMessageData[]
  crisisAlerts: CrisisData[]
  
  // Connection health across all services
  connectionStatus: Record<string, 'connected' | 'connecting' | 'disconnected'>
  lastHeartbeat: Record<string, string>
  serviceHealth: Record<string, 'healthy' | 'degraded' | 'error'>
}

// Actions for state updates
type RealtimeAction = 
  | { type: 'SET_USER_CONTEXT'; payload: ContextData }
  | { type: 'SET_INTELLIGENCE'; payload: IntelligenceData }
  | { type: 'SET_EMOTION_STATE'; payload: EmotionData }
  | { type: 'SET_RISK_SCORE'; payload: RiskData }
  | { type: 'ADD_INTERVENTION'; payload: InterventionData }
  | { type: 'SET_ACTIVE_ASSISTANCE'; payload: AssistanceData }
  | { type: 'ADD_ASSISTANCE_HISTORY'; payload: AssistanceData }
  | { type: 'ADD_ASSISTANCE_EVALUATION'; payload: EvaluationData }
  | { type: 'ADD_ASSISTANCE_DELIVERY'; payload: DeliveryData }
  | { type: 'SET_VOICE_SESSION'; payload: SessionData }
  | { type: 'ADD_VOICE_COMMAND'; payload: CommandData }
  | { type: 'SET_VOICE_ACTIVITY'; payload: number }
  | { type: 'ADD_NOTIFICATION'; payload: NotificationData }
  | { type: 'SET_MOOD_STATE'; payload: MoodEntryData }
  | { type: 'ADD_MOOD_PATTERN'; payload: PatternData }
  | { type: 'ADD_ADAPTIVE_QUESTION'; payload: QuestionData }
  | { type: 'ADD_CHAT_MESSAGE'; payload: ChatMessageData }
  | { type: 'ADD_CRISIS_ALERT'; payload: CrisisData }
  | { type: 'UPDATE_CONNECTION_STATUS'; payload: { service: string; status: string } }
  | { type: 'UPDATE_SERVICE_HEALTH'; payload: { service: string; health: string } }

const initialState: RealtimeState = {
  userContext: null,
  contextLastUpdated: null,
  contextIntelligence: null,
  currentEmotionState: null,
  riskScore: null,
  interventionSuggestions: [],
  activeAssistance: null,
  assistanceHistory: [],
  assistanceEvaluations: [],
  assistanceDeliveries: [],
  voiceSession: null,
  voiceCommands: [],
  voiceActivityLevel: 0,
  activeNotifications: [],
  notificationHistory: [],
  currentMoodState: null,
  moodPatterns: [],
  adaptiveQuestions: [],
  chatMessages: [],
  crisisAlerts: [],
  connectionStatus: {
    notifications: 'disconnected',
    assistance: 'disconnected',
    aiContext: 'disconnected',
    aiEvents: 'disconnected',
    voiceEvents: 'disconnected',
    voice: 'disconnected',
    mood: 'disconnected',
    chat: 'disconnected'
  },
  lastHeartbeat: {},
  serviceHealth: {}
}

function realtimeReducer(state: RealtimeState, action: RealtimeAction): RealtimeState {
  switch (action.type) {
    case 'SET_USER_CONTEXT':
      return {
        ...state,
        userContext: action.payload,
        contextLastUpdated: new Date().toISOString()
      }
    
    case 'SET_INTELLIGENCE':
      return {
        ...state,
        contextIntelligence: action.payload
      }
    
    case 'SET_EMOTION_STATE':
      return {
        ...state,
        currentEmotionState: action.payload
      }
    
    case 'SET_RISK_SCORE':
      return {
        ...state,
        riskScore: action.payload
      }
    
    case 'ADD_INTERVENTION':
      return {
        ...state,
        interventionSuggestions: [...state.interventionSuggestions, action.payload].slice(-10) // Keep last 10
      }
    
    case 'SET_ACTIVE_ASSISTANCE':
      return {
        ...state,
        activeAssistance: action.payload
      }
    
    case 'ADD_ASSISTANCE_HISTORY':
      return {
        ...state,
        assistanceHistory: [...state.assistanceHistory, action.payload].slice(-50) // Keep last 50
      }
    
    case 'ADD_ASSISTANCE_EVALUATION':
      return {
        ...state,
        assistanceEvaluations: [...state.assistanceEvaluations, action.payload].slice(-20) // Keep last 20
      }
    
    case 'ADD_ASSISTANCE_DELIVERY':
      return {
        ...state,
        assistanceDeliveries: [...state.assistanceDeliveries, action.payload].slice(-20)
      }
    
    case 'SET_VOICE_SESSION':
      return {
        ...state,
        voiceSession: action.payload
      }
    
    case 'ADD_VOICE_COMMAND':
      return {
        ...state,
        voiceCommands: [...state.voiceCommands, action.payload].slice(-20)
      }
    
    case 'SET_VOICE_ACTIVITY':
      return {
        ...state,
        voiceActivityLevel: action.payload
      }
    
    case 'ADD_NOTIFICATION':
      return {
        ...state,
        activeNotifications: [...state.activeNotifications, action.payload].slice(-10),
        notificationHistory: [...state.notificationHistory, action.payload].slice(-100)
      }
    
    case 'SET_MOOD_STATE':
      return {
        ...state,
        currentMoodState: action.payload
      }
    
    case 'ADD_MOOD_PATTERN':
      return {
        ...state,
        moodPatterns: [...state.moodPatterns, action.payload].slice(-10)
      }
    
    case 'ADD_ADAPTIVE_QUESTION':
      return {
        ...state,
        adaptiveQuestions: [...state.adaptiveQuestions, action.payload].slice(-5)
      }
    
    case 'ADD_CHAT_MESSAGE':
      return {
        ...state,
        chatMessages: [...state.chatMessages, action.payload].slice(-50)
      }
    
    case 'ADD_CRISIS_ALERT':
      return {
        ...state,
        crisisAlerts: [...state.crisisAlerts, action.payload].slice(-5)
      }
    
    case 'UPDATE_CONNECTION_STATUS':
      return {
        ...state,
        connectionStatus: {
          ...state.connectionStatus,
          [action.payload.service]: action.payload.status as any
        }
      }
    
    case 'UPDATE_SERVICE_HEALTH':
      return {
        ...state,
        serviceHealth: {
          ...state.serviceHealth,
          [action.payload.service]: action.payload.health as any
        }
      }
    
    default:
      return state
  }
}

// Context
const RealtimeContext = createContext<{
  state: RealtimeState
  dispatch: React.Dispatch<RealtimeAction>
  isConnected: boolean
  connectionError: string | null
  reconnectAll: () => void
} | null>(null)

// Provider Component
export function RealtimeProvider({ children }: { children: React.ReactNode }) {
  const { user } = useAuth()
  const [state, dispatch] = useReducer(realtimeReducer, initialState)
  
  const {
    isConnected,
    connectionError,
    addEventHandler,
    reconnectAll
  } = useRobustWebSocket(user?.id)
  
  // Set up event handlers for each backend service
  useEffect(() => {
    if (!user) return
    
    // AI Context Store events (Port 8013)
    addEventHandler('context.updated', {
      id: 'context_updated',
      handler: (message) => {
        if ('context' in message.data) {
          dispatch({ type: 'SET_USER_CONTEXT', payload: message.data as ContextData })
        }
      },
      priority: 2
    })
    
    addEventHandler('context.intelligence_generated', {
      id: 'intelligence_generated',
      handler: (message) => {
        if ('insights' in message.data) {
          dispatch({ type: 'SET_INTELLIGENCE', payload: message.data as IntelligenceData })
        }
      },
      priority: 2
    })
    
    // AI Event Processor events (Port 8014)
    addEventHandler('ai.emotion_detected', {
      id: 'emotion_detected',
      handler: (message) => {
        if ('emotion' in message.data) {
          dispatch({ type: 'SET_EMOTION_STATE', payload: message.data as EmotionData })
        }
      },
      priority: 2
    })
    
    addEventHandler('ai.risk_score_updated', {
      id: 'risk_updated',
      handler: (message) => {
        if ('riskScore' in message.data) {
          dispatch({ type: 'SET_RISK_SCORE', payload: message.data as RiskData })
        }
      },
      priority: 2
    })
    
    addEventHandler('ai.intervention_needed', {
      id: 'intervention_needed',
      handler: (message) => {
        if ('type' in message.data) {
          dispatch({ type: 'ADD_INTERVENTION', payload: message.data as InterventionData })
        }
      },
      priority: 3
    })
    
    // Proactive Assistance Engine events (Port 8018) - Primary Sprint 2 Focus
    addEventHandler('assistance.triggered', {
      id: 'assistance_triggered',
      handler: (message) => {
        if ('assistanceType' in message.data) {
          const assistanceData = message.data as AssistanceData
          dispatch({ type: 'SET_ACTIVE_ASSISTANCE', payload: assistanceData })
          dispatch({ type: 'ADD_ASSISTANCE_HISTORY', payload: assistanceData })
        }
      },
      priority: 3
    })
    
    addEventHandler('assistance.evaluation_complete', {
      id: 'assistance_evaluation',
      handler: (message) => {
        if ('evaluation' in message.data) {
          dispatch({ type: 'ADD_ASSISTANCE_EVALUATION', payload: message.data as EvaluationData })
        }
      },
      priority: 2
    })
    
    addEventHandler('assistance.delivered', {
      id: 'assistance_delivered',
      handler: (message) => {
        if ('deliveryMethod' in message.data) {
          dispatch({ type: 'ADD_ASSISTANCE_DELIVERY', payload: message.data as DeliveryData })
        }
      },
      priority: 2
    })
    
    // Voice Events (Port 8015 + Port 8000)
    addEventHandler('voice.session_started', {
      id: 'voice_session_started',
      handler: (message) => {
        if ('sessionId' in message.data) {
          dispatch({ type: 'SET_VOICE_SESSION', payload: message.data as SessionData })
        }
      },
      priority: 2
    })
    
    addEventHandler('voice.command_processed', {
      id: 'voice_command',
      handler: (message) => {
        if ('command' in message.data) {
          dispatch({ type: 'ADD_VOICE_COMMAND', payload: message.data as CommandData })
        }
      },
      priority: 2
    })
    
    addEventHandler('voice.activity_detected', {
      id: 'voice_activity',
      handler: (message) => {
        if ('activityLevel' in message.data) {
          dispatch({ type: 'SET_VOICE_ACTIVITY', payload: (message.data as VoiceData).activityLevel })
        }
      },
      priority: 1
    })
    
    // Notification events (Port 3001)
    addEventHandler('notification.sent', {
      id: 'notification_sent',
      handler: (message) => {
        if ('title' in message.data) {
          dispatch({ type: 'ADD_NOTIFICATION', payload: message.data as NotificationData })
        }
      },
      priority: 2
    })
    
    // Mood Service events (Port 8002)
    addEventHandler('mood.entry_created', {
      id: 'mood_entry',
      handler: (message) => {
        if ('moodValue' in message.data) {
          dispatch({ type: 'SET_MOOD_STATE', payload: message.data as MoodEntryData })
        }
      },
      priority: 2
    })
    
    addEventHandler('mood.pattern_detected', {
      id: 'mood_pattern',
      handler: (message) => {
        if ('pattern' in message.data) {
          dispatch({ type: 'ADD_MOOD_PATTERN', payload: message.data as PatternData })
        }
      },
      priority: 2
    })
    
    addEventHandler('mood.adaptive_question_triggered', {
      id: 'adaptive_question',
      handler: (message) => {
        if ('question' in message.data) {
          dispatch({ type: 'ADD_ADAPTIVE_QUESTION', payload: message.data as QuestionData })
        }
      },
      priority: 2
    })
    
    // Chat Service events (Port 8004)
    addEventHandler('chat.message_received', {
      id: 'chat_message',
      handler: (message) => {
        if ('messageId' in message.data) {
          dispatch({ type: 'ADD_CHAT_MESSAGE', payload: message.data as ChatMessageData })
        }
      },
      priority: 2
    })
    
    addEventHandler('chat.crisis_detected', {
      id: 'crisis_detected',
      handler: (message) => {
        if ('severity' in message.data) {
          dispatch({ type: 'ADD_CRISIS_ALERT', payload: message.data as CrisisData })
        }
      },
      priority: 3
    })
    
  }, [user, addEventHandler])
  
  // Monitor connection status
  useEffect(() => {
    const services = ['notifications', 'assistance', 'aiContext', 'aiEvents', 'voiceEvents', 'voice', 'mood', 'chat']
    
    services.forEach(service => {
      dispatch({
        type: 'UPDATE_CONNECTION_STATUS',
        payload: { service, status: isConnected ? 'connected' : 'disconnected' }
      })
    })
  }, [isConnected])
  
  return (
    <RealtimeContext.Provider value={{
      state,
      dispatch,
      isConnected,
      connectionError,
      reconnectAll
    }}>
      {children}
    </RealtimeContext.Provider>
  )
}

// Hook to use the realtime context
export function useRealtime() {
  const context = useContext(RealtimeContext)
  if (!context) {
    throw new Error('useRealtime must be used within a RealtimeProvider')
  }
  return context.state
}

export function useRealtimeActions() {
  const context = useContext(RealtimeContext)
  if (!context) {
    throw new Error('useRealtimeActions must be used within a RealtimeProvider')
  }
  return {
    dispatch: context.dispatch,
    isConnected: context.isConnected,
    connectionError: context.connectionError,
    reconnectAll: context.reconnectAll
  }
}
