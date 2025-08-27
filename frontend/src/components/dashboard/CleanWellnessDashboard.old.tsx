import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Trophy, Heart, Target, Palette } from "@phosphor-icons/react"
import { useUserStats, useWellness } from "@/hooks/useWellness"
import { useJournal } from "@/hooks/useJournal"
import { useMoodBasedTheme } from "@/hooks/useMoodTheme"
import { MoodQuickEntry, EnhancedMoodTracker, EmotionalWeatherWidget, MoodInsightsPanel } from "@/components/mood"

import { motion, AnimatePresence } from "framer-motion"
import { toast } from "sonner"

export function CleanWellnessDashboard() {
  const { moodEntries, analytics } = useWellness()
  const { entries } = useJournal()
  const { stats, loading: statsLoading, error: statsError } = useUserStats()
  const { currentTheme, availableThemes, applyTheme, autoApplyMoodTheme, getCurrentMood, isThemeChanging } = useMoodBasedTheme()
  
  const [moodTrend, setMoodTrend] = useState<'improving' | 'declining' | 'stable'>('stable')
  
  const recentMoods = moodEntries.slice(0, 7)
  const userCurrentMood = getCurrentMood()
  
  // Get mood trend from analytics
  useEffect(() => {
    if (analytics?.moodTrend) {
      setMoodTrend(analytics.moodTrend)
    }
  }, [analytics])
  
  const handleThemeChange = (themeKey: string) => {
    applyTheme(themeKey)
    toast.success(`Theme changed to ${availableThemes[themeKey]?.name}`, {
      description: availableThemes[themeKey]?.description,
      duration: 2000,
    })
  }
  
  const handleAutoTheme = () => {
    const wasChanged = autoApplyMoodTheme()
    
    if (wasChanged) {
      const newThemeName = availableThemes[stats?.currentTheme || 'default']?.name || 'Default'
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
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <Card className="bg-gradient-to-r from-primary/5 to-accent/5">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <CardTitle className="flex items-center gap-2">
                  <Target className="text-primary" size={24} />
                  Your Wellness Journey
                </CardTitle>
              </div>
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleAutoTheme}
                  className="text-xs"
                >
                  <Palette size={14} className="mr-1" />
                  Auto Theme
                </Button>
                <AnimatePresence>
                  {isThemeChanging && (
                    <motion.div
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      exit={{ scale: 0 }}
                      className="w-2 h-2 bg-primary rounded-full"
                    />
                  )}
                </AnimatePresence>
                <Badge variant="secondary" className="text-xs">
                  Theme: {availableThemes[currentTheme]?.name || 'Default'}
                </Badge>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium">Wellness Score</span>
                  <span className="text-2xl font-bold text-primary">{wellnessScore}%</span>
                </div>
                <Progress value={wellnessScore} className="h-3" />
                <p className="text-xs text-muted-foreground mt-1">
                  Based on your recent mood patterns and activities
                </p>
              </div>
              
              {moodTrend === 'improving' && (
                <div className="text-sm text-green-600 bg-green-50 p-3 rounded-lg">
                  🌟 You're doing great! Your mood has been trending positively.
                </div>
              )}
              
              {moodTrend === 'declining' && (
                <div className="text-sm text-orange-600 bg-orange-50 p-3 rounded-lg">
                  💜 Remember to be gentle with yourself. Consider reaching out for support.
                </div>
              )}

              {/* Current Mood Status */}
              {recentMoods.length > 0 && (
                <div className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
                  <span className="text-sm font-medium">Current Mood:</span>
                  <div className="flex items-center gap-2">
                    <Badge 
                      variant={userCurrentMood === 'excellent' || userCurrentMood === 'good' ? 'default' : 'secondary'}
                      className="capitalize"
                    >
                      {userCurrentMood}
                    </Badge>
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </motion.div>

      <Tabs defaultValue="overview" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="mood">Mood Tracking</TabsTrigger>
          <TabsTrigger value="insights">Insights</TabsTrigger>
        </TabsList>
        
        <TabsContent value="overview" className="space-y-6">
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {/* Emotional Weather Widget */}
            <div className="lg:col-span-2">
              <EmotionalWeatherWidget 
                showDetails={true}
                autoRefresh={false}
                className="h-full"
              />
            </div>

            {/* Quick Stats */}
            <div className="space-y-4">
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-base flex items-center gap-2">
                    <Heart className="text-red-500" size={18} />
                    This Week
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Mood Entries</span>
                      <Badge variant="outline">
                        {recentMoods.length}
                      </Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Journal Entries</span>
                      <Badge variant="outline">
                        {entries.length}
                      </Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Streak Days</span>
                      <Badge variant="outline">
                        {stats?.moodStreak || 0}
                      </Badge>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Achievements */}
              {stats && stats.badges && stats.badges.length > 0 && (
                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-base flex items-center gap-2">
                      <Trophy className="text-yellow-500" size={18} />
                      Recent Achievements
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      {stats.badges.slice(0, 3).map((badge) => (
                        <Badge key={badge} variant="secondary" className="text-sm">
                          🏆 {badge}
                        </Badge>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          </div>
        </TabsContent>
        
        <TabsContent value="mood" className="space-y-6">
          <div className="grid gap-6 md:grid-cols-2">
            <MoodQuickEntry />
            <EnhancedMoodTracker />
          </div>
        </TabsContent>

        <TabsContent value="insights" className="space-y-6">
          <MoodInsightsPanel />
        </TabsContent>
      </Tabs>
    </div>
  )
}
