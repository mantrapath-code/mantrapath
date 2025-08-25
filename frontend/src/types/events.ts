// Shared frontend event types mirroring backend shared models

export type UrgencyLevel = 'critical' | 'high' | 'medium' | 'low' | 'none'

export interface AssistanceInterventionNeeded {
  user_id: string
  risk_level: UrgencyLevel | string
  recommended_actions: string[]
  reason: string
  ts: string
}

export interface AssistanceTriggered {
  user_id: string
  assistance_type?: string | null
  channel?: string | null
  ts: string
}

export interface AssistanceDelivered {
  user_id: string
  assistance_type?: string | null
  status: string
  ts: string
}

export interface AssistanceUserResponse {
  user_id: string
  assistance_type?: string | null
  response: 'accepted' | 'declined'
  feedback?: string
  ts: string
}

export interface ContextUpdated {
  user_id: string
  fields_changed: string[]
  ts: string
}

export interface AIEmotionDetected {
  user_id: string
  emotion: string
  score: number
  ts: string
}

export interface VoiceActivityDetected {
  user_id: string
  activity: string
  details?: Record<string, any>
  ts: string
}

export type EventEnvelope<T = unknown> = {
  type: string
  data: T
  timestamp: string
  id?: string
  priority?: 'low' | 'normal' | 'high' | 'critical'
}
