import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Trophy, Heart, BookOpen, Users, Target, Brain, Palette } from "@phosphor-icons/react"
import { useMoods, useJournal, useUserStats } from "@/hooks/useWellness"
import { useMoodBasedTheme } from "@/hooks/useMoodTheme"
import { MoodInsights } from "@/components/MoodInsights"
import { MoodPatternNotifications } from "@/components/MoodPatternNotifications"
import { motion } from "framer-motion"

export function WellnessDashboard() {
  const { moods, getMoodTrend } = useMoods()
  const { entries } = useJournal()
  const { stats } = useUserStats()
  const { currentTheme, availableThemes, applyTheme, autoApplyMoodTheme, getCurrentMood } = useMoodBasedTheme()
  
  const recentMoods = moods.slice(0, 7)
  const moodTrend = getMoodTrend()
  const userCurrentMood = getCurrentMood()
  
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
                  onClick={autoApplyMoodTheme}
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
            <Card>
              <CardHeader>
                <CardTitle>Recent Mood Timeline</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="relative h-32 overflow-hidden">
                  <svg className="w-full h-full" viewBox="0 0 280 120" preserveAspectRatio="none">
                    {/* Grid lines */}
                    <defs>
                      <linearGradient id="moodGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                        <stop offset="0%" stopColor="var(--primary)" stopOpacity="0.3" />
                        <stop offset="100%" stopColor="var(--primary)" stopOpacity="0.05" />
                      </linearGradient>
                    </defs>
                    
                    {/* Background grid */}
                    {[0, 1, 2, 3, 4].map((i) => (
                      <line
                        key={i}
                        x1="0"
                        y1={24 * i}
                        x2="280"
                        y2={24 * i}
                        stroke="var(--border)"
                        strokeWidth="0.5"
                        opacity="0.3"
                      />
                    ))}
                    
                    {/* Area chart */}
                    <path
                      d={(() => {
                        const points = recentMoods.reverse().map((mood, index) => {
                          const x = (index / (recentMoods.length - 1)) * 280
                          const y = 120 - ((getMoodValue(mood.mood) - 1) / 4) * 120
                          return `${x},${y}`
                        })
                        
                        const pathData = `M 0,120 L ${points.join(' L ')} L 280,120 Z`
                        return pathData
                      })()}
                      fill="url(#moodGradient)"
                      className="transition-all duration-1000"
                    />
                    
                    {/* Mood line */}
                    <path
                      d={(() => {
                        const points = recentMoods.map((mood, index) => {
                          const x = (index / (recentMoods.length - 1)) * 280
                          const y = 120 - ((getMoodValue(mood.mood) - 1) / 4) * 120
                          return `${x},${y}`
                        })
                        
                        return `M ${points.join(' L ')}`
                      })()}
                      fill="none"
                      stroke="var(--primary)"
                      strokeWidth="3"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      className="transition-all duration-1000"
                    />
                    
                    {/* Data points */}
                    {recentMoods.map((mood, index) => {
                      const x = (index / (recentMoods.length - 1)) * 280
                      const y = 120 - ((getMoodValue(mood.mood) - 1) / 4) * 120
                      const colors = {
                        'excellent': '#22c55e',
                        'good': '#3b82f6',
                        'neutral': '#eab308',
                        'low': '#f97316',
                        'very-low': '#ef4444'
                      }
                      
                      return (
                        <motion.circle
                          key={mood.id}
                          cx={x}
                          cy={y}
                          r="4"
                          fill={colors[mood.mood]}
                          stroke="white"
                          strokeWidth="2"
                          initial={{ scale: 0 }}
                          animate={{ scale: 1 }}
                          transition={{ delay: index * 0.1 }}
                          className="cursor-pointer"
                          title={`${mood.mood} - ${new Date(mood.timestamp).toLocaleDateString()}`}
                        />
                      )
                    })}
                  </svg>
                  
                  {/* Y-axis labels */}
                  <div className="absolute left-0 top-0 h-full flex flex-col justify-between text-xs text-muted-foreground py-1">
                    <span>Excellent</span>
                    <span>Good</span>
                    <span>Neutral</span>
                    <span>Low</span>
                    <span>Very Low</span>
                  </div>
                </div>
                
                <div className="flex justify-between text-xs text-muted-foreground mt-4">
                  <span>7 days ago</span>
                  <span>Today</span>
                </div>
                
                {/* Legend */}
                <div className="flex items-center justify-center gap-4 mt-3 text-xs">
                  <div className="flex items-center gap-1">
                    <div className="w-3 h-3 rounded-full bg-green-500"></div>
                    <span>Excellent</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <div className="w-3 h-3 rounded-full bg-blue-500"></div>
                    <span>Good</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
                    <span>Neutral</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <div className="w-3 h-3 rounded-full bg-orange-500"></div>
                    <span>Low</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <div className="w-3 h-3 rounded-full bg-red-500"></div>
                    <span>Very Low</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
          
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
                    className={`flex items-center justify-between p-4 border rounded-lg cursor-pointer transition-colors ${
                      currentTheme === key ? 'border-primary bg-primary/5' : 'border-border hover:bg-muted/50'
                    }`}
                    onClick={() => applyTheme(key)}
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
                        <div>
                          <h3 className="font-medium">{theme.name}</h3>
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
                <h4 className="font-medium mb-2">Smart Theme Suggestions</h4>
                <p className="text-sm text-muted-foreground mb-3">
                  Based on your current mood ({userCurrentMood}), we recommend:
                </p>
                <Button 
                  onClick={autoApplyMoodTheme}
                  variant="outline"
                  className="w-full"
                >
                  <Palette size={16} className="mr-2" />
                  Apply Mood-Based Theme
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}