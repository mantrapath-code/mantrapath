import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { 
  Heart, 
  Smile, 
  Meh, 
  Frown, 
  X, 
  Clock,
  MapPin,
  User,
  Plus,
  Check
} from "@phosphor-icons/react"
import { useMoods } from "@/hooks/useMoods"
import { MoodEntry } from "@/types"
import { motion } from "framer-motion"

interface MoodTrackerProps {
  onMoodLogged?: (mood: MoodEntry) => void
}

export function MoodTracker({ onMoodLogged }: MoodTrackerProps) {
  const { addMood, getMoodTrend, loading } = useMoods()
  const [selectedMood, setSelectedMood] = useState<MoodEntry['mood'] | null>(null)
  const [showDetails, setShowDetails] = useState(false)
  const [note, setNote] = useState("")
  const [energy, setEnergy] = useState<'high' | 'medium' | 'low'>('medium')
  const [customTrigger, setCustomTrigger] = useState("")
  const [selectedTriggers, setSelectedTriggers] = useState<string[]>([])
  const [context, setContext] = useState<string[]>([])
  const [trend, setTrend] = useState<'positive' | 'concerning' | 'stable'>('stable')
  const [submitting, setSubmitting] = useState(false)
  
  // Load initial mood trend
  useEffect(() => {
    const loadTrend = async () => {
      try {
        const currentTrend = await getMoodTrend()
        setTrend(currentTrend)
      } catch (error) {
        console.error('Failed to load mood trend:', error)
      }
    }
    loadTrend()
  }, [getMoodTrend])
  
  const moodOptions = [
    { value: 'excellent' as const, icon: Heart, label: 'Excellent', color: 'text-green-500', description: 'Feeling amazing!' },
    { value: 'good' as const, icon: Smile, label: 'Good', color: 'text-blue-500', description: 'Things are going well' },
    { value: 'neutral' as const, icon: Meh, label: 'Neutral', color: 'text-yellow-500', description: 'Just okay, nothing special' },
    { value: 'low' as const, icon: Frown, label: 'Low', color: 'text-orange-500', description: 'Having a tough time' },
    { value: 'very-low' as const, icon: X, label: 'Very Low', color: 'text-red-500', description: 'Really struggling today' }
  ]

  const commonTriggers = [
    'Work stress', 'Sleep quality', 'Social interaction', 'Exercise', 'Weather',
    'Family', 'Health', 'Finances', 'Routine change', 'Accomplishment'
  ]

  const contextOptions = [
    'At home', 'At work', 'With friends', 'Alone', 'Traveling', 'Exercising'
  ]

  const energyOptions = [
    { value: 'high' as const, label: 'High Energy', color: 'text-green-600' },
    { value: 'medium' as const, label: 'Medium Energy', color: 'text-yellow-600' },
    { value: 'low' as const, label: 'Low Energy', color: 'text-red-600' }
  ]
  
  const handleMoodSelect = (mood: MoodEntry['mood']) => {
    setSelectedMood(mood)
    setShowDetails(true)
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

      const entry = await addMood(
        selectedMood, 
        note || undefined, 
        selectedTriggers.length > 0 ? selectedTriggers : undefined
      )

      // Add additional metadata for callback
      const enhancedEntry = {
        ...entry,
        dayOfWeek: new Date().getDay(),
        timeOfDay: getTimeOfDay(),
        energy,
        context: context.length > 0 ? context : undefined
      }

      onMoodLogged?.(enhancedEntry)
      
      // Reset form
      setSelectedMood(null)
      setShowDetails(false)
      setNote("")
      setSelectedTriggers([])
      setContext([])
      setCustomTrigger("")
      setEnergy('medium')
      
      // Update trend after successful submission
      const newTrend = await getMoodTrend()
      setTrend(newTrend)
      
    } catch (error) {
      console.error('Failed to submit mood:', error)
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
    if (customTrigger.trim() && !selectedTriggers.includes(customTrigger.trim())) {
      setSelectedTriggers(prev => [...prev, customTrigger.trim()])
      setCustomTrigger("")
    }
  }

  const toggleContext = (ctx: string) => {
    setContext(prev => 
      prev.includes(ctx) 
        ? prev.filter(c => c !== ctx)
        : [...prev, ctx]
    )
  }
  

  if (showDetails && selectedMood) {
    const selectedOption = moodOptions.find(opt => opt.value === selectedMood)!
    const IconComponent = selectedOption.icon

    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="space-y-4"
      >
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <IconComponent className={selectedOption.color} size={24} />
              Feeling {selectedOption.label}
            </CardTitle>
            <p className="text-sm text-muted-foreground">{selectedOption.description}</p>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Energy Level */}
            <div>
              <label className="text-sm font-medium mb-2 block">Energy Level</label>
              <div className="grid grid-cols-3 gap-2">
                {energyOptions.map((option) => (
                  <Button
                    key={option.value}
                    variant={energy === option.value ? "default" : "outline"}
                    size="sm"
                    onClick={() => setEnergy(option.value)}
                    className="text-xs"
                  >
                    <span className={option.color}>●</span>
                    {option.label}
                  </Button>
                ))}
              </div>
            </div>

            {/* Context */}
            <div>
              <label className="text-sm font-medium mb-2 block flex items-center gap-2">
                <MapPin size={16} />
                Where are you? (Optional)
              </label>
              <div className="flex flex-wrap gap-2">
                {contextOptions.map((ctx) => (
                  <Badge
                    key={ctx}
                    variant={context.includes(ctx) ? "default" : "outline"}
                    className="cursor-pointer text-xs"
                    onClick={() => toggleContext(ctx)}
                  >
                    {context.includes(ctx) && <Check size={12} className="mr-1" />}
                    {ctx}
                  </Badge>
                ))}
              </div>
            </div>

            {/* Triggers */}
            <div>
              <label className="text-sm font-medium mb-2 block">What's influencing your mood? (Optional)</label>
              <div className="flex flex-wrap gap-2 mb-3">
                {commonTriggers.map((trigger) => (
                  <Badge
                    key={trigger}
                    variant={selectedTriggers.includes(trigger) ? "default" : "outline"}
                    className="cursor-pointer text-xs"
                    onClick={() => toggleTrigger(trigger)}
                  >
                    {selectedTriggers.includes(trigger) && <Check size={12} className="mr-1" />}
                    {trigger}
                  </Badge>
                ))}
              </div>
              
              <div className="flex gap-2">
                <Input
                  placeholder="Add custom trigger..."
                  value={customTrigger}
                  onChange={(e) => setCustomTrigger(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && addCustomTrigger()}
                  className="text-sm"
                />
                <Button size="sm" onClick={addCustomTrigger} disabled={!customTrigger.trim()}>
                  <Plus size={16} />
                </Button>
              </div>
            </div>

            {/* Note */}
            <div>
              <label className="text-sm font-medium mb-2 block">Add a note (Optional)</label>
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
                disabled={submitting || loading}
              >
                <Check size={16} className="mr-2" />
                {submitting ? 'Logging...' : 'Log Mood'}
              </Button>
              <Button 
                variant="outline" 
                onClick={() => {
                  setShowDetails(false)
                  setSelectedMood(null)
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
                >
                  <IconComponent size={28} className={option.color} />
                  <span className="text-xs font-medium">{option.label}</span>
                </Button>
              </motion.div>
            )
          })}
        </div>
        
        {trend === 'concerning' && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-sm text-orange-600 bg-orange-50 p-3 rounded-lg"
          >
            We noticed you've been feeling low lately. Remember, it's okay to have difficult days. 
            Consider chatting with Mantra-Mitra or exploring our support resources. 💜
          </motion.div>
        )}
        
        {trend === 'positive' && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-sm text-green-600 bg-green-50 p-3 rounded-lg"
          >
            You've been doing great this week! Keep up the positive momentum. 🌟
          </motion.div>
        )}
      </CardContent>
    </Card>
  )
}