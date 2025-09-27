import { useState, useEffect, useRef } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Textarea } from '@/components/ui/textarea'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Progress } from '@/components/ui/progress'
import { 
  Microphone, 
  MicrophoneSlash, 
  Stop, 
  Play,
  Pause,
  ArrowClockwise,
  SpeakerHigh,
  Warning,
  CheckCircle,
  Circle
} from '@phosphor-icons/react'
import { motion, AnimatePresence } from 'framer-motion'
import { toast } from 'sonner'
import { apiService } from '@/services/api'

// Speech Recognition type declarations
declare global {
  interface Window {
    SpeechRecognition: any
    webkitSpeechRecognition: any
  }
}

interface SpeechRecognitionEvent {
  results: SpeechRecognitionResultList
  resultIndex: number
}

interface SpeechRecognitionErrorEvent {
  error: string
}

type VoiceState = 'idle' | 'listening' | 'processing' | 'completed' | 'error'
type VoiceMode = 'push-to-talk' | 'continuous' | 'auto'

interface VoiceMoodEntryProps {
  onVoiceInput?: (transcript: string) => void
  onVoiceComplete?: (finalTranscript: string, confidence: number) => void
  onMoodSaved?: (moodData: any) => void
  voiceState?: VoiceState
  supportedLanguages?: string[]
  currentLanguage?: string
  onLanguageChange?: (language: string) => void
  mode?: VoiceMode
  disabled?: boolean
  placeholder?: string
  culturalContext?: {
    region?: string
    language?: string
    voicePrompts?: Record<string, string>
  }
}

interface VoicePermissions {
  microphone: 'granted' | 'denied' | 'prompt'
  speechRecognition: boolean
}

export function VoiceMoodEntry({
  onVoiceInput,
  onVoiceComplete,
  onMoodSaved,
  voiceState: externalVoiceState,
  supportedLanguages = ['en-US', 'es-ES', 'fr-FR', 'de-DE', 'ja-JP'],
  currentLanguage = 'en-US',
  onLanguageChange,
  mode = 'push-to-talk',
  disabled = false,
  placeholder = "Describe how you're feeling...",
  culturalContext
}: VoiceMoodEntryProps) {
  const [internalVoiceState, setInternalVoiceState] = useState<VoiceState>('idle')
  const [transcript, setTranscript] = useState('')
  const [confidence, setConfidence] = useState(0)
  const [permissions, setPermissions] = useState<VoicePermissions>({
    microphone: 'prompt',
    speechRecognition: false
  })
  const [audioLevel, setAudioLevel] = useState(0)
  const [recordingDuration, setRecordingDuration] = useState(0)
  const [error, setError] = useState<string | null>(null)
  
  const recognitionRef = useRef<any | null>(null)
  const audioContextRef = useRef<AudioContext | null>(null)
  const analyserRef = useRef<AnalyserNode | null>(null)
  const micStreamRef = useRef<MediaStream | null>(null)
  const recordingStartTimeRef = useRef<number | null>(null)
  const animationFrameRef = useRef<number | null>(null)

  // Use external state if provided, otherwise use internal state
  const voiceState = externalVoiceState || internalVoiceState

  // Check browser support and permissions on mount
  useEffect(() => {
    checkBrowserSupport()
    checkMicrophonePermission()
    
    return () => {
      cleanup()
    }
  }, [])

  // Update recording duration
  useEffect(() => {
    let interval: NodeJS.Timeout | null = null
    
    if (voiceState === 'listening' && recordingStartTimeRef.current) {
      interval = setInterval(() => {
        if (recordingStartTimeRef.current) {
          setRecordingDuration(Date.now() - recordingStartTimeRef.current)
        }
      }, 100)
    } else {
      setRecordingDuration(0)
    }
    
    return () => {
      if (interval) clearInterval(interval)
    }
  }, [voiceState])

  const checkBrowserSupport = () => {
    const speechRecognitionSupported = 
      'SpeechRecognition' in window || 'webkitSpeechRecognition' in window
    
    setPermissions(prev => ({
      ...prev,
      speechRecognition: speechRecognitionSupported
    }))
    
    if (!speechRecognitionSupported) {
      setError('Speech recognition is not supported in this browser')
    }
  }

  const checkMicrophonePermission = async () => {
    try {
      const result = await navigator.permissions.query({ name: 'microphone' as PermissionName })
      setPermissions(prev => ({
        ...prev,
        microphone: result.state as 'granted' | 'denied' | 'prompt'
      }))
    } catch (err) {
      console.warn('Could not check microphone permissions:', err)
    }
  }

  const requestMicrophoneAccess = async (): Promise<boolean> => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      micStreamRef.current = stream
      
      setPermissions(prev => ({
        ...prev,
        microphone: 'granted'
      }))
      
      setupAudioAnalyzer(stream)
      return true
    } catch (err) {
      console.error('Microphone access denied:', err)
      setPermissions(prev => ({
        ...prev,
        microphone: 'denied'
      }))
      setError('Microphone access is required for voice input')
      return false
    }
  }

  const setupAudioAnalyzer = (stream: MediaStream) => {
    try {
      audioContextRef.current = new AudioContext()
      analyserRef.current = audioContextRef.current.createAnalyser()
      
      const source = audioContextRef.current.createMediaStreamSource(stream)
      source.connect(analyserRef.current)
      
      analyserRef.current.fftSize = 256
      startAudioLevelMonitoring()
    } catch (err) {
      console.error('Failed to setup audio analyzer:', err)
    }
  }

  const startAudioLevelMonitoring = () => {
    if (!analyserRef.current) return
    
    const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount)
    
    const updateAudioLevel = () => {
      if (analyserRef.current && voiceState === 'listening') {
        analyserRef.current.getByteFrequencyData(dataArray)
        const average = dataArray.reduce((a, b) => a + b) / dataArray.length
        setAudioLevel(Math.min(100, (average / 128) * 100))
        
        animationFrameRef.current = requestAnimationFrame(updateAudioLevel)
      }
    }
    
    updateAudioLevel()
  }

  const initializeSpeechRecognition = () => {
    if (!permissions.speechRecognition) return null
    
    const SpeechRecognition = 
      window.SpeechRecognition || (window as any).webkitSpeechRecognition
    
    const recognition = new SpeechRecognition()
    recognition.continuous = mode === 'continuous'
    recognition.interimResults = true
    recognition.lang = currentLanguage
    
    // Enhanced language detection settings
    recognition.maxAlternatives = 3
    recognition.serviceURI = undefined // Use default service for better language detection
    
    recognition.onstart = () => {
      setInternalVoiceState('listening')
      recordingStartTimeRef.current = Date.now()
      setError(null)
      
      // Start language detection with backend voice service
      detectLanguageWithBackend()
    }
    
    recognition.onresult = (event) => {
      let finalTranscript = ''
      let interimTranscript = ''
      let bestConfidence = 0
      
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const result = event.results[i]
        const transcript = result[0].transcript
        const confidence = result[0].confidence || 0
        
        if (result.isFinal) {
          finalTranscript += transcript
          bestConfidence = Math.max(bestConfidence, confidence)
        } else {
          interimTranscript += transcript
        }
      }
      
      const fullTranscript = finalTranscript || interimTranscript
      setTranscript(fullTranscript)
      setConfidence(bestConfidence)
      
      // Send real-time updates
      onVoiceInput?.(fullTranscript)
      
      if (finalTranscript) {
        setInternalVoiceState('completed')
        
        // Enhanced mood processing with backend voice service
        processVoiceInputWithBackend(finalTranscript, bestConfidence)
        
        onVoiceComplete?.(finalTranscript, bestConfidence)
      }
    }
    
    recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error)
      setInternalVoiceState('error')
      setError(`Speech recognition error: ${event.error}`)
      
      if (event.error === 'not-allowed') {
        setPermissions(prev => ({ ...prev, microphone: 'denied' }))
      }
    }
    
    recognition.onend = () => {
      if (voiceState === 'listening' && mode === 'continuous') {
        // Restart if in continuous mode
        recognition.start()
      } else {
        setInternalVoiceState('idle')
        recordingStartTimeRef.current = null
        if (animationFrameRef.current) {
          cancelAnimationFrame(animationFrameRef.current)
        }
      }
    }
    
    return recognition
  }

  const startListening = async () => {
    if (disabled || voiceState === 'listening') return
    
    setError(null)
    
    // Check microphone permission
    if (permissions.microphone !== 'granted') {
      const accessGranted = await requestMicrophoneAccess()
      if (!accessGranted) return
    }
    
    // Initialize speech recognition
    recognitionRef.current = initializeSpeechRecognition()
    if (!recognitionRef.current) {
      setError('Speech recognition could not be initialized')
      return
    }
    
    try {
      setTranscript('')
      setConfidence(0)
      recognitionRef.current.start()
    } catch (err) {
      console.error('Failed to start speech recognition:', err)
      setError('Failed to start voice recording')
    }
  }

  const stopListening = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop()
    }
    setInternalVoiceState('idle')
    recordingStartTimeRef.current = null
    
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current)
    }
  }

  const cleanup = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop()
    }
    
    if (micStreamRef.current) {
      micStreamRef.current.getTracks().forEach(track => track.stop())
    }
    
    if (audioContextRef.current) {
      audioContextRef.current.close()
    }
    
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current)
    }
  }

  const resetVoiceInput = () => {
    setTranscript('')
    setConfidence(0)
    setError(null)
    setInternalVoiceState('idle')
  }

  // Enhanced language detection using backend voice service
  const detectLanguageWithBackend = async () => {
    if (!micStreamRef.current) return
    
    try {
      // Create a short audio sample for language detection
      const mediaRecorder = new MediaRecorder(micStreamRef.current)
      const chunks: Blob[] = []
      
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunks.push(event.data)
        }
      }
      
      mediaRecorder.onstop = async () => {
        if (chunks.length > 0) {
          const audioBlob = new Blob(chunks, { type: 'audio/webm' })
          await sendAudioForLanguageDetection(audioBlob)
        }
      }
      
      // Record a short sample for language detection
      mediaRecorder.start()
      setTimeout(() => {
        if (mediaRecorder.state === 'recording') {
          mediaRecorder.stop()
        }
      }, 2000) // 2 seconds sample
    } catch (error) {
      console.warn('Language detection failed:', error)
    }
  }

  const sendAudioForLanguageDetection = async (audioBlob: Blob) => {
    try {
      const formData = new FormData()
      formData.append('audio', audioBlob, 'voice-sample.webm')
      formData.append('detect_language', 'true')
      
  const voiceBase = import.meta.env.VITE_VOICE_SERVICE_URL || 'http://voice-service:8011'
  const response = await fetch(`${voiceBase}/stt`, {
        method: 'POST',
        body: formData
      })
      
      if (response.ok) {
        const result = await response.json()
        if (result.detected_language && result.detected_language !== currentLanguage) {
          console.log('Language detected:', result.detected_language)
          onLanguageChange?.(result.detected_language)
          
          toast.info(`Language detected: ${result.detected_language}`, {
            description: 'Voice input language updated automatically'
          })
        }
      }
    } catch (error) {
      console.warn('Backend language detection failed:', error)
    }
  }

  const processVoiceInputWithBackend = async (transcript: string, confidence: number) => {
    try {
      setInternalVoiceState('processing')
      
      let moodData: {
        mood_score: number;
        energy_level: number;
        stress_level: number;
        notes: string;
        mood_label: string;
        detected_emotions: any;
      } | null = null
      
      // Try to use the voice service's emotion analysis
      try {
  const voiceBase = import.meta.env.VITE_VOICE_SERVICE_URL || 'http://voice-service:8011'
  const response = await fetch(`${voiceBase}/emotion-analysis`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            text: transcript,
            language: currentLanguage
          })
        })

        if (response.ok) {
          const emotionResult = await response.json()
          moodData = mapEmotionToMood(emotionResult, transcript)
        } else {
          console.warn('Emotion analysis failed:', await response.text())
        }
      } catch (emotionError) {
        console.warn('Emotion analysis service not available:', emotionError)
      }
      
      // Fallback: create a basic mood entry with just the transcript
      if (!moodData) {
        moodData = {
          mood_score: 5, // Default neutral mood
          energy_level: 5,
          stress_level: 5,
          notes: transcript,
          mood_label: 'Voice Note',
          detected_emotions: null
        }
      }
      
      // Save the mood data to the backend (moodData is guaranteed to be non-null here)
      try {
        const savedMoodEntry = await apiService.createMoodEntry({
          mood_score: moodData.mood_score,
          energy_level: moodData.energy_level,
          stress_level: moodData.stress_level,
          notes: moodData.notes,
          mood_confidence: confidence,
          context_tags: ['voice_input'],
          environmental_context: {
            source: 'voice',
            detected_emotions: moodData.detected_emotions,
            language: currentLanguage,
            original_transcript: transcript
          }
        })
        
        if (savedMoodEntry) {
          const successMessage = moodData.detected_emotions 
            ? `${moodData.mood_label} mood recorded with ${Math.round(confidence * 100)}% confidence`
            : 'Voice note saved successfully'
            
          toast.success('Voice mood saved!', {
            description: successMessage,
            duration: 4000
          })
          setInternalVoiceState('completed')
          
          // Notify parent component
          onMoodSaved?.(savedMoodEntry)
          
          // Clear the transcript after successful save
          setTimeout(() => {
            setTranscript('')
            setInternalVoiceState('idle')
          }, 2000)
        } else {
          throw new Error('Failed to save mood entry')
        }
      } catch (saveError) {
        console.error('Failed to save mood entry:', saveError)
        toast.error('Failed to save mood entry', {
          description: 'Your voice was processed but could not be saved. Please try again.',
          duration: 4000
        })
        setInternalVoiceState('error')
      }
    } catch (error) {
      console.warn('Voice processing failed:', error)
      toast.error('Voice processing failed', {
        description: 'There was an error processing your voice input. Please try again.',
        duration: 3000
      })
      setInternalVoiceState('error')
    }
  }

  const mapEmotionToMood = (emotionResult: any, transcript: string) => {
    // Map emotion analysis results to mood scores
    if (!emotionResult.emotions) return null

    const emotions = emotionResult.emotions
    let mood_score = 5 // Default neutral
    let energy_level = 5
    let stress_level = 5

    // Analyze dominant emotions
    if (emotions.joy > 0.6 || emotions.happiness > 0.6) {
      mood_score = Math.round(7 + (emotions.joy || emotions.happiness) * 3)
      energy_level = Math.round(6 + (emotions.joy || emotions.happiness) * 4)
    } else if (emotions.sadness > 0.5 || emotions.anger > 0.5) {
      mood_score = Math.round(2 + (1 - Math.max(emotions.sadness, emotions.anger)) * 3)
      stress_level = Math.round(6 + Math.max(emotions.sadness, emotions.anger) * 4)
    } else if (emotions.anxiety > 0.5 || emotions.fear > 0.5) {
      stress_level = Math.round(7 + Math.max(emotions.anxiety, emotions.fear) * 3)
      energy_level = Math.round(3 + (1 - Math.max(emotions.anxiety, emotions.fear)) * 2)
    }

    return {
      mood_score: Math.max(1, Math.min(10, mood_score)),
      energy_level: Math.max(1, Math.min(10, energy_level)),
      stress_level: Math.max(1, Math.min(10, stress_level)),
      notes: transcript,
      mood_label: getMoodLabel(mood_score),
      detected_emotions: emotions
    }
  }

  const getMoodLabel = (score: number): string => {
    if (score >= 8) return 'Excellent'
    if (score >= 6) return 'Good'  
    if (score >= 4) return 'Neutral'
    if (score >= 2) return 'Low'
    return 'Very Low'
  }

  const getVoicePrompt = () => {
    if (culturalContext?.voicePrompts) {
      return culturalContext.voicePrompts[currentLanguage] || placeholder
    }
    return placeholder
  }

  const formatDuration = (ms: number) => {
    const seconds = Math.floor(ms / 1000)
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
  }

  // Handle browser compatibility
  if (!permissions.speechRecognition) {
    return (
      <Card className="w-full">
        <CardContent className="p-6">
          <Alert>
            <Warning className="h-4 w-4" />
            <AlertDescription>
              Voice input is not supported in your current browser. 
              Please use Chrome, Edge, or Safari for voice features.
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Microphone size={20} className="text-blue-500" />
            <span>Voice Mood Input</span>
          </div>
          <div className="flex items-center gap-2">
            {voiceState === 'listening' && (
              <Badge variant="outline" className="text-red-600">
                <Circle className="w-2 h-2 mr-1 animate-pulse fill-current" />
                Recording
              </Badge>
            )}
            {confidence > 0 && (
              <Badge variant="outline">
                {Math.round(confidence * 100)}% confident
              </Badge>
            )}
          </div>
        </CardTitle>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Voice Controls */}
        <div className="flex items-center justify-center gap-3">
          <AnimatePresence mode="wait">
            {voiceState === 'idle' ? (
              <motion.div
                key="start"
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.9, opacity: 0 }}
              >
                <Button
                  onClick={startListening}
                  disabled={disabled || permissions.microphone === 'denied'}
                  size="lg"
                  className="h-16 w-16 rounded-full"
                >
                  <Microphone size={24} />
                </Button>
              </motion.div>
            ) : (
              <motion.div
                key="stop"
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.9, opacity: 0 }}
              >
                <Button
                  onClick={stopListening}
                  variant="destructive"
                  size="lg"
                  className="h-16 w-16 rounded-full"
                >
                  <Stop size={24} />
                </Button>
              </motion.div>
            )}
          </AnimatePresence>

          {transcript && (
            <Button
              onClick={resetVoiceInput}
              variant="outline"
              size="sm"
            >
              <ArrowClockwise size={16} />
              Reset
            </Button>
          )}
        </div>

        {/* Voice Instructions */}
        <div className="text-center text-sm text-muted-foreground">
          {voiceState === 'idle' && (
            <p>{mode === 'push-to-talk' ? 'Tap microphone to start' : 'Tap to start continuous recording'}</p>
          )}
          {voiceState === 'listening' && (
            <div className="space-y-2">
              <p className="text-blue-600 font-medium">Listening... speak naturally</p>
              <p className="text-xs">{getVoicePrompt()}</p>
              {recordingDuration > 0 && (
                <p className="text-xs">Duration: {formatDuration(recordingDuration)}</p>
              )}
            </div>
          )}
        </div>

        {/* Audio Level Visualization */}
        {voiceState === 'listening' && (
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <SpeakerHigh size={16} className="text-blue-500" />
              <Progress value={audioLevel} className="flex-1 h-2" />
              <span className="text-xs text-muted-foreground w-8">
                {Math.round(audioLevel)}%
              </span>
            </div>
          </div>
        )}

        {/* Transcript Display */}
        {transcript && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-2"
          >
            <div className="flex items-center gap-2">
              <CheckCircle size={16} className="text-green-500" />
              <span className="text-sm font-medium">Transcript:</span>
            </div>
            <Textarea
              value={transcript}
              onChange={(e) => setTranscript(e.target.value)}
              placeholder={getVoicePrompt()}
              className="min-h-[100px]"
              readOnly={voiceState === 'listening'}
            />
          </motion.div>
        )}

        {/* Error Display */}
        {error && (
          <Alert>
            <Warning className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Language Selection */}
        {supportedLanguages.length > 1 && (
          <div className="flex items-center gap-2">
            <span className="text-sm text-muted-foreground">Language:</span>
            <div className="flex flex-wrap gap-1">
              {supportedLanguages.map((lang) => (
                <Badge
                  key={lang}
                  variant={lang === currentLanguage ? "default" : "outline"}
                  className="cursor-pointer text-xs"
                  onClick={() => onLanguageChange?.(lang)}
                >
                  {lang.split('-')[0].toUpperCase()}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {/* Permission Help */}
        {permissions.microphone === 'denied' && (
          <Alert>
            <MicrophoneSlash className="h-4 w-4" />
            <AlertDescription>
              Microphone access was denied. Please enable microphone permissions 
              in your browser settings to use voice input.
            </AlertDescription>
          </Alert>
        )}
      </CardContent>
    </Card>
  )
}
