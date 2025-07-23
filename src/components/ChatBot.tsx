import { useState, useRef, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { ChatCircle, Robot, User, Expand, Minimize } from "@phosphor-icons/react"
import { useChat, useMoods } from "@/hooks/useWellness"
import { motion, AnimatePresence } from "framer-motion"
import { cn } from "@/lib/utils"

interface ChatBotProps {
  className?: string
}

export function ChatBot({ className }: ChatBotProps) {
  const { messages, addMessage, getMitraResponse } = useChat()
  const { addMood } = useMoods()
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [isExpanded, setIsExpanded] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }
  
  useEffect(() => {
    scrollToBottom()
  }, [messages])
  
  const handleSend = async () => {
    if (!input.trim()) return
    
    const userMessage = input.trim()
    setInput("")
    setIsLoading(true)
    
    addMessage(userMessage, 'user')
    
    try {
      const response = await getMitraResponse(userMessage)
      
      const suggestedMood = detectMoodFromMessage(userMessage)
      const context = suggestedMood ? { suggestedMood } : undefined
      
      addMessage(response, 'mitra', context)
      
      if (suggestedMood) {
        setTimeout(() => {
          const shouldLog = window.confirm(
            `I noticed you might be feeling ${suggestedMood}. Would you like me to log this in your mood tracker?`
          )
          if (shouldLog) {
            addMood(suggestedMood)
          }
        }, 2000)
      }
      
    } catch (error) {
      addMessage("I'm having trouble connecting right now. Please try again in a moment.", 'mitra')
    } finally {
      setIsLoading(false)
    }
  }
  
  const quickReplies = [
    "How are you feeling?",
    "I'm feeling anxious",
    "Need support",
    "Gratitude practice",
    "Breathing exercise"
  ]
  
  return (
    <Card className={cn("flex flex-col h-96", isExpanded && "fixed inset-4 z-50 h-auto", className)}>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="flex items-center gap-2">
          <Robot className="text-primary" size={24} />
          Mantra-Mitra
          <Badge variant="secondary" className="text-xs">AI Companion</Badge>
        </CardTitle>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setIsExpanded(!isExpanded)}
        >
          {isExpanded ? <Minimize size={16} /> : <Expand size={16} />}
        </Button>
      </CardHeader>
      
      <CardContent className="flex-1 flex flex-col gap-4 p-4">
        <div className="flex-1 overflow-y-auto space-y-4 max-h-64">
          <AnimatePresence>
            {messages.length === 0 && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-center p-4 bg-muted/50 rounded-lg"
              >
                <p className="text-sm text-muted-foreground">
                  Hello! I'm Mantra-Mitra, your wellness companion. 
                  How can I support you today? 💜
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
                {message.sender === 'mitra' && (
                  <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center shrink-0 mt-1">
                    <Robot size={16} className="text-primary" />
                  </div>
                )}
                
                <div className={cn(
                  "max-w-[80%] p-3 rounded-lg text-sm",
                  message.sender === 'user' 
                    ? "bg-primary text-primary-foreground" 
                    : "bg-muted"
                )}>
                  <p>{message.content}</p>
                  {message.context?.suggestedMood && (
                    <div className="mt-2 pt-2 border-t border-muted-foreground/20">
                      <p className="text-xs opacity-70">
                        Suggested mood: {message.context.suggestedMood}
                      </p>
                    </div>
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
                onClick={() => setInput(reply)}
              >
                {reply}
              </Button>
            ))}
          </div>
        )}
        
        <div className="flex gap-2">
          <Input
            placeholder="Share what's on your mind..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            disabled={isLoading}
          />
          <Button onClick={handleSend} disabled={isLoading || !input.trim()}>
            <ChatCircle size={16} />
          </Button>
        </div>
      </CardContent>
    </Card>
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