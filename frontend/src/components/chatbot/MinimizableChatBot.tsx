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
  const [isMinimized, setIsMinimized] = useState(true) // Start minimized by default
  const [showBreathingExercise, setShowBreathingExercise] = useState(false)
  const [isListening, setIsListening] = useState(false)
  const [recognition, setRecognition] = useState<any>(null)
  const [isSpeaking, setIsSpeaking] = useState(false)
  const [voiceEnabled, setVoiceEnabled] = useState(true)
  const [selectedLanguage, setSelectedLanguage] = useState('en')
  const [autoTranslate, setAutoTranslate] = useState(false)
  const [autoTTS, setAutoTTS] = useState(false) // Disable auto TTS by default
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
      <>
        <audio ref={audioRef} onEnded={() => setIsSpeaking(false)} />
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          className="fixed bottom-6 right-6 z-50"
        >
          <Button
            size="lg"
            className="rounded-full h-16 w-16 shadow-2xl hover:shadow-xl transition-all hover:scale-110 bg-gradient-to-r from-primary to-purple-600 hover:from-primary/90 hover:to-purple-600/90"
            onClick={() => setIsMinimized(false)}
            title="Open Mantra-Mitra Chat"
          >
            <ChatCircle size={28} weight="fill" className="text-white" />
          </Button>
          {messages.length > 0 && messages[messages.length - 1].sender === 'assistant' && (
            <div className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 rounded-full animate-pulse border-2 border-white flex items-center justify-center">
              <span className="text-xs text-white font-bold">{messages.filter(m => m.sender === 'assistant').length}</span>
            </div>
          )}
        </motion.div>
      </>
    )
  }
  
  return (
    <>
      <audio ref={audioRef} onEnded={() => setIsSpeaking(false)} />
      
      {/* Floating Chat Window */}
      <motion.div
        initial={{ opacity: 0, scale: 0.9, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.9, y: 20 }}
        className="fixed bottom-6 right-6 z-50 w-[420px]"
        style={{ maxHeight: 'calc(100vh - 120px)' }}
      >
  <Card className="flex flex-col shadow-2xl border-0 max-h-[80vh] min-h-[520px] overflow-hidden bg-gradient-to-b from-slate-50 to-white dark:from-slate-900 dark:to-slate-950">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 py-3 px-4 shrink-0 border-b border-primary/20 bg-gradient-to-r from-primary/20 via-purple-500/20 to-pink-500/20 backdrop-blur-sm">
            <CardTitle className="flex items-center gap-2 min-w-0 flex-1">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary via-purple-600 to-pink-600 flex items-center justify-center shrink-0 shadow-lg ring-2 ring-white/50">
                <Robot className="text-white" size={20} weight="fill" />
              </div>
              <div className="flex flex-col min-w-0">
                <span className="text-sm font-bold truncate bg-gradient-to-r from-primary via-purple-600 to-pink-600 bg-clip-text text-transparent">Mantra-Mitra</span>
                <span className="text-xs text-muted-foreground font-medium truncate">AI Companion</span>
              </div>
            </CardTitle>
            <div className="flex items-center gap-1 shrink-0 ml-2">
              {/* Translation Button */}
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setAutoTranslate(!autoTranslate)}
                title={autoTranslate ? "Disable translation" : "Enable translation"}
                className={cn(
                  "h-8 w-8 p-0 hover:bg-primary/10",
                  autoTranslate && "bg-primary/20 text-primary"
                )}
              >
                <Translate size={16} />
              </Button>
              
              {/* Settings */}
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowSettings(!showSettings)}
                title="Chat settings"
                className={cn(
                  "h-8 w-8 p-0 hover:bg-primary/10",
                  showSettings && "bg-primary/20 text-primary"
                )}
              >
                <Gear size={16} />
              </Button>
              
              {/* Minimize Button */}
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsMinimized(true)}
                title="Minimize chat"
                className="h-8 w-8 p-0 hover:bg-destructive/10 hover:text-destructive"
              >
                <Minus size={18} weight="bold" />
              </Button>
              
              {/* Close Button */}
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsMinimized(true)}
                title="Close chat"
                className="h-8 w-8 p-0 hover:bg-destructive/10 hover:text-destructive"
              >
                <X size={18} weight="bold" />
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
        
        <CardContent className="flex-1 flex flex-col p-0 min-h-0 bg-gradient-to-b from-slate-50/50 to-white/50 dark:from-slate-900/50 dark:to-slate-950/50">
          {/* Messages Area */}
          <div className={cn(
            "flex-1 overflow-y-auto space-y-3 px-4 pt-3 pb-2",
            isExpanded ? "max-h-none" : "max-h-64"
          )} 
          style={{
            scrollbarWidth: 'thin',
            scrollbarColor: 'rgba(155, 155, 155, 0.5) transparent'
          }}>
            <AnimatePresence mode="popLayout">
              {messages.length === 0 && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="text-center p-6 bg-gradient-to-br from-primary/10 via-purple-500/10 to-pink-500/10 rounded-xl border border-primary/20 shadow-sm"
                >
                  <div className="w-16 h-16 rounded-full bg-gradient-to-br from-primary via-purple-600 to-pink-600 flex items-center justify-center mx-auto mb-3 shadow-lg">
                    <Robot className="text-white" size={32} weight="fill" />
                  </div>
                  <p className="text-sm font-medium text-foreground mb-1">
                    Hello! I'm Mantra-Mitra 💜
                  </p>
                  <p className="text-xs text-muted-foreground">
                    Your AI wellness companion is here to support you
                  </p>
                  {voiceEnabled && (
                    <p className="text-xs text-primary font-medium mt-2">
                      🔊 Voice responses enabled
                    </p>
                  )}
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
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary/20 via-purple-500/20 to-pink-500/20 flex items-center justify-center shrink-0 border border-primary/20">
                      <Robot size={16} className="text-primary" weight="fill" />
                    </div>
                  )}
                  
                  <div className={cn(
                    "max-w-[70%] p-3 rounded-xl shadow-sm",
                    message.sender === "user" 
                      ? "bg-gradient-to-br from-primary via-purple-600 to-pink-600 text-white" 
                      : "bg-gradient-to-br from-slate-100 to-slate-50 dark:from-slate-800 dark:to-slate-900 border border-slate-200 dark:border-slate-700"
                  )}>
                    <p className="text-sm whitespace-pre-wrap leading-relaxed">{message.content}</p>
                    
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
          
          {/* Quick Replies - moved inside messages area */}
          {messages.length === 0 && (
            <div className="flex flex-wrap gap-2 px-4 pb-2">
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
          <div className="flex gap-2 p-2 border-t border-primary/10 bg-gradient-to-r from-slate-50/80 to-white/80 dark:from-slate-900/80 dark:to-slate-950/80 backdrop-blur-sm shrink-0">
            <div className="flex-1 relative">
              <Input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Share what's on your mind..."
                className="pr-12 border-primary/20 bg-white dark:bg-slate-900 focus:ring-2 focus:ring-primary/20 rounded-xl h-10"
                disabled={isLoading}
              />
              
              {/* Voice Recording Button */}
              {recognition && (
                <Button
                  variant="ghost"
                  size="sm"
                  className={cn(
                    "absolute right-1 top-1/2 -translate-y-1/2 h-8 w-8 p-0 rounded-lg",
                    isListening && "text-red-500 bg-red-50 dark:bg-red-950 animate-pulse"
                  )}
                  onClick={toggleVoiceRecording}
                  title={isListening ? "Stop recording" : "Start voice recording"}
                >
                  {isListening ? <MicrophoneSlash size={16} weight="fill" /> : <Microphone size={16} />}
                </Button>
              )}
            </div>
            
            <Button 
              onClick={handleSendMessage} 
              disabled={isLoading || !input.trim()}
              className="bg-gradient-to-r from-primary via-purple-600 to-pink-600 hover:from-primary/90 hover:via-purple-600/90 hover:to-pink-600/90 text-white shadow-md rounded-xl px-5 h-10"
              size="sm"
            >
              Send
            </Button>
          </div>
        </CardContent>
        </Card>
      </motion.div>
      
      {/* Breathing Exercise Modal */}
      <AnimatePresence>
        {showBreathingExercise && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-[60] flex items-center justify-center p-4"
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
    </>
  )
}