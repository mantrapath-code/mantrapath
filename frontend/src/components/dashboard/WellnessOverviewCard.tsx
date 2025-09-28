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
    const wasChanged = autoApplyMoodTheme(true) // Force apply theme
    
    const newThemeName = availableThemes[currentTheme || 'default']?.name || 'Default'
    toast.success(`Theme applied based on your mood`, {
      description: `Applied ${newThemeName} theme for ${userCurrentMood} mood`,
      duration: 3000,
    })
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
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
            {/* Left Side - Welcome & Icon */}
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
              </div>
            </div>
            
            {/* Center - Wellness Score & Mood Trend */}
            <div className="space-y-4">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium">Wellness Score</span>
                  <span className="text-2xl font-bold text-primary">{wellnessScore}%</span>
                </div>
                <Progress value={wellnessScore} className="w-full h-3" />
              </div>
              
              <div className="pt-2 border-t border-muted/50">
                <div className="flex items-center gap-2 justify-center">
                  {moodTrend === 'improving' && <TrendingUp className="w-4 h-4 text-green-600" />}
                  {moodTrend === 'declining' && <TrendingDown className="w-4 h-4 text-red-600" />}
                  {moodTrend === 'stable' && <Activity className="w-4 h-4 text-blue-600" />}
                  <span className="text-sm font-medium capitalize">{moodTrend}</span>
                  <span className="text-xs text-muted-foreground">trend</span>
                </div>
              </div>
            </div>
            
            {/* Right Side - Theme Controls */}
            <div className="flex flex-col items-end gap-2 lg:items-center">
              <Button
                variant="outline"
                size="sm"
                onClick={handleAutoTheme}
                className="text-xs w-full lg:w-auto"
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