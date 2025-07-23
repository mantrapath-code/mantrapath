import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { BookOpen, Sparkles } from "@phosphor-icons/react"
import { useJournal } from "@/hooks/useWellness"
import { motion } from "framer-motion"

export function JournalSection() {
  const { entries, addEntry } = useJournal()
  const [isWriting, setIsWriting] = useState(false)
  const [title, setTitle] = useState("")
  const [content, setContent] = useState("")
  
  const handleSubmit = () => {
    if (!title.trim() || !content.trim()) return
    
    addEntry(title, content)
    setTitle("")
    setContent("")
    setIsWriting(false)
  }
  
  const prompts = [
    "What are three things you're grateful for today?",
    "Describe a moment when you felt peaceful recently.",
    "What challenge are you working through right now?",
    "How did you show kindness to yourself or others today?",
    "What does your ideal day look like?"
  ]
  
  const randomPrompt = prompts[Math.floor(Math.random() * prompts.length)]
  
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BookOpen className="text-primary" size={24} />
            Personal Journal
          </CardTitle>
        </CardHeader>
        <CardContent>
          {!isWriting ? (
            <div className="space-y-4">
              <div className="text-center p-6 bg-muted/50 rounded-lg">
                <Sparkles className="mx-auto text-accent mb-2" size={32} />
                <p className="text-sm text-muted-foreground mb-4">
                  Writing prompt: <em>"{randomPrompt}"</em>
                </p>
                <Button onClick={() => setIsWriting(true)}>
                  Start Writing
                </Button>
              </div>
            </div>
          ) : (
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-4"
            >
              <Input
                placeholder="Entry title..."
                value={title}
                onChange={(e) => setTitle(e.target.value)}
              />
              <Textarea
                placeholder="What's on your mind? You can use the prompt above or write about anything..."
                value={content}
                onChange={(e) => setContent(e.target.value)}
                className="min-h-32"
                autoFocus
              />
              <div className="flex gap-2">
                <Button onClick={handleSubmit} disabled={!title.trim() || !content.trim()}>
                  Save Entry
                </Button>
                <Button variant="outline" onClick={() => setIsWriting(false)}>
                  Cancel
                </Button>
              </div>
            </motion.div>
          )}
        </CardContent>
      </Card>
      
      {entries.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Recent Entries</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {entries.slice(0, 3).map((entry) => (
                <motion.div
                  key={entry.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="border-l-4 border-primary/30 pl-4 space-y-2"
                >
                  <div className="flex items-center justify-between">
                    <h4 className="font-medium">{entry.title}</h4>
                    <div className="flex items-center gap-2">
                      <Badge variant={
                        entry.sentiment === 'positive' ? 'default' :
                        entry.sentiment === 'negative' ? 'destructive' : 'secondary'
                      }>
                        {entry.sentiment === 'positive' ? '😊' : 
                         entry.sentiment === 'negative' ? '😔' : '😐'} {entry.sentiment}
                      </Badge>
                    </div>
                  </div>
                  <p className="text-sm text-muted-foreground line-clamp-2">
                    {entry.content}
                  </p>
                  {entry.keywords.length > 0 && (
                    <div className="flex gap-1">
                      {entry.keywords.slice(0, 3).map((keyword) => (
                        <Badge key={keyword} variant="outline" className="text-xs">
                          {keyword}
                        </Badge>
                      ))}
                    </div>
                  )}
                  <p className="text-xs text-muted-foreground">
                    {new Date(entry.timestamp).toLocaleDateString()}
                  </p>
                </motion.div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}