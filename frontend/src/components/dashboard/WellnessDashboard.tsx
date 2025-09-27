import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { 
  Trophy, 
  Heart, 
  BookOpen, 
  Target, 
  Palette, 
  BarChart3 as ChartBar, 
  Mic as Microphone, 
  Calendar,
  TrendingUp,
  TrendingDown,
  Activity,
  Zap,
  Users,
  Brain,
  Star,
  Plus,
  ArrowRight,
  Clock,
  CheckCircle,
  AlertCircle
} from "lucide-react"
import { useUserStats, useWellness } from "@/hooks/useWellness"
import { useJournal } from "@/hooks/useJournal"
import { useMoodBasedTheme } from "@/hooks/useMoodTheme"
import { EmotionalWeatherWidget, VoiceMoodEntry, MoodInsightsPanel, MoodQuickEntry } from "@/components/mood"
import { MoodTrendChart } from "./MoodTrendChart"
import { RealTimeWidget } from "./RealTimeWidget"
import { PersonalizedInsights } from "./PersonalizedInsights"

import { motion, AnimatePresence } from "framer-motion"
import { toast } from "sonner"

export function WellnessDashboard() {
  const { moodEntries, analytics } = useWellness()
  const { entries } = useJournal()
  const { stats } = useUserStats()
  const { currentTheme, availableThemes, autoApplyMoodTheme, getCurrentMood } = useMoodBasedTheme()
  
  const [moodTrend, setMoodTrend] = useState<'improving' | 'declining' | 'stable'>('stable')
  const [selectedTimeframe, setSelectedTimeframe] = useState<'week' | 'month' | 'year'>('week')
  
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
  
  // Mock data for enhanced dashboard features
  const todayGoals = [
    { id: 1, title: "Mood Check-in", completed: true, icon: Heart },
    { id: 2, title: "Journal Entry", completed: false, icon: BookOpen },
    { id: 3, title: "Mindfulness", completed: false, icon: Brain },
  ]
  
  const recentAchievements = [
    { title: "7-Day Streak", description: "Mood tracking consistency", earned: "2 days ago", icon: Trophy },
    { title: "Mindful Moments", description: "Completed 10 sessions", earned: "1 week ago", icon: Star },
  ]
  
  const quickActions = [
    { title: "Quick Mood Entry", icon: Heart, action: "mood" },
    { title: "Voice Note", icon: Microphone, action: "voice" },
    { title: "New Journal", icon: BookOpen, action: "journal" },
    { title: "Chat with AI", icon: Brain, action: "chat" },
  ]
  
  const handleQuickAction = (actionType: string) => {
    switch (actionType) {
      case 'mood':
        toast.info('Opening mood entry...')
        break
      case 'voice':
        toast.info('Starting voice recording...')
        break
      case 'journal':
        toast.info('Opening journal...')
        break
      case 'chat':
        toast.info('Opening AI chat...')
        break
      default:
        break
    }
  }
  
  return (
    <div className="space-y-6 p-1">
      {/* Modern Header with Wellness Score */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative overflow-hidden"
      >
        <Card className="border-none bg-gradient-to-br from-primary/10 via-accent/5 to-secondary/10">
          <CardContent className="p-6">
            <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4">
              {/* Left Side - Welcome & Score */}
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-4">
                  <div className="p-2 bg-primary/10 rounded-full">
                    <Target className="w-6 h-6 text-primary" />
                  </div>
                  <div>
                    <h1 className="text-2xl font-bold">Welcome back!</h1>
                    <p className="text-muted-foreground">Here's your wellness overview</p>
                  </div>
                </div>
                
                {/* Wellness Score */}
                <div className="flex items-center gap-4">
                  <div className="text-center">
                    <div className="text-3xl font-bold text-primary mb-1">{wellnessScore}%</div>
                    <div className="text-sm text-muted-foreground">Wellness Score</div>
                  </div>
                  <div className="flex-1 max-w-xs">
                    <Progress value={wellnessScore} className="h-2" />
                    <div className="flex items-center gap-2 mt-2">
                      {moodTrend === 'improving' && <TrendingUp className="w-4 h-4 text-green-600" />}
                      {moodTrend === 'declining' && <TrendingDown className="w-4 h-4 text-red-600" />}
                      {moodTrend === 'stable' && <Activity className="w-4 h-4 text-blue-600" />}
                      <span className="text-xs text-muted-foreground capitalize">{moodTrend}</span>
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Right Side - Quick Actions */}
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

      {/* Quick Actions Grid */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {quickActions.map((action, index) => (
            <motion.div
              key={action.action}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.1 + index * 0.05 }}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <Card 
                className="cursor-pointer hover:shadow-md transition-all duration-200 border-none bg-gradient-to-br from-background to-muted/20"
                onClick={() => handleQuickAction(action.action)}
              >
                <CardContent className="p-4 text-center">
                  <action.icon className="w-8 h-8 mx-auto mb-2 text-primary" />
                  <div className="font-medium text-sm">{action.title}</div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* Main Dashboard Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Column - Today's Goals & Recent Activity */}
        <div className="space-y-6">
          {/* Today's Goals */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
          >
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="flex items-center gap-2 text-lg">
                  <Target className="w-5 h-5 text-primary" />
                  Today's Goals
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {todayGoals.map((goal) => (
                  <motion.div
                    key={goal.id}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="flex items-center gap-3 p-3 rounded-lg bg-muted/30"
                  >
                    <div className={`p-1.5 rounded-full ${goal.completed ? 'bg-green-100' : 'bg-gray-100'}`}>
                      {goal.completed ? (
                        <CheckCircle className="w-4 h-4 text-green-600" />
                      ) : (
                        <goal.icon className="w-4 h-4 text-muted-foreground" />
                      )}
                    </div>
                    <div className="flex-1">
                      <div className={`font-medium text-sm ${goal.completed ? 'line-through text-muted-foreground' : ''}`}>
                        {goal.title}
                      </div>
                    </div>
                  </motion.div>
                ))}
                <Button size="sm" variant="ghost" className="w-full text-xs">
                  <Plus className="w-4 h-4 mr-1" />
                  Add Goal
                </Button>
              </CardContent>
            </Card>
          </motion.div>

          {/* Recent Achievements */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
          >
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="flex items-center gap-2 text-lg">
                  <Trophy className="w-5 h-5 text-yellow-600" />
                  Recent Achievements
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {recentAchievements.map((achievement, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.3 + index * 0.1 }}
                    className="flex items-center gap-3 p-3 rounded-lg bg-gradient-to-r from-yellow-50 to-orange-50 border border-yellow-200"
                  >
                    <achievement.icon className="w-6 h-6 text-yellow-600" />
                    <div className="flex-1">
                      <div className="font-medium text-sm">{achievement.title}</div>
                      <div className="text-xs text-muted-foreground">{achievement.description}</div>
                      <div className="text-xs text-yellow-600 mt-1">{achievement.earned}</div>
                    </div>
                  </motion.div>
                ))}
              </CardContent>
            </Card>
          </motion.div>

          {/* Real-Time Widget */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.4 }}
          >
            <RealTimeWidget />
          </motion.div>
        </div>

        {/* Middle Column - Mood & Insights */}
        <div className="space-y-6">
          {/* Current Mood Status */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
          >
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="flex items-center gap-2 text-lg">
                  <Heart className="w-5 h-5 text-red-500" />
                  Current Mood
                </CardTitle>
              </CardHeader>
              <CardContent>
                {recentMoods.length > 0 ? (
                  <div className="text-center space-y-4">
                    <div className="text-4xl font-bold text-primary capitalize">
                      {userCurrentMood}
                    </div>
                    <div className="text-sm text-muted-foreground">
                      Last updated: {new Date(recentMoods[0].timestamp).toLocaleDateString()}
                    </div>
                    <Progress value={recentMoods[0].mood * 10} className="h-3" />
                    <div className="flex justify-between text-xs text-muted-foreground">
                      <span>Low</span>
                      <span>High</span>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <Heart className="w-12 h-12 mx-auto text-muted-foreground mb-3" />
                    <div className="text-sm text-muted-foreground">No mood data yet</div>
                    <Button size="sm" className="mt-3">
                      <Plus className="w-4 h-4 mr-1" />
                      Add First Entry
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          </motion.div>

          {/* Mood Trend Chart */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
          >
            <MoodTrendChart 
              data={moodEntries}
              trend={moodTrend}
            />
          </motion.div>

          {/* Personalized AI Insights */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.7 }}
          >
            <PersonalizedInsights />
          </motion.div>
        </div>

        {/* Right Column - Stats & Activity */}
        <div className="space-y-6">
          {/* Key Stats */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.8 }}
          >
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="flex items-center gap-2 text-lg">
                  <ChartBar className="w-5 h-5 text-blue-600" />
                  Key Stats
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="text-center p-3 bg-red-50 rounded-lg">
                    <Heart className="w-6 h-6 mx-auto text-red-500 mb-1" />
                    <div className="text-xl font-bold">{stats?.moodStreak || 0}</div>
                    <div className="text-xs text-muted-foreground">Day Streak</div>
                  </div>
                  <div className="text-center p-3 bg-blue-50 rounded-lg">
                    <BookOpen className="w-6 h-6 mx-auto text-blue-500 mb-1" />
                    <div className="text-xl font-bold">{entries.length}</div>
                    <div className="text-xs text-muted-foreground">Journals</div>
                  </div>
                  <div className="text-center p-3 bg-purple-50 rounded-lg">
                    <Calendar className="w-6 h-6 mx-auto text-purple-500 mb-1" />
                    <div className="text-xl font-bold">{moodEntries.length}</div>
                    <div className="text-xs text-muted-foreground">Days Tracked</div>
                  </div>
                  <div className="text-center p-3 bg-yellow-50 rounded-lg">
                    <Trophy className="w-6 h-6 mx-auto text-yellow-500 mb-1" />
                    <div className="text-xl font-bold">{stats?.badges?.length || 0}</div>
                    <div className="text-xs text-muted-foreground">Badges</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* Emotional Weather Widget */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.9 }}
          >
            <EmotionalWeatherWidget />
          </motion.div>

          {/* Quick Mood Entry */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 1.0 }}
          >
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="flex items-center gap-2 text-lg">
                  <Zap className="w-5 h-5 text-yellow-600" />
                  Quick Entry
                </CardTitle>
              </CardHeader>
              <CardContent>
                <MoodQuickEntry onEntryAdded={(moodData) => {
                  toast.success('Mood logged successfully!')
                }} />
              </CardContent>
            </Card>
          </motion.div>
        </div>
      </div>

      {/* Enhanced Mood Trend Alert */}
      <AnimatePresence>
        {moodTrend === 'improving' && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="fixed bottom-4 right-4 z-50 max-w-sm"
          >
            <Card className="border-green-200 bg-green-50">
              <CardContent className="p-4">
                <div className="flex items-center gap-2 mb-2">
                  <TrendingUp className="w-5 h-5 text-green-600" />
                  <span className="font-medium text-green-800">Great Progress!</span>
                </div>
                <p className="text-sm text-green-700">
                  Your mood has been trending positively. Keep up the great work!
                </p>
              </CardContent>
            </Card>
          </motion.div>
        )}
        
        {moodTrend === 'declining' && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="fixed bottom-4 right-4 z-50 max-w-sm"
          >
            <Card className="border-orange-200 bg-orange-50">
              <CardContent className="p-4">
                <div className="flex items-center gap-2 mb-2">
                  <AlertCircle className="w-5 h-5 text-orange-600" />
                  <span className="font-medium text-orange-800">Take Care</span>
                </div>
                <p className="text-sm text-orange-700">
                  Remember to be gentle with yourself. Consider reaching out for support.
                </p>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}