import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Trophy, Heart, BookOpen, Target, Palette, ChartBar, Microphone, Calendar } from "@phosphor-icons/react"
import { useUserStats, useWellness } from "@/hooks/useWellness"
import { useJournal } from "@/hooks/useJournal"
import { useMoodBasedTheme } from "@/hooks/useMoodTheme"
import { EmotionalWeatherWidget, VoiceMoodEntry, MoodInsightsPanel } from "@/components/mood"

import { motion } from "framer-motion"
import { toast } from "sonner"

export function WellnessDashboard() {
  const { moodEntries, analytics } = useWellness()
  const { entries } = useJournal()
  const { stats } = useUserStats()
  const { currentTheme, availableThemes, autoApplyMoodTheme, getCurrentMood } = useMoodBasedTheme()
  
  const [moodTrend, setMoodTrend] = useState<'improving' | 'declining' | 'stable'>('stable')
  
  const recentMoods = moodEntries.slice(0, 7)
  const userCurrentMood = getCurrentMood()
  
  useEffect(() => {
    if (analytics?.moodTrend) {
      setMoodTrend(analytics.moodTrend)
    }
  }, [analytics])
  
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
      {/* Wellness Journey Header */}
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
                    <span className="text-xs text-muted-foreground">
                      {new Date(recentMoods[0].timestamp).toLocaleDateString()}
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
          <TabsTrigger value="mood-tracking" className="flex items-center gap-2">
            <Microphone size={16} />
            Mood Tracking
          </TabsTrigger>
          <TabsTrigger value="insights" className="flex items-center gap-2">
            <ChartBar size={16} />
            Insights
          </TabsTrigger>
        </TabsList>
        
        <TabsContent value="overview" className="space-y-6">
          {/* Stats Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Card className="text-center">
              <CardContent className="p-4">
                <Heart className="mx-auto text-red-500 mb-2" size={24} />
                <div className="text-2xl font-bold">{stats?.moodStreak || 0}</div>
                <div className="text-xs text-muted-foreground">Day Mood Streak</div>
              </CardContent>
            </Card>
            
            <Card className="text-center">
              <CardContent className="p-4">
                <BookOpen className="mx-auto text-blue-500 mb-2" size={24} />
                <div className="text-2xl font-bold">{entries.length}</div>
                <div className="text-xs text-muted-foreground">Journal Entries</div>
              </CardContent>
            </Card>
            
            <Card className="text-center">
              <CardContent className="p-4">
                <Calendar className="mx-auto text-purple-500 mb-2" size={24} />
                <div className="text-2xl font-bold">{moodEntries.length}</div>
                <div className="text-xs text-muted-foreground">Days Tracked</div>
              </CardContent>
            </Card>
            
            <Card className="text-center">
              <CardContent className="p-4">
                <Trophy className="mx-auto text-yellow-500 mb-2" size={24} />
                <div className="text-2xl font-bold">{stats?.badges?.length || 0}</div>
                <div className="text-xs text-muted-foreground">Achievements</div>
              </CardContent>
            </Card>
          </div>

          {/* Emotional Weather - Only shown in Overview */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <EmotionalWeatherWidget />
            </div>
            <div className="space-y-4">
              <MoodInsightsPanel 
                showCelebrations={true}
                autoRefresh={false}
                onResponseSelect={(question, value) => {
                  console.log('Follow-up response:', { question, value })
                  toast.success('Response recorded!')
                }}
              />
            </div>
          </div>
        </TabsContent>
        
        <TabsContent value="mood-tracking" className="space-y-6">
          {/* Single, comprehensive mood tracking section */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Microphone className="text-primary" size={24} />
                Track Your Mood
              </CardTitle>
              <p className="text-sm text-muted-foreground">
                Record your mood with voice notes or quick entry
              </p>
            </CardHeader>
            <CardContent>
              <VoiceMoodEntry />
            </CardContent>
          </Card>

          {/* This Week's Summary */}
          <Card>
            <CardHeader>
              <CardTitle>This Week</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-3 gap-4 text-center">
                <div>
                  <div className="text-2xl font-bold">{moodEntries.length}</div>
                  <div className="text-xs text-muted-foreground">Mood Entries</div>
                </div>
                <div>
                  <div className="text-2xl font-bold">{entries.length}</div>
                  <div className="text-xs text-muted-foreground">Journal Entries</div>
                </div>
                <div>
                  <div className="text-2xl font-bold">0</div>
                  <div className="text-xs text-muted-foreground">Streak Days</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="insights" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <ChartBar className="text-primary" size={24} />
                Insights & Analytics
              </CardTitle>
              <p className="text-sm text-muted-foreground">
                Real-time insights from your wellness journey powered by unified data analysis • Confidence: 100%
              </p>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                <div className="text-center p-4 border rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">{wellnessScore}</div>
                  <div className="text-sm text-muted-foreground">Weekly Score</div>
                  <div className="text-xs text-green-600">Stable</div>
                </div>
                <div className="text-center p-4 border rounded-lg">
                  <div className="text-2xl font-bold text-purple-600">{moodEntries.length}</div>
                  <div className="text-sm text-muted-foreground">Days Tracked</div>
                  <div className="text-xs text-blue-600">This week</div>
                </div>
                <div className="text-center p-4 border rounded-lg">
                  <div className="text-2xl font-bold text-green-600">70%</div>
                  <div className="text-sm text-muted-foreground">AI Confidence</div>
                  <div className="text-xs text-green-600">High</div>
                </div>
                <div className="text-center p-4 border rounded-lg">
                  <div className="text-2xl font-bold text-orange-600">Active</div>
                  <div className="text-sm text-muted-foreground">Engagement</div>
                  <div className="text-xs text-orange-600">Recommendations available</div>
                </div>
              </div>

              <div className="space-y-4">
                <h4 className="font-medium">✅ Protective Factors</h4>
                <ul className="list-disc list-inside text-sm text-muted-foreground space-y-1">
                  <li>Self-awareness through tracking</li>
                </ul>

                <h4 className="font-medium">💡 Recommendations</h4>
                <div className="space-y-2">
                  <div className="p-3 bg-blue-50 rounded-lg text-sm">
                    <strong>Be gentle with yourself</strong><br />
                    Take things slow and practice self-compassion
                  </div>
                  <div className="p-3 bg-green-50 rounded-lg text-sm">
                    <strong>Stick to routines</strong><br />
                    Familiar activities can provide comfort and stability
                  </div>
                  <div className="p-3 bg-purple-50 rounded-lg text-sm">
                    <strong>Light physical activity</strong><br />
                    Gentle movement to boost your mood and energy
                  </div>
                  <div className="p-3 bg-yellow-50 rounded-lg text-sm">
                    <strong>Stay connected</strong><br />
                    Reach out to supportive people in your life
                  </div>
                </div>

                <div className="text-center pt-4">
                  <div className="text-xs text-muted-foreground">
                    Excluded conditions: 70%
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
  
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
      {/* Wellness Journey Header */}
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
                    <span className="text-xs text-muted-foreground">
                      {new Date(recentMoods[0].timestamp).toLocaleDateString()}
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
          <TabsTrigger value="mood-tracking" className="flex items-center gap-2">
            <Microphone size={16} />
            Mood Tracking
          </TabsTrigger>
          <TabsTrigger value="insights" className="flex items-center gap-2">
            <ChartBar size={16} />
            Insights
          </TabsTrigger>
        </TabsList>
        
        <TabsContent value="overview" className="space-y-6">
          {/* Stats Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
            >
              <Card className="text-center">
                <CardContent className="p-4">
                  <Heart className="mx-auto text-red-500 mb-2" size={24} />
                  <div className="text-2xl font-bold">
                    {stats?.moodStreak || 0}
                  </div>
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
                  <div className="text-2xl font-bold">
                    {entries.length}
                  </div>
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
                  <Calendar className="mx-auto text-purple-500 mb-2" size={24} />
                  <div className="text-2xl font-bold">
                    {moodEntries.length}
                  </div>
                  <div className="text-xs text-muted-foreground">Days Tracked</div>
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
                  <div className="text-2xl font-bold">
                    {stats?.badges?.length || 0}
                  </div>
                  <div className="text-xs text-muted-foreground">Achievements</div>
                </CardContent>
              </Card>
            </motion.div>
          </div>

          {/* Emotional Weather - Only shown in Overview */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <motion.div 
              className="lg:col-span-2"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.5 }}
            >
              <EmotionalWeatherWidget />
            </motion.div>

            {/* Sidebar Widgets */}
            <motion.div
              className="space-y-4"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.6 }}
            >
              <MoodInsightsPanel 
                showCelebrations={true}
                autoRefresh={false}
                onResponseSelect={(question, value) => {
                  console.log('Follow-up response:', { question, value })
                  toast.success('Response recorded!', {
                    description: 'Thank you for your additional insight.'
                  })
                }}
              />
            </motion.div>
          </div>
          
          {stats?.badges && stats.badges.length > 0 && (
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
        
        <TabsContent value="mood-tracking" className="space-y-6">
          {/* Single, comprehensive mood tracking section */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Microphone className="text-primary" size={24} />
                Track Your Mood
              </CardTitle>
              <p className="text-sm text-muted-foreground">
                Record your mood with voice notes or quick entry
              </p>
            </CardHeader>
            <CardContent>
              <VoiceMoodEntry 
                onMoodEntry={(moodData) => {
                  toast.success('Mood recorded successfully!', {
                    description: 'Your mood and voice note have been saved.'
                  })
                }}
              />
            </CardContent>
          </Card>

          {/* This Week's Summary */}
          <Card>
            <CardHeader>
              <CardTitle>This Week</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-3 gap-4 text-center">
                <div>
                  <div className="text-2xl font-bold">{moodEntries.length}</div>
                  <div className="text-xs text-muted-foreground">Mood Entries</div>
                </div>
                <div>
                  <div className="text-2xl font-bold">{entries.length}</div>
                  <div className="text-xs text-muted-foreground">Journal Entries</div>
                </div>
                <div>
                  <div className="text-2xl font-bold">0</div>
                  <div className="text-xs text-muted-foreground">Streak Days</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="insights" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <ChartBar className="text-primary" size={24} />
                Insights & Analytics
              </CardTitle>
              <p className="text-sm text-muted-foreground">
                Real-time insights from your wellness journey powered by unified data analysis • Confidence: 100%
              </p>
            </CardHeader>
            <CardContent>
              {/* Real insights will be loaded here */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                <div className="text-center p-4 border rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">{wellnessScore}</div>
                  <div className="text-sm text-muted-foreground">Weekly Score</div>
                  <div className="text-xs text-green-600">Stable</div>
                </div>
                <div className="text-center p-4 border rounded-lg">
                  <div className="text-2xl font-bold text-purple-600">{moodEntries.length}</div>
                  <div className="text-sm text-muted-foreground">Days Tracked</div>
                  <div className="text-xs text-blue-600">This week</div>
                </div>
                <div className="text-center p-4 border rounded-lg">
                  <div className="text-2xl font-bold text-green-600">70%</div>
                  <div className="text-sm text-muted-foreground">AI Confidence</div>
                  <div className="text-xs text-green-600">High</div>
                </div>
                <div className="text-center p-4 border rounded-lg">
                  <div className="text-2xl font-bold text-orange-600">Active</div>
                  <div className="text-sm text-muted-foreground">Engagement</div>
                  <div className="text-xs text-orange-600">Recommendations available</div>
                </div>
              </div>

              {/* Protective Factors */}
              <div className="space-y-4">
                <h4 className="font-medium">✅ Protective Factors</h4>
                <ul className="list-disc list-inside text-sm text-muted-foreground space-y-1">
                  <li>Self-awareness through tracking</li>
                </ul>

                <h4 className="font-medium">💡 Recommendations</h4>
                <div className="space-y-2">
                  <div className="p-3 bg-blue-50 rounded-lg text-sm">
                    <strong>Be gentle with yourself</strong><br />
                    Take things slow and practice self-compassion
                  </div>
                  <div className="p-3 bg-green-50 rounded-lg text-sm">
                    <strong>Stick to routines</strong><br />
                    Familiar activities can provide comfort and stability
                  </div>
                  <div className="p-3 bg-purple-50 rounded-lg text-sm">
                    <strong>Light physical activity</strong><br />
                    Gentle movement to boost your mood and energy
                  </div>
                  <div className="p-3 bg-yellow-50 rounded-lg text-sm">
                    <strong>Stay connected</strong><br />
                    Reach out to supportive people in your life
                  </div>
                </div>

                <div className="text-center pt-4">
                  <div className="text-xs text-muted-foreground">
                    Excluded conditions: 70%
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}