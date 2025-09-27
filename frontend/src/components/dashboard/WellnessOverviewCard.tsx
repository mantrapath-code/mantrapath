import { useState } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { 
  TrendingUp, 
  TrendingDown, 
  Activity, 
  Palette,
  Heart,
  CheckCircle
} from "lucide-react"
import { useMoodBasedTheme } from "@/hooks/useMoodTheme"
import { useWellness } from "@/hooks/useWellness"
import { motion } from "framer-motion"
import { toast } from "sonner"

export function WellnessOverviewCard() {
  const { moodEntries, analytics } = useWellness()
  const { currentTheme, availableThemes, autoApplyMoodTheme, getCurrentMood } = useMoodBasedTheme()
  
  const recentMoods = moodEntries.slice(0, 7)
  const userCurrentMood = getCurrentMood()
  const [moodTrend, setMoodTrend] = useState<'improving' | 'declining' | 'stable'>('stable')
  
  const handleAutoTheme = () => {
    const wasChanged = autoApplyMoodTheme()
    
    if (wasChanged) {
      const newThemeName = availableThemes[currentTheme || 'default']?.name || 'Default'
      toast.success(`Theme auto-applied based on your mood`, {
        description: `Switched to ${newThemeName} theme`,
        duration: 3000,
      })
    } else {
      toast.info(`Theme already matches your mood`, {
        description: `${availableThemes[currentTheme]?.name} theme is perfect for ${userCurrentMood} mood`,
        duration: 2000,
      })
    }
  }
  
  const averageMood = recentMoods.length > 0 
    ? recentMoods.reduce((sum, mood) => sum + mood.mood, 0) / recentMoods.length
    : 3
  
  const wellnessScore = Math.round((averageMood / 10) * 100)
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <Card className="overflow-hidden bg-gradient-to-br from-primary/5 to-secondary/5 border-none shadow-lg">
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            {/* Left Side - Wellness Overview */}
            <div className="flex items-center gap-4">
              <div className="relative">
                <div className="w-16 h-16 rounded-full bg-gradient-to-br from-primary/20 to-secondary/20 flex items-center justify-center">
                  <Heart className="w-8 h-8 text-primary" />
                </div>
                <div className="absolute -top-1 -right-1 w-6 h-6 bg-green-500 rounded-full flex items-center justify-center">
                  <CheckCircle className="w-4 h-4 text-white" />
                </div>
              </div>
              
              <div className="space-y-1">
                <h3 className="text-lg font-semibold">Welcome back!</h3>
                <p className="text-sm text-muted-foreground">Here's your wellness overview</p>
                
                <div className="flex items-center gap-4 mt-3">
                  <div>
                    <div className="text-2xl font-bold text-primary">{wellnessScore}%</div>
                    <div className="text-xs text-muted-foreground">Wellness Score</div>
                    <Progress value={wellnessScore} className="w-24 h-2 mt-1" />
                  </div>
                  
                  <div className="h-8 w-px bg-border" />
                  
                  <div>
                    <div className="flex items-center gap-2">
                      {moodTrend === 'improving' && <TrendingUp className="w-4 h-4 text-green-600" />}
                      {moodTrend === 'declining' && <TrendingDown className="w-4 h-4 text-red-600" />}
                      {moodTrend === 'stable' && <Activity className="w-4 h-4 text-blue-600" />}
                      <span className="text-sm font-medium capitalize">{moodTrend}</span>
                    </div>
                    <div className="text-xs text-muted-foreground">Mood trend</div>
                  </div>
                </div>
              </div>
            </div>
            
            {/* Right Side - Theme Controls */}
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={handleAutoTheme}
                className="text-xs"
              >
                <Palette className="w-4 h-4 mr-2" />
                Auto Theme
              </Button>
              <Badge variant="secondary" className="text-xs">
                {availableThemes[currentTheme]?.name || 'Default'}
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}