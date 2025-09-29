/**
 * Chatbot API client using unified httpClient
 * Provides strongly-typed, auth-aware access to chatbot endpoints.
 */
import { post, get } from './httpClient'

export interface ChatSession {
  session_id: string
  created_at: string
  last_activity?: string
  metadata?: Record<string, any>
}

export interface ChatMessage {
  id?: string
  role: 'user' | 'assistant' | 'system'
  content: string
  created_at?: string
  session_id?: string
}

export interface CreateSessionResponse {
  session_id: string
  message?: string
}

export interface ChatHistoryResponse {
  session_id: string
  messages: ChatMessage[]
}

export interface SuggestionsResponse {
  suggestions: string[]
}

export interface SendMessageResponse {
  session_id: string
  message: ChatMessage
  response: ChatMessage
  tokens_used?: number
}

const BASE = '/api/chatbot'

export const chatbotApi = {
  createSession: (initialMessage?: string) => post<CreateSessionResponse>(`${BASE}/chat/session`, initialMessage ? { initial_message: initialMessage } : {}),
  getSession: () => get<ChatSession>(`${BASE}/chat/session`),
  getSessions: () => get<ChatSession[]>(`${BASE}/chat/sessions`),
  sendMessage: (sessionId: string, content: string) => post<SendMessageResponse>(`${BASE}/chat`, { session_id: sessionId, message: content }),
  getHistory: (sessionId: string) => get<ChatHistoryResponse>(`${BASE}/chat/history?session_id=${encodeURIComponent(sessionId)}`),
  getSuggestions: () => get<SuggestionsResponse>(`${BASE}/chat/suggestions`)
}

export type ChatbotApi = typeof chatbotApi
