import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { 
  Heart,
  Plus,
  PaperPlaneTilt,
  Sparkle
} from "@phosphor-icons/react"
import { motion, AnimatePresence } from "framer-motion"
import { useMoods } from "@/hooks/useMoods"
import { toast } from "sonner"
import { apiService } from "@/services/api"

interface QuickMoodEntryProps {
  onEntryComplete?: () => void
  onCelebrationTriggered?: (celebrations: any[]) => void
  compact?: boolean
}

export function QuickMoodEntry({ onEntryComplete, onCelebrationTriggered, compact = false }: QuickMoodEntryProps) {
  const { addMood, loading } = useMoods()
  const [selectedMood, setSelectedMood] = useState<string>("")
  const [note, setNote] = useState("")
  const [isExpanded, setIsExpanded] = useState(false)
  const [submitting, setSubmitting] = useState(false)

  const moodOptions = [
    { value: 'excellent', label: '😄', emoji: '😄', color: 'bg-green-500' },
    { value: 'good', label: '😊', emoji: '😊', color: 'bg-blue-500' },
    { value: 'neutral', label: '😐', emoji: '😐', color: 'bg-yellow-500' },
    { value: 'low', label: '😔', emoji: '😔', color: 'bg-orange-500' },
    { value: 'very-low', label: '😢', emoji: '😢', color: 'bg-red-500' }
  ]

  const handleMoodSelect = (mood: string) => {
    setSelectedMood(mood)
    if (compact) {
      // In compact mode, submit immediately without note
      handleSubmit(mood, "")
    } else {
      setIsExpanded(true)
    }
  }

  const handleSubmit = async (moodValue?: string, noteValue?: string) => {
    const finalMood = moodValue || selectedMood
    const finalNote = noteValue !== undefined ? noteValue : note
    
    if (!finalMood) return

    try {
      setSubmitting(true)
      
      await addMood(
        finalMood as any,
        finalNote || undefined,
        []
      )

      // Check for celebrations after mood entry
      try {
        const celebrationData = {
          mood: finalMood,
          note: finalNote,
          timestamp: Date.now()
        };
        
        const celebrations = await apiService.getCelebrations(celebrationData);
        if (celebrations.length > 0 && onCelebrationTriggered) {
          onCelebrationTriggered(celebrations);
        }
      } catch (error) {
        console.log('Could not check for celebrations:', error);
      }

      toast.success("Mood logged!", {
        description: `Your ${finalMood} mood has been recorded.`,
        duration: 2000,
      })

      // Reset form
      setSelectedMood("")
      setNote("")
      setIsExpanded(false)
      
      onEntryComplete?.()
      
    } catch (error) {
      console.error('Failed to create mood entry:', error)
      toast.error("Failed to log mood", {
        description: "Please try again later.",
        duration: 3000,
      })
    } finally {
      setSubmitting(false)
    }
  }

  if (compact) {
    return (
      <Card className="bg-gradient-to-r from-primary/5 to-accent/5">
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-sm">
            <Heart className="text-primary" size={16} />
            Quick Mood
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-0">
          <div className="grid grid-cols-5 gap-1">
            {moodOptions.map((mood) => (
              <Button
                key={mood.value}
                variant="outline"
                size="sm"
                className="h-8 w-8 p-0 text-lg hover:scale-110 transition-transform"
                onClick={() => handleMoodSelect(mood.value)}
                disabled={submitting}
              >
                {mood.emoji}
              </Button>
            ))}
          </div>
          {submitting && (
            <div className="mt-2 text-xs text-center text-muted-foreground">
              Logging mood...
            </div>
          )}
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="relative overflow-hidden">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Heart className="text-primary" size={20} />
          Quick Mood Entry
        </CardTitle>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Mood Selection */}
        <div>
          <div className="text-sm font-medium mb-2">How are you feeling?</div>
          <div className="grid grid-cols-5 gap-2">
            {moodOptions.map((mood) => (
              <motion.div
                key={mood.value}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <Button
                  variant={selectedMood === mood.value ? "default" : "outline"}
                  size="sm"
                  className="h-12 w-full flex flex-col items-center gap-1"
                  onClick={() => handleMoodSelect(mood.value)}
                  disabled={submitting}
                >
                  <span className="text-lg">{mood.emoji}</span>
                  <span className="text-xs capitalize">{mood.value.replace('-', ' ')}</span>
                </Button>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Expanded Note Section */}
        <AnimatePresence>
          {isExpanded && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              className="space-y-3"
            >
              <div>
                <div className="text-sm font-medium mb-2">Add a note (optional)</div>
                <Input
                  placeholder="What's on your mind?"
                  value={note}
                  onChange={(e) => setNote(e.target.value)}
                  className="resize-none"
                  disabled={submitting}
                />
              </div>

              <div className="flex items-center gap-2">
                <Button
                  onClick={() => handleSubmit()}
                  disabled={!selectedMood || submitting}
                  size="sm"
                  className="flex-1"
                >
                  {submitting ? (
                    <div className="flex items-center gap-2">
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      Logging...
                    </div>
                  ) : (
                    <>
                      <PaperPlaneTilt size={14} className="mr-2" />
                      Log Mood
                    </>
                  )}
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    setIsExpanded(false)
                    setSelectedMood("")
                    setNote("")
                  }}
                  disabled={submitting}
                >
                  Cancel
                </Button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Selected Mood Preview */}
        {selectedMood && !isExpanded && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex items-center justify-between p-3 bg-muted/50 rounded-lg"
          >
            <div className="flex items-center gap-2">
              <span className="text-lg">
                {moodOptions.find(m => m.value === selectedMood)?.emoji}
              </span>
              <span className="text-sm font-medium capitalize">
                {selectedMood.replace('-', ' ')} mood
              </span>
            </div>
            <Badge variant="outline" className="text-xs">
              Ready to log
            </Badge>
          </motion.div>
        )}
      </CardContent>
    </Card>
  )
}
