import { useState, useRef, useEffect, useCallback } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
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
  SpeakerX, 
  Translate, 
  Gear, 
  X,
  Minus
} from "@phosphor-icons/react"
import { useChatbot } from "@/hooks/useChatbot"
import { BreathingExercise } from "../common/BreathingExercise"
import { motion, AnimatePresence } from "framer-motion"
import { cn } from "@/lib/utils"
import { toast } from "sonner"
import { apiService } from "@/services/api"

interface MinimizableChatBotProps {
  className?: string
}

export function MinimizableChatBot({ className }: MinimizableChatBotProps) {
  const { messages, actions } = useChatbot()
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [isExpanded, setIsExpanded] = useState(false)
  const [isMinimized, setIsMinimized] = useState(false)
  const [showBreathingExercise, setShowBreathingExercise] = useState(false)
  const [isListening, setIsListening] = useState(false)
  const [recognition, setRecognition] = useState<any>(null)
  const [isSpeaking, setIsSpeaking] = useState(false)
  const [voiceEnabled, setVoiceEnabled] = useState(true)
  const [selectedLanguage, setSelectedLanguage] = useState('en')
  const [autoTranslate, setAutoTranslate] = useState(false)
  const [autoTTS, setAutoTTS] = useState(true)
  const [showSettings, setShowSettings] = useState(false)
  const [supportedLanguages, setSupportedLanguages] = useState<any[]>([])
  const [lastInputMethod, setLastInputMethod] = useState<'text' | 'voice'>('text')
  const [lastTTSMessageId, setLastTTSMessageId] = useState<string | null>(null)
  const isMountedRef = useRef(true)
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
    
    return () => {
      isMountedRef.current = false
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
        toast.error("Speech recognition failed. Please try again.")
      }
      
      setRecognition(recognitionInstance)
    }
  }, [selectedLanguage])

  const handleSendMessage = async () => {
    if (!input.trim() || isLoading) return
    
    const messageText = input.trim()
    setInput("")
    setIsLoading(true)
    setLastInputMethod('text')
    
    try {
      await actions.sendMessage(messageText, autoTranslate)
    } catch (error) {
      console.error('Error sending message:', error)
      toast.error("Failed to send message. Please try again.")
    } finally {
      setIsLoading(false)
    }
  }

  const toggleVoiceRecording = () => {
    if (isListening) {
      recognition?.stop()
    } else {
      recognition?.start()
      setIsListening(true)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const quickReplies = [
    "How are you feeling?",
    "I'm feeling anxious", 
    "Need support",
    "Breathing exercise",
    "Gratitude practice"
  ]

  const startBreathingExercise = () => {
    setShowBreathingExercise(true)
    actions.sendMessage("I'd like to try a breathing exercise")
  }

  const onBreathingComplete = () => {
    setShowBreathingExercise(false)
    actions.sendMessage("Great job! How are you feeling now?")
  }

  // Auto-synthesize speech for assistant messages
  useEffect(() => {
    if (voiceEnabled && messages.length > 0) {
      const lastMessage = messages[messages.length - 1]
      const shouldPlayTTS = (
        lastMessage.sender === 'assistant' && 
        lastMessage.id !== lastTTSMessageId &&
        (lastInputMethod === 'voice' ? autoTTS : true)
      )
      
      if (shouldPlayTTS && isMountedRef.current) {
        synthesizeSpeech(lastMessage.content, lastMessage.id)
      }
    }
  }, [messages, voiceEnabled, autoTTS, lastInputMethod, lastTTSMessageId])

  const synthesizeSpeech = async (text: string, messageId: string) => {
    try {
      setIsSpeaking(true)
      setLastTTSMessageId(messageId)

      const cleanText = text.replace(/[*#]/g, '').substring(0, 500)
      
      const response = await apiService.request('/voice/tts', {
        method: 'POST',
        body: JSON.stringify({
          text: cleanText,
          language: selectedLanguage,
          voice: selectedLanguage === 'en' ? 'en_female' : `${selectedLanguage}_female`
        })
      })

      if ((response as any)?.audio_url && isMountedRef.current) {
        if (audioRef.current) {
          audioRef.current.src = (response as any).audio_url
          await audioRef.current.play()
        }
      }
    } catch (error) {
      console.error('TTS Error:', error)
    } finally {
      if (isMountedRef.current) {
        setIsSpeaking(false)
      }
    }
  }

  const stopSpeaking = () => {
    if (audioRef.current) {
      audioRef.current.pause()
      audioRef.current.currentTime = 0
    }
    setIsSpeaking(false)
  }

  // If minimized, show only the floating button
  if (isMinimized) {
    return (
      <motion.div
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        className={cn(
          "fixed bottom-4 right-4 z-50",
          className
        )}
      >
        <Button
          size="lg"
          className="rounded-full h-16 w-16 shadow-lg hover:shadow-xl transition-shadow bg-primary hover:bg-primary/90"
          onClick={() => setIsMinimized(false)}
        >
          <Robot size={24} />
        </Button>
        {messages.length > 0 && messages[messages.length - 1].sender === 'assistant' && (
          <div className="absolute -top-2 -right-2 w-4 h-4 bg-red-500 rounded-full animate-pulse" />
        )}
      </motion.div>
    )
  }
  
  return (
    <div className={cn("space-y-4", className)} data-chat-widget>
      <audio ref={audioRef} onEnded={() => setIsSpeaking(false)} />
      
      <Card className={cn(
        "flex flex-col transition-all duration-300",
        isExpanded ? "h-[90vh]" : "h-96"
      )}>
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
            
            {/* Minimize */}
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsMinimized(true)}
              title="Minimize chatbot"
            >
              <Minus size={16} />
            </Button>
            
            {/* Expand/Collapse */}
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsExpanded(!isExpanded)}
              title={isExpanded ? "Collapse" : "Expand"}
            >
              {isExpanded ? <ArrowsIn size={16} /> : <ArrowsOut size={16} />}
            </Button>
          </div>
        </CardHeader>
        
        {/* Settings Panel */}
        <AnimatePresence>
          {showSettings && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              className="border-b bg-muted/30 overflow-hidden"
            >
              <div className="p-4 space-y-3">
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
                    className="w-full text-sm border rounded px-2 py-1 bg-background"
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
            </motion.div>
          )}
        </AnimatePresence>
        
        <CardContent className="flex-1 flex flex-col gap-4 p-4 min-h-0">
          {/* Messages Area */}
          <div className={cn(
            "flex-1 overflow-y-auto space-y-4",
            isExpanded ? "max-h-none" : "max-h-64"
          )}>
            <AnimatePresence mode="popLayout">
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
                </motion.div>
              )}
              
              {messages.map((message) => (
                <motion.div
                  key={message.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  className={cn(
                    "flex gap-2",
                    message.sender === "user" ? "justify-end" : "justify-start"
                  )}
                >
                  {message.sender === "assistant" && (
                    <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center shrink-0">
                      <Robot size={16} className="text-primary" />
                    </div>
                  )}
                  
                  <div className={cn(
                    "max-w-[70%] p-3 rounded-lg",
                    message.sender === "user" 
                      ? "bg-primary text-primary-foreground" 
                      : "bg-muted"
                  )}>
                    <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                    
                    {/* Message metadata */}
                    {message.sender === 'assistant' && message.orchestration_metadata && (
                      <div className="mt-2 text-xs text-muted-foreground border-t pt-2">
                        <div>Response Time: {message.orchestration_metadata.execution_time_ms}ms</div>
                        {message.orchestration_metadata.services_involved && (
                          <div>Services: {message.orchestration_metadata.services_involved.join(', ')}</div>
                        )}
                      </div>
                    )}
                    
                    {/* Suggested Actions */}
                    {message.sender === 'assistant' && message.suggested_actions && message.suggested_actions.length > 0 && (
                      <div className="space-y-1 mt-2">
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
                                  toast.info('Opening mood tracker...')
                                } else if (action.action === 'start_breathing') {
                                  startBreathingExercise()
                                } else if (action.action === 'journal_entry') {
                                  toast.info('Opening journal...')
                                }
                              }}
                            >
                              {action.label}
                            </Button>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                  
                  {message.sender === "user" && (
                    <div className="w-8 h-8 rounded-full bg-secondary flex items-center justify-center shrink-0">
                      <User size={16} />
                    </div>
                  )}
                </motion.div>
              ))}
              
              {isLoading && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="flex gap-2 justify-start"
                >
                  <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                    <Robot size={16} className="text-primary" />
                  </div>
                  <div className="bg-muted p-3 rounded-lg">
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-muted-foreground/60 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                      <div className="w-2 h-2 bg-muted-foreground/60 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                      <div className="w-2 h-2 bg-muted-foreground/60 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
            
            <div ref={messagesEndRef} />
          </div>
          
          {/* Quick Replies */}
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
          
          {/* Input Area */}
          <div className="flex gap-2">
            <div className="flex-1 relative">
              <Input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Share what's on your mind..."
                className="pr-12"
                disabled={isLoading}
              />
              
              {/* Voice Recording Button */}
              {recognition && (
                <Button
                  variant="ghost"
                  size="sm"
                  className={cn(
                    "absolute right-1 top-1 h-8 w-8 p-0",
                    isListening && "text-red-500 animate-pulse"
                  )}
                  onClick={toggleVoiceRecording}
                  title={isListening ? "Stop recording" : "Start voice recording"}
                >
                  {isListening ? <MicrophoneSlash size={14} /> : <Microphone size={14} />}
                </Button>
              )}
            </div>
            
            <Button 
              onClick={handleSendMessage} 
              disabled={isLoading || !input.trim()}
              size="sm"
            >
              Send
            </Button>
          </div>
        </CardContent>
      </Card>
      
      {/* Breathing Exercise Modal */}
      <AnimatePresence>
        {showBreathingExercise && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-background rounded-lg p-6 max-w-md w-full"
            >
              <BreathingExercise onComplete={onBreathingComplete} />
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}