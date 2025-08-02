import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { Slider } from "@/components/ui/slider"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"
import { 
  Heart, 
  Smiley, 
  SmileyMeh, 
  SmileySad, 
  X, 
  Lightning,
  ShieldCheck,
  Bed,
  Plus,
  Check,
  Sparkle
} from "@phosphor-icons/react"
import { useWellness } from "@/hooks/useWellness"
import { motion, AnimatePresence } from "framer-motion"
import { apiService } from "@/services/api"

interface EnhancedMoodTrackerProps {
  onMoodLogged?: (mood: any) => void
}

export function MoodTracker({ onMoodLogged }: EnhancedMoodTrackerProps) {
  const { moodEntries, analytics, loading, actions } = useWellness()
  
  // Enhanced mood tracking state
  const [moodScore, setMoodScore] = useState<number>(5)
  const [energyLevel, setEnergyLevel] = useState<number>(5)
  const [stressLevel, setStressLevel] = useState<number>(5)
  const [sleepQuality, setSleepQuality] = useState<number>(5)
  const [notes, setNotes] = useState("")
  const [contextTags, setContextTags] = useState<string[]>([])
  
  // Enhanced features
  const [emotionalGranularity, setEmotionalGranularity] = useState<number>(3)
  const [moodConfidence, setMoodConfidence] = useState<number>(8)
  const [showEnhancedMode, setShowEnhancedMode] = useState(false)
  const [adaptiveQuestions, setAdaptiveQuestions] = useState<any[]>([])
  const [adaptiveResponses, setAdaptiveResponses] = useState<any[]>([])
  
  const [customTag, setCustomTag] = useState("")
  const [submitting, setSubmitting] = useState(false)
  
  // Enhanced mood scale descriptions
  const getMoodLabel = (score: number): string => {
    const labels: Record<number, string> = {
      1: "Extremely Low", 2: "Very Low", 3: "Low", 4: "Below Average",
      5: "Average", 6: "Above Average", 7: "Good", 8: "Very Good",
      9: "Excellent", 10: "Outstanding"
    }
    return labels[score] || "Average"
  }

  const getMoodIcon = (score: number) => {
    if (score <= 2) return <X className="w-6 h-6 text-red-500" />
    if (score <= 4) return <SmileySad className="w-6 h-6 text-orange-500" />
    if (score <= 6) return <SmileyMeh className="w-6 h-6 text-yellow-500" />
    if (score <= 8) return <Smiley className="w-6 h-6 text-blue-500" />
    return <Heart className="w-6 h-6 text-green-500" />
  }

  const commonTags = [
    'Work', 'Family', 'Friends', 'Exercise', 'Sleep', 'Weather',
    'Health', 'Finances', 'Creativity', 'Nature', 'Music', 'Learning'
  ]

  const handleTagToggle = (tag: string) => {
    setContextTags(prev => 
      prev.includes(tag) 
        ? prev.filter(t => t !== tag)
        : [...prev, tag]
    )
  }

  const handleAddCustomTag = () => {
    if (customTag.trim() && !contextTags.includes(customTag.trim())) {
      setContextTags(prev => [...prev, customTag.trim()])
      setCustomTag("")
    }
  }

  const handleAdaptiveResponse = (questionIndex: number, response: any) => {
    setAdaptiveResponses(prev => {
      const newResponses = [...prev]
      newResponses[questionIndex] = response
      return newResponses
    })
  }

  const handleSubmit = async () => {
    if (submitting) return
    
    setSubmitting(true)
    try {
      const moodData = {
        mood: moodScore,
        energy: energyLevel,
        stress: stressLevel,
        sleep: sleepQuality,
        note: notes || undefined,
        tags: contextTags,
        emotional_granularity: emotionalGranularity,
        mood_confidence: moodConfidence / 10, // Convert to 0-1 scale
        adaptive_responses: adaptiveResponses.filter(r => r),
        environmental_context: {
          timestamp: new Date().toISOString()
        }
      }

      // Use the wellness hook's addMoodEntry method
      await actions.addMoodEntry(moodData)
      
      if (onMoodLogged) {
        onMoodLogged(moodData)
      }

      // Reset form
      setMoodScore(5)
      setEnergyLevel(5)
      setStressLevel(5)
      setSleepQuality(5)
      setNotes("")
      setContextTags([])
      setAdaptiveResponses([])
      
      // Fetch adaptive questions for next time
      await fetchAdaptiveQuestions()
      
    } catch (error) {
      console.error('Error submitting mood entry:', error)
    } finally {
      setSubmitting(false)
    }
  }

  const fetchAdaptiveQuestions = async () => {
    try {
      const questions = await apiService.getAdaptiveQuestions()
      setAdaptiveQuestions(questions)
    } catch (error) {
      console.error('Error fetching adaptive questions:', error)
    }
  }

  useEffect(() => {
    fetchAdaptiveQuestions()
  }, [])

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              {getMoodIcon(moodScore)}
              Enhanced Mood Tracking
            </CardTitle>
            <div className="flex items-center gap-2">
              <Label htmlFor="enhanced-mode" className="text-sm">Enhanced Mode</Label>
              <Switch
                id="enhanced-mode"
                checked={showEnhancedMode}
                onCheckedChange={setShowEnhancedMode}
              />
            </div>
          </div>
        </CardHeader>
        
        <CardContent className="space-y-6">
          {/* Primary Mood Score */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <Label className="text-base font-medium">How are you feeling?</Label>
              <Badge variant="outline" className="text-sm">
                {moodScore}/10 - {getMoodLabel(moodScore)}
              </Badge>
            </div>
            <Slider
              value={[moodScore]}
              onValueChange={(value) => setMoodScore(value[0])}
              max={10}
              min={1}
              step={1}
              className="w-full"
            />
          </div>

          {/* Enhanced Tracking */}
          <AnimatePresence>
            {showEnhancedMode && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
                className="space-y-6"
              >
                {/* Energy Level */}
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <Label className="flex items-center gap-2">
                      <Lightning className="w-4 h-4" />
                      Energy Level
                    </Label>
                    <Badge variant="outline">{energyLevel}/10</Badge>
                  </div>
                  <Slider
                    value={[energyLevel]}
                    onValueChange={(value) => setEnergyLevel(value[0])}
                    max={10}
                    min={1}
                    step={1}
                    className="w-full"
                  />
                </div>

                {/* Stress Level */}
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <Label className="flex items-center gap-2">
                      <ShieldCheck className="w-4 h-4" />
                      Stress Level
                    </Label>
                    <Badge variant="outline">{stressLevel}/10</Badge>
                  </div>
                  <Slider
                    value={[stressLevel]}
                    onValueChange={(value) => setStressLevel(value[0])}
                    max={10}
                    min={1}
                    step={1}
                    className="w-full"
                  />
                </div>

                {/* Sleep Quality */}
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <Label className="flex items-center gap-2">
                      <Bed className="w-4 h-4" />
                      Sleep Quality
                    </Label>
                    <Badge variant="outline">{sleepQuality}/10</Badge>
                  </div>
                  <Slider
                    value={[sleepQuality]}
                    onValueChange={(value) => setSleepQuality(value[0])}
                    max={10}
                    min={1}
                    step={1}
                    className="w-full"
                  />
                </div>

                {/* Mood Confidence */}
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <Label className="flex items-center gap-2">
                      <Sparkle className="w-4 h-4" />
                      Confidence in Rating
                    </Label>
                    <Badge variant="outline">{moodConfidence}/10</Badge>
                  </div>
                  <Slider
                    value={[moodConfidence]}
                    onValueChange={(value) => setMoodConfidence(value[0])}
                    max={10}
                    min={1}
                    step={1}
                    className="w-full"
                  />
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Context Tags */}
          <div className="space-y-3">
            <Label>What's influencing your mood?</Label>
            <div className="flex flex-wrap gap-2">
              {commonTags.map((tag) => (
                <Badge
                  key={tag}
                  variant={contextTags.includes(tag) ? "default" : "outline"}
                  className="cursor-pointer hover:bg-opacity-80 transition-colors"
                  onClick={() => handleTagToggle(tag)}
                >
                  {tag}
                </Badge>
              ))}
            </div>
            
            {/* Custom tag input */}
            <div className="flex gap-2">
              <Input
                placeholder="Add custom tag..."
                value={customTag}
                onChange={(e) => setCustomTag(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleAddCustomTag()}
                className="flex-1"
              />
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={handleAddCustomTag}
                disabled={!customTag.trim()}
              >
                <Plus className="w-4 h-4" />
              </Button>
            </div>
          </div>

          {/* Notes */}
          <div className="space-y-3">
            <Label>Additional notes (optional)</Label>
            <Textarea
              placeholder="What's on your mind? Any thoughts about your mood today..."
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              rows={3}
            />
          </div>

          {/* Adaptive Questions */}
          <AnimatePresence>
            {adaptiveQuestions.length > 0 && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
                className="space-y-4"
              >
                <Label className="text-base font-medium">Quick follow-up questions</Label>
                {adaptiveQuestions.map((question, index) => (
                  <Card key={index} className="p-4">
                    <p className="mb-3 text-sm">{question.question_text}</p>
                    <div className="flex flex-wrap gap-2">
                      {question.options?.map((option: any, optionIndex: number) => (
                        <Badge
                          key={optionIndex}
                          variant={adaptiveResponses[index]?.value === option.value ? "default" : "outline"}
                          className="cursor-pointer hover:bg-opacity-80 transition-colors"
                          onClick={() => handleAdaptiveResponse(index, option)}
                        >
                          {option.label}
                        </Badge>
                      ))}
                    </div>
                  </Card>
                ))}
              </motion.div>
            )}
          </AnimatePresence>

          {/* Submit Button */}
          <Button 
            onClick={handleSubmit} 
            disabled={submitting}
            className="w-full"
            size="lg"
          >
            {submitting ? (
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Saving...
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <Check className="w-4 h-4" />
                Log Mood Entry
              </div>
            )}
          </Button>
        </CardContent>
      </Card>
    </motion.div>
  )
}
