import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { 
  Heart,
  Brain,
  Cloud,
  Trophy,
  Plus,
  TrendUp,
  Calendar,
  Star
} from "@phosphor-icons/react"
import { motion, AnimatePresence } from "framer-motion"

import { AdaptiveMoodTracker } from "./AdaptiveMoodTracker"
import { EmotionalWeatherWidget } from "./EmotionalWeatherWidget"
import { CelebrationModal, useCelebrations } from "./CelebrationModal"
import { apiService } from "@/services/api"

interface MoodStats {
  current_streak: number
  total_entries: number
  average_mood: number
  improvement_rate: number
  consistency_score: number
}

interface EnhancedMoodTrackerProps {
  onMoodSubmitted?: (moodData: any) => void
  className?: string
}

export function EnhancedMoodTracker({ onMoodSubmitted, className }: EnhancedMoodTrackerProps) {
  const [activeTab, setActiveTab] = useState("track")
  const [moodStats, setMoodStats] = useState<MoodStats | null>(null)
  const [showAddMood, setShowAddMood] = useState(false)
  const [isLoadingStats, setIsLoadingStats] = useState(true)

  const {
    pendingCelebrations,
    showCelebrations,
    checkForCelebrations,
    markCelebrationsAsSeen,
    closeCelebrations
  } = useCelebrations()

  useEffect(() => {
    loadMoodStats()
    checkForCelebrations()
  }, [])

  const loadMoodStats = async () => {
    try {
      setIsLoadingStats(true)
      const data = await apiService.getMoodAnalyticsSummary()
      setMoodStats({
        current_streak: data.current_streak || 0,
        total_entries: data.total_entries || 0,
        average_mood: data.average_mood || 0,
        improvement_rate: data.improvement_rate || 0,
        consistency_score: data.consistency_score || 0
      })
    } catch (error) {
      console.error('Failed to load mood stats:', error)
    } finally {
      setIsLoadingStats(false)
    }
  }

  const handleMoodSubmitted = async (moodData: any) => {
    // Refresh stats after mood submission
    await loadMoodStats()
    
    // Check for new celebrations
    setTimeout(checkForCelebrations, 1000)
    
    // Switch to weather view to show updated forecast
    setActiveTab("weather")
    setShowAddMood(false)
    
    if (onMoodSubmitted) {
      onMoodSubmitted(moodData)
    }
  }

  const getStreakMessage = (streak: number) => {
    if (streak === 0) return "Start your tracking journey!"
    if (streak === 1) return "Great start! Keep it up!"
    if (streak < 7) return `${streak} days strong!`
    if (streak < 30) return `Amazing ${streak}-day streak!`
    return `Incredible ${streak}-day streak! 🏆`
  }

  const getImprovementColor = (rate: number) => {
    if (rate > 0.1) return "text-green-600"
    if (rate > 0) return "text-green-500"
    if (rate === 0) return "text-gray-500"
    return "text-orange-500"
  }

  const getImprovementIcon = (rate: number) => {
    if (rate > 0.05) return "📈"
    if (rate > 0) return "📊"
    if (rate === 0) return "➡️"
    return "📉"
  }

  return (
    <div className={`enhanced-mood-tracker space-y-6 ${className}`}>
      {/* Header with Quick Stats */}
      <Card className="bg-gradient-to-r from-blue-50 to-purple-50 border-blue-200">
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2">
            <Heart size={24} className="text-red-500" />
            Your Emotional Journey
          </CardTitle>
        </CardHeader>
        <CardContent>
          {!isLoadingStats && moodStats ? (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">
                  {moodStats.current_streak}
                </div>
                <div className="text-xs text-muted-foreground">
                  {getStreakMessage(moodStats.current_streak)}
                </div>
              </div>
              
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">
                  {moodStats.total_entries}
                </div>
                <div className="text-xs text-muted-foreground">
                  Total entries
                </div>
              </div>
              
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {moodStats.average_mood.toFixed(1)}
                </div>
                <div className="text-xs text-muted-foreground">
                  Average mood
                </div>
              </div>
              
              <div className="text-center">
                <div className={`text-2xl font-bold ${getImprovementColor(moodStats.improvement_rate)}`}>
                  {getImprovementIcon(moodStats.improvement_rate)}
                </div>
                <div className="text-xs text-muted-foreground">
                  {moodStats.improvement_rate > 0 ? 'Improving' : 
                   moodStats.improvement_rate < 0 ? 'Needs attention' : 'Stable'}
                </div>
              </div>
            </div>
          ) : (
            <div className="grid grid-cols-4 gap-4">
              {Array.from({ length: 4 }).map((_, i) => (
                <div key={i} className="text-center">
                  <div className="h-8 bg-gray-200 rounded animate-pulse mb-1"></div>
                  <div className="h-3 bg-gray-200 rounded animate-pulse"></div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Main Content Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="track" className="flex items-center gap-2">
            <Heart size={16} />
            Track Mood
          </TabsTrigger>
          <TabsTrigger value="weather" className="flex items-center gap-2">
            <Cloud size={16} />
            Weather
          </TabsTrigger>
          <TabsTrigger value="insights" className="flex items-center gap-2">
            <Brain size={16} />
            Insights
          </TabsTrigger>
        </TabsList>

        <TabsContent value="track" className="space-y-4">
          <AnimatePresence mode="wait">
            {!showAddMood ? (
              <motion.div
                key="track-overview"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="space-y-4"
              >
                <Card>
                  <CardContent className="pt-6 text-center space-y-4">
                    <div className="text-6xl">🌟</div>
                    <h3 className="text-xl font-semibold">Ready to check in?</h3>
                    <p className="text-muted-foreground">
                      Track your mood with our enhanced adaptive system that learns from your patterns
                    </p>
                    <Button 
                      onClick={() => setShowAddMood(true)}
                      size="lg"
                      className="w-full max-w-sm"
                    >
                      <Plus size={20} className="mr-2" />
                      Track My Mood
                    </Button>
                  </CardContent>
                </Card>

                {/* Recent Progress Highlight */}
                {moodStats && moodStats.current_streak > 0 && (
                  <Card className="border-green-200 bg-green-50">
                    <CardContent className="pt-4">
                      <div className="flex items-center gap-3">
                        <Trophy className="text-green-600" size={24} />
                        <div>
                          <div className="font-medium text-green-800">
                            {getStreakMessage(moodStats.current_streak)}
                          </div>
                          <div className="text-sm text-green-600">
                            You're building healthy habits! Keep up the momentum.
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                )}
              </motion.div>
            ) : (
              <motion.div
                key="adaptive-tracker"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
              >
                <AdaptiveMoodTracker 
                  onMoodLogged={handleMoodSubmitted}
                  onCelebrationTriggered={(celebrations) => {
                    // Handle celebrations if needed
                  }}
                />
              </motion.div>
            )}
          </AnimatePresence>
        </TabsContent>

        <TabsContent value="weather" className="space-y-4">
          <EmotionalWeatherWidget />
        </TabsContent>

        <TabsContent value="insights" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendUp size={24} />
                Personal Insights
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {moodStats ? (
                <div className="space-y-4">
                  <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                    <h4 className="font-medium text-blue-800 mb-2">Consistency Score</h4>
                    <div className="flex items-center gap-2">
                      <div className="flex-1 bg-blue-200 rounded-full h-2">
                        <div 
                          className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                          style={{ width: `${(moodStats.consistency_score * 100)}%` }}
                        ></div>
                      </div>
                      <Badge variant="outline" className="bg-blue-100 text-blue-800">
                        {Math.round(moodStats.consistency_score * 100)}%
                      </Badge>
                    </div>
                    <p className="text-sm text-blue-600 mt-2">
                      {moodStats.consistency_score > 0.8 ? "Excellent tracking consistency!" :
                       moodStats.consistency_score > 0.6 ? "Good tracking habits developing." :
                       moodStats.consistency_score > 0.4 ? "Building consistency over time." :
                       "Try tracking daily for better insights."}
                    </p>
                  </div>

                  <div className="bg-purple-50 p-4 rounded-lg border border-purple-200">
                    <h4 className="font-medium text-purple-800 mb-2">Mood Trend</h4>
                    <div className="flex items-center gap-2">
                      <span className="text-2xl">
                        {getImprovementIcon(moodStats.improvement_rate)}
                      </span>
                      <span className={`font-medium ${getImprovementColor(moodStats.improvement_rate)}`}>
                        {moodStats.improvement_rate > 0.1 ? "Strong improvement" :
                         moodStats.improvement_rate > 0 ? "Gradual improvement" :
                         moodStats.improvement_rate === 0 ? "Stable mood" :
                         "Consider support strategies"}
                      </span>
                    </div>
                    <p className="text-sm text-purple-600 mt-2">
                      Your average mood is {moodStats.average_mood.toFixed(1)}/10 over recent entries.
                    </p>
                  </div>

                  {moodStats.total_entries < 7 && (
                    <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
                      <div className="flex items-center gap-2">
                        <Star className="text-yellow-600" size={20} />
                        <h4 className="font-medium text-yellow-800">
                          Building Your Profile
                        </h4>
                      </div>
                      <p className="text-sm text-yellow-600 mt-1">
                        Track for {7 - moodStats.total_entries} more days to unlock detailed insights and emotional weather forecasts!
                      </p>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center text-muted-foreground py-8">
                  <Calendar size={48} className="mx-auto mb-4 opacity-50" />
                  <p>Start tracking your mood to see personalized insights here!</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Celebration Modal */}
      {showCelebrations && (
        <CelebrationModal
          celebrations={pendingCelebrations}
          onClose={closeCelebrations}
          onCelebrationsSeen={markCelebrationsAsSeen}
        />
      )}
    </div>
  )
}
