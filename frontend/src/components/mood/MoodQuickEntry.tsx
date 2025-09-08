import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Slider } from '@/components/ui/slider'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { Heart, Lightning, Brain, CheckCircle } from '@phosphor-icons/react'
import { motion, AnimatePresence } from 'framer-motion'
import { toast } from 'sonner'
import { useMoodInsights } from '@/hooks/useRealtimeInsights'
import { apiService } from '@/services/api'

interface MoodQuickEntryProps {
  onEntryAdded?: (moodData: any) => void
}

export function MoodQuickEntry({ onEntryAdded }: MoodQuickEntryProps) {
  const [mood, setMood] = useState([7])
  const [energy, setEnergy] = useState([7])
  const [stress, setStress] = useState([3])
  const [note, setNote] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [lastSubmitted, setLastSubmitted] = useState<Date | null>(null)

  // E4: Real-time mood insights integration
  const { daysTracked, moodStreak, isConnected, updateFromMoodEntry } = useMoodInsights()

  const handleSubmit = async () => {
    try {
      setIsSubmitting(true)
      
      const moodData = {
        mood_score: mood[0],
        energy_level: energy[0],
        stress_level: stress[0],
        sleep_quality: 5, // Default sleep quality
        notes: note.trim(),
        context_tags: ['manual_entry'],
        emotional_granularity: 3, // Default granularity
        mood_confidence: 1.0, // High confidence for manual entry
        environmental_context: {
          source: 'manual',
          timestamp: new Date().toISOString(),
          device_type: 'web'
        }
      }

      // E4: Optimistic real-time update
      updateFromMoodEntry(mood[0])

      // Submit to backend using the proper API service
      const result = await apiService.createMoodEntry(moodData)
      
      if (!result) {
        throw new Error('Failed to submit mood entry')
      }
      
      setLastSubmitted(new Date())
      toast.success('Mood logged successfully! 🎉', {
        description: `Your mood streak is now ${moodStreak + 1} days`
      })

      // Reset form
      setNote('')
      onEntryAdded?.(result)

    } catch (error) {
      console.error('Failed to log mood:', error)
      toast.error('Failed to log mood', {
        description: 'Please try again later'
      })
    } finally {
      setIsSubmitting(false)
    }
  }

  const getMoodLabel = (value: number) => {
    if (value >= 9) return { label: 'Excellent', color: 'text-green-600' }
    if (value >= 7) return { label: 'Good', color: 'text-blue-600' }
    if (value >= 5) return { label: 'Okay', color: 'text-yellow-600' }
    if (value >= 3) return { label: 'Low', color: 'text-orange-600' }
    return { label: 'Very Low', color: 'text-red-600' }
  }

  const moodLabel = getMoodLabel(mood[0])

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Heart className="text-red-500" size={20} />
            Quick Mood Check-in
          </div>
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            {isConnected && (
              <Badge variant="outline" className="text-green-600">
                <div className="w-2 h-2 bg-green-500 rounded-full mr-1 animate-pulse" />
                Live
              </Badge>
            )}
            {daysTracked > 0 && (
              <Badge variant="secondary">
                {daysTracked} days tracked
              </Badge>
            )}
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Mood Slider */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <label className="text-sm font-medium">How are you feeling?</label>
            <Badge className={moodLabel.color}>
              {moodLabel.label} ({mood[0]}/10)
            </Badge>
          </div>
          <Slider
            value={mood}
            onValueChange={setMood}
            max={10}
            min={1}
            step={1}
            className="w-full"
          />
          <div className="flex justify-between text-xs text-muted-foreground">
            <span>1 (Very Low)</span>
            <span>10 (Excellent)</span>
          </div>
        </div>

        {/* Energy Level */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <label className="text-sm font-medium flex items-center gap-1">
              <Lightning size={14} />
              Energy Level
            </label>
            <span className="text-sm text-muted-foreground">{energy[0]}/10</span>
          </div>
          <Slider
            value={energy}
            onValueChange={setEnergy}
            max={10}
            min={1}
            step={1}
            className="w-full"
          />
        </div>

        {/* Stress Level */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <label className="text-sm font-medium flex items-center gap-1">
              <Brain size={14} />
              Stress Level
            </label>
            <span className="text-sm text-muted-foreground">{stress[0]}/10</span>
          </div>
          <Slider
            value={stress}
            onValueChange={setStress}
            max={10}
            min={1}
            step={1}
            className="w-full"
          />
        </div>

        {/* Optional Note */}
        <div className="space-y-2">
          <label className="text-sm font-medium">Note (optional)</label>
          <Textarea
            value={note}
            onChange={(e) => setNote(e.target.value)}
            placeholder="How was your day? Any thoughts to share..."
            className="resize-none"
            rows={2}
          />
        </div>

        {/* Submit Button */}
        <Button 
          onClick={handleSubmit} 
          disabled={isSubmitting}
          className="w-full"
        >
          {isSubmitting ? (
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
              Logging mood...
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <CheckCircle size={16} />
              Log Mood Entry
            </div>
          )}
        </Button>

        {/* Last submitted indicator */}
        <AnimatePresence>
          {lastSubmitted && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="text-xs text-center text-green-600 bg-green-50 p-2 rounded"
            >
              ✅ Last logged: {lastSubmitted.toLocaleTimeString()}
              {isConnected && ' • Real-time updates active'}
            </motion.div>
          )}
        </AnimatePresence>
      </CardContent>
    </Card>
  )
}
