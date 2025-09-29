/**
 * Voice Event Processor Service Client
 * Handles real-time voice analytics and event processing
 */

import { get, post } from './httpClient'

export interface VoiceEventProcessorConfig {
  baseUrl?: string
  wsUrl?: string
  reconnectInterval?: number
  maxReconnectAttempts?: number
}

export interface VoiceEvent {
  eventType: string
  timestamp: number
  confidence?: number
  metadata?: Record<string, any>
}

export interface EmotionAnalysisResult {
  emotion: string
  confidence: number
  valence?: number
  arousal?: number
}

export interface VoiceStreamConfig {
  sampleRate?: number
  chunkSize?: number
  vadSensitivity?: number
  emotionAnalysis?: boolean
}

export interface AnalyticsData {
  totalConnections: number
  activeStreams: number
  processedEvents: number
  detectedEmotions: number
  voiceActivityEvents: number
}

export type VoiceEventCallback = (event: VoiceEvent) => void
export type ConnectionStatusCallback = (status: 'connected' | 'disconnected' | 'error') => void

class VoiceEventProcessorClient {
  private baseUrl: string
  private wsUrl: string
  private ws: WebSocket | null = null
  private clientId: string
  private reconnectInterval: number
  private maxReconnectAttempts: number
  private reconnectAttempts = 0
  private isConnecting = false
  
  private eventCallbacks: VoiceEventCallback[] = []
  private statusCallbacks: ConnectionStatusCallback[] = []

  constructor(config: VoiceEventProcessorConfig = {}) {
    this.baseUrl = config.baseUrl || this.getVoiceEventProcessorUrl()
    this.wsUrl = config.wsUrl || this.getVoiceEventProcessorWsUrl()
    this.clientId = this.generateClientId()
    this.reconnectInterval = config.reconnectInterval || 5000
    this.maxReconnectAttempts = config.maxReconnectAttempts || 5
  }

  private getVoiceEventProcessorUrl(): string {
    return import.meta.env.VITE_VOICE_EVENT_PROCESSOR_URL || 'http://localhost:8015'
  }

  private getVoiceEventProcessorWsUrl(): string {
    const baseUrl = this.getVoiceEventProcessorUrl()
    return baseUrl.replace(/^http/, 'ws')
  }

  private generateClientId(): string {
    return `client_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  }

  /**
   * Health check for voice event processor
   */
  async healthCheck(): Promise<{ status: string; activeConnections: number; activeStreams: number }> {
    try {
      const response = await get<{ status: string; activeConnections: number; activeStreams: number }>(`${this.baseUrl}/health`)
      return response
    } catch (error) {
      console.error('Voice event processor health check failed:', error)
      throw error
    }
  }

  /**
   * Get service information
   */
  async getServiceInfo(): Promise<any> {
    try {
      const response = await get(`${this.baseUrl}/`)
      return response
    } catch (error) {
      console.error('Failed to get voice event processor info:', error)
      throw error
    }
  }

  /**
   * Get current streams status
   */
  async getStreamsStatus(): Promise<any> {
    try {
      const response = await get(`${this.baseUrl}/api/v1/streams/status`)
      return response
    } catch (error) {
      console.error('Failed to get streams status:', error)
      throw error
    }
  }

  /**
   * Process voice chunk (non-streaming)
   */
  async processVoiceChunk(audioData: Uint8Array, config?: VoiceStreamConfig): Promise<{ success: boolean; events: VoiceEvent[] }> {
    try {
      const response = await post<{ success: boolean; events: VoiceEvent[] }>(
        `${this.baseUrl}/api/v1/voice/process`,
        audioData
      )
      return response
    } catch (error) {
      console.error('Voice chunk processing failed:', error)
      return { success: false, events: [] }
    }
  }

  /**
   * Get analytics and statistics
   */
  async getAnalytics(): Promise<AnalyticsData> {
    try {
      const response = await get<AnalyticsData>(`${this.baseUrl}/api/v1/stats`)
      return response
    } catch (error) {
      console.error('Failed to get analytics:', error)
      throw error
    }
  }

  /**
   * Get processing configuration
   */
  async getConfig(): Promise<any> {
    try {
      const response = await get(`${this.baseUrl}/api/v1/config`)
      return response
    } catch (error) {
      console.error('Failed to get config:', error)
      throw error
    }
  }

  /**
   * Connect to WebSocket for real-time voice streaming
   */
  async connectWebSocket(): Promise<void> {
    if (this.isConnecting || (this.ws && this.ws.readyState === WebSocket.OPEN)) {
      return
    }

    this.isConnecting = true

    try {
      const wsUrl = `${this.wsUrl}/ws/voice/${this.clientId}`
      console.log(`🔌 Connecting to voice event processor: ${wsUrl}`)
      
      this.ws = new WebSocket(wsUrl)

      this.ws.onopen = () => {
        console.log('✅ Voice event processor WebSocket connected')
        this.isConnecting = false
        this.reconnectAttempts = 0
        this.notifyStatusChange('connected')
      }

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          this.handleWebSocketMessage(data)
        } catch (error) {
          console.error('Error parsing WebSocket message:', error)
        }
      }

      this.ws.onclose = () => {
        console.log('🔌 Voice event processor WebSocket disconnected')
        this.isConnecting = false
        this.notifyStatusChange('disconnected')
        this.handleReconnect()
      }

      this.ws.onerror = (error) => {
        console.error('❌ Voice event processor WebSocket error:', error)
        this.isConnecting = false
        this.notifyStatusChange('error')
      }

    } catch (error) {
      console.error('Failed to connect WebSocket:', error)
      this.isConnecting = false
      this.notifyStatusChange('error')
    }
  }

  /**
   * Disconnect WebSocket
   */
  disconnectWebSocket(): void {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }

  /**
   * Start voice streaming
   */
  async startVoiceStream(): Promise<void> {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      await this.connectWebSocket()
    }

    this.sendWebSocketMessage({
      type: 'start_stream',
      timestamp: Date.now()
    })
  }

  /**
   * Stop voice streaming
   */
  stopVoiceStream(): void {
    this.sendWebSocketMessage({
      type: 'stop_stream',
      timestamp: Date.now()
    })
  }

  /**
   * Send audio chunk via WebSocket
   */
  sendAudioChunk(audioData: ArrayBuffer): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.warn('WebSocket not connected, cannot send audio chunk')
      return
    }

    // Convert to base64 for WebSocket transmission
    const base64Audio = this.arrayBufferToBase64(audioData)
    
    this.sendWebSocketMessage({
      type: 'audio_chunk',
      audioData: base64Audio,
      timestamp: Date.now()
    })
  }

  /**
   * Send ping to keep connection alive
   */
  ping(): void {
    this.sendWebSocketMessage({
      type: 'ping',
      timestamp: Date.now()
    })
  }

  /**
   * Add event callback
   */
  onVoiceEvent(callback: VoiceEventCallback): void {
    this.eventCallbacks.push(callback)
  }

  /**
   * Add status callback
   */
  onStatusChange(callback: ConnectionStatusCallback): void {
    this.statusCallbacks.push(callback)
  }

  /**
   * Remove event callback
   */
  removeVoiceEventCallback(callback: VoiceEventCallback): void {
    const index = this.eventCallbacks.indexOf(callback)
    if (index > -1) {
      this.eventCallbacks.splice(index, 1)
    }
  }

  /**
   * Remove status callback
   */
  removeStatusCallback(callback: ConnectionStatusCallback): void {
    const index = this.statusCallbacks.indexOf(callback)
    if (index > -1) {
      this.statusCallbacks.splice(index, 1)
    }
  }

  private sendWebSocketMessage(message: any): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message))
    }
  }

  private handleWebSocketMessage(data: any): void {
    switch (data.type) {
      case 'connection_established':
        console.log('🔗 Connection established:', data.client_id)
        break
      
      case 'stream_started':
        console.log('🎵 Voice stream started')
        break
      
      case 'stream_stopped':
        console.log('🔇 Voice stream stopped')
        break
      
      case 'voice_event':
        this.notifyVoiceEvent(data.event)
        break
      
      case 'pong':
        // Handle ping/pong for keep-alive
        break
      
      case 'error':
        console.error('WebSocket error:', data.message)
        break
      
      default:
        console.log('Unknown message type:', data.type, data)
    }
  }

  private notifyVoiceEvent(event: VoiceEvent): void {
    this.eventCallbacks.forEach(callback => {
      try {
        callback(event)
      } catch (error) {
        console.error('Error in voice event callback:', error)
      }
    })
  }

  private notifyStatusChange(status: 'connected' | 'disconnected' | 'error'): void {
    this.statusCallbacks.forEach(callback => {
      try {
        callback(status)
      } catch (error) {
        console.error('Error in status callback:', error)
      }
    })
  }

  private handleReconnect(): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      console.log(`🔄 Reconnecting... (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`)
      
      setTimeout(() => {
        this.connectWebSocket()
      }, this.reconnectInterval)
    } else {
      console.error('❌ Max reconnection attempts reached')
    }
  }

  private arrayBufferToBase64(buffer: ArrayBuffer): string {
    const bytes = new Uint8Array(buffer)
    let binary = ''
    for (let i = 0; i < bytes.byteLength; i++) {
      binary += String.fromCharCode(bytes[i])
    }
    return btoa(binary)
  }
}

export const voiceEventProcessorClient = new VoiceEventProcessorClient()

// Auto-connect in development
if (import.meta.env.DEV) {
  setTimeout(() => {
    voiceEventProcessorClient.connectWebSocket().then(() => {
      console.log('🎤 Voice event processor connected in dev mode')
    }).catch(error => {
      console.warn('Could not auto-connect to voice event processor:', error)
    })
  }, 2000)
}