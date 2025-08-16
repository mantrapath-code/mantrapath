import { useState, useRef, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { ChatCircle, Robot, User, ArrowsOut, ArrowsIn, Wind, Microphone, MicrophoneSlash, SpeakerHigh, SpeakerX, Translate, Gear, X } from "@phosphor-icons/react"
import { useChatbot } from "@/hooks/useChatbot"
import { BreathingExercise } from "../common/BreathingExercise"
import { motion, AnimatePresence } from "framer-motion"
import { cn } from "@/lib/utils"
import { toast } from "sonner"
import { apiService } from "@/services/api"

interface ChatBotProps {
  className?: string
}

export function ChatBot({ className }: ChatBotProps) {
  const { messages, actions } = useChatbot()
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [isExpanded, setIsExpanded] = useState(false)
  const [showBreathingExercise, setShowBreathingExercise] = useState(false)
  const [isListening, setIsListening] = useState(false)
  const [recognition, setRecognition] = useState<any>(null)
  const [isSpeaking, setIsSpeaking] = useState(false)
  const [voiceEnabled, setVoiceEnabled] = useState(true)
  const [selectedLanguage, setSelectedLanguage] = useState('en')
  const [autoTranslate, setAutoTranslate] = useState(false)
  const [autoTTS, setAutoTTS] = useState(true) // New setting for auto TTS on voice input
  const [showSettings, setShowSettings] = useState(false)
  const [supportedLanguages, setSupportedLanguages] = useState<any[]>([])
  const [lastInputMethod, setLastInputMethod] = useState<'text' | 'voice'>('text') // Track input method
  const [lastTTSMessageId, setLastTTSMessageId] = useState<string | null>(null) // Prevent TTS loops
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const audioRef = useRef<HTMLAudioElement>(null)
  
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }
  
  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Initialize chat session on mount
  useEffect(() => {
    if (messages.length === 0) {
      actions.startNewSession()
    }
  }, [actions, messages.length])

  // Initialize speech recognition
  useEffect(() => {
    if (typeof window !== 'undefined' && (window.SpeechRecognition || window.webkitSpeechRecognition)) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
      const recognitionInstance = new SpeechRecognition()
      
      recognitionInstance.continuous = false
      recognitionInstance.interimResults = true
      recognitionInstance.lang = selectedLanguage === 'en' ? 'en-US' : `${selectedLanguage}-${selectedLanguage.toUpperCase()}`
      
      recognitionInstance.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript
        setInput(transcript)
      }
      
      recognitionInstance.onend = () => {
        setIsListening(false)
      }
      
      recognitionInstance.onerror = (event: any) => {
        console.error('Speech recognition error:', event.error)
        setIsListening(false)
        toast.error(`Speech recognition error: ${event.error}`)
      }
      
      setRecognition(recognitionInstance)
    } else {
      console.warn('Speech recognition not supported, will use backend STT service')
    }
  }, [selectedLanguage])
  
  // Effect to handle TTS for new bot messages (only for voice responses when user spoke and auto TTS is enabled)
  useEffect(() => {
    if (voiceEnabled && autoTTS && messages.length > 0) {
      const lastMessage = messages[messages.length - 1]
      // Only trigger TTS for assistant responses that are NOT greeting/welcome messages
      // and only if the user used voice input (indicating they want voice interaction)
      // and we haven't already spoken this message
      if (lastMessage && 
          lastMessage.sender === 'assistant' && 
          lastMessage.messageType !== 'greeting' &&
          lastInputMethod === 'voice' &&
          lastMessage.id !== lastTTSMessageId &&
          messages.length > 1) { // Ensure there's been at least one user message
        // Delay TTS slightly to ensure message is rendered
        setTimeout(() => {
          speakMessage(lastMessage.content)
          setLastTTSMessageId(lastMessage.id) // Mark this message as spoken
        }, 500)
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [messages, voiceEnabled, autoTTS, lastInputMethod])

  const handleSend = async () => {
    if (!input.trim()) return
    
    let userMessage = input.trim()
    const originalMessage = userMessage
    setInput("")
    setIsLoading(true)
    setLastInputMethod('text') // Mark this as text input
    
    try {
      // Step 1: Handle language detection and translation if enabled
      if (autoTranslate && selectedLanguage !== 'en') {
        userMessage = await handleLanguageDetectionAndTranslation(userMessage)
      }
      
      // Step 2: Send message to enhanced chatbot (includes automatic mood analysis and orchestration)
      await actions.sendMessage(userMessage)
      
      toast.success('Message sent successfully', {
        description: 'AI analysis and mood tracking completed'
      })
      
    } catch (error) {
      console.error('Failed to send message:', error)
      toast.error('Failed to send message')
    } finally {
      setIsLoading(false)
    }
  }

  // Dedicated function for handling voice input sending
  const handleSendVoiceInput = async (transcribedText: string) => {
    if (!transcribedText.trim()) {
      console.log('handleSendVoiceInput: Empty text, aborting')
      return
    }
    
    console.log('handleSendVoiceInput: Processing text:', transcribedText)
    
    setInput("")
    setIsLoading(true)
    setLastInputMethod('voice') // Ensure it's marked as voice input
    
    try {
      // Step 1: Handle language detection and translation if enabled
      let userMessage = transcribedText.trim()
      if (autoTranslate && selectedLanguage !== 'en') {
        console.log('Attempting translation for voice input')
        userMessage = await handleLanguageDetectionAndTranslation(userMessage)
      }
      
      console.log('Sending voice message to enhanced chatbot:', userMessage)
      
      // Step 2: Send message to enhanced chatbot (includes automatic mood analysis, intent recognition, and orchestration)
      await actions.sendMessage(userMessage)
      
      toast.success('Voice message sent successfully', {
        description: 'AI analysis, intent recognition, and mood tracking completed'
      })
      
    } catch (error) {
      console.error('Failed to send voice message:', error)
      toast.error('Failed to send voice message', {
        description: error instanceof Error ? error.message : 'Unknown error occurred'
      })
      // Restore the input so user can try again
      setInput(transcribedText)
    } finally {
      setIsLoading(false)
    }
  }

  const handleVoiceInput = async () => {
    if (!recognition) {
      toast.error('Speech recognition not supported in this browser')
      return
    }

    if (isListening) {
      recognition.stop()
      setIsListening(false)
    } else {
      try {
        setIsListening(true)
        
        toast.info('Voice recording started', {
          description: 'Speak clearly about how you\'re feeling...'
        })
        
        // Start recording for backend processing
        const stream = await navigator.mediaDevices.getUserMedia({ 
          audio: {
            echoCancellation: true,
            noiseSuppression: true,
            sampleRate: 44100
          } 
        })
        
        // Check if MediaRecorder is supported
        if (!MediaRecorder.isTypeSupported('audio/webm')) {
          throw new Error('Audio recording not supported in this browser')
        }
        
        const mediaRecorder = new MediaRecorder(stream, {
          mimeType: 'audio/webm'
        })
        const audioChunks: BlobPart[] = []
        
        console.log('MediaRecorder created, state:', mediaRecorder.state)
        
        mediaRecorder.ondataavailable = (event) => {
          console.log('Audio data available, size:', event.data.size)
          if (event.data.size > 0) {
            audioChunks.push(event.data)
          }
        }
        
        mediaRecorder.onstart = () => {
          console.log('MediaRecorder started successfully, state:', mediaRecorder.state)
        }
        
        mediaRecorder.onerror = (event) => {
          console.error('MediaRecorder error:', event)
          toast.error('Recording error occurred')
          setIsListening(false)
        }
        
        mediaRecorder.onstop = async () => {
          console.log('MediaRecorder stopped, chunks:', audioChunks.length)
          const audioBlob = new Blob(audioChunks, { type: 'audio/webm' })
          console.log('Created audio blob, size:', audioBlob.size, 'type:', audioBlob.type)
          
          if (audioBlob.size === 0) {
            toast.error('No audio recorded', {
              description: 'Please check your microphone permissions'
            })
            return
          }
          
          try {
            toast.info('Processing voice input...', {
              description: 'Converting speech to text'
            })
            
            // Use backend speech-to-text service
            const sttResult = await apiService.speechToText(audioBlob, selectedLanguage)
            console.log('STT Result:', sttResult) // Debug log
            
            // Extract text from VoiceResponse structure: data.transcription.text
            let transcribedText = ''
            if (sttResult && (sttResult as any).success && (sttResult as any).data?.transcription?.text) {
              transcribedText = (sttResult as any).data.transcription.text.trim()
            } else if (sttResult && (sttResult as any).text) {
              // Fallback for other response formats
              transcribedText = (sttResult as any).text.trim()
            }
            
            if (transcribedText) {
              setInput(transcribedText)
              setLastInputMethod('voice') // Mark this as voice input
              
              toast.success('Voice input captured', {
                description: `Detected: "${transcribedText.substring(0, 50)}..."`
              })
              
              // Auto-send after voice input with a reasonable delay
              setTimeout(() => {
                // Double check the input is still there and send
                if (transcribedText) {
                  handleSendVoiceInput(transcribedText)
                }
              }, 1500)
            } else {
              console.log('STT result empty or missing text:', sttResult)
              toast.error('No speech detected', {
                description: 'Please try speaking again, louder and clearer'
              })
            }
          } catch (error) {
            console.error('Speech-to-text error:', error)
            toast.error('Backend speech-to-text failed', {
              description: 'Please try again or type your message'
            })
            
            // Restore the text input as fallback
            setInput('')
          }
          
          // Stop all tracks and cleanup
          stream.getTracks().forEach(track => track.stop())
          clearTimeout(autoStopTimeout)
          setIsListening(false)
        }
        
        // Start recording
        try {
          mediaRecorder.start(1000) // Collect data every 1000ms
          console.log('MediaRecorder.start() called, waiting for onstart event...')
          
          // Verify recording started after a brief delay
          setTimeout(() => {
            console.log('MediaRecorder state after start attempt:', mediaRecorder.state)
            if (mediaRecorder.state !== 'recording') {
              throw new Error('Failed to start recording - check microphone permissions')
            }
          }, 100)
          
        } catch (startError) {
          console.error('Failed to start MediaRecorder:', startError)
          stream.getTracks().forEach(track => track.stop())
          setIsListening(false)
          toast.error('Failed to start recording', {
            description: 'Please check microphone permissions and try again'
          })
          return
        }
        
        toast.info('Voice input started', {
          description: 'Speak naturally about how you\'re feeling. Recording will stop automatically.'
        })
        
        // Auto-stop after 10 seconds
        const autoStopTimeout = setTimeout(() => {
          if (mediaRecorder.state === 'recording') {
            console.log('Auto-stopping recording after 10 seconds')
            mediaRecorder.stop()
          }
        }, 10000)
        
      } catch (error) {
        console.error('Failed to start voice input:', error)
        toast.error('Failed to access microphone', {
          description: error instanceof Error ? error.message : 'Please check permissions and try again'
        })
        setIsListening(false)
      }
    }
  }
  
  const quickReplies = [
    "How are you feeling?",
    "I'm feeling anxious",
    "Need support", 
    "Gratitude practice",
    "Breathing exercise"
  ]

  const startBreathingExercise = () => {
    setShowBreathingExercise(true)
    actions.sendMessage("I'd like to try a breathing exercise")
  }

  const onBreathingComplete = () => {
    setShowBreathingExercise(false)
    actions.sendMessage("Great job! How are you feeling now? Remember, you can always come back to breathing exercises whenever you need them. 🌟")
  }

  // Load supported languages on mount
  useEffect(() => {
    const loadLanguages = async () => {
      try {
        const languages = await apiService.getSupportedLanguages()
        setSupportedLanguages(Array.isArray(languages) ? languages : [])
      } catch (error) {
        console.error('Failed to load supported languages:', error)
      }
    }
    loadLanguages()
  }, [])

  // Text-to-Speech functionality
  const speakMessage = async (text: string) => {
    if (!voiceEnabled || isSpeaking) return
    
    try {
      setIsSpeaking(true)
      
      // Try backend TTS first
      try {
        const audioResponse = await apiService.textToSpeech(text, selectedLanguage, 'default') as any
        
        if (audioResponse && (audioResponse.audio_url || audioResponse.audio_data)) {
          const audioUrl = audioResponse.audio_url || 
            `data:audio/mp3;base64,${audioResponse.audio_data}`
          
          const audio = new Audio(audioUrl)
          audio.onended = () => setIsSpeaking(false)
          audio.onerror = () => {
            setIsSpeaking(false)
            // Fallback to browser TTS
            fallbackTTS(text)
          }
          await audio.play()
          return
        }
      } catch (backendError) {
        console.warn('Backend TTS failed, falling back to browser TTS:', backendError)
      }
      
      // Fallback to browser TTS
      fallbackTTS(text)
      
    } catch (error) {
      console.error('Text-to-speech error:', error)
      setIsSpeaking(false)
      toast.error('Voice output failed')
    }
  }

  // Fallback browser TTS
  const fallbackTTS = (text: string) => {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text)
      utterance.lang = selectedLanguage === 'en' ? 'en-US' : selectedLanguage
      utterance.rate = 0.9
      utterance.pitch = 1.0
      utterance.volume = 0.8
      
      utterance.onend = () => setIsSpeaking(false)
      utterance.onerror = () => {
        setIsSpeaking(false)
        toast.error('Voice output failed')
      }
      
      speechSynthesis.speak(utterance)
      
      toast.info('Using browser voice synthesis', {
        description: 'Backend TTS unavailable'
      })
    } else {
      setIsSpeaking(false)
      toast.error('Text-to-speech not supported in this browser')
    }
  }

  // Language detection and translation
  const handleLanguageDetectionAndTranslation = async (message: string) => {
    if (!autoTranslate) return message
    
    try {
      const detectedLang = await apiService.detectLanguage(message) as any
      
      if (detectedLang && detectedLang.language !== selectedLanguage) {
        const translated = await apiService.translateText(message, selectedLanguage, detectedLang.language) as any
        
        if (translated && translated.translated_text) {
          toast.info(`Translated from ${detectedLang.language}`, {
            description: `Original: "${message.substring(0, 50)}..."`
          })
          return translated.translated_text
        }
      }
    } catch (error) {
      console.error('Translation error:', error)
    }
    
    return message
  }

  // Stop speech synthesis
  const stopSpeaking = () => {
    if (audioRef.current) {
      audioRef.current.pause()
      audioRef.current.currentTime = 0
    }
    setIsSpeaking(false)
  }
  
  return (
    <div className="space-y-4">
      <Card className={cn("flex flex-col", isExpanded ? "h-[90vh]" : "h-96", className)}>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2 shrink-0">
          <CardTitle className="flex items-center gap-2">
            <Robot className="text-primary" size={24} />
            Mantra-Mitra
            <Badge variant="secondary" className="text-xs">AI Companion</Badge>
          </CardTitle>
          <div className="flex items-center gap-1">
            {/* Voice Toggle */}
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setVoiceEnabled(!voiceEnabled)}
              title={voiceEnabled ? "Disable voice output" : "Enable voice output"}
            >
              {voiceEnabled ? <SpeakerHigh size={16} /> : <SpeakerX size={16} />}
            </Button>
            
            {/* Stop Speaking */}
            {isSpeaking && (
              <Button
                variant="ghost"
                size="sm"
                onClick={stopSpeaking}
                title="Stop speaking"
                className="text-red-500"
              >
                <SpeakerX size={16} />
              </Button>
            )}
            
            {/* Translation Toggle */}
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setAutoTranslate(!autoTranslate)}
              title={autoTranslate ? "Disable auto-translation" : "Enable auto-translation"}
              className={autoTranslate ? "text-blue-500" : ""}
            >
              <Translate size={16} />
            </Button>
            
            {/* Settings */}
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowSettings(!showSettings)}
              title="Language settings"
            >
              <Gear size={16} />
            </Button>
            
            {/* Expand/Collapse */}
            {!className?.includes('h-full') && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsExpanded(!isExpanded)}
              >
                {isExpanded ? <ArrowsIn size={16} /> : <ArrowsOut size={16} />}
              </Button>
            )}
          </div>
        </CardHeader>
        
        {/* Settings Panel */}
        {showSettings && (
          <div className="border-b bg-muted/30 p-4 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Language Settings</span>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowSettings(false)}
              >
                <X size={14} />
              </Button>
            </div>
            
            <div className="space-y-2">
              <label className="text-xs text-muted-foreground">Voice Language</label>
              <select 
                value={selectedLanguage} 
                onChange={(e) => setSelectedLanguage(e.target.value)}
                className="w-full text-sm border rounded px-2 py-1"
              >
                <option value="en">English</option>
                <option value="es">Spanish</option>
                <option value="fr">French</option>
                <option value="de">German</option>
                <option value="it">Italian</option>
                <option value="pt">Portuguese</option>
                <option value="hi">Hindi</option>
                <option value="zh">Chinese</option>
              </select>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-xs text-muted-foreground">Auto-translate messages</span>
              <Button
                variant={autoTranslate ? "default" : "outline"}
                size="sm"
                onClick={() => setAutoTranslate(!autoTranslate)}
              >
                {autoTranslate ? "On" : "Off"}
              </Button>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-xs text-muted-foreground">Voice responses</span>
              <Button
                variant={voiceEnabled ? "default" : "outline"}
                size="sm"
                onClick={() => setVoiceEnabled(!voiceEnabled)}
              >
                {voiceEnabled ? "On" : "Off"}
              </Button>
            </div>
            
            {voiceEnabled && (
              <div className="flex items-center justify-between">
                <span className="text-xs text-muted-foreground">Auto TTS for voice input</span>
                <Button
                  variant={autoTTS ? "default" : "outline"}
                  size="sm"
                  onClick={() => setAutoTTS(!autoTTS)}
                  title="Automatically speak responses when you use voice input"
                >
                  {autoTTS ? "On" : "Off"}
                </Button>
              </div>
            )}
          </div>
        )}
        
        <CardContent className="flex-1 flex flex-col gap-4 p-4 min-h-0">
          <div className={cn(
            "flex-1 overflow-y-auto space-y-4",
            className?.includes('h-full') ? "max-h-none" : "max-h-64"
          )}>
            <AnimatePresence>
              {messages.length === 0 && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="text-center p-4 bg-muted/50 rounded-lg"
                >
                  <p className="text-sm text-muted-foreground">
                    Hello! I'm Mantra-Mitra, your AI wellness companion. 💜
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">
                    {voiceEnabled && "🔊 Voice responses enabled"} 
                    {autoTranslate && " • 🌐 Auto-translation active"}
                    {selectedLanguage !== 'en' && ` • Language: ${selectedLanguage.toUpperCase()}`}
                  </p>
                  <p className="text-sm text-muted-foreground mt-2">
                    How can I support you today?
                  </p>
                </motion.div>
              )}
              
              {messages.map((message) => (
                <motion.div
                  key={message.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={cn(
                    "flex gap-2",
                    message.sender === 'user' ? "justify-end" : "justify-start"
                  )}
                >
                  {message.sender === 'assistant' && (
                    <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center shrink-0 mt-1">
                      <Robot size={16} className="text-primary" />
                    </div>
                  )}
                  
                  <div className={cn(
                    "max-w-[80%] p-3 rounded-lg text-sm space-y-2",
                    message.sender === 'user' 
                      ? "bg-primary text-primary-foreground" 
                      : "bg-muted"
                  )}>
                    <p>{message.content}</p>
                    
                    {/* Enhanced AI Features Display */}
                    {message.sender === 'assistant' && message.orchestration_metadata && (
                      <div className="text-xs text-muted-foreground bg-background/50 p-2 rounded border">
                        <div className="flex items-center gap-2 mb-1">
                          <Badge variant="outline" className="text-xs">
                            AI Enhanced
                          </Badge>
                          {message.confidence_score && (
                            <span>Confidence: {Math.round(message.confidence_score * 100)}%</span>
                          )}
                        </div>
                        {message.intent && (
                          <div>Intent: {message.intent.intent_type} ({Math.round(message.intent.confidence * 100)}%)</div>
                        )}
                        {message.orchestration_metadata.services_involved && (
                          <div>Services: {message.orchestration_metadata.services_involved.join(', ')}</div>
                        )}
                      </div>
                    )}
                    
                    {/* Suggested Actions */}
                    {message.sender === 'assistant' && message.suggested_actions && message.suggested_actions.length > 0 && (
                      <div className="space-y-1">
                        <p className="text-xs text-muted-foreground font-medium">Suggested Actions:</p>
                        <div className="flex flex-wrap gap-1">
                          {message.suggested_actions.map((action, index) => (
                            <Button
                              key={index}
                              variant="outline"
                              size="sm"
                              className="text-xs h-6"
                              onClick={() => {
                                if (action.action === 'track_mood') {
                                  // Navigate to mood tracking or trigger mood entry
                                  toast.info('Opening mood tracker...')
                                } else if (action.action === 'start_breathing') {
                                  startBreathingExercise()
                                } else if (action.action === 'create_journal') {
                                  toast.info('Opening journal...')
                                } else {
                                  // Generic action
                                  setInput(action.label)
                                }
                              }}
                              title={action.description}
                            >
                              {action.label}
                            </Button>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    {/* Mood Insights */}
                    {message.sender === 'assistant' && message.mood_insights && (
                      <div className="text-xs bg-blue-50 dark:bg-blue-950 p-2 rounded border">
                        <p className="font-medium text-blue-700 dark:text-blue-300">Mood Insight:</p>
                        <p className="text-blue-600 dark:text-blue-400">
                          {message.mood_insights.mood_level && `Mood: ${message.mood_insights.mood_level}`}
                          {message.mood_insights.sentiment && ` • Sentiment: ${message.mood_insights.sentiment}`}
                        </p>
                      </div>
                    )}
                    
                    {message.sender === 'assistant' && (
                      <div className="flex gap-2 mt-2">
                        {message.breathingExercise && (
                          <Button
                            onClick={startBreathingExercise}
                            size="sm"
                            variant="outline"
                          >
                            <Wind size={14} className="mr-2" />
                            Start Breathing Exercise
                          </Button>
                        )}
                        {voiceEnabled && (
                          <Button
                            onClick={() => speakMessage(message.content)}
                            size="sm"
                            variant="ghost"
                            disabled={isSpeaking}
                            title="Play voice response"
                          >
                            <SpeakerHigh size={14} />
                          </Button>
                        )}
                      </div>
                    )}
                    
                    {message.breathingExercise && message.sender === 'assistant' && !voiceEnabled && (
                      <Button
                        onClick={startBreathingExercise}
                        size="sm"
                        variant="outline"
                        className="mt-2"
                      >
                        <Wind size={14} className="mr-2" />
                        Start Breathing Exercise
                      </Button>
                    )}
                  </div>
                  
                  {message.sender === 'user' && (
                    <div className="w-8 h-8 rounded-full bg-accent/10 flex items-center justify-center shrink-0 mt-1">
                      <User size={16} className="text-accent-foreground" />
                    </div>
                  )}
                </motion.div>
              ))}
            </AnimatePresence>
            
            {isLoading && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex justify-start"
              >
                <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center shrink-0">
                  <Robot size={16} className="text-primary" />
                </div>
                <div className="ml-2 bg-muted p-3 rounded-lg">
                  <div className="flex gap-1">
                    <div className="w-2 h-2 bg-muted-foreground/60 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                    <div className="w-2 h-2 bg-muted-foreground/60 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                    <div className="w-2 h-2 bg-muted-foreground/60 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                  </div>
                </div>
              </motion.div>
            )}
            
            <div ref={messagesEndRef} />
          </div>
          
          {messages.length === 0 && (
            <div className="flex flex-wrap gap-2">
              {quickReplies.map((reply) => (
                <Button
                  key={reply}
                  variant="outline"
                  size="sm"
                  className="text-xs"
                  onClick={() => {
                    if (reply === "Breathing exercise") {
                      startBreathingExercise()
                    } else {
                      setInput(reply)
                    }
                  }}
                >
                  {reply}
                </Button>
              ))}
            </div>
          )}
          
          <div className="flex gap-2">
            <div className="flex-1 relative">
              <Input
                placeholder="Share what's on your mind..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                disabled={isLoading}
                className={cn(
                  "flex-1",
                  (autoTranslate || isSpeaking) && "pr-32"
                )}
              />
              {/* Status indicators */}
              {(autoTranslate || isSpeaking) && (
                <div className="absolute right-2 top-1/2 transform -translate-y-1/2 flex gap-1">
                  {autoTranslate && (
                    <Badge variant="secondary" className="text-xs h-5">
                      Auto-translate
                    </Badge>
                  )}
                  {isSpeaking && (
                    <Badge variant="default" className="text-xs h-5 bg-blue-500">
                      Speaking...
                    </Badge>
                  )}
                </div>
              )}
            </div>
            {recognition && (
              <Button
                onClick={handleVoiceInput}
                variant={isListening ? "destructive" : "outline"}
                size="icon"
                disabled={isLoading}
                title={isListening ? "Stop recording" : "Start voice input"}
              >
                {isListening ? <MicrophoneSlash size={16} /> : <Microphone size={16} />}
              </Button>
            )}
            
            {/* Debug: Test Voice Input Button - Remove in production */}
            {process.env.NODE_ENV === 'development' && (
              <Button
                onClick={() => {
                  const testMessage = "Hello, I'm testing voice input"
                  setInput(testMessage)
                  setLastInputMethod('voice')
                  setTimeout(() => handleSendVoiceInput(testMessage), 500)
                }}
                variant="outline"
                size="sm"
                title="Test voice input flow"
              >
                Test Voice
              </Button>
            )}
            
            <Button onClick={handleSend} disabled={isLoading || !input.trim()}>
              <ChatCircle size={16} />
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Breathing Exercise Modal */}
      <AnimatePresence>
        {showBreathingExercise && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.2 }}
          >
            <BreathingExercise 
              onComplete={onBreathingComplete}
              className="border-2 border-primary/20"
            />
          </motion.div>
        )}
      </AnimatePresence>
      
      {/* Audio element for TTS */}
      <audio ref={audioRef} style={{ display: 'none' }} />
    </div>
  )
}

function detectMoodFromMessage(message: string): 'very-low' | 'low' | 'neutral' | 'good' | 'excellent' | null {
  const lowerMessage = message.toLowerCase()
  
  const veryLowKeywords = ['terrible', 'awful', 'hopeless', 'suicidal', 'can\'t go on']
  const lowKeywords = ['sad', 'depressed', 'anxious', 'stressed', 'worried', 'overwhelmed', 'struggling']
  const goodKeywords = ['happy', 'excited', 'grateful', 'peaceful', 'content', 'positive']
  const excellentKeywords = ['amazing', 'fantastic', 'incredible', 'wonderful', 'ecstatic', 'thrilled']
  
  if (veryLowKeywords.some(word => lowerMessage.includes(word))) return 'very-low'
  if (lowKeywords.some(word => lowerMessage.includes(word))) return 'low'
  if (excellentKeywords.some(word => lowerMessage.includes(word))) return 'excellent'
  if (goodKeywords.some(word => lowerMessage.includes(word))) return 'good'
  
  return null
}

function checkForBreathingRequest(message: string): boolean {
  const lowerMessage = message.toLowerCase()
  const breathingKeywords = [
    'breathing', 'breathe', 'stress', 'anxious', 'anxiety', 'panic', 'calm', 'relax', 'overwhelmed'
  ]
  return breathingKeywords.some(word => lowerMessage.includes(word))
}

function getRecommendedExerciseType(message: string): '4-7-8' | '4-4-4-4' | 'box' {
  const lowerMessage = message.toLowerCase()
  
  if (lowerMessage.includes('panic') || lowerMessage.includes('anxiety')) {
    return '4-7-8' // Best for anxiety
  }
  if (lowerMessage.includes('focus') || lowerMessage.includes('concentrate')) {
    return '4-4-4-4' // Box breathing for focus
  }
  return 'box' // Default simple breathing
}