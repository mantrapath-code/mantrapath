import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { 
  Heart, 
  Plus, 
  Sparkles,
  Sun,
  Cloud,
  CloudRain
} from "lucide-react"
import { motion } from "framer-motion"
import { useWellness } from "@/hooks/useWellness"
import { toast } from "sonner"

const getMoodIcon = (mood: string) => {
  switch (mood.toLowerCase()) {
    case 'excellent':
    case 'great':
      return <Sun className="w-12 h-12 text-yellow-500" />
    case 'good':
    case 'okay':
      return <Cloud className="w-12 h-12 text-blue-500" />
    case 'poor':
    case 'bad':
      return <CloudRain className="w-12 h-12 text-gray-500" />
    default:
      return <Heart className="w-12 h-12 text-pink-500" />
  }
}

const getMoodColor = (mood: string) => {
  switch (mood.toLowerCase()) {
    case 'excellent':
    case 'great':
      return 'from-yellow-100 to-orange-100 border-yellow-300'
    case 'good':
    case 'okay':
      return 'from-blue-100 to-cyan-100 border-blue-300'
    case 'poor':
    case 'bad':
      return 'from-gray-100 to-slate-100 border-gray-300'
    default:
      return 'from-pink-100 to-rose-100 border-pink-300'
  }
}

interface CurrentMoodCardProps {
  onNavigate?: (tab: string) => void
}

export function CurrentMoodCard({ onNavigate }: CurrentMoodCardProps) {
  const { moodEntries } = useWellness()
  
  const latestMood = moodEntries.length > 0 ? moodEntries[0] : null
  const currentMoodValue = latestMood?.mood || 'No mood data'
  const moodTimestamp = latestMood?.timestamp || null
  
  // Convert numeric mood to text
  const getMoodText = (moodValue: number | string) => {
    if (typeof moodValue === 'string') return moodValue
    if (moodValue >= 8) return 'Excellent'
    if (moodValue >= 6) return 'Good'
    if (moodValue >= 4) return 'Okay'
    if (moodValue >= 2) return 'Poor'
    return 'Bad'
  }

  const moodText = getMoodText(currentMoodValue)
  const hasRecentMood = moodTimestamp && 
    (new Date().getTime() - new Date(moodTimestamp).getTime()) < 24 * 60 * 60 * 1000

  const handleAddMoodEntry = () => {
    if (onNavigate) {
      onNavigate('mood')
      toast.success('Opening mood tracker...')
    } else {
      toast.info('Mood tracker coming soon!')
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.4 }}
    >
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
          <CardTitle className="flex items-center gap-2 text-lg">
            <Heart className="text-pink-500" size={20} />
            Current Mood
          </CardTitle>
          <Button 
            variant="outline" 
            size="sm"
            onClick={handleAddMoodEntry}
          >
            <Plus size={16} className="mr-1" />
            Add Entry
          </Button>
        </CardHeader>
        <CardContent>
          {latestMood ? (
            <div className={`p-6 rounded-lg bg-gradient-to-br border ${getMoodColor(moodText)}`}>
              <div className="text-center space-y-4">
                <div className="flex justify-center">
                  {getMoodIcon(moodText)}
                </div>
                
                <div className="space-y-2">
                  <Badge 
                    className={`text-lg px-4 py-1 font-semibold ${
                      moodText === 'Excellent' || moodText === 'Great' 
                        ? 'bg-yellow-200 text-yellow-800' 
                        : moodText === 'Good' || moodText === 'Okay'
                        ? 'bg-blue-200 text-blue-800'
                        : 'bg-gray-200 text-gray-800'
                    }`}
                  >
                    {moodText}
                  </Badge>
                  
                  {typeof currentMoodValue === 'number' && (
                    <div className="text-sm text-muted-foreground">
                      Score: {currentMoodValue}/10
                    </div>
                  )}
                </div>
                
                {moodTimestamp && (
                  <div className="text-xs text-muted-foreground">
                    {hasRecentMood ? (
                      <div className="flex items-center justify-center gap-1">
                        <Sparkles className="w-3 h-3" />
                        Updated {new Date(moodTimestamp).toLocaleDateString()}
                      </div>
                    ) : (
                      <div>Last update: {new Date(moodTimestamp).toLocaleDateString()}</div>
                    )}
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="text-center py-8 space-y-4">
              <div className="w-16 h-16 rounded-full bg-muted/50 flex items-center justify-center mx-auto">
                <Heart className="w-8 h-8 text-muted-foreground" />
              </div>
              <div>
                <h3 className="text-sm font-medium text-muted-foreground">No mood data yet</h3>
                <p className="text-xs text-muted-foreground mt-1">
                  Add your first mood entry to start tracking your wellness
                </p>
              </div>
              <Button 
                onClick={handleAddMoodEntry}
                className="mt-4"
              >
                <Plus size={16} className="mr-2" />
                Add First Entry
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  )
}