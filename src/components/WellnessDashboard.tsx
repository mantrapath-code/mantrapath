import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Trophy, Heart, BookOpen, Users, Target, Brain, Palette } from "@phosphor-icons/react"
import { useMoods, useJournal, useUserStats } from "@/hooks/useWellness"
import { useMoodBasedTheme } from "@/hooks/useMoodTheme"
import { MoodInsights } from "./MoodInsights"
import { MoodPatternNotifications } from "./MoodPatternNotifications"
import { EnhancedMoodChart } from "./EnhancedMoodChart"
import { motion, AnimatePresence } from "framer-motion"
import { toast } from "sonner"

export function WellnessDashboard() {
  const { moods, getMoodTrend } = useMoods()
  const { entries } = useJournal()
  const { stats } = useUserStats()
  const { currentTheme, availableThemes, applyTheme, autoApplyMoodTheme, getCurrentMood, isThemeChanging } = useMoodBasedTheme()
  
  const recentMoods = moods.slice(0, 7)
  const moodTrend = getMoodTrend()
  const userCurrentMood = getCurrentMood()
  
  const handleThemeChange = (themeKey: string) => {
    applyTheme(themeKey)
    toast.success(`Theme changed to ${availableThemes[themeKey]?.name}`, {
      description: availableThemes[themeKey]?.description,
      duration: 2000,
    })
  }
  
  const handleAutoTheme = () => {
    const oldTheme = currentTheme
    const wasChanged = autoApplyMoodTheme()
    
    if (wasChanged) {
      const newThemeName = availableThemes[stats.currentTheme || 'default']?.name || 'Default'
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
  
  const getMoodValue = (mood: string) => {
    switch (mood) {
      case 'excellent': return 5
      case 'good': return 4
      case 'neutral': return 3
      case 'low': return 2
      case 'very-low': return 1
      default: return 3
    }
  }
  
  const averageMood = recentMoods.length > 0 
    ? recentMoods.reduce((sum, mood) => sum + getMoodValue(mood.mood), 0) / recentMoods.length
    : 3
  
  const wellnessScore = Math.round((averageMood / 5) * 100)
  
  return (
    <div className="space-y-6">
      {/* Mood Pattern Notifications */}
      <MoodPatternNotifications />

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <Card className="bg-gradient-to-r from-primary/5 to-accent/5">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <Target className="text-primary" size={24} />
                Your Wellness Journey
              </CardTitle>
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
              
              {moodTrend === 'positive' && (
                <div className="text-sm text-green-600 bg-green-50 p-3 rounded-lg">
                  🌟 You're doing great! Your mood has been trending positively.
                </div>
              )}
              
              {moodTrend === 'concerning' && (
                <div className="text-sm text-orange-600 bg-orange-50 p-3 rounded-lg">
                  💜 Remember to be gentle with yourself. Consider reaching out for support.
                </div>
              )}

              {/* Current Mood Status */}
              {moods.length > 0 && (
                <div className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
                  <span className="text-sm font-medium">Current Mood:</span>
                  <div className="flex items-center gap-2">
                    <Badge 
                      variant={userCurrentMood === 'excellent' || userCurrentMood === 'good' ? 'default' : 'secondary'}
                      className="capitalize"
                    >
                      {userCurrentMood}
                    </Badge>
                    <span className="text-xs text-muted-foreground">
                      {new Date(moods[0].timestamp).toLocaleDateString()}
                    </span>
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
          <TabsTrigger value="insights" className="flex items-center gap-2">
            <Brain size={16} />
            Insights
          </TabsTrigger>
          <TabsTrigger value="themes" className="flex items-center gap-2">
            <Palette size={16} />
            Themes
          </TabsTrigger>
        </TabsList>
        
        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
            >
              <Card className="text-center">
                <CardContent className="p-4">
                  <Heart className="mx-auto text-red-500 mb-2" size={24} />
                  <div className="text-2xl font-bold">{stats.moodStreak}</div>
                  <div className="text-xs text-muted-foreground">Day Mood Streak</div>
                </CardContent>
              </Card>
            </motion.div>
            
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
            >
              <Card className="text-center">
                <CardContent className="p-4">
                  <BookOpen className="mx-auto text-blue-500 mb-2" size={24} />
                  <div className="text-2xl font-bold">{entries.length}</div>
                  <div className="text-xs text-muted-foreground">Journal Entries</div>
                </CardContent>
              </Card>
            </motion.div>
            
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
            >
              <Card className="text-center">
                <CardContent className="p-4">
                  <Users className="mx-auto text-green-500 mb-2" size={24} />
                  <div className="text-2xl font-bold">{stats.communityContributions}</div>
                  <div className="text-xs text-muted-foreground">Community Posts</div>
                </CardContent>
              </Card>
            </motion.div>
            
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
            >
              <Card className="text-center">
                <CardContent className="p-4">
                  <Trophy className="mx-auto text-yellow-500 mb-2" size={24} />
                  <div className="text-2xl font-bold">{stats.badges.length}</div>
                  <div className="text-xs text-muted-foreground">Badges Earned</div>
                </CardContent>
              </Card>
            </motion.div>
          </div>
          
          {recentMoods.length > 0 && (
            <EnhancedMoodChart />
          )}
          
          {/* Theme Debug Info - Remove in production */}
          <Card className="border-orange-200 bg-orange-50/50">
            <CardHeader>
              <CardTitle className="text-sm text-orange-700">Theme Debug Info</CardTitle>
            </CardHeader>
            <CardContent className="text-xs space-y-2">
              <div className="grid grid-cols-2 gap-2">
                <div>Current Theme: <span className="font-mono">{currentTheme}</span></div>
                <div>Current Mood: <span className="font-mono">{userCurrentMood}</span></div>
                <div>Recommended Theme: <span className="font-mono">
                  {Object.entries(availableThemes).find(([key, theme]) => 
                    theme.moodRange.includes(userCurrentMood as any))?.[0] || 'default'}
                </span></div>
                <div>Is Changing: <span className="font-mono">{isThemeChanging ? 'Yes' : 'No'}</span></div>
              </div>
              <div className="text-orange-600">
                Try logging a different mood in the Mood tab to see the theme change automatically!
              </div>
            </CardContent>
          </Card>
          
          {stats.badges.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Your Achievements</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {stats.badges.map((badge) => (
                    <Badge key={badge} variant="secondary" className="text-sm">
                      🏆 {badge}
                    </Badge>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>
        
        <TabsContent value="insights" className="space-y-6">
          <MoodInsights />
        </TabsContent>

        <TabsContent value="themes" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Palette className="text-primary" size={24} />
                Personalized Themes
              </CardTitle>
              <p className="text-sm text-muted-foreground">
                Choose a theme that matches your current mood or let the app adapt automatically
              </p>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-3">
                {Object.entries(availableThemes).map(([key, theme]) => (
                  <motion.div
                    key={key}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className={`flex items-center justify-between p-4 border rounded-lg cursor-pointer transition-all ${
                      currentTheme === key ? 'border-primary bg-primary/5 shadow-md' : 'border-border hover:bg-muted/50'
                    }`}
                    onClick={() => handleThemeChange(key)}
                  >
                    <div className="flex-1">
                      <div className="flex items-center gap-3">
                        <div className="flex gap-1">
                          {theme.moodRange.map((mood, index) => {
                            const colors = {
                              'excellent': 'bg-green-400',
                              'good': 'bg-blue-400',
                              'neutral': 'bg-yellow-400',
                              'low': 'bg-orange-400',
                              'very-low': 'bg-red-400'
                            }
                            return (
                              <div
                                key={index}
                                className={`w-3 h-3 rounded-full ${colors[mood]}`}
                                title={mood}
                              />
                            )
                          })}
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <h3 className="font-medium">{theme.name}</h3>
                            {currentTheme === key && (
                              <div className="w-2 h-2 bg-primary rounded-full animate-pulse" />
                            )}
                          </div>
                          <p className="text-sm text-muted-foreground">{theme.description}</p>
                        </div>
                      </div>
                    </div>
                    {currentTheme === key && (
                      <Badge variant="default" className="text-xs">Active</Badge>
                    )}
                  </motion.div>
                ))}
              </div>
              
              <div className="pt-4 border-t">
                <div className="space-y-3">
                  <h4 className="font-medium">Smart Theme Suggestions</h4>
                  <p className="text-sm text-muted-foreground">
                    Based on your current mood ({userCurrentMood}), we recommend:
                  </p>
                  
                  <div className="text-xs text-muted-foreground">
                    Current theme: {currentTheme} | Mood: {userCurrentMood} | 
                    Recommended: {Object.entries(availableThemes).find(([key, theme]) => 
                      theme.moodRange.includes(userCurrentMood as any))?.[0] || 'default'}
                  </div>
                  
                  <Button 
                    onClick={handleAutoTheme}
                    variant="outline"
                    className="w-full"
                  >
                    <Palette size={16} className="mr-2" />
                    Apply Mood-Based Theme
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}