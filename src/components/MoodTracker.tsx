import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Heart, Smile, Meh, Frown, X } from "@phosphor-icons/react"
import { useMoods } from "@/hooks/useWellness"
import { MoodEntry } from "@/types"

interface MoodTrackerProps {
  onMoodLogged?: (mood: MoodEntry) => void
}

export function MoodTracker({ onMoodLogged }: MoodTrackerProps) {
  const { addMood, getMoodTrend } = useMoods()
  
  const moodOptions = [
    { value: 'excellent' as const, icon: Heart, label: 'Excellent', color: 'text-green-500' },
    { value: 'good' as const, icon: Smile, label: 'Good', color: 'text-blue-500' },
    { value: 'neutral' as const, icon: Meh, label: 'Neutral', color: 'text-yellow-500' },
    { value: 'low' as const, icon: Frown, label: 'Low', color: 'text-orange-500' },
    { value: 'very-low' as const, icon: X, label: 'Very Low', color: 'text-red-500' }
  ]
  
  const handleMoodSelect = (mood: MoodEntry['mood']) => {
    const entry = addMood(mood)
    onMoodLogged?.(entry)
  }
  
  const trend = getMoodTrend()
  
  return (
    <Card className="breathing-animation">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Heart className="text-primary" size={24} />
          How are you feeling?
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-5 gap-2 mb-4">
          {moodOptions.map((option) => {
            const IconComponent = option.icon
            return (
              <Button
                key={option.value}
                variant="outline"
                className="h-16 flex flex-col gap-1 hover:scale-105 transition-transform"
                onClick={() => handleMoodSelect(option.value)}
              >
                <IconComponent size={24} className={option.color} />
                <span className="text-xs">{option.label}</span>
              </Button>
            )
          })}
        </div>
        
        {trend === 'concerning' && (
          <div className="text-sm text-orange-600 bg-orange-50 p-3 rounded-lg">
            We noticed you've been feeling low lately. Remember, it's okay to have difficult days. 
            Consider chatting with Mantra-Mitra or exploring our support resources.
          </div>
        )}
        
        {trend === 'positive' && (
          <div className="text-sm text-green-600 bg-green-50 p-3 rounded-lg">
            You've been doing great this week! Keep up the positive momentum. 🌟
          </div>
        )}
      </CardContent>
    </Card>
  )
}