import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"
import { Trophy, Heart, BookOpen, Users, Target } from "@phosphor-icons/react"
import { useMoods, useJournal, useUserStats } from "@/hooks/useWellness"
import { motion } from "framer-motion"

export function WellnessDashboard() {
  const { moods, getMoodTrend } = useMoods()
  const { entries } = useJournal()
  const { stats } = useUserStats()
  
  const recentMoods = moods.slice(0, 7)
  const moodTrend = getMoodTrend()
  
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
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <Card className="bg-gradient-to-r from-primary/5 to-accent/5">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Target className="text-primary" size={24} />
              Your Wellness Journey
            </CardTitle>
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
            </div>
          </CardContent>
        </Card>
      </motion.div>
      
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
            <div className="flex items-end gap-2 h-20">
              {recentMoods.reverse().map((mood, index) => {
                const height = (getMoodValue(mood.mood) / 5) * 100
                const colors = {
                  'excellent': 'bg-green-500',
                  'good': 'bg-blue-500',
                  'neutral': 'bg-yellow-500',
                  'low': 'bg-orange-500',
                  'very-low': 'bg-red-500'
                }
                
                return (
                  <motion.div
                    key={mood.id}
                    initial={{ height: 0 }}
                    animate={{ height: `${height}%` }}
                    transition={{ delay: index * 0.1 }}
                    className={`flex-1 rounded-t ${colors[mood.mood]} min-h-1`}
                    title={`${mood.mood} - ${new Date(mood.timestamp).toLocaleDateString()}`}
                  />
                )
              })}
            </div>
            <div className="flex justify-between text-xs text-muted-foreground mt-2">
              <span>7 days ago</span>
              <span>Today</span>
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
    </div>
  )
}