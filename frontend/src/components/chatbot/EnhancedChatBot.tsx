import { useState, useRef, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { 
  ChatCircle, 
  Robot, 
  User, 
  ArrowsOut, 
  ArrowsIn, 
  Wind, 
  Microphone, 
  MicrophoneSlash,
  SpeakerHigh,
  SpeakerSlash,
  Translate,
  Globe
} from "@phosphor-icons/react"
import { useChatbot } from "@/hooks/useChatbot"
import { BreathingExercise } from "../common/BreathingExercise"
import { motion, AnimatePresence } from "framer-motion"
import { cn } from "@/lib/utils"
import { toast } from "sonner"
import { apiService } from "@/services/api"

interface ChatBotProps {
  className?: string
}

interface VoiceSettings {
  enabled: boolean
  language: string
  voice: string
  autoSpeak: boolean
}

interface TranslationSettings {
  enabled: boolean
  targetLanguage: string
  showOriginal: boolean
}

interface LanguageDetectionResult {
  language: string
  confidence: number
}

interface SupportedLanguage {
  code: string
  name: string
}

interface TTSResponse {
  audio_url?: string
  success: boolean
}

interface TranslationResult {
  translated_text: string
  source_language: string
  target_language: string
}

export function EnhancedChatBot({ className }: ChatBotProps) {
  const { messages, actions } = useChatbot()
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [isExpanded, setIsExpanded] = useState(false)
  const [showBreathingExercise, setShowBreathingExercise] = useState(false)
  const [isListening, setIsListening] = useState(false)
  const [recognition, setRecognition] = useState<any>(null)
  const [currentLanguage, setCurrentLanguage] = useState("en")
  const [supportedLanguages, setSupportedLanguages] = useState<SupportedLanguage[]>([])
  const [isDetectingLanguage, setIsDetectingLanguage] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  
  // Voice settings
  const [voiceSettings, setVoiceSettings] = useState<VoiceSettings>({
    enabled: true,
    language: "en",
    voice: "default",
    autoSpeak: true
  })
  
  // Translation settings
  const [translationSettings, setTranslationSettings] = useState<TranslationSettings>({
    enabled: false,
    targetLanguage: "en",
    showOriginal: true
  })
  
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

  // Load supported languages
  useEffect(() => {
    const loadLanguages = async () => {
      try {
        const languages = await apiService.getSupportedLanguages()
        setSupportedLanguages(languages as SupportedLanguage[])
      } catch (error) {
        console.warn('Failed to load supported languages:', error)
        // Set default languages
        setSupportedLanguages([
          { code: 'en', name: 'English' },
          { code: 'es', name: 'Spanish' },
          { code: 'fr', name: 'French' },
          { code: 'de', name: 'German' },
          { code: 'hi', name: 'Hindi' },
          { code: 'zh', name: 'Chinese' }
        ])
      }
    }
    loadLanguages()
  }, [])

  // Initialize speech recognition
  useEffect(() => {
    if (typeof window !== 'undefined' && (window.SpeechRecognition || window.webkitSpeechRecognition)) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
      const recognitionInstance = new SpeechRecognition()
      
      recognitionInstance.continuous = false
      recognitionInstance.interimResults = true
      recognitionInstance.lang = voiceSettings.language || 'en-US'
      
      recognitionInstance.onresult = async (event: any) => {
        const transcript = event.results[0][0].transcript
        setInput(transcript)
        
        // Auto-detect language if enabled
        if (isDetectingLanguage) {
          try {
            const result = await apiService.detectLanguage(transcript) as LanguageDetectionResult
            if (result.language && result.language !== currentLanguage) {
              setCurrentLanguage(result.language)
              setVoiceSettings(prev => ({ ...prev, language: result.language }))
              toast.info(`Language detected: ${result.language}`)
            }
          } catch (error) {
            console.warn('Language detection failed:', error)
          }
        }
      }
      
      recognitionInstance.onend = () => {
        setIsListening(false)
      }
      
      recognitionInstance.onerror = (event: any) => {
        console.error('Speech recognition error:', event.error)
        setIsListening(false)
        toast.error('Voice input failed', {
          description: 'Please try again or check your microphone'
        })
      }
      
      setRecognition(recognitionInstance)
    }
  }, [voiceSettings.language, currentLanguage, isDetectingLanguage])

  const handleSend = async () => {
    if (!input.trim()) return
    
    const userMessage = input.trim()
    setInput("")
    setIsLoading(true)
    
    try {
      await actions.sendMessage(userMessage)
      
      // Get the last bot response
      const lastBotMessage = messages[messages.length - 1]
      if (lastBotMessage && lastBotMessage.sender === 'assistant' && voiceSettings.enabled && voiceSettings.autoSpeak) {
        await speakText(lastBotMessage.content)
      }
      
    } catch (error) {
      console.error('Failed to send message:', error)
      toast.error('Failed to send message', {
        description: 'Please try again'
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleVoiceInput = () => {
    if (!recognition) {
      toast.error('Voice input not supported', {
        description: 'Your browser does not support voice input'
      })
      return
    }

    if (isListening) {
      recognition.stop()
      setIsListening(false)
    } else {
      recognition.start()
      setIsListening(true)
      
      toast.info('Voice input started', {
        description: 'Speak naturally about how you\'re feeling'
      })
    }
  }

  const speakText = async (text: string) => {
    if (!voiceSettings.enabled) return
    
    try {
      // Use backend TTS service
      const audioResponse = await apiService.textToSpeech(
        text, 
        voiceSettings.language, 
        voiceSettings.voice
      ) as TTSResponse
      
      // Play the audio
      if (audioResponse.audio_url) {
        const audio = new Audio(audioResponse.audio_url)
        audio.play()
      }
    } catch (error) {
      console.warn('Text-to-speech failed:', error)
      // Fallback to browser TTS
      if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(text)
        utterance.lang = voiceSettings.language
        speechSynthesis.speak(utterance)
      }
    }
  }

  const translateMessage = async (text: string, targetLang: string) => {
    try {
      const result = await apiService.translateText(text, targetLang) as TranslationResult
      return result.translated_text || text
    } catch (error) {
      console.warn('Translation failed:', error)
      return text
    }
  }

  const toggleTranslation = () => {
    setTranslationSettings(prev => ({ 
      ...prev, 
      enabled: !prev.enabled 
    }))
  }

  const toggleVoiceOutput = () => {
    setVoiceSettings(prev => ({ 
      ...prev, 
      enabled: !prev.enabled 
    }))
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
    actions.sendMessage("Great job! How are you feeling now?")
  }
  
  return (
    <div className="space-y-4">
      <Card className={cn("flex flex-col", isExpanded ? "h-[90vh]" : "h-96", className)}>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2 shrink-0">
          <CardTitle className="flex items-center gap-2">
            <Robot className="text-primary" size={24} />
            Mantra-Mitra
            <Badge variant="secondary" className="text-xs">AI Companion</Badge>
            {currentLanguage !== 'en' && (
              <Badge variant="outline" className="text-xs">
                <Globe size={12} className="mr-1" />
                {currentLanguage.toUpperCase()}
              </Badge>
            )}
          </CardTitle>
          
          <div className="flex items-center gap-2">
            {/* Language/Translation Controls */}
            <Button
              variant="ghost"
              size="sm"
              onClick={toggleTranslation}
              className={cn(
                "h-8 w-8 p-0",
                translationSettings.enabled && "bg-blue-100 text-blue-600"
              )}
            >
              <Translate size={16} />
            </Button>
            
            {/* Voice Output Toggle */}
            <Button
              variant="ghost"
              size="sm"
              onClick={toggleVoiceOutput}
              className={cn(
                "h-8 w-8 p-0",
                voiceSettings.enabled && "bg-green-100 text-green-600"
              )}
            >
              {voiceSettings.enabled ? <SpeakerHigh size={16} /> : <SpeakerSlash size={16} />}
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
        
        {/* Language/Translation Settings Panel */}
        {translationSettings.enabled && (
          <div className="px-4 pb-2 border-b">
            <div className="flex items-center gap-2 text-sm">
              <span className="text-muted-foreground">Translate to:</span>
              <Select
                value={translationSettings.targetLanguage}
                onValueChange={(value) => 
                  setTranslationSettings(prev => ({ ...prev, targetLanguage: value }))
                }
              >
                <SelectTrigger className="w-32 h-7">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {supportedLanguages.map((lang) => (
                    <SelectItem key={lang.code} value={lang.code}>
                      {lang.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        )}
        
        <CardContent className="flex-1 flex flex-col gap-4 p-4 min-h-0">
          <div className="flex-1 overflow-y-auto space-y-4">
            <AnimatePresence>
              {messages.map((message) => (
                <MessageBubble
                  key={message.id}
                  message={message}
                  translationSettings={translationSettings}
                  voiceSettings={voiceSettings}
                  onSpeak={speakText}
                  onTranslate={translateMessage}
                />
              ))}
            </AnimatePresence>
            <div ref={messagesEndRef} />
          </div>
          
          {/* Quick Reply Buttons */}
          <div className="flex flex-wrap gap-2">
            {quickReplies.map((reply) => (
              <Button
                key={reply}
                variant="outline"
                size="sm"
                onClick={() => setInput(reply)}
                className="text-xs"
              >
                {reply}
              </Button>
            ))}
            <Button
              variant="outline"
              size="sm"
              onClick={startBreathingExercise}
              className="text-xs"
            >
              <Wind size={14} className="mr-1" />
              Breathing
            </Button>
          </div>
          
          {/* Message Input */}
          <div className="flex gap-2">
            <div className="flex-1 relative">
              <Input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Share what's on your mind..."
                onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && handleSend()}
                disabled={isLoading}
              />
              {isDetectingLanguage && (
                <div className="absolute right-2 top-1/2 -translate-y-1/2">
                  <Globe size={14} className="animate-pulse text-blue-500" />
                </div>
              )}
            </div>
            
            <Button
              variant="outline"
              size="sm"
              onClick={handleVoiceInput}
              disabled={isLoading}
              className={cn(
                "h-10 w-10 p-0",
                isListening && "bg-red-100 text-red-600 animate-pulse"
              )}
            >
              {isListening ? <MicrophoneSlash size={16} /> : <Microphone size={16} />}
            </Button>
            
            <Button onClick={handleSend} disabled={!input.trim() || isLoading} size="sm">
              {isLoading ? 'Sending...' : 'Send'}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Breathing Exercise Modal */}
      {showBreathingExercise && (
        <BreathingExercise onComplete={onBreathingComplete} />
      )}
    </div>
  )
}

// Message Bubble Component with Translation and Voice Features
function MessageBubble({ 
  message, 
  translationSettings, 
  voiceSettings, 
  onSpeak, 
  onTranslate 
}: {
  message: any
  translationSettings: TranslationSettings
  voiceSettings: VoiceSettings
  onSpeak: (text: string) => void
  onTranslate: (text: string, targetLang: string) => Promise<string>
}) {
  const [translatedText, setTranslatedText] = useState<string | null>(null)
  const [isTranslating, setIsTranslating] = useState(false)
  
  useEffect(() => {
    if (translationSettings.enabled && message.sender === 'assistant') {
      const translate = async () => {
        setIsTranslating(true)
        try {
          const translated = await onTranslate(message.content, translationSettings.targetLanguage)
          setTranslatedText(translated)
        } catch (error) {
          console.warn('Translation failed:', error)
        } finally {
          setIsTranslating(false)
        }
      }
      translate()
    } else {
      setTranslatedText(null)
    }
  }, [message.content, translationSettings, onTranslate])
  
  const handleSpeak = () => {
    const textToSpeak = translatedText || message.content
    onSpeak(textToSpeak)
  }
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={cn(
        "flex gap-3",
        message.sender === 'user' ? "justify-end" : "justify-start"
      )}
    >
      {message.sender === 'assistant' && (
        <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center shrink-0">
          <Robot size={16} className="text-primary" />
        </div>
      )}
      
      <div className={cn(
        "max-w-[80%] rounded-lg p-3",
        message.sender === 'user' 
          ? "bg-primary text-primary-foreground" 
          : "bg-muted"
      )}>
        {/* Original message */}
        {translationSettings.enabled && translationSettings.showOriginal && translatedText && (
          <div className="text-xs opacity-70 mb-2 border-b border-current/20 pb-2">
            {message.content}
          </div>
        )}
        
        {/* Main content (translated or original) */}
        <div className="whitespace-pre-wrap">
          {isTranslating ? (
            <div className="flex items-center gap-2">
              <div className="animate-spin w-3 h-3 border border-current border-t-transparent rounded-full" />
              <span className="text-sm opacity-70">Translating...</span>
            </div>
          ) : (
            translatedText || message.content
          )}
        </div>
        
        {/* Voice button for assistant messages */}
        {message.sender === 'assistant' && voiceSettings.enabled && (
          <Button
            variant="ghost"
            size="sm"
            onClick={handleSpeak}
            className="mt-2 h-6 px-2 text-xs opacity-70 hover:opacity-100"
          >
            <SpeakerHigh size={12} className="mr-1" />
            Speak
          </Button>
        )}
      </div>
      
      {message.sender === 'user' && (
        <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center shrink-0">
          <User size={16} className="text-primary" />
        </div>
      )}
    </motion.div>
  )
}

export default EnhancedChatBot
