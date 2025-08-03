import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Textarea } from "@/components/ui/textarea"
import { Checkbox } from "@/components/ui/checkbox"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Calendar, TrendUp, Users, ChatCircle, Trophy, Star, Target, ArrowBendUpLeft } from "@phosphor-icons/react"
import { motion, AnimatePresence } from "framer-motion"
import { toast } from "sonner"
import { communityApi } from "@/services/api"
import { useAuth } from "@/hooks/useAuth"
import { getRelativeTime, getDisplayName, formatFullDate } from "@/utils/timeUtils"

interface ChallengeProgressData {
  id: string
  date: string
  completed: boolean
  notes?: string
  mood_rating?: number
  reflection?: string
  streak_count: number
  difficulty_rating?: number
  created_at: string
}

interface LeaderboardEntry {
  user_id: string
  name: string
  completion_percentage: number
  completed_days: number
  current_streak: number
  joined_at: string
}

interface Comment {
  id: string
  content: string
  author: {
    id: string
    name: string
    avatar_url?: string
    badges: string[]
  }
  created_at: string
  like_count: number
  is_liked: boolean
  parent_id?: string
  replies: Comment[]
}

interface EnhancedChallengeCardProps {
  challenge: {
    id: string
    title: string
    description: string
    category: string
    duration_days: number
    start_date: string
    end_date: string
    participant_count: number
    is_participating: boolean
    created_at: string
    comment_count?: number
  }
  onJoin: () => void
  onLeave: () => void
  onRefresh?: () => void
}

const getMoodEmoji = (rating: number) => {
  switch (rating) {
    case 1: return "😞"
    case 2: return "😕"
    case 3: return "😐"
    case 4: return "😊"
    case 5: return "😄"
    default: return "😐"
  }
}

const getDifficultyLabel = (rating: number) => {
  switch (rating) {
    case 1: return "Very Easy"
    case 2: return "Easy"
    case 3: return "Moderate"
    case 4: return "Hard"
    case 5: return "Very Hard"
    default: return "Not Rated"
  }
}

export function EnhancedChallengeCard({ challenge, onJoin, onLeave, onRefresh }: EnhancedChallengeCardProps) {
  const { isAuthenticated } = useAuth()
  const [isLoading, setIsLoading] = useState(false)
  const [showProgress, setShowProgress] = useState(false)
  const [showCommunity, setShowCommunity] = useState(false)
  const [showComments, setShowComments] = useState(false)
  
  // Progress tracking state
  const [progressData, setProgressData] = useState<ChallengeProgressData[]>([])
  const [todayCompleted, setTodayCompleted] = useState(false)
  const [progressNote, setProgressNote] = useState('')
  const [moodRating, setMoodRating] = useState<number>(3)
  const [difficultyRating, setDifficultyRating] = useState<number>(3)
  const [reflection, setReflection] = useState('')
  
  // Community connections and comments state
  const [communityMembers, setCommunityMembers] = useState<LeaderboardEntry[]>([])
  const [comments, setComments] = useState<Comment[]>([])
  const [newComment, setNewComment] = useState('')
  const [replyTo, setReplyTo] = useState<string | null>(null)
  const [replyContent, setReplyContent] = useState('')
  
  // Calculate progress statistics with safety checks
  const completedDays = Array.isArray(progressData) ? progressData.filter(p => p.completed).length : 0
  const progressPercentage = challenge.duration_days > 0 ? (completedDays / challenge.duration_days) * 100 : 0
  const currentStreak = Array.isArray(progressData) && progressData.length > 0 ? (progressData[0].streak_count || 0) : 0
  
  const isActive = new Date(challenge.end_date) > new Date()
  const daysRemaining = Math.ceil((new Date(challenge.end_date).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24))

  useEffect(() => {
    if (challenge.is_participating && isAuthenticated) {
      loadProgressData()
      
      // Check if user has completed today
      const today = new Date().toISOString().split('T')[0]
      const todayProgress = Array.isArray(progressData) ? progressData.find(p => p.date === today) : null
      setTodayCompleted(todayProgress?.completed || false)
    }
  }, [challenge.id, challenge.is_participating, isAuthenticated])

  const loadProgressData = async () => {
    try {
      const data = await communityApi.getChallengeProgress(challenge.id)
      
      // Handle both array response and object with daily_completions
      let progressArray: ChallengeProgressData[] = []
      if (Array.isArray(data)) {
        progressArray = data as ChallengeProgressData[]
      } else if (data && Array.isArray(data.daily_completions)) {
        progressArray = data.daily_completions as ChallengeProgressData[]
      }
      
      setProgressData(progressArray)
      
      // Check if user has completed today
      const today = new Date().toISOString().split('T')[0]
      const todayProgress = progressArray.find(p => p.date === today)
      setTodayCompleted(todayProgress?.completed || false)
      
      // If today's progress exists, populate the form
      if (todayProgress) {
        setProgressNote(todayProgress.notes || '')
        setReflection(todayProgress.reflection || '')
        setMoodRating(todayProgress.mood_rating || 3)
        setDifficultyRating(todayProgress.difficulty_rating || 3)
      }
      
    } catch (error: any) {
      console.error('Failed to load progress data:', error)
      // Set empty array on error to prevent crashes
      setProgressData([])
      
      // Show user-friendly error message
      if (error?.status !== 401) { // Don't show error for auth issues
        toast.error('Unable to load progress data. Please refresh and try again.')
      }
    }
  }

  const loadCommunityMembers = async () => {
    try {
      const data = await communityApi.getChallengeLeaderboard(challenge.id)
      setCommunityMembers(data)
    } catch (error) {
      console.error('Failed to load community members:', error)
    }
  }

  const loadComments = async () => {
    try {
      const data = await communityApi.getChallengeComments(challenge.id)
      setComments(Array.isArray(data) ? data : [])
    } catch (error: any) {
      console.error('Failed to load comments:', error)
      setComments([])
      
      // Only show error if it's not an auth issue
      if (error?.status !== 401) {
        toast.error('Unable to load comments. Please refresh and try again.')
      }
    }
  }

  const handleProgressUpdate = async () => {
    if (!isAuthenticated) {
      toast.error('Please log in to update progress')
      return
    }

    setIsLoading(true)
    try {
      // Update progress with comprehensive data
      const progressUpdate = {
        completed: todayCompleted,
        notes: progressNote.trim() || undefined,
        mood_rating: moodRating,
        reflection: reflection.trim() || undefined,
        difficulty_rating: difficultyRating
      }
      
      const response = await communityApi.updateChallengeProgress(challenge.id, progressUpdate)
      
      // Show success message with streak info
      const streakMessage = response.streak_count > 1 
        ? `🔥 ${response.streak_count} day streak!` 
        : 'Progress updated!'
        
      toast.success(streakMessage)
      
      // Clear form and reload data
      await loadProgressData()
      setProgressNote('')
      setReflection('')
      setMoodRating(3)
      setDifficultyRating(3)
      
      if (onRefresh) {
        onRefresh()
      }
    } catch (error: any) {
      console.error('Failed to update progress:', error)
      const errorMessage = error?.message || 'Failed to update progress. Please try again.'
      toast.error(errorMessage)
    } finally {
      setIsLoading(false)
    }
  }

  const handleAddComment = async () => {
    if (!newComment.trim()) {
      toast.error('Please enter a comment')
      return
    }

    if (!isAuthenticated) {
      toast.error('Please log in to add comments')
      return
    }

    try {
      await communityApi.addChallengeComment(challenge.id, {
        content: newComment.trim()
      })
      toast.success('Comment added!')
      setNewComment('')
      await loadComments()
      // Refresh challenge data to update comment count
      if (onRefresh) {
        onRefresh()
      }
    } catch (error: any) {
      console.error('Failed to add comment:', error)
      const errorMessage = error?.message || 'Failed to add comment. Please try again.'
      toast.error(errorMessage)
    }
  }

  const handleAddReply = async (parentId: string) => {
    if (!replyContent.trim()) {
      toast.error('Please enter a reply')
      return
    }

    if (!isAuthenticated) {
      toast.error('Please log in to reply')
      return
    }

    try {
      await communityApi.addChallengeComment(challenge.id, {
        content: replyContent.trim(),
        parent_id: parentId
      })
      toast.success('Reply added!')
      setReplyContent('')
      setReplyTo(null)
      await loadComments()
      // Refresh challenge data to update comment count
      if (onRefresh) {
        onRefresh()
      }
    } catch (error: any) {
      console.error('Failed to add reply:', error)
      const errorMessage = error?.message || 'Failed to add reply. Please try again.'
      toast.error(errorMessage)
    }
  }
  const handleAction = async () => {
    if (!isAuthenticated) {
      toast.error('Please log in to join or leave challenges')
      return
    }

    setIsLoading(true)
    try {
      if (challenge.is_participating) {
        await onLeave()
        toast.success('Successfully left the challenge')
      } else {
        await onJoin()
        toast.success('Successfully joined the challenge!')
      }
      // Refresh challenge data to update participant count
      if (onRefresh) {
        onRefresh()
      }
    } catch (error: any) {
      console.error('Failed to join/leave challenge:', error)
      const action = challenge.is_participating ? 'leave' : 'join'
      const errorMessage = error?.message || `Failed to ${action} challenge. Please try again.`
      toast.error(errorMessage)
    } finally {
      setIsLoading(false)
    }
  }

  const getCategoryColor = (category: string) => {
    switch (category.toLowerCase()) {
      case 'mindfulness': return 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200'
      case 'fitness': return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
      case 'nutrition': return 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200'
      case 'sleep': return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
      case 'mental-health': return 'bg-pink-100 text-pink-800 dark:bg-pink-900 dark:text-pink-200'
      case 'social': return 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200'
      case 'habits': return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'
    }
  }

  return (
    <Card className="enhanced-challenge-card hover:shadow-lg transition-shadow">
      <CardHeader>
        <div className="flex justify-between items-start">
          <div className="space-y-2">
            <CardTitle className="text-lg">{challenge.title}</CardTitle>
            <div className="flex gap-2 items-center">
              <Badge className={getCategoryColor(challenge.category)}>
                {challenge.category}
              </Badge>
              <Badge variant="outline">
                {challenge.duration_days} days
              </Badge>
              {!isActive && (
                <Badge variant="secondary">Ended</Badge>
              )}
            </div>
          </div>
          
          {challenge.is_participating && (
            <div className="text-right">
              <div className="text-2xl font-bold text-primary">
                {Math.round(progressPercentage)}%
              </div>
              <div className="text-sm text-muted-foreground">
                {currentStreak} day streak
              </div>
            </div>
          )}
        </div>
      </CardHeader>
      
      <CardContent className="space-y-4">
        <p className="text-sm text-muted-foreground">{challenge.description}</p>
        
        {/* Progress visualization for participants */}
        {challenge.is_participating && (
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>Progress</span>
              <span>{completedDays}/{challenge.duration_days} days</span>
            </div>
            <Progress value={progressPercentage} className="h-2" />
          </div>
        )}
        
        {/* Today's progress update section */}
        {challenge.is_participating && isActive && isAuthenticated && (
          <motion.div 
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            className="space-y-4 p-4 bg-muted/50 rounded-lg"
          >
            <h4 className="font-medium flex items-center gap-2">
              <Target className="w-4 h-4" />
              Today's Progress
            </h4>
            
            <div className="flex items-center gap-2">
              <Checkbox 
                checked={todayCompleted}
                onCheckedChange={(checked) => setTodayCompleted(checked === true)}
              />
              <span className="text-sm">Mark today as completed</span>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium">How are you feeling?</label>
                <div className="flex gap-1 mt-1">
                  {[1, 2, 3, 4, 5].map((rating) => (
                    <Button
                      key={rating}
                      variant={moodRating === rating ? "default" : "outline"}
                      size="sm"
                      onClick={() => setMoodRating(rating)}
                    >
                      {getMoodEmoji(rating)}
                    </Button>
                  ))}
                </div>
              </div>
              
              <div>
                <label className="text-sm font-medium">Difficulty Level</label>
                <div className="flex gap-1 mt-1">
                  {[1, 2, 3, 4, 5].map((rating) => (
                    <Button
                      key={rating}
                      variant={difficultyRating === rating ? "default" : "outline"}
                      size="sm"
                      onClick={() => setDifficultyRating(rating)}
                    >
                      {rating}
                    </Button>
                  ))}
                </div>
              </div>
            </div>
            
            <Textarea
              placeholder="Add a note about today's experience..."
              value={progressNote}
              onChange={(e) => setProgressNote(e.target.value)}
              className="min-h-[60px]"
            />
            
            <Textarea
              placeholder="Any reflections or insights from today?"
              value={reflection}
              onChange={(e) => setReflection(e.target.value)}
              className="min-h-[60px]"
            />
            
            <Button 
              onClick={handleProgressUpdate}
              disabled={isLoading}
              className="w-full"
            >
              {isLoading ? 'Updating...' : 'Update Progress'}
            </Button>
            
            {/* Quick Share Progress */}
            {todayCompleted && (
              <Button
                variant="outline"
                onClick={() => {
                  const shareText = `🎉 Completed Day ${completedDays + 1} of the "${challenge.title}" challenge! ${moodRating > 3 ? getMoodEmoji(moodRating) : ''}`
                  setNewComment(shareText)
                  setShowComments(true)
                }}
                className="w-full text-sm"
              >
                🎉 Share Today's Win with Community
              </Button>
            )}
          </motion.div>
        )}
        
        {/* Challenge stats */}
        <div className="grid grid-cols-2 gap-4">
          <div className="text-center p-3 bg-muted/30 rounded">
            <div className="text-lg font-bold">{challenge.participant_count}</div>
            <div className="text-sm text-muted-foreground">Participants</div>
          </div>
          {isActive && daysRemaining > 0 && (
            <div className="text-center p-3 bg-muted/30 rounded">
              <div className="text-lg font-bold">{daysRemaining}</div>
              <div className="text-sm text-muted-foreground">Days Left</div>
            </div>
          )}
        </div>
        
        {/* Action buttons */}
        <div className="flex flex-wrap gap-2">
          {challenge.is_participating ? (
            <Button variant="outline" onClick={handleAction} disabled={isLoading}>
              {isLoading ? 'Loading...' : 'Leave Challenge'}
            </Button>
          ) : (
            <Button onClick={handleAction} disabled={isLoading || !isAuthenticated}>
              {isLoading ? 'Loading...' : 'Join Challenge'}
            </Button>
          )}
          
          {challenge.is_participating && (
            <Dialog open={showProgress} onOpenChange={setShowProgress}>
              <DialogTrigger asChild>
                <Button variant="outline" onClick={loadProgressData}>
                  <TrendUp className="w-4 h-4 mr-2" />
                  View Progress
                </Button>
              </DialogTrigger>
              <DialogContent className="max-w-4xl">
                <DialogHeader>
                  <DialogTitle className="flex items-center gap-2">
                    <Target className="w-5 h-5" />
                    Your Progress Journey
                  </DialogTitle>
                  <DialogDescription>
                    Track your daily progress and celebrate your achievements
                  </DialogDescription>
                </DialogHeader>
                
                {/* Progress Overview */}
                <div className="grid grid-cols-4 gap-4 mb-6">
                  <div className="text-center p-4 bg-gradient-to-br from-green-50 to-green-100 rounded-lg">
                    <div className="text-2xl font-bold text-green-700">{completedDays}</div>
                    <div className="text-sm text-green-600">Days Completed</div>
                  </div>
                  <div className="text-center p-4 bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg">
                    <div className="text-2xl font-bold text-blue-700">{Math.round(progressPercentage)}%</div>
                    <div className="text-sm text-blue-600">Progress</div>
                  </div>
                  <div className="text-center p-4 bg-gradient-to-br from-orange-50 to-orange-100 rounded-lg">
                    <div className="text-2xl font-bold text-orange-700 flex items-center justify-center gap-1">
                      🔥 {currentStreak}
                    </div>
                    <div className="text-sm text-orange-600">Current Streak</div>
                  </div>
                  <div className="text-center p-4 bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg">
                    <div className="text-2xl font-bold text-purple-700">{challenge.participant_count}</div>
                    <div className="text-sm text-purple-600">Community</div>
                  </div>
                </div>
                
                {/* Progress Chart */}
                <div className="mb-6">
                  <h4 className="font-medium mb-3 flex items-center justify-between">
                    <span>Daily Progress</span>
                    <span className="text-sm text-muted-foreground">
                      {progressData.length > 0 ? `${progressData.length} days tracked` : 'Start tracking your progress!'}
                    </span>
                  </h4>
                  <div className="grid grid-cols-7 gap-2 mb-4">
                    {Array.isArray(progressData) ? progressData.slice(0, 21).map((day, index) => (
                      <div key={day.id || day.date || index} className="text-center">
                        <div className={`w-8 h-8 rounded-full mx-auto mb-1 flex items-center justify-center text-xs font-medium transition-all ${
                          day.completed 
                            ? 'bg-green-500 text-white shadow-md hover:scale-110' 
                            : 'bg-gray-200 text-gray-500 hover:bg-gray-300'
                        }`}>
                          {day.completed ? '✓' : index + 1}
                        </div>
                        <div className="text-xs text-gray-500">
                          {new Date(day.date).toLocaleDateString('en-US', { weekday: 'short' })}
                        </div>
                        {day.mood_rating && (
                          <div className="text-xs">
                            {getMoodEmoji(day.mood_rating)}
                          </div>
                        )}
                      </div>
                    )) : (
                      <div className="col-span-7 text-center text-gray-500 py-8">
                        <Target className="w-8 h-8 mx-auto mb-2 opacity-50" />
                        <p>No progress data available</p>
                        <p className="text-sm">Complete today's challenge to start tracking!</p>
                      </div>
                    )}
                  </div>
                  
                  {/* Progress Motivation */}
                  {progressData.length > 0 && (
                    <div className="text-center p-3 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg">
                      <p className="text-sm font-medium text-gray-700">
                        {progressPercentage >= 80 ? "🎉 Amazing progress! You're crushing this challenge!" :
                         progressPercentage >= 50 ? "💪 You're doing great! Keep up the momentum!" :
                         progressPercentage >= 25 ? "🌟 Good start! Every step counts!" :
                         "🚀 Just getting started? That's perfectly fine!"
                        }
                      </p>
                    </div>
                  )}
                </div>
                
                <ScrollArea className="max-h-80">
                  <div className="space-y-3">
                    <h4 className="font-medium">Daily Entries</h4>
                    {Array.isArray(progressData) ? progressData.map((day, index) => (
                      <div key={day.id || day.date || index} className={`p-4 border rounded-lg transition-all hover:shadow-md ${
                        day.completed ? 'bg-green-50 border-green-200' : 'bg-gray-50 border-gray-200'
                      }`}>
                        <div className="flex items-start justify-between">
                          <div className="flex items-center gap-3 flex-1">
                            <div className={`w-6 h-6 rounded-full flex items-center justify-center ${
                              day.completed ? 'bg-green-500 text-white' : 'bg-gray-300 text-gray-600'
                            }`}>
                              {day.completed ? '✓' : '○'}
                            </div>
                            <div className="flex-1">
                              <div className="font-medium">
                                {new Date(day.date).toLocaleDateString('en-US', { 
                                  weekday: 'long', 
                                  year: 'numeric', 
                                  month: 'short', 
                                  day: 'numeric' 
                                })}
                              </div>
                              {day.notes && (
                                <div className="text-sm text-gray-600 mt-1 p-2 bg-white rounded border">
                                  💭 "{day.notes}"
                                </div>
                              )}
                              {day.reflection && (
                                <div className="text-sm text-gray-600 mt-1 p-2 bg-white rounded border">
                                  🤔 "{day.reflection}"
                                </div>
                              )}
                            </div>
                          </div>
                          <div className="text-right space-y-1">
                            {day.mood_rating && (
                              <div className="flex items-center gap-1 text-sm">
                                <span>Mood:</span>
                                <span>{getMoodEmoji(day.mood_rating)}</span>
                              </div>
                            )}
                            {day.difficulty_rating && (
                              <div className="text-sm text-gray-500">
                                Difficulty: {day.difficulty_rating}/5
                              </div>
                            )}
                            <div className="text-xs text-gray-400">
                              Streak: {day.streak_count}
                            </div>
                          </div>
                        </div>
                      </div>
                    )) : (
                      <div className="text-center py-8 text-gray-500">
                        <Target className="w-8 h-8 mx-auto mb-2 opacity-50" />
                        <p>No progress data available. Start tracking your progress!</p>
                      </div>
                    )}
                  </div>
                </ScrollArea>
              </DialogContent>
            </Dialog>
          )}
          
          <Dialog open={showCommunity} onOpenChange={setShowCommunity}>
            <DialogTrigger asChild>
              <Button variant="outline" onClick={loadCommunityMembers}>
                <Users className="w-4 h-4 mr-2" />
                Community ({challenge.participant_count})
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Challenge Community</DialogTitle>
                <DialogDescription>
                  Connect with other participants and share your journey
                </DialogDescription>
              </DialogHeader>
              <ScrollArea className="max-h-80">
                <div className="space-y-2">
                  <div className="text-sm text-muted-foreground mb-4 p-3 bg-blue-50 rounded-lg">
                    💡 <strong>Find Your Challenge Buddies!</strong> Connect with participants at similar stages to stay motivated together.
                  </div>
                  
                  {communityMembers.map((member, index) => (
                    <div key={member.user_id} className="flex items-center justify-between p-3 border rounded hover:bg-muted/50 transition-colors">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-400 to-purple-500 flex items-center justify-center text-white font-bold">
                          {(member.name || `User${member.user_id}`).charAt(0).toUpperCase()}
                        </div>
                        <div className="flex-1">
                          <div className="font-medium">
                            {member.name || `User${member.user_id}`}
                          </div>
                          <div className="text-sm text-muted-foreground">
                            {member.completed_days} days completed • Joined {getRelativeTime(member.joined_at)} ago
                          </div>
                          <div className="flex items-center gap-2 mt-1">
                            <div className="text-xs px-2 py-1 bg-green-100 text-green-700 rounded-full">
                              {Math.round(member.completion_percentage)}% complete
                            </div>
                            {member.current_streak > 0 && (
                              <div className="text-xs px-2 py-1 bg-orange-100 text-orange-700 rounded-full flex items-center gap-1">
                                🔥 {member.current_streak} day streak
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <Button variant="outline" size="sm" className="text-xs">
                          👋 Connect
                        </Button>
                      </div>
                    </div>
                  ))}
                  
                  {communityMembers.length === 0 && (
                    <div className="text-center py-8 text-muted-foreground">
                      <Users className="w-8 h-8 mx-auto mb-2 opacity-50" />
                      <p>No participants yet. Join the challenge to connect with others!</p>
                      <p className="text-sm mt-2">Be the first to start this journey and inspire others to join!</p>
                    </div>
                  )}
                </div>
              </ScrollArea>
            </DialogContent>
          </Dialog>
          
          <Dialog open={showComments} onOpenChange={setShowComments}>
            <DialogTrigger asChild>
              <Button variant="outline" onClick={loadComments}>
                <ChatCircle className="w-4 h-4 mr-2" />
                Comments ({challenge.comment_count || 0})
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>Challenge Discussion</DialogTitle>
                <DialogDescription>
                  Share your thoughts and connect with other participants
                </DialogDescription>
              </DialogHeader>
              
              {isAuthenticated && (
                <div className="space-y-2">
                  <Textarea
                    placeholder="Share your experience or ask a question..."
                    value={newComment}
                    onChange={(e) => setNewComment(e.target.value)}
                  />
                  <Button onClick={handleAddComment} disabled={!newComment.trim()}>
                    Add Comment
                  </Button>
                </div>
              )}
              
              <ScrollArea className="max-h-80">
                <div className="space-y-4">
                  {comments
                    .filter(comment => !comment.parent_id) // Only show top-level comments first
                    .map((comment) => (
                    <div key={comment.id} className="space-y-3">
                      {/* Main Comment */}
                      <div className="p-4 border rounded-lg bg-background/50">
                        <div className="flex items-start justify-between mb-3">
                          <div className="flex items-center gap-2">
                            <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                              <span className="text-sm font-medium">
                                {getDisplayName(comment.author).charAt(0).toUpperCase()}
                              </span>
                            </div>
                            <div>
                              <div className="font-medium text-sm">
                                {getDisplayName(comment.author)}
                              </div>
                              <div className="text-xs text-muted-foreground">
                                {getRelativeTime(comment.created_at)}
                              </div>
                            </div>
                          </div>
                          <div className="flex items-center gap-1 text-xs text-muted-foreground">
                            {comment.author.badges?.map((badge, idx) => (
                              <Badge key={idx} variant="outline" className="text-xs">
                                {badge}
                              </Badge>
                            ))}
                          </div>
                        </div>
                        
                        <div className="text-sm mb-3 leading-relaxed">
                          {comment.content}
                        </div>
                        
                        <div className="flex items-center gap-3 text-xs">
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-6 px-2 text-xs"
                            onClick={() => setReplyTo(replyTo === comment.id ? null : comment.id)}
                          >
                            <ArrowBendUpLeft className="w-3 h-3 mr-1" />
                            Reply
                          </Button>
                          <span className="text-muted-foreground">
                            {comment.like_count || 0} likes
                          </span>
                        </div>
                        
                        {/* Reply Form */}
                        {replyTo === comment.id && isAuthenticated && (
                          <div className="mt-3 space-y-2">
                            <Textarea
                              placeholder={`Reply to ${getDisplayName(comment.author)}...`}
                              value={replyContent}
                              onChange={(e) => setReplyContent(e.target.value)}
                              className="min-h-[80px] text-sm"
                            />
                            <div className="flex gap-2">
                              <Button
                                size="sm"
                                onClick={() => handleAddReply(comment.id)}
                                disabled={!replyContent.trim()}
                              >
                                Post Reply
                              </Button>
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => {
                                  setReplyTo(null)
                                  setReplyContent('')
                                }}
                              >
                                Cancel
                              </Button>
                            </div>
                          </div>
                        )}
                      </div>
                      
                      {/* Replies */}
                      {comment.replies && comment.replies.length > 0 && (
                        <div className="ml-6 space-y-2">
                          {comment.replies.map((reply) => (
                            <div key={reply.id} className="p-3 border rounded bg-muted/20">
                              <div className="flex items-start justify-between mb-2">
                                <div className="flex items-center gap-2">
                                  <div className="w-6 h-6 rounded-full bg-primary/10 flex items-center justify-center">
                                    <span className="text-xs font-medium">
                                      {getDisplayName(reply.author).charAt(0).toUpperCase()}
                                    </span>
                                  </div>
                                  <div>
                                    <div className="font-medium text-xs">
                                      {getDisplayName(reply.author)}
                                    </div>
                                    <div className="text-xs text-muted-foreground">
                                      {getRelativeTime(reply.created_at)}
                                    </div>
                                  </div>
                                </div>
                              </div>
                              <div className="text-xs leading-relaxed">
                                {reply.content}
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                      
                      {/* Show nested replies from the comments array */}
                      {comments
                        .filter(reply => reply.parent_id === comment.id)
                        .map((reply) => (
                          <div key={reply.id} className="ml-6">
                            <div className="p-3 border rounded bg-muted/20">
                              <div className="flex items-start justify-between mb-2">
                                <div className="flex items-center gap-2">
                                  <div className="w-6 h-6 rounded-full bg-primary/10 flex items-center justify-center">
                                    <span className="text-xs font-medium">
                                      {getDisplayName(reply.author).charAt(0).toUpperCase()}
                                    </span>
                                  </div>
                                  <div>
                                    <div className="font-medium text-xs">
                                      {getDisplayName(reply.author)}
                                    </div>
                                    <div className="text-xs text-muted-foreground">
                                      {getRelativeTime(reply.created_at)}
                                    </div>
                                  </div>
                                </div>
                              </div>
                              <div className="text-xs leading-relaxed">
                                {reply.content}
                              </div>
                            </div>
                          </div>
                        ))}
                    </div>
                  ))}
                  
                  {comments.length === 0 && (
                    <div className="text-center py-8 text-muted-foreground">
                      <ChatCircle className="w-8 h-8 mx-auto mb-2 opacity-50" />
                      <p>No comments yet. Be the first to share your thoughts!</p>
                    </div>
                  )}
                </div>
              </ScrollArea>
            </DialogContent>
          </Dialog>
        </div>
      </CardContent>
    </Card>
  )
}
