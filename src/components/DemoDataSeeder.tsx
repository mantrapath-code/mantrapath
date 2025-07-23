import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Database, Sparkle } from "@phosphor-icons/react"
import { useKV } from '@github/spark/hooks'
import { MoodEntry } from "@/types"
import { toast } from "sonner"

export function DemoDataSeeder() {
  const [moods, setMoods] = useKV<MoodEntry[]>('user-moods', [])

  const generateDemoData = () => {
    // Only seed if there's less than 10 entries
    if (moods.length >= 10) {
      toast.info("You already have plenty of mood data to analyze!")
      return
    }

    // Generate realistic demo data for the past 2 weeks
    const now = Date.now()
    const demoMoods: MoodEntry[] = []

    // Create patterns for demonstration
    for (let i = 14; i >= 0; i--) {
      const timestamp = now - (i * 24 * 60 * 60 * 1000)
      const date = new Date(timestamp)
      const dayOfWeek = date.getDay()
      const hour = 9 + Math.floor(Math.random() * 8) // Between 9 AM and 5 PM

      // Create realistic patterns
      let mood: 'excellent' | 'good' | 'neutral' | 'low' | 'very-low'
      let triggers: string[] = []
      let energy: 'high' | 'medium' | 'low' = 'medium'

      // Monday blues pattern
      if (dayOfWeek === 1) {
        mood = Math.random() > 0.7 ? 'neutral' : 'low'
        triggers = ['Work stress', 'Routine change']
        energy = 'low'
      }
      // Friday energy
      else if (dayOfWeek === 5) {
        mood = Math.random() > 0.3 ? 'good' : 'excellent'
        triggers = ['Accomplishment', 'Social interaction']
        energy = 'high'
      }
      // Weekend patterns
      else if (dayOfWeek === 0 || dayOfWeek === 6) {
        mood = Math.random() > 0.2 ? 'good' : 'excellent'
        triggers = ['Exercise', 'Family', 'Sleep quality']
        energy = Math.random() > 0.5 ? 'high' : 'medium'
      }
      // Midweek
      else {
        const rand = Math.random()
        if (rand > 0.7) mood = 'excellent'
        else if (rand > 0.4) mood = 'good'
        else if (rand > 0.2) mood = 'neutral'
        else mood = 'low'
        
        triggers = ['Work stress', 'Exercise', 'Social interaction'].filter(() => Math.random() > 0.5)
        energy = Math.random() > 0.6 ? 'high' : Math.random() > 0.3 ? 'medium' : 'low'
      }

      // Adjust timestamp to include hour
      const adjustedTimestamp = timestamp + (hour * 60 * 60 * 1000)

      const getTimeOfDay = (hour: number): 'morning' | 'afternoon' | 'evening' | 'night' => {
        if (hour >= 5 && hour < 12) return 'morning'
        if (hour >= 12 && hour < 17) return 'afternoon'
        if (hour >= 17 && hour < 21) return 'evening'
        return 'night'
      }

      demoMoods.push({
        id: `demo-${adjustedTimestamp}`,
        mood,
        timestamp: adjustedTimestamp,
        dayOfWeek,
        timeOfDay: getTimeOfDay(hour),
        energy,
        triggers: triggers.length > 0 ? triggers : undefined,
        context: ['At work', 'At home'].filter(() => Math.random() > 0.5),
        note: i % 4 === 0 ? `Demo mood entry for ${date.toLocaleDateString()} - feeling ${mood}` : undefined
      })
    }

    // Merge with existing moods and sort by timestamp
    const allMoods = [...moods, ...demoMoods].sort((a, b) => b.timestamp - a.timestamp)
    setMoods(allMoods)
    
    toast.success(`Added ${demoMoods.length} demo mood entries! Check out the Insights & Patterns tab.`)
  }

  return (
    <Card className="border-dashed">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Database className="text-blue-600" size={24} />
          Demo Mode
        </CardTitle>
      </CardHeader>
      <CardContent className="text-center space-y-4">
        <p className="text-sm text-muted-foreground">
          Don't have enough mood data yet? Try our demo data to see how patterns and insights work.
        </p>
        <Button onClick={generateDemoData} variant="outline" className="w-full">
          <Sparkle className="mr-2" size={16} />
          Add Demo Mood Data
        </Button>
        <p className="text-xs text-muted-foreground">
          This adds 2 weeks of realistic mood patterns including Monday blues, Friday energy, and weekend highs.
        </p>
      </CardContent>
    </Card>
  )
}