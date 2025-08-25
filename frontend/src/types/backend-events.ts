/**
 * Backend Event Types for Sprint 2 Real-time Integration
 * Based on actual backend services discovered in MantraPath
 */

// Common base interfaces
export interface BaseEventData {
  userId: string
  timestamp: string
  servicePort: number
  source: string
}

// AI Event Processor (Port 8014) Event Types
export interface EmotionData extends BaseEventData {
  emotion: string
  confidence: number
  valence: number
  arousal: number
  context?: string
  triggers?: string[]
}

export interface RiskData extends BaseEventData {
  riskScore: number
  factors: string[]
  severity: 'low' | 'medium' | 'high' | 'critical'
  recommendations: string[]
}

export interface InterventionData extends BaseEventData {
  type: 'crisis' | 'mood' | 'support' | 'guidance'
  urgency: 'low' | 'medium' | 'high' | 'immediate'
  message: string
  actions: string[]
  culturalContext?: string
}

// AI Context Store (Port 8013) Event Types
export interface ContextData extends BaseEventData {
  context: {
    mood: number
    energy: number
    stress: number
    engagement: number
    recentActivities: string[]
    patterns: string[]
  }
  culturalProfile?: {
    language: string
    region: string
    communicationStyle: string
  }
}

export interface AggregatedData extends BaseEventData {
  aggregatedInsights: {
    moodTrend: 'improving' | 'stable' | 'declining'
    riskFactors: string[]
    strengths: string[]
    opportunities: string[]
  }
  crossServiceData: Record<string, any>
}

export interface IntelligenceData extends BaseEventData {
  insights: {
    type: 'pattern' | 'prediction' | 'recommendation'
    content: string
    confidence: number
    actionable: boolean
  }[]
  predictions: {
    moodForecast: number[]
    riskProbability: number
    engagementTrend: string
  }
}

// Proactive Assistance Engine (Port 8018) Event Types - Primary Sprint 2 Focus
export interface AssistanceData extends BaseEventData {
  assistanceType: 'proactive' | 'reactive' | 'preventive'
  suggestion: {
    message: string
    culturalTone: string
    urgency: 'low' | 'medium' | 'high'
    category: 'wellness' | 'mood' | 'social' | 'achievement'
  }
  evaluationScore: number
  responseTimeMs: number
}

export interface DeliveryData extends BaseEventData {
  deliveryMethod: 'notification' | 'overlay' | 'voice' | 'chat'
  assistanceId: string
  culturalAdaptations: {
    language: string
    tone: string
    formality: 'casual' | 'formal'
  }
}

export interface FeedbackData extends BaseEventData {
  assistanceId: string
  response: 'accepted' | 'declined' | 'deferred'
  reason?: string
  rating?: number
  culturalFeedback?: string
}

export interface EvaluationData extends BaseEventData {
  evaluation: {
    contextScore: number
    culturalFit: number
    timingScore: number
    overallScore: number
  }
  factors: string[]
  improvements: string[]
}

// Voice Event Processor (Port 8015) + API Gateway (Port 8000) Event Types
export interface VoiceData extends BaseEventData {
  activityLevel: number
  sessionId?: string
  duration?: number
  language?: string
  confidence?: number
}

export interface SessionData extends BaseEventData {
  sessionId: string
  action: 'started' | 'ended' | 'paused' | 'resumed'
  duration?: number
  quality?: number
  language?: string
}

export interface CommandData extends BaseEventData {
  command: string
  intent: string
  confidence: number
  response?: string
  culturalContext?: string
}

// Notification Service (Port 3001) Event Types
export interface NotificationData extends BaseEventData {
  id: string
  type: 'info' | 'warning' | 'success' | 'error' | 'assistance'
  title: string
  message: string
  priority: 'low' | 'normal' | 'high' | 'critical'
  culturalTone?: string
  actionable?: boolean
}

export interface InteractionData extends BaseEventData {
  notificationId: string
  interaction: 'viewed' | 'clicked' | 'dismissed' | 'acted'
  timeToInteraction?: number
  context?: string
}

// Mood Service (Port 8002) Event Types
export interface MoodEntryData extends BaseEventData {
  moodValue: number
  energyLevel: number
  stressLevel: number
  notes?: string
  triggers?: string[]
  adaptiveQuestionTriggered?: boolean
}

export interface PatternData extends BaseEventData {
  pattern: {
    type: 'daily' | 'weekly' | 'seasonal' | 'contextual'
    description: string
    strength: number
    trend: 'improving' | 'stable' | 'declining'
  }
  insights: string[]
  recommendations: string[]
}

export interface QuestionData extends BaseEventData {
  question: {
    id: string
    text: string
    type: 'scale' | 'choice' | 'text'
    options?: string[]
    culturalContext?: string
  }
  trigger: string
  priority: number
}

// Chat Service (Port 8004) Event Types
export interface ChatMessageData extends BaseEventData {
  messageId: string
  content: string
  type: 'user' | 'bot' | 'system'
  sentiment?: number
  intent?: string
  responseTime?: number
}

export interface ChatInsight extends BaseEventData {
  insight: {
    type: 'emotional_state' | 'crisis_indicator' | 'progress_marker'
    confidence: number
    description: string
    recommendations: string[]
  }
  interventionSuggested?: boolean
}

export interface CrisisData extends BaseEventData {
  severity: 'mild' | 'moderate' | 'severe' | 'critical'
  indicators: string[]
  immediateActions: string[]
  escalationRequired: boolean
  culturalConsiderations?: string[]
}

// Union type for all possible event data
export type AllEventData = 
  | EmotionData 
  | RiskData 
  | InterventionData
  | ContextData 
  | AggregatedData 
  | IntelligenceData
  | AssistanceData 
  | DeliveryData 
  | FeedbackData 
  | EvaluationData
  | VoiceData 
  | SessionData 
  | CommandData
  | NotificationData 
  | InteractionData
  | MoodEntryData 
  | PatternData 
  | QuestionData
  | ChatMessageData 
  | ChatInsight 
  | CrisisData

// Event type mapping for type safety
export interface BackendEventTypeMap {
  'ai.emotion_detected': EmotionData
  'ai.risk_score_updated': RiskData
  'ai.intervention_needed': InterventionData
  'context.updated': ContextData
  'context.aggregated': AggregatedData
  'context.intelligence_generated': IntelligenceData
  'assistance.triggered': AssistanceData
  'assistance.delivered': DeliveryData
  'assistance.accepted': FeedbackData
  'assistance.declined': FeedbackData
  'assistance.evaluation_complete': EvaluationData
  'voice.activity_detected': VoiceData
  'voice.session_started': SessionData
  'voice.session_ended': SessionData
  'voice.command_processed': CommandData
  'notification.sent': NotificationData
  'notification.delivered': DeliveryData
  'notification.interacted': InteractionData
  'mood.entry_created': MoodEntryData
  'mood.pattern_detected': PatternData
  'mood.adaptive_question_triggered': QuestionData
  'chat.message_received': ChatMessageData
  'chat.intervention_suggested': InterventionData
  'chat.crisis_detected': CrisisData
}
