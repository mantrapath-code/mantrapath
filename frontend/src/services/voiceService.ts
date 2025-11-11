/**
 * Voice Service API Client
 * Handles communication with the voice service backend
 */

import { get, post } from './httpClient'
import { getApiBaseUrl } from '@/config/api-config'

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

export interface LanguageDetectionRequest {
  text: string
}

export interface LanguageDetectionResponse {
  detected_language: string
  confidence: number
  supported_languages: string[]
}

export interface VoiceTestRequest {
  text?: string
  language?: string
}

export interface VoiceTestResponse {
  success: boolean
  original_text: string
  transcribed_text: string
  detected_language: string
  similarity_score: number
  tts_model: string
  stt_model: string
  audio_duration: number
  pipeline_quality: 'excellent' | 'good' | 'fair' | 'poor'
  error?: string
  stage?: 'tts' | 'stt'
}

export interface IndicLanguageInfo {
  code: string
  name: string
  native_name: string
  script: string
  supported_stt: boolean
  supported_tts: boolean
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
    // Use same-origin approach for HTTPS compatibility
    return getApiBaseUrl() || 'http://localhost:8000'
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

  /**
   * Detect language from text using Indic script analysis
   */
  async detectLanguage(request: LanguageDetectionRequest): Promise<LanguageDetectionResponse> {
    try {
      const response = await post<LanguageDetectionResponse>(
        `${this.baseUrl}/api/v1/language/detect`,
        request
      )
      return response
    } catch (error) {
      console.error('Language detection failed:', error)
      throw error
    }
  }

  /**
   * Test complete voice pipeline (TTS -> STT round-trip)
   */
  async testVoicePipeline(request: VoiceTestRequest): Promise<VoiceTestResponse> {
    try {
      const response = await post<VoiceTestResponse>(
        `${this.baseUrl}/api/v1/test/voice-pipeline`,
        request
      )
      return response
    } catch (error) {
      console.error('Voice pipeline test failed:', error)
      throw error
    }
  }

  /**
   * Get supported Indic languages with detailed information
   */
  async getSupportedIndicLanguages(): Promise<IndicLanguageInfo[]> {
    const languages: IndicLanguageInfo[] = [
      { code: 'hi', name: 'Hindi', native_name: 'हिन्दी', script: 'Devanagari', supported_stt: true, supported_tts: true },
      { code: 'bn', name: 'Bengali', native_name: 'বাংলা', script: 'Bengali', supported_stt: true, supported_tts: true },
      { code: 'gu', name: 'Gujarati', native_name: 'ગુજરાતી', script: 'Gujarati', supported_stt: true, supported_tts: true },
      { code: 'kn', name: 'Kannada', native_name: 'ಕನ್ನಡ', script: 'Kannada', supported_stt: true, supported_tts: true },
      { code: 'ml', name: 'Malayalam', native_name: 'മലയാളം', script: 'Malayalam', supported_stt: true, supported_tts: true },
      { code: 'mr', name: 'Marathi', native_name: 'मराठी', script: 'Devanagari', supported_stt: true, supported_tts: true },
      { code: 'or', name: 'Odia', native_name: 'ଓଡ଼ିଆ', script: 'Odia', supported_stt: true, supported_tts: true },
      { code: 'pa', name: 'Punjabi', native_name: 'ਪੰਜਾਬੀ', script: 'Gurmukhi', supported_stt: true, supported_tts: true },
      { code: 'ta', name: 'Tamil', native_name: 'தமிழ்', script: 'Tamil', supported_stt: true, supported_tts: true },
      { code: 'te', name: 'Telugu', native_name: 'తెలుగు', script: 'Telugu', supported_stt: true, supported_tts: true },
      { code: 'ur', name: 'Urdu', native_name: 'اردو', script: 'Arabic', supported_stt: true, supported_tts: true },
      { code: 'as', name: 'Assamese', native_name: 'অসমীয়া', script: 'Bengali', supported_stt: true, supported_tts: true },
      { code: 'en', name: 'English', native_name: 'English', script: 'Latin', supported_stt: true, supported_tts: true },
    ]
    
    return languages
  }

  /**
   * Enhanced STT with automatic language detection
   */
  async speechToTextWithAutoDetect(request: SpeechToTextRequest): Promise<SpeechToTextResponse> {
    try {
      const formData = new FormData()
      
      if (request.audioData instanceof Blob) {
        formData.append('audio', request.audioData)
      } else if (request.audioData instanceof ArrayBuffer) {
        const blob = new Blob([request.audioData], { type: 'audio/wav' })
        formData.append('audio', blob)
      }

      formData.append('language', request.language || 'auto')
      
      if (request.options?.detectLanguage) {
        formData.append('detect_language', 'true')
      }

      const response = await post<{
        success: boolean
        text?: string
        language_detected?: string
        confidence?: number
        model_used?: string
        error?: string
      }>(`${this.baseUrl}/api/v1/stt/transcribe`, formData)

      return {
        success: response.success,
        transcription: response.text,
        confidence: response.confidence,
        language: response.language_detected,
        error: response.error
      }
    } catch (error) {
      console.error('Enhanced STT failed:', error)
      throw error
    }
  }

  /**
   * Enhanced TTS with automatic language detection
   */
  async textToSpeechWithAutoDetect(request: TextToSpeechRequest): Promise<TextToSpeechResponse> {
    try {
      // Auto-detect language if not specified
      let language = request.language || 'auto'
      
      if (language === 'auto') {
        try {
          const detection = await this.detectLanguage({ text: request.text })
          language = detection.detected_language
        } catch (error) {
          console.warn('Language auto-detection failed, defaulting to Hindi:', error)
          language = 'hi' // Default to Hindi for Indic content
        }
      }

      const response = await post<{
        success: boolean
        audio_data?: ArrayBuffer
        sample_rate?: number
        duration?: number
        model_used?: string
        error?: string
      }>(`${this.baseUrl}/api/v1/tts/synthesize`, {
        text: request.text,
        language: language,
        voice: request.voice
      })

      if (response.success && response.audio_data) {
        const audioBlob = new Blob([response.audio_data], { type: 'audio/wav' })
        return {
          success: true,
          audioBlob: audioBlob,
          duration: response.duration
        }
      }

      return {
        success: false,
        error: response.error || 'TTS synthesis failed'
      }
    } catch (error) {
      console.error('Enhanced TTS failed:', error)
      throw error
    }
  }
}

export const voiceServiceClient = new VoiceServiceClient()