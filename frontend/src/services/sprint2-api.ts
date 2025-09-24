/**
 * Sprint 2 Backend API Integration Service
 * Direct integration with real backend services - no mocks
 */

import { getAuthToken } from '../utils/auth'

// Get environment-aware API base URL
const getApiBaseUrl = () => {
  return import.meta.env.VITE_API_GATEWAY_URL || import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
};

// Real Backend Service Endpoints - Sprint 2
const BACKEND_API_ENDPOINTS = {
  // API Gateway (Port 8000) - Primary entry point
  gateway: {
    base: getApiBaseUrl(),
    health: '/api/v3/health/enhanced',
    voiceCommand: '/api/v3/voice/command',
    metrics: '/api/v3/metrics/performance'
  },
  
  // AI Context Store (Port 8013) - via API Gateway
  context: {
    base: `${getApiBaseUrl()}/ai-context`,
    root: '/',
    metrics: '/metrics'
  },
  
  // AI Event Processor (Port 8014) - via API Gateway
  aiEvents: {
    base: `${getApiBaseUrl()}/ai-events`,
    health: '/health',
    metrics: '/metrics'
  },
  
  // Voice Event Processor (Port 8015) - via API Gateway
  voiceEvents: {
    base: `${getApiBaseUrl()}/voice-events`,
    health: '/health',
    metrics: '/metrics'
  },
  
  // Proactive Assistance Engine (Port 8018) - via API Gateway
  assistance: {
    base: `${getApiBaseUrl()}/assistance`,
    evaluate: (userId: string) => `/api/v3/assistance/evaluate/${userId}`,
    status: (userId: string) => `/api/v3/assistance/status/${userId}`,
    trigger: (userId: string) => `/api/v3/assistance/trigger/${userId}`,
    voiceAssistance: (userId: string) => `/api/v3/assistance/voice/${userId}`,
    multilingualResponse: '/api/v3/assistance/multilingual-response',
    sentimentAnalysis: '/api/v3/assistance/sentiment-analysis',
    modelsStatus: '/api/v3/models/status',
    health: '/health',
    metrics: '/metrics'
  },
  
  // Notification Service (Port 8007) - via API Gateway
  notifications: {
    base: `${getApiBaseUrl()}/notifications`,
    health: '/health',
    // WebSocket primary: /ws/{user_id}
  },
  
  // Mood Service (Port 8002) - via API Gateway
  mood: {
    base: `${getApiBaseUrl()}/mood`,
    health: '/health',
    // Align with API Gateway router rules (supports /mood/* or /api/v1/mood/*)
    entries: '/api/v1/mood/entries',
    patterns: '/api/v1/mood/patterns',
    insights: '/api/v1/mood/insights'
  },
  
  // Chatbot Service (Port 8004) - via API Gateway
  chatbot: {
    base: `${getApiBaseUrl()}/chatbot`,
    health: '/health',
    // API Gateway routes chatbot under /api/chatbot/* (and /chat/*)
    chat: '/api/chatbot/chat',
    sessions: '/api/chatbot/chat/sessions'
  }
}

class Sprint2ApiService {
  private getHeaders(): HeadersInit {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    }

    const token = getAuthToken()
    if (token) {
      headers.Authorization = `Bearer ${token}`
    }

    return headers
  }

  private async makeRequest<T>(url: string, options: RequestInit = {}): Promise<T> {
    const response = await fetch(url, {
      ...options,
      headers: {
        ...this.getHeaders(),
        ...options.headers
      }
    })

    if (!response.ok) {
      throw new Error(`API request failed: ${response.status} ${response.statusText}`)
    }

    return response.json()
  }

  // Proactive Assistance Engine API calls (Port 8018) - Primary Sprint 2 Focus
  async evaluateAssistance(userId: string, context?: any): Promise<any> {
    return this.makeRequest(
      `${BACKEND_API_ENDPOINTS.assistance.base}${BACKEND_API_ENDPOINTS.assistance.evaluate(userId)}`,
      {
        method: 'POST',
        body: context ? JSON.stringify(context) : undefined
      }
    )
  }

  async getAssistanceStatus(userId: string): Promise<any> {
    return this.makeRequest(
      `${BACKEND_API_ENDPOINTS.assistance.base}${BACKEND_API_ENDPOINTS.assistance.status(userId)}`
    )
  }

  async triggerAssistance(userId: string, trigger?: any): Promise<any> {
    return this.makeRequest(
      `${BACKEND_API_ENDPOINTS.assistance.base}${BACKEND_API_ENDPOINTS.assistance.trigger(userId)}`,
      {
        method: 'POST',
        body: trigger ? JSON.stringify(trigger) : undefined
      }
    )
  }

  async getVoiceAssistance(userId: string, audioData?: any): Promise<any> {
    return this.makeRequest(
      `${BACKEND_API_ENDPOINTS.assistance.base}${BACKEND_API_ENDPOINTS.assistance.voiceAssistance(userId)}`,
      {
        method: 'POST',
        body: audioData ? JSON.stringify(audioData) : undefined
      }
    )
  }

  async getMultilingualResponse(request: any): Promise<any> {
    return this.makeRequest(
      `${BACKEND_API_ENDPOINTS.assistance.base}${BACKEND_API_ENDPOINTS.assistance.multilingualResponse}`,
      {
        method: 'POST',
        body: JSON.stringify(request)
      }
    )
  }

  async analyzeSentiment(text: string): Promise<any> {
    return this.makeRequest(
      `${BACKEND_API_ENDPOINTS.assistance.base}${BACKEND_API_ENDPOINTS.assistance.sentimentAnalysis}`,
      {
        method: 'POST',
        body: JSON.stringify({ text })
      }
    )
  }

  async getModelsStatus(): Promise<any> {
    return this.makeRequest(
      `${BACKEND_API_ENDPOINTS.assistance.base}${BACKEND_API_ENDPOINTS.assistance.modelsStatus}`
    )
  }

  // AI Context Store API calls (Port 8013)
  async getContextRoot(): Promise<any> {
    return this.makeRequest(
      `${BACKEND_API_ENDPOINTS.context.base}${BACKEND_API_ENDPOINTS.context.root}`
    )
  }

  async getContextMetrics(): Promise<any> {
    return this.makeRequest(
      `${BACKEND_API_ENDPOINTS.context.base}${BACKEND_API_ENDPOINTS.context.metrics}`
    )
  }

  // Voice Command API (API Gateway Port 8000)
  async sendVoiceCommand(command: any): Promise<any> {
    return this.makeRequest(
      `${BACKEND_API_ENDPOINTS.gateway.base}${BACKEND_API_ENDPOINTS.gateway.voiceCommand}`,
      {
        method: 'POST',
        body: JSON.stringify(command)
      }
    )
  }

  // Mood Service API calls (Port 8002)
  async getMoodEntries(userId: string, limit?: number): Promise<any> {
    const params = new URLSearchParams()
    if (limit) params.append('limit', limit.toString())
    
    return this.makeRequest(
      `${BACKEND_API_ENDPOINTS.mood.base}${BACKEND_API_ENDPOINTS.mood.entries}?${params}`
    )
  }

  async getMoodPatterns(userId: string): Promise<any> {
    return this.makeRequest(
      `${BACKEND_API_ENDPOINTS.mood.base}${BACKEND_API_ENDPOINTS.mood.patterns}?user_id=${userId}`
    )
  }

  async getMoodInsights(userId: string): Promise<any> {
    return this.makeRequest(
      `${BACKEND_API_ENDPOINTS.mood.base}${BACKEND_API_ENDPOINTS.mood.insights}?user_id=${userId}`
    )
  }

  async createMoodEntry(moodData: any): Promise<any> {
    return this.makeRequest(
      `${BACKEND_API_ENDPOINTS.mood.base}${BACKEND_API_ENDPOINTS.mood.entries}`,
      {
        method: 'POST',
        body: JSON.stringify(moodData)
      }
    )
  }

  // Chatbot Service API calls (Port 8004)
  async sendChatMessage(message: string, sessionId?: string): Promise<any> {
    return this.makeRequest(
      `${BACKEND_API_ENDPOINTS.chatbot.base}${BACKEND_API_ENDPOINTS.chatbot.chat}`,
      {
        method: 'POST',
        body: JSON.stringify({ message, session_id: sessionId })
      }
    )
  }

  async getChatSessions(userId: string): Promise<any> {
    return this.makeRequest(
      `${BACKEND_API_ENDPOINTS.chatbot.base}${BACKEND_API_ENDPOINTS.chatbot.sessions}?user_id=${userId}`
    )
  }

  // Health checks for all services
  async checkServiceHealth(): Promise<Record<string, any>> {
    const healthChecks = await Promise.allSettled([
      this.checkAssistanceHealth(),
      this.checkContextHealth(),
      this.checkAiEventsHealth(),
      this.checkVoiceEventsHealth(),
      this.checkNotificationsHealth(),
      this.checkMoodHealth(),
      this.checkChatbotHealth(),
      this.checkGatewayHealth()
    ])

    return {
      assistance: healthChecks[0],
      context: healthChecks[1],
      aiEvents: healthChecks[2],
      voiceEvents: healthChecks[3],
      notifications: healthChecks[4],
      mood: healthChecks[5],
      chatbot: healthChecks[6],
      gateway: healthChecks[7]
    }
  }

  private async checkAssistanceHealth(): Promise<any> {
    try {
      return await this.makeRequest(
        `${BACKEND_API_ENDPOINTS.assistance.base}${BACKEND_API_ENDPOINTS.assistance.health}`
      )
    } catch (error) {
      return { status: 'error', error: error.message }
    }
  }

  private async checkContextHealth(): Promise<any> {
    try {
      return await this.makeRequest(
        `${BACKEND_API_ENDPOINTS.context.base}${BACKEND_API_ENDPOINTS.context.root}`
      )
    } catch (error) {
      return { status: 'error', error: error.message }
    }
  }

  private async checkAiEventsHealth(): Promise<any> {
    try {
      return await this.makeRequest(
        `${BACKEND_API_ENDPOINTS.aiEvents.base}${BACKEND_API_ENDPOINTS.aiEvents.health}`
      )
    } catch (error) {
      return { status: 'error', error: error.message }
    }
  }

  private async checkVoiceEventsHealth(): Promise<any> {
    try {
      return await this.makeRequest(
        `${BACKEND_API_ENDPOINTS.voiceEvents.base}${BACKEND_API_ENDPOINTS.voiceEvents.health}`
      )
    } catch (error) {
      return { status: 'error', error: error.message }
    }
  }

  private async checkNotificationsHealth(): Promise<any> {
    try {
      return await this.makeRequest(
        `${BACKEND_API_ENDPOINTS.notifications.base}${BACKEND_API_ENDPOINTS.notifications.health}`
      )
    } catch (error) {
      return { status: 'error', error: error.message }
    }
  }

  private async checkMoodHealth(): Promise<any> {
    try {
      return await this.makeRequest(
        `${BACKEND_API_ENDPOINTS.mood.base}${BACKEND_API_ENDPOINTS.mood.health}`
      )
    } catch (error) {
      return { status: 'error', error: error.message }
    }
  }

  private async checkChatbotHealth(): Promise<any> {
    try {
      return await this.makeRequest(
        `${BACKEND_API_ENDPOINTS.chatbot.base}${BACKEND_API_ENDPOINTS.chatbot.health}`
      )
    } catch (error) {
      return { status: 'error', error: error.message }
    }
  }

  private async checkGatewayHealth(): Promise<any> {
    try {
      return await this.makeRequest(
        `${BACKEND_API_ENDPOINTS.gateway.base}${BACKEND_API_ENDPOINTS.gateway.health}`
      )
    } catch (error) {
      return { status: 'error', error: error.message }
    }
  }

  // Get comprehensive metrics from all services
  async getAllServiceMetrics(): Promise<Record<string, any>> {
    const metricsChecks = await Promise.allSettled([
      this.getAssistanceMetrics(),
      this.getContextMetrics(),
      this.getGatewayMetrics()
    ])

    return {
      assistance: metricsChecks[0],
      context: metricsChecks[1],
      gateway: metricsChecks[2]
    }
  }

  private async getAssistanceMetrics(): Promise<any> {
    try {
      return await this.makeRequest(
        `${BACKEND_API_ENDPOINTS.assistance.base}${BACKEND_API_ENDPOINTS.assistance.metrics}`
      )
    } catch (error) {
      return { status: 'error', error: error.message }
    }
  }

  private async getGatewayMetrics(): Promise<any> {
    try {
      return await this.makeRequest(
        `${BACKEND_API_ENDPOINTS.gateway.base}${BACKEND_API_ENDPOINTS.gateway.metrics}`
      )
    } catch (error) {
      return { status: 'error', error: error.message }
    }
  }
}

// Export singleton instance
export const sprint2ApiService = new Sprint2ApiService()

// Export API endpoints for use in other components
export { BACKEND_API_ENDPOINTS }
