/**
 * Voice Service API Client
 * Handles communication with the voice service backend
 */

import { get, post } from './httpClient'

export interface VoiceServiceConfig {
  baseUrl?: string
  timeout?: number
}

export interface AudioProcessingOptions {
  sampleRate?: number
  channels?: number
  format?: 'wav' | 'mp3' | 'webm'
  enhanceAudio?: boolean
  detectLanguage?: boolean
}

export interface SpeechToTextRequest {
  audioData: Blob | ArrayBuffer
  language?: string
  options?: AudioProcessingOptions
}

export interface SpeechToTextResponse {
  success: boolean
  transcription?: string
  confidence?: number
  language?: string
  duration?: number
  error?: string
}

export interface TextToSpeechRequest {
  text: string
  language?: string
  voice?: string
  speed?: number
  pitch?: number
}

export interface TextToSpeechResponse {
  success: boolean
  audioUrl?: string
  audioBlob?: Blob
  duration?: number
  error?: string
}

export interface VoiceSessionData {
  sessionId: string
  userId?: string
  metadata?: Record<string, any>
}

export interface ConversationContext {
  sessionId: string
  conversationId?: string
  context?: Record<string, any>
}

class VoiceServiceClient {
  private baseUrl: string
  private timeout: number

  constructor(config: VoiceServiceConfig = {}) {
    this.baseUrl = config.baseUrl || this.getVoiceServiceUrl()
    this.timeout = config.timeout || 30000
  }

  private getVoiceServiceUrl(): string {
    // Use API Gateway URL since all services route through it
    return import.meta.env.VITE_API_GATEWAY_URL || import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
  }

  /**
   * Health check for voice service
   */
  async healthCheck(): Promise<{ status: string; version: string }> {
    try {
      // Check voice service health through API Gateway
      const response = await get<any>(`${this.baseUrl}/api/v1/voice/status`)
      if (response && response.voice_service) {
        return {
          status: response.voice_service.status,
          version: response.voice_service.version
        }
      }
      // Fallback to basic health check
      const basicResponse = await get<{ status: string; service: string }>(`${this.baseUrl}/health`)
      return {
        status: basicResponse.status,
        version: '2.0.0'
      }
    } catch (error) {
      console.error('Voice service health check failed:', error)
      throw error
    }
  }

  /**
   * Get voice service information
   */
  async getServiceInfo(): Promise<any> {
    try {
      // Get voice service status through API Gateway
      const response = await get(`${this.baseUrl}/api/v1/voice/status`)
      return response
    } catch (error) {
      console.error('Failed to get voice service info:', error)
      throw error
    }
  }

  /**
   * Convert speech to text
   */
  async speechToText(request: SpeechToTextRequest): Promise<SpeechToTextResponse> {
    try {
      const formData = new FormData()
      
      if (request.audioData instanceof Blob) {
        formData.append('audio', request.audioData, 'audio.webm')
      } else {
        // Convert ArrayBuffer to Blob
        const blob = new Blob([request.audioData], { type: 'audio/webm' })
        formData.append('audio', blob, 'audio.webm')
      }

      if (request.language) {
        formData.append('language', request.language)
      }

      if (request.options) {
        formData.append('options', JSON.stringify(request.options))
      }

      const response = await post<SpeechToTextResponse>(
        `${this.baseUrl}/api/v1/voice/stt`,
        formData
      )

      return response
    } catch (error) {
      console.error('Speech to text conversion failed:', error)
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      }
    }
  }

  /**
   * Convert text to speech
   */
  async textToSpeech(request: TextToSpeechRequest): Promise<TextToSpeechResponse> {
    try {
      // For blob responses, we need to use fetch directly since our httpClient assumes JSON
      // Use the legacy endpoint for compatibility
      const url = `${this.baseUrl}/api/v1/voice/text-to-speech`
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request)
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }

      const audioBlob = await response.blob()
      const audioUrl = URL.createObjectURL(audioBlob)

      return {
        success: true,
        audioUrl,
        audioBlob,
        duration: 0 // Would be provided by service
      }
    } catch (error) {
      console.error('Text to speech conversion failed:', error)
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      }
    }
  }

  /**
   * Start a voice session
   */
  async startSession(sessionData?: Partial<VoiceSessionData>): Promise<VoiceSessionData> {
    try {
      const response = await post<any>(`${this.baseUrl}/api/v1/session/start`, sessionData)
      // Handle the response format from our voice service
      if (response.success && response.session) {
        return {
          sessionId: response.session.session_id,
          userId: response.session.user_id,
          metadata: response.session
        }
      }
      throw new Error(response.error || 'Failed to create session')
    } catch (error) {
      console.error('Failed to start voice session:', error)
      throw error
    }
  }

  /**
   * End a voice session
   */
  async endSession(sessionId: string): Promise<void> {
    try {
      // Since we don't have a session end endpoint, just log for now
      console.log('Session ended:', sessionId)
      // TODO: Implement session cleanup when backend supports it
    } catch (error) {
      console.error('Failed to end voice session:', error)
      throw error
    }
  }

  /**
   * Get session status
   */
  async getSessionStatus(sessionId: string): Promise<any> {
    try {
      const response = await get(`${this.baseUrl}/api/v1/session/${sessionId}/status`)
      return response
    } catch (error) {
      console.error('Failed to get session status:', error)
      throw error
    }
  }

  /**
   * Start a conversation
   */
  async startConversation(context?: ConversationContext): Promise<any> {
    try {
      const response = await post(`${this.baseUrl}/api/v1/conversation/start`, context)
      return response
    } catch (error) {
      console.error('Failed to start conversation:', error)
      throw error
    }
  }

  /**
   * Send message in conversation
   */
  async sendConversationMessage(conversationId: string, message: string): Promise<any> {
    try {
      const response = await post(
        `${this.baseUrl}/api/v1/conversation/${conversationId}/message`,
        { message }
      )
      return response
    } catch (error) {
      console.error('Failed to send conversation message:', error)
      throw error
    }
  }

  /**
   * Get conversation history
   */
  async getConversationHistory(conversationId: string): Promise<any> {
    try {
      const response = await get(`${this.baseUrl}/api/v1/conversation/${conversationId}/history`)
      return response
    } catch (error) {
      console.error('Failed to get conversation history:', error)
      throw error
    }
  }

  /**
   * Process audio chunk (for streaming)
   */
  async processAudioChunk(audioData: ArrayBuffer, sessionId?: string): Promise<any> {
    try {
      const formData = new FormData()
      const blob = new Blob([audioData], { type: 'audio/webm' })
      formData.append('audio', blob)
      
      if (sessionId) {
        formData.append('sessionId', sessionId)
      }

      const response = await post(
        `${this.baseUrl}/api/v1/voice/process-chunk`,
        formData
      )

      return response
    } catch (error) {
      console.error('Audio chunk processing failed:', error)
      throw error
    }
  }
}

export const voiceServiceClient = new VoiceServiceClient()