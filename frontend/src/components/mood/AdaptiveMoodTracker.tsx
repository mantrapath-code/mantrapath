import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Label } from "@/components/ui/label"
import { Slider } from "@/components/ui/slider"
import { 
  Heart, 
  Smiley, 
  SmileyMeh, 
  SmileySad, 
  X, 
  Clock,
  ArrowRight,
  Check,
  Sparkle,
  Brain
} from "@phosphor-icons/react"
import { useWellness } from "@/hooks/useWellness"
import { MoodEntry } from "@/types"
import { motion, AnimatePresence } from "framer-motion"
import { apiService } from "@/services/api"

interface AdaptiveQuestion {
  question_type: string
  question_text: string
  options?: Array<{value: string, label: string}>
  trigger_pattern?: string
  scale?: boolean
  scale_type?: string
  range?: [number, number]
  labels?: string[]
  open_text?: boolean
}

interface AdaptiveMoodTrackerProps {
  onMoodLogged?: (mood: MoodEntry) => void
  onCelebrationTriggered?: (celebrations: any[]) => void
}

export function AdaptiveMoodTracker({ onMoodLogged, onCelebrationTriggered }: AdaptiveMoodTrackerProps) {
  const { moodEntries, analytics, loading, actions } = useWellness()
  
  // Core mood tracking state
  const [selectedMood, setSelectedMood] = useState<MoodEntry['mood'] | null>(null)
  const [showDetails, setShowDetails] = useState(false)
  const [note, setNote] = useState("")
  const [energy, setEnergy] = useState<'high' | 'medium' | 'low'>('medium')
  const [stress, setStress] = useState(5)
  const [sleep, setSleep] = useState(5)
  const [customTrigger, setCustomTrigger] = useState("")
  const [selectedTriggers, setSelectedTriggers] = useState<string[]>([])
  const [submitting, setSubmitting] = useState(false)
  
  // Phase 1 enhancement state
  const [emotionalGranularity, setEmotionalGranularity] = useState(3)
  const [moodConfidence, setMoodConfidence] = useState(1.0)
  const [adaptiveQuestions, setAdaptiveQuestions] = useState<AdaptiveQuestion[]>([])
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0)
  const [adaptiveResponses, setAdaptiveResponses] = useState<any[]>([])
  const [showAdaptiveQuestions, setShowAdaptiveQuestions] = useState(false)
  const [loadingQuestions, setLoadingQuestions] = useState(false)
  
  const moodOptions = [
    { value: 'excellent' as const, icon: Heart, label: 'Excellent', color: 'text-green-500', description: 'Feeling amazing!', score: 10 },
    { value: 'good' as const, icon: Smiley, label: 'Good', color: 'text-blue-500', description: 'Things are going well', score: 7 },
    { value: 'neutral' as const, icon: SmileyMeh, label: 'Neutral', color: 'text-yellow-500', description: 'Just okay, nothing special', score: 5 },
    { value: 'low' as const, icon: SmileySad, label: 'Low', color: 'text-orange-500', description: 'Having a tough time', score: 3 },
    { value: 'very-low' as const, icon: X, label: 'Very Low', color: 'text-red-500', description: 'Really struggling today', score: 1 }
  ]

  const commonTriggers = [
    'Work stress', 'Sleep quality', 'Social interaction', 'Exercise', 'Weather',
    'Family', 'Health', 'Finances', 'Routine change', 'Accomplishment'
  ]

  const energyOptions = [
    { value: 'high' as const, label: 'High Energy', color: 'text-green-600', score: 8 },
    { value: 'medium' as const, label: 'Medium Energy', color: 'text-yellow-600', score: 5 },
    { value: 'low' as const, label: 'Low Energy', color: 'text-red-600', score: 2 }
  ]
  
  const handleMoodSelect = async (mood: MoodEntry['mood']) => {
    setSelectedMood(mood)
    setShowDetails(true)
    
    // Load adaptive questions based on mood selection and user patterns
    await loadAdaptiveQuestions()
  }

  const loadAdaptiveQuestions = async () => {
    try {
      setLoadingQuestions(true)
      const questions = await apiService.getAdaptiveQuestions()
      setAdaptiveQuestions(questions)
      if (questions.length > 0) {
        setShowAdaptiveQuestions(true)
        setCurrentQuestionIndex(0)
      }
    } catch (error) {
      console.error('Error loading adaptive questions:', error)
    } finally {
      setLoadingQuestions(false)
    }
  }

  const handleAdaptiveResponse = (questionIndex: number, response: any) => {
    const newResponses = [...adaptiveResponses]
    newResponses[questionIndex] = {
      question_type: adaptiveQuestions[questionIndex].question_type,
      question_text: adaptiveQuestions[questionIndex].question_text,
      answer: response
    }
    setAdaptiveResponses(newResponses)
  }

  const proceedToNextQuestion = () => {
    if (currentQuestionIndex < adaptiveQuestions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1)
    } else {
      setShowAdaptiveQuestions(false)
    }
  }

  const skipAdaptiveQuestions = () => {
    setShowAdaptiveQuestions(false)
    setAdaptiveQuestions([])
    setAdaptiveResponses([])
  }

  const getTimeOfDay = (): 'morning' | 'afternoon' | 'evening' | 'night' => {
    const hour = new Date().getHours()
    if (hour >= 5 && hour < 12) return 'morning'
    if (hour >= 12 && hour < 17) return 'afternoon'
    if (hour >= 17 && hour < 21) return 'evening'
    return 'night'
  }

  const handleSubmit = async () => {
    if (!selectedMood || submitting) return

    try {
      setSubmitting(true)

      const moodData = {
        mood: moodOptions.find(opt => opt.value === selectedMood)?.score || 5,
        energy: energyOptions.find(opt => opt.value === energy)?.score || 5,
        stress: stress,
        sleep: sleep,
        note: note || undefined, 
        tags: selectedTriggers.length > 0 ? selectedTriggers : undefined,
        // Phase 1 enhancements
        emotional_granularity: emotionalGranularity,
        mood_confidence: moodConfidence,
        adaptive_responses: adaptiveResponses.length > 0 ? adaptiveResponses : []
      }

      const entry = await actions.addMoodEntry(moodData)

      // Enhanced entry for callback
      const enhancedEntry: MoodEntry = {
        id: entry.id,
        mood: selectedMood,
        timestamp: Date.now(),
        note: note || undefined,
        triggers: selectedTriggers.length > 0 ? selectedTriggers : undefined,
        energy: energy
      }

      // Check for celebrations
      try {
        const celebrationData = {
          mood: selectedMood,
          energy: energy,
          stress: stress,
          sleep: sleep,
          activities: selectedTriggers,
          note: note,
          emotional_granularity: emotionalGranularity,
          mood_confidence: moodConfidence,
          adaptive_responses: adaptiveResponses
        };
        
        const celebrations = await apiService.getCelebrations(celebrationData);
        if (celebrations.length > 0 && onCelebrationTriggered) {
          onCelebrationTriggered(celebrations);
        }
      } catch (error) {
        console.log('Could not check for celebrations:', error);
      }

      if (onMoodLogged) {
        onMoodLogged(enhancedEntry)
      }

      // Reset form
      setSelectedMood(null)
      setShowDetails(false)
      setNote("")
      setSelectedTriggers([])
      setAdaptiveQuestions([])
      setAdaptiveResponses([])
      setShowAdaptiveQuestions(false)

    } catch (error) {
      console.error('Failed to submit mood entry:', error)
    } finally {
      setSubmitting(false)
    }
  }

  const toggleTrigger = (trigger: string) => {
    setSelectedTriggers(prev => 
      prev.includes(trigger) 
        ? prev.filter(t => t !== trigger)
        : [...prev, trigger]
    )
  }

  const addCustomTrigger = () => {
    if (customTrigger.trim() && !selectedTriggers.includes(customTrigger)) {
      setSelectedTriggers(prev => [...prev, customTrigger])
      setCustomTrigger("")
    }
  }

  // Render adaptive question
  const renderAdaptiveQuestion = (question: AdaptiveQuestion, index: number) => {
    return (
      <motion.div
        key={index}
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        className="space-y-4"
      >
        <div className="flex items-center gap-2 text-sm text-purple-600 font-medium">
          <Brain size={16} />
          Personalized Question {index + 1}/{adaptiveQuestions.length}
        </div>
        
        <h3 className="text-lg font-medium">{question.question_text}</h3>
        
        {question.options && question.options.length > 0 && (
          <RadioGroup 
            value={adaptiveResponses[index]?.answer || ""}
            onValueChange={(value) => handleAdaptiveResponse(index, value)}
          >
            <div className="grid grid-cols-1 gap-2">
              {question.options.map((option) => (
                <div key={option.value} className="flex items-center space-x-2">
                  <RadioGroupItem value={option.value} id={`option-${option.value}`} />
                  <Label htmlFor={`option-${option.value}`} className="text-sm">
                    {option.label}
                  </Label>
                </div>
              ))}
            </div>
          </RadioGroup>
        )}
        
        {question.scale && (
          <div className="space-y-2">
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>{question.labels?.[0] || "Low"}</span>
              <span>{question.labels?.[question.labels.length - 1] || "High"}</span>
            </div>
            <Slider
              value={[adaptiveResponses[index]?.answer || 3]}
              onValueChange={(value) => handleAdaptiveResponse(index, value[0])}
              max={question.range?.[1] || 5}
              min={question.range?.[0] || 1}
              step={1}
              className="w-full"
            />
          </div>
        )}
        
        {question.open_text && (
          <Textarea
            placeholder="Share your thoughts... (optional)"
            value={adaptiveResponses[index]?.answer || ""}
            onChange={(e) => handleAdaptiveResponse(index, e.target.value)}
            className="text-sm"
            rows={3}
          />
        )}
        
        <div className="flex gap-2 pt-2">
          <Button onClick={proceedToNextQuestion} className="flex-1">
            {index < adaptiveQuestions.length - 1 ? (
              <>Next <ArrowRight size={16} className="ml-2" /></>
            ) : (
              <>Continue <Check size={16} className="ml-2" /></>
            )}
          </Button>
          <Button variant="outline" onClick={skipAdaptiveQuestions}>
            Skip Questions
          </Button>
        </div>
      </motion.div>
    )
  }

  // Show adaptive questions overlay
  if (showAdaptiveQuestions && adaptiveQuestions.length > 0) {
    return (
      <Card className="breathing-animation border-purple-200">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-purple-700">
            <Sparkle className="text-purple-500" size={24} />
            Personalized Check-in
          </CardTitle>
          <p className="text-sm text-muted-foreground">
            Based on your patterns, I have some questions that might help provide better insights.
          </p>
        </CardHeader>
        <CardContent>
          {renderAdaptiveQuestion(adaptiveQuestions[currentQuestionIndex], currentQuestionIndex)}
        </CardContent>
      </Card>
    )
  }

  // Show detailed mood entry form
  if (showDetails && selectedMood) {
    const selectedMoodOption = moodOptions.find(opt => opt.value === selectedMood)
    const IconComponent = selectedMoodOption?.icon || Heart

    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="space-y-4"
      >
        <Card className="breathing-animation border-2 border-primary/20">
          <CardHeader>
            <CardTitle className="flex items-center gap-3">
              <IconComponent size={32} className={selectedMoodOption?.color} />
              <div>
                <div className="text-xl">{selectedMoodOption?.label}</div>
                <div className="text-sm text-muted-foreground font-normal">
                  {selectedMoodOption?.description}
                </div>
              </div>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            
            {/* Energy Level */}
            <div>
              <label className="text-sm font-medium mb-3 block">Energy Level</label>
              <div className="grid grid-cols-3 gap-2">
                {energyOptions.map((option) => (
                  <Button
                    key={option.value}
                    variant={energy === option.value ? "default" : "outline"}
                    onClick={() => setEnergy(option.value)}
                    className="text-xs"
                  >
                    {option.label}
                  </Button>
                ))}
              </div>
            </div>

            {/* Stress Level */}
            <div>
              <label className="text-sm font-medium mb-2 block">
                Stress Level: {stress}/10
              </label>
              <Slider
                value={[stress]}
                onValueChange={(value) => setStress(value[0])}
                max={10}
                min={1}
                step={1}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-muted-foreground mt-1">
                <span>Very Calm</span>
                <span>Very Stressed</span>
              </div>
            </div>

            {/* Sleep Quality */}
            <div>
              <label className="text-sm font-medium mb-2 block">
                Sleep Quality: {sleep}/10
              </label>
              <Slider
                value={[sleep]}
                onValueChange={(value) => setSleep(value[0])}
                max={10}
                min={1}
                step={1}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-muted-foreground mt-1">
                <span>Poor</span>
                <span>Excellent</span>
              </div>
            </div>

            {/* Mood Confidence */}
            <div>
              <label className="text-sm font-medium mb-2 block">
                How confident are you in this mood rating? {Math.round(moodConfidence * 100)}%
              </label>
              <Slider
                value={[moodConfidence]}
                onValueChange={(value) => setMoodConfidence(value[0])}
                max={1}
                min={0.1}
                step={0.1}
                className="w-full"
              />
            </div>

            {/* Context Tags */}
            <div>
              <label className="text-sm font-medium mb-3 block">What's influencing your mood? (Optional)</label>
              <div className="flex flex-wrap gap-2 mb-3">
                {commonTriggers.map((trigger) => (
                  <Badge
                    key={trigger}
                    variant={selectedTriggers.includes(trigger) ? "default" : "outline"}
                    className="cursor-pointer"
                    onClick={() => toggleTrigger(trigger)}
                  >
                    {trigger}
                  </Badge>
                ))}
              </div>
              
              <div className="flex gap-2">
                <Input
                  placeholder="Add custom context..."
                  value={customTrigger}
                  onChange={(e) => setCustomTrigger(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && addCustomTrigger()}
                  className="text-sm"
                />
                <Button size="sm" onClick={addCustomTrigger} disabled={!customTrigger.trim()}>
                  Add
                </Button>
              </div>
            </div>

            {/* Note */}
            <div>
              <label className="text-sm font-medium mb-2 block">Additional thoughts (Optional)</label>
              <Textarea
                placeholder="How are you feeling? What's on your mind?"
                value={note}
                onChange={(e) => setNote(e.target.value)}
                className="text-sm"
                rows={3}
              />
            </div>

            {/* Action Buttons */}
            <div className="flex gap-2 pt-4">
              <Button 
                onClick={handleSubmit} 
                className="flex-1"
                disabled={submitting || loading || loadingQuestions}
              >
                <Check size={16} className="mr-2" />
                {submitting ? 'Logging...' : loadingQuestions ? 'Processing...' : 'Log Mood'}
              </Button>
              <Button 
                variant="outline" 
                onClick={() => {
                  setShowDetails(false)
                  setSelectedMood(null)
                  setAdaptiveQuestions([])
                  setAdaptiveResponses([])
                }}
                disabled={submitting}
              >
                Back
              </Button>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    )
  }

  // Main mood selection interface
  return (
    <Card className="breathing-animation">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Heart className="text-primary" size={24} />
          How are you feeling?
        </CardTitle>
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <Clock size={16} />
          {new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} • {getTimeOfDay()}
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-5 gap-3 mb-4">
          {moodOptions.map((option) => {
            const IconComponent = option.icon
            return (
              <motion.div key={option.value} whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                <Button
                  variant="outline"
                  className="h-20 w-full flex flex-col gap-2 hover:shadow-md transition-all"
                  onClick={() => handleMoodSelect(option.value)}
                  disabled={loadingQuestions}
                >
                  <IconComponent size={28} className={option.color} />
                  <span className="text-xs font-medium">{option.label}</span>
                </Button>
              </motion.div>
            )
          })}
        </div>
        
        {/* Contextual insights */}
        <AnimatePresence>
          {analytics?.moodTrend === 'declining' && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="text-sm text-orange-600 bg-orange-50 p-3 rounded-lg"
            >
              We noticed you've been feeling low lately. Remember, it's okay to have difficult days. 
              Consider exploring our support resources or chatting with Mantra-Mitra. 💜
            </motion.div>
          )}
          
          {analytics?.moodTrend === 'improving' && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="text-sm text-green-600 bg-green-50 p-3 rounded-lg"
            >
              You've been doing great this week! Keep up the positive momentum. 🌟
            </motion.div>
          )}
        </AnimatePresence>
      </CardContent>
    </Card>
  )
}
