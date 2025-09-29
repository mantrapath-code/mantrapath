/**
 * Voice Interface Component
 * Integrates voice recording, speech-to-text, text-to-speech, and real-time analytics
 */

import React, { useState, useRef, useCallback, useEffect } from 'react'
import { Mic, MicOff, Volume2, VolumeX, Activity, Play, Pause, Square } from 'lucide-react'
import { voiceServiceClient } from '@/services/voiceService'
import { voiceEventProcessorClient, type VoiceEvent } from '@/services/voiceEventProcessor'
import { voicePermissionManager } from '@/utils/voicePermissions'
import { ensureDevTokenExists } from '@/utils/auth'

export interface VoiceInterfaceProps {
  onTranscription?: (text: string) => void
  onVoiceEvent?: (event: VoiceEvent) => void
  showAnalytics?: boolean
  autoSpeak?: boolean
  language?: string
}

export const VoiceInterface: React.FC<VoiceInterfaceProps> = ({
  onTranscription,
  onVoiceEvent,
  showAnalytics = true,
  autoSpeak = false,
  language = 'en'
}) => {
  // Recording state
  const [isRecording, setIsRecording] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [transcription, setTranscription] = useState('')
  const [error, setError] = useState<string | null>(null)
  
  // Audio playback state
  const [isPlaying, setIsPlaying] = useState(false)
  const [audioUrl, setAudioUrl] = useState<string | null>(null)
  
  // Analytics state
  const [isConnected, setIsConnected] = useState(false)
  const [voiceEvents, setVoiceEvents] = useState<VoiceEvent[]>([])
  const [analytics, setAnalytics] = useState({
    totalConnections: 0,
    activeStreams: 0,
    processedEvents: 0
  })
  
  // Permissions state
  const [hasPermissions, setHasPermissions] = useState(false)
  
  // Refs
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const audioChunksRef = useRef<Blob[]>([])
  const audioElementRef = useRef<HTMLAudioElement | null>(null)
  const sessionIdRef = useRef<string | null>(null)

  // Initialize component
  useEffect(() => {
    initializeVoiceInterface()
    return () => {
      cleanup()
    }
  }, [])

  const initializeVoiceInterface = async () => {
    try {
      // Ensure dev token exists for testing
      ensureDevTokenExists()
      
      // Check and request permissions
      const permissions = await voicePermissionManager.initializeAllPermissions()
      setHasPermissions(permissions.microphone)
      
      if (!permissions.microphone) {
        setError('Microphone permission is required for voice features')
        return
      }

      // Connect to voice event processor for analytics
      if (showAnalytics) {
        await connectToAnalytics()
      }

      // Start voice session
      await startVoiceSession()
      
      console.log('🎤 Voice interface initialized successfully')
    } catch (error) {
      console.error('Failed to initialize voice interface:', error)
      setError('Failed to initialize voice features')
    }
  }

  const connectToAnalytics = async () => {
    try {
      // Connect to WebSocket for real-time events
      await voiceEventProcessorClient.connectWebSocket()
      
      // Set up event listeners
      voiceEventProcessorClient.onVoiceEvent(handleVoiceEvent)
      voiceEventProcessorClient.onStatusChange(handleConnectionStatus)
      
      // Start voice streaming for analytics
      await voiceEventProcessorClient.startVoiceStream()
      
      // Get initial analytics
      const analyticsData = await voiceEventProcessorClient.getAnalytics()
      setAnalytics(analyticsData)
      
    } catch (error) {
      console.warn('Failed to connect to analytics:', error)
    }
  }

  const startVoiceSession = async () => {
    try {
      const sessionData = await voiceServiceClient.startSession({
        userId: 'current_user', // Replace with actual user ID
        metadata: { language }
      })
      sessionIdRef.current = sessionData.sessionId
      console.log('📱 Voice session started:', sessionData.sessionId)
    } catch (error) {
      console.error('Failed to start voice session:', error)
    }
  }

  const handleVoiceEvent = useCallback((event: VoiceEvent) => {
    setVoiceEvents(prev => [event, ...prev.slice(0, 9)]) // Keep last 10 events
    onVoiceEvent?.(event)
  }, [onVoiceEvent])

  const handleConnectionStatus = useCallback((status: 'connected' | 'disconnected' | 'error') => {
    setIsConnected(status === 'connected')
  }, [])

  const startRecording = async () => {
    if (!hasPermissions) {
      await voicePermissionManager.requestMicrophonePermission()
      return
    }

    try {
      setError(null)
      setIsRecording(true)
      
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
          sampleRate: 16000
        }
      })

      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      })
      
      mediaRecorderRef.current = mediaRecorder
      audioChunksRef.current = []

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data)
          
          // Send chunk to analytics if connected
          if (isConnected) {
            event.data.arrayBuffer().then(buffer => {
              voiceEventProcessorClient.sendAudioChunk(buffer)
            })
          }
        }
      }

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' })
        await processAudio(audioBlob)
        
        // Stop tracks
        stream.getTracks().forEach(track => track.stop())
      }

      mediaRecorder.start(250) // Collect data every 250ms
      console.log('🎙️ Recording started')
      
    } catch (error) {
      console.error('Failed to start recording:', error)
      setError('Failed to start recording. Please check your microphone.')
      setIsRecording(false)
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
      console.log('⏹️ Recording stopped')
    }
  }

  const processAudio = async (audioBlob: Blob) => {
    setIsProcessing(true)
    
    try {
      // Send to voice service for transcription
      const result = await voiceServiceClient.speechToText({
        audioData: audioBlob,
        language,
        options: {
          enhanceAudio: true,
          detectLanguage: true
        }
      })

      if (result.success && result.transcription) {
        setTranscription(result.transcription)
        onTranscription?.(result.transcription)
        
        // Auto-speak if enabled
        if (autoSpeak) {
          await speakText(`I heard you say: ${result.transcription}`)
        }
      } else {
        setError(result.error || 'Failed to transcribe audio')
      }
      
    } catch (error) {
      console.error('Audio processing failed:', error)
      setError('Failed to process audio')
    } finally {
      setIsProcessing(false)
    }
  }

  const speakText = async (text: string) => {
    try {
      setIsPlaying(true)
      
      const result = await voiceServiceClient.textToSpeech({
        text,
        language,
        voice: 'default',
        speed: 1.0
      })

      if (result.success && result.audioUrl) {
        setAudioUrl(result.audioUrl)
        
        // Play audio
        const audio = new Audio(result.audioUrl)
        audioElementRef.current = audio
        
        audio.onended = () => {
          setIsPlaying(false)
          setAudioUrl(null)
        }
        
        audio.onerror = () => {
          setIsPlaying(false)
          setAudioUrl(null)
          setError('Failed to play audio')
        }
        
        await audio.play()
      } else {
        setError(result.error || 'Failed to generate speech')
        setIsPlaying(false)
      }
      
    } catch (error) {
      console.error('Text-to-speech failed:', error)
      setError('Failed to speak text')
      setIsPlaying(false)
    }
  }

  const stopAudio = () => {
    if (audioElementRef.current) {
      audioElementRef.current.pause()
      audioElementRef.current.currentTime = 0
      setIsPlaying(false)
      setAudioUrl(null)
    }
  }

  const testVoice = async () => {
    await speakText('Hello! This is a test of the voice interface.')
  }

  const cleanup = () => {
    // Stop recording if active
    if (isRecording) {
      stopRecording()
    }
    
    // Stop audio playback
    stopAudio()
    
    // Clean up URLs
    if (audioUrl) {
      URL.revokeObjectURL(audioUrl)
    }
    
    // End voice session
    if (sessionIdRef.current) {
      voiceServiceClient.endSession(sessionIdRef.current).catch(console.error)
    }
    
    // Disconnect from analytics
    voiceEventProcessorClient.disconnectWebSocket()
  }

  return (
    <div className="voice-interface p-6 bg-white dark:bg-gray-800 rounded-lg shadow-lg">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-semibold text-gray-800 dark:text-white">
          Voice Interface
        </h3>
        {showAnalytics && (
          <div className="flex items-center space-x-2">
            <Activity 
              className={`w-4 h-4 ${isConnected ? 'text-green-500' : 'text-red-500'}`} 
            />
            <span className="text-sm text-gray-600 dark:text-gray-300">
              {isConnected ? 'Analytics Connected' : 'Analytics Disconnected'}
            </span>
          </div>
        )}
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
          <button 
            onClick={() => setError(null)}
            className="float-right font-bold"
          >
            ×
          </button>
        </div>
      )}

      {/* Main Controls */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* Voice Recording */}
        <div className="space-y-4">
          <h4 className="font-medium text-gray-700 dark:text-gray-200">
            Voice Recording
          </h4>
          
          <div className="flex space-x-3">
            <button
              onClick={isRecording ? stopRecording : startRecording}
              disabled={!hasPermissions || isProcessing}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
                isRecording 
                  ? 'bg-red-500 hover:bg-red-600 text-white' 
                  : 'bg-blue-500 hover:bg-blue-600 text-white disabled:bg-gray-400'
              }`}
            >
              {isRecording ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
              <span>{isRecording ? 'Stop' : 'Record'}</span>
            </button>
            
            {isProcessing && (
              <div className="flex items-center space-x-2 text-gray-600">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500"></div>
                <span className="text-sm">Processing...</span>
              </div>
            )}
          </div>

          {transcription && (
            <div className="bg-gray-100 dark:bg-gray-700 p-3 rounded-lg">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">
                Transcription:
              </p>
              <p className="text-gray-800 dark:text-white">{transcription}</p>
            </div>
          )}
        </div>

        {/* Voice Playback */}
        <div className="space-y-4">
          <h4 className="font-medium text-gray-700 dark:text-gray-200">
            Voice Playback
          </h4>
          
          <div className="flex space-x-3">
            <button
              onClick={testVoice}
              disabled={isPlaying}
              className="flex items-center space-x-2 px-4 py-2 bg-green-500 hover:bg-green-600 disabled:bg-gray-400 text-white rounded-lg transition-colors"
            >
              {isPlaying ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
              <span>Test Voice</span>
            </button>
            
            {isPlaying && (
              <button
                onClick={stopAudio}
                className="flex items-center space-x-2 px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg transition-colors"
              >
                <Square className="w-4 h-4" />
                <span>Stop</span>
              </button>
            )}
          </div>

          {transcription && (
            <button
              onClick={() => speakText(transcription)}
              disabled={isPlaying || !transcription}
              className="flex items-center space-x-2 px-4 py-2 bg-purple-500 hover:bg-purple-600 disabled:bg-gray-400 text-white rounded-lg transition-colors"
            >
              <Play className="w-4 h-4" />
              <span>Speak Transcription</span>
            </button>
          )}
        </div>
      </div>

      {/* Analytics Dashboard */}
      {showAnalytics && (
        <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-600">
          <h4 className="font-medium text-gray-700 dark:text-gray-200 mb-4">
            Voice Analytics
          </h4>
          
          <div className="grid grid-cols-3 gap-4 mb-4">
            <div className="bg-blue-100 dark:bg-blue-900 p-3 rounded-lg text-center">
              <div className="text-2xl font-bold text-blue-600 dark:text-blue-300">
                {analytics.totalConnections}
              </div>
              <div className="text-sm text-blue-500 dark:text-blue-400">
                Total Connections
              </div>
            </div>
            <div className="bg-green-100 dark:bg-green-900 p-3 rounded-lg text-center">
              <div className="text-2xl font-bold text-green-600 dark:text-green-300">
                {analytics.activeStreams}
              </div>
              <div className="text-sm text-green-500 dark:text-green-400">
                Active Streams
              </div>
            </div>
            <div className="bg-purple-100 dark:bg-purple-900 p-3 rounded-lg text-center">
              <div className="text-2xl font-bold text-purple-600 dark:text-purple-300">
                {analytics.processedEvents}
              </div>
              <div className="text-sm text-purple-500 dark:text-purple-400">
                Events Processed
              </div>
            </div>
          </div>

          {/* Recent Events */}
          {voiceEvents.length > 0 && (
            <div>
              <h5 className="font-medium text-gray-600 dark:text-gray-300 mb-2">
                Recent Voice Events
              </h5>
              <div className="space-y-2 max-h-32 overflow-y-auto">
                {voiceEvents.slice(0, 5).map((event, index) => (
                  <div key={index} className="text-sm bg-gray-50 dark:bg-gray-700 p-2 rounded">
                    <span className="font-medium text-blue-600 dark:text-blue-400">
                      {event.eventType}
                    </span>
                    <span className="text-gray-500 dark:text-gray-400 ml-2">
                      {new Date(event.timestamp).toLocaleTimeString()}
                    </span>
                    {event.confidence && (
                      <span className="text-green-600 dark:text-green-400 ml-2">
                        ({(event.confidence * 100).toFixed(0)}%)
                      </span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default VoiceInterface