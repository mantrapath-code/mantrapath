/**
 * Mood Pattern Sharing Component - Share anonymized mood patterns with community for peer support
 * 
 * Features:
 * - Anonymous mood pattern sharing
 * - Community encouragement system
 * - Peer milestone celebrations
 * - Inspirational story sharing
 * - Pattern comparison and insights
 */

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Progress } from '@/components/ui/progress'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { 
  Share, 
  Heart, 
  TrendUp, 
  Users, 
  Shield, 
  Star,
  ChartLine,
  ChatCircle,
  Trophy,
  Sparkle,
  Eye,
  EyeSlash,
  HandHeart
} from '@phosphor-icons/react'
import { motion, AnimatePresence } from 'framer-motion'
import { toast } from 'sonner'
import { useMoods } from "@/hooks/useMoods"
import { useMoodAnalytics } from "@/hooks/useWellness"
import { useKV } from '@/hooks/useKV'
import { useCommunityData } from '@/hooks/useCommunityData'
import { formatRelativeTime } from '@/utils/timeFormat'
import { PersonalizedInsights } from './PersonalizedInsights'

interface SharedMoodPattern {
  id: string
  userId: string // anonymized
  type: 'milestone' | 'breakthrough' | 'support-request' | 'inspiration'
  title: string
  description: string
  anonymizedPattern: {
    weeklyTrend: 'improving' | 'stable' | 'challenging'
    majorWin: string
    daysTracked: number
    improvementScore: number
  }
  tags: string[]
  timestamp: number
  encouragements: number
  encouragedBy: string[] // Array of user IDs who have given encouragements
  replies: CommunityReply[]
  isAnonymous: boolean
}

interface CommunityReply {
  id: string
  userId: string // anonymized
  content: string
  timestamp: number
  hearts: number
  isFromModerator?: boolean
  likedBy: string[] // Array of user IDs who have liked this reply
}

interface UserCommunityStats {
  patternsShared: number
  encouragementsGiven: number
  encouragementsReceived: number
  supportStreak: number
  helpfulReplies: number
}

export function MoodPatternSharing() {
  const [sharedPatterns, setSharedPatterns] = useKV<SharedMoodPattern[]>('community-mood-patterns', [])
  const [userStats, setUserStats] = useKV<UserCommunityStats>('community-stats', {
    patternsShared: 0,
    encouragementsGiven: 0,
    encouragementsReceived: 0,
    supportStreak: 0,
    helpfulReplies: 0
  })
  
  // Current user ID for tracking interactions - create unique ID per session for testing
  const [currentUserId] = useState(() => {
    const stored = localStorage.getItem('mood_sharing_user_id')
    if (stored) return stored
    
    const newId = `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    localStorage.setItem('mood_sharing_user_id', newId)
    return newId
  })
  
  // Get shared community data from main forums
  const { 
    forums, 
    threads, 
    joinedForums, 
    communityStats,
    enhancedStats,
    loading: communityLoading,
    loadForums,
    loadThreads,
    loadUserStats
  } = useCommunityData()
  
  // Calculate liked threads from threads data
  const likedThreads = (threads || []).filter(thread => thread.is_liked)
  
  // Use enhanced stats when available
  const displayStats = enhancedStats || {
    patternsShared: userStats.patternsShared,
    encouragementsGiven: userStats.encouragementsGiven,
    encouragementsReceived: userStats.encouragementsReceived,
    supportStreak: userStats.supportStreak,
    helpfulReplies: userStats.helpfulReplies,
    threads_created: 0,
    likes_received: 0
  }
  const [activeTab, setActiveTab] = useState('insights')
  const [showShareDialog, setShowShareDialog] = useState(false)
  const [selectedPattern, setSelectedPattern] = useState<SharedMoodPattern | null>(null)
  const [newShare, setNewShare] = useState({
    type: 'milestone' as SharedMoodPattern['type'],
    title: '',
    description: '',
    tags: [] as string[],
    isAnonymous: true
  })

  const { moods } = useMoods()
  const { getWeeklyInsights } = useMoodAnalytics()

  useEffect(() => {
    // Load actual community data when component mounts
    loadCommunityActivity()
  }, [])

  // Separate useEffect for migration to ensure it runs whenever sharedPatterns changes
  useEffect(() => {
    // Migrate existing patterns to include encouragedBy field and likedBy for replies
    const migratedPatterns = sharedPatterns.map(pattern => {
      const needsEncourageMigration = !pattern.encouragedBy
      const needsReplyMigration = pattern.replies.some(reply => !reply.likedBy)
      
      if (needsEncourageMigration || needsReplyMigration) {
        return { 
          ...pattern, 
          encouragedBy: pattern.encouragedBy || [],
          replies: pattern.replies.map(reply => ({
            ...reply,
            likedBy: reply.likedBy || []
          }))
        }
      }
      return pattern
    })
    
    // Update patterns if migration was needed
    if (migratedPatterns.some((pattern, index) => 
      !sharedPatterns[index]?.encouragedBy || 
      sharedPatterns[index]?.replies.some(reply => !reply.likedBy)
    )) {
      setSharedPatterns(migratedPatterns)
    }
  }, [sharedPatterns.length]) // Run when patterns array changes size

  const loadCommunityActivity = async () => {
    // Load real community data - forums and recent threads
    try {
      await loadForums()
      // If user has joined forums, load recent threads for them
      if (joinedForums.length > 0) {
        // Load threads from the first joined forum as an example
        await loadThreads(joinedForums[0])
      }
    } catch (error) {
      console.error('Failed to load community activity:', error)
    }
  }

  const generateMyMoodPattern = () => {
    const oneWeekAgo = Date.now() - (7 * 24 * 60 * 60 * 1000)
    const weekMoods = moods.filter(mood => mood.timestamp >= oneWeekAgo)
    
    if (weekMoods.length === 0) {
      return {
        weeklyTrend: 'stable' as const,
        majorWin: 'Starting mood tracking journey',
        daysTracked: 0,
        improvementScore: 50
      }
    }

    const moodValues = { 'very-low': 1, 'low': 2, 'neutral': 3, 'good': 4, 'excellent': 5 }
    const avgMood = weekMoods.reduce((sum, mood) => sum + moodValues[mood.mood], 0) / weekMoods.length
    const recentInsights = getWeeklyInsights()
    
    const trend = avgMood > 3.5 ? 'improving' as const : avgMood < 2.5 ? 'challenging' as const : 'stable' as const
    const majorWin = recentInsights.insights?.length > 0 
      ? recentInsights.insights[0] 
      : 'Consistent mood tracking'

    return {
      weeklyTrend: trend,
      majorWin,
      daysTracked: weekMoods.length,
      improvementScore: Math.round(avgMood * 20)
    }
  }

  const sharePattern = () => {
    if (!newShare.title.trim() || !newShare.description.trim()) {
      toast.error('Please fill in the title and description')
      return
    }

    const pattern: SharedMoodPattern = {
      id: Date.now().toString(),
      userId: 'current_user_anon',
      type: newShare.type,
      title: newShare.title,
      description: newShare.description,
      anonymizedPattern: generateMyMoodPattern(),
      tags: newShare.tags,
      timestamp: Date.now(),
      encouragements: 0,
      encouragedBy: [], // Initialize empty array for user tracking
      replies: [],
      isAnonymous: newShare.isAnonymous
    }

    setSharedPatterns([pattern, ...sharedPatterns])
    setUserStats({ 
      ...userStats, 
      patternsShared: userStats.patternsShared + 1 
    })

    // Reset form
    setNewShare({
      type: 'milestone',
      title: '',
      description: '',
      tags: [],
      isAnonymous: true
    })
    setShowShareDialog(false)

    toast.success('Your pattern has been shared with the community! 🎉')
  }

  const giveEncouragement = (patternId: string) => {
    const pattern = sharedPatterns.find(p => p.id === patternId)
    if (!pattern) return
    
    const hasEncouraged = pattern.encouragedBy?.includes(currentUserId) || false
    const isOwnPattern = pattern.userId === currentUserId
    
    const updatedPatterns = sharedPatterns.map(pattern => {
      if (pattern.id === patternId) {
        // Ensure encouragedBy exists
        const encouragedBy = pattern.encouragedBy || []
        
        if (hasEncouraged) {
          // Remove encouragement (toggle off)
          return {
            ...pattern,
            encouragements: Math.max(0, pattern.encouragements - 1),
            encouragedBy: encouragedBy.filter(userId => userId !== currentUserId)
          }
        } else {
          // Add encouragement (toggle on)
          return {
            ...pattern,
            encouragements: pattern.encouragements + 1,
            encouragedBy: [...encouragedBy, currentUserId]
          }
        }
      }
      return pattern
    })
    
    setSharedPatterns(updatedPatterns)
    
    // Update user stats
    if (!hasEncouraged) {
      // When giving encouragement
      setUserStats({
        ...userStats,
        encouragementsGiven: userStats.encouragementsGiven + 1,
        supportStreak: userStats.supportStreak + 1,
        // If this is the user's own pattern, also update encouragements received
        encouragementsReceived: isOwnPattern 
          ? userStats.encouragementsReceived + 1 
          : userStats.encouragementsReceived
      })
      toast.success('Encouragement sent! 💙')
    } else {
      // When removing encouragement
      setUserStats({
        ...userStats,
        encouragementsGiven: Math.max(0, userStats.encouragementsGiven - 1),
        supportStreak: Math.max(0, userStats.supportStreak - 1),
        // If this is the user's own pattern, also decrease encouragements received
        encouragementsReceived: isOwnPattern 
          ? Math.max(0, userStats.encouragementsReceived - 1)
          : userStats.encouragementsReceived
      })
      toast.success('Encouragement removed')
    }
  }

  const hasUserEncouraged = (patternId: string) => {
    const pattern = sharedPatterns.find(p => p.id === patternId)
    return pattern?.encouragedBy?.includes(currentUserId) || false
  }

  const hasUserLikedReply = (reply: CommunityReply) => {
    return reply.likedBy?.includes(currentUserId) || false
  }

  const switchUser = () => {
    const newId = `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    localStorage.setItem('mood_sharing_user_id', newId)
    window.location.reload() // Simple way to refresh with new user ID
  }

  const addReply = (patternId: string, content: string) => {
    if (!content.trim()) return

    const reply: CommunityReply = {
      id: Date.now().toString(),
      userId: 'current_user_anon',
      content,
      timestamp: Date.now(),
      hearts: 0,
      likedBy: []
    }

    const updatedPatterns = sharedPatterns.map(pattern => 
      pattern.id === patternId 
        ? { ...pattern, replies: [...pattern.replies, reply] }
        : pattern
    )
    setSharedPatterns(updatedPatterns)

    setUserStats({
      ...userStats,
      helpfulReplies: userStats.helpfulReplies + 1
    })

    toast.success('Reply added!')
  }

  const toggleReplyLike = (patternId: string, replyId: string) => {
    const updatedPatterns = sharedPatterns.map(pattern => {
      if (pattern.id === patternId) {
        const updatedReplies = pattern.replies.map(reply => {
          if (reply.id === replyId) {
            const currentUserHasLiked = reply.likedBy.includes(currentUserId)
            const newLikedBy = currentUserHasLiked
              ? reply.likedBy.filter(userId => userId !== currentUserId)
              : [...reply.likedBy, currentUserId]
            
            return {
              ...reply,
              likedBy: newLikedBy,
              hearts: newLikedBy.length
            }
          }
          return reply
        })
        return { ...pattern, replies: updatedReplies }
      }
      return pattern
    })
    
    setSharedPatterns(updatedPatterns)
    
    // Also update selectedPattern if it's the one being modified
    if (selectedPattern && selectedPattern.id === patternId) {
      const updatedSelectedPattern = updatedPatterns.find(p => p.id === patternId)
      if (updatedSelectedPattern) {
        setSelectedPattern(updatedSelectedPattern)
      }
    }
  }

  const getPatternIcon = (type: SharedMoodPattern['type']) => {
    switch (type) {
      case 'milestone': return <Trophy className="w-4 h-4 text-yellow-500" />
      case 'breakthrough': return <Sparkle className="w-4 h-4 text-purple-500" />
      case 'support-request': return <HandHeart className="w-4 h-4 text-blue-500" />
      case 'inspiration': return <Star className="w-4 h-4 text-green-500" />
    }
  }

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'improving': return <TrendUp className="w-4 h-4 text-green-500" />
      case 'challenging': return <TrendUp className="w-4 h-4 text-red-500 rotate-180" />
      default: return <div className="w-4 h-4 bg-gray-400 rounded-full" />
    }
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Users className="w-5 h-5" />
                Community Support
              </CardTitle>
              <CardDescription>
                Share your journey and support others in their wellness path
              </CardDescription>
            </div>
            <div className="flex gap-2">
              <Button 
                variant="outline" 
                size="sm"
                onClick={switchUser}
                title="Switch to a different user for testing multi-user functionality"
              >
                Switch User
              </Button>
              <Button onClick={() => setShowShareDialog(true)}>
                <Share className="w-4 h-4 mr-2" />
                Share Progress
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsList className="grid w-full grid-cols-5">
              <TabsTrigger value="insights">Personalized Insights</TabsTrigger>
              <TabsTrigger value="sharing">Pattern Sharing</TabsTrigger>
              <TabsTrigger value="community">Community Activity</TabsTrigger>
              <TabsTrigger value="my-patterns">My Shares</TabsTrigger>
              <TabsTrigger value="stats">My Impact</TabsTrigger>
            </TabsList>

            <TabsContent value="insights" className="space-y-4">
              {/* Enhanced Personalized Insights with Smart Notifications */}
              <PersonalizedInsights />
            </TabsContent>

            <TabsContent value="community" className="space-y-4">
              {/* Main Community Activity Section */}
              <Card className="border-2 border-primary/20">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Users className="text-primary" size={20} />
                    Recent Community Activity
                  </CardTitle>
                  <CardDescription>
                    Stay connected with your joined forums and liked discussions
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {communityLoading ? (
                    <div className="text-center py-4 text-muted-foreground">
                      Loading community activity...
                    </div>
                  ) : (
                    <>
                      {/* Community Stats */}
                      <div className="grid grid-cols-3 gap-4 mb-4">
                        <div className="text-center">
                          <div className="text-lg font-semibold text-primary">{(joinedForums || []).length}</div>
                          <div className="text-xs text-muted-foreground">Forums Joined</div>
                        </div>
                        <div className="text-center">
                          <div className="text-lg font-semibold text-red-500">{likedThreads.length}</div>
                          <div className="text-xs text-muted-foreground">Posts Liked</div>
                        </div>
                        <div className="text-center">
                          <div className="text-lg font-semibold text-yellow-500">{communityStats.reputation}</div>
                          <div className="text-xs text-muted-foreground">Reputation</div>
                        </div>
                      </div>
                      
                      {/* Recent Threads */}
                      {(threads || []).length > 0 ? (
                        <div className="space-y-2">
                          <h4 className="font-medium text-sm">Recent Discussions</h4>
                          {(threads || []).slice(0, 3).map((thread) => (
                            <div key={thread.id} className="flex items-start gap-3 p-3 bg-secondary/20 rounded-lg">
                              <div className="flex-1">
                                <h5 className="font-medium text-sm line-clamp-1">{thread.title}</h5>
                                <p className="text-xs text-muted-foreground line-clamp-2">{thread.content}</p>
                                <div className="flex items-center gap-2 mt-1">
                                  <Badge variant="outline" className="text-xs">{thread.forum_name}</Badge>
                                  <span className="text-xs text-muted-foreground flex items-center gap-1">
                                    <Heart size={12} className={thread.is_liked ? "text-red-500 fill-red-500" : ""} />
                                    {thread.like_count}
                                  </span>
                                  <span className="text-xs text-muted-foreground">
                                    {formatRelativeTime(thread.created_at)}
                                  </span>
                                </div>
                              </div>
                            </div>
                          ))}
                          {(joinedForums || []).length > 0 && (
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => setActiveTab('community')}
                              className="w-full mt-2"
                            >
                              View All Community Activity
                            </Button>
                          )}
                        </div>
                      ) : (
                        <div className="text-center py-6 text-muted-foreground">
                          <ChatCircle size={48} className="mx-auto mb-3 opacity-50" />
                          <h4 className="font-medium mb-2">Join the Community</h4>
                          <p className="text-sm mb-4">Connect with others on their wellness journey by joining forums and discussions!</p>
                          {(forums || []).length > 0 ? (
                            <Button
                              variant="outline"
                              onClick={() => setActiveTab('community')}
                              className="mx-auto"
                            >
                              Browse Community
                            </Button>
                          ) : (
                            <Button
                              variant="outline"
                              onClick={loadCommunityActivity}
                              disabled={communityLoading}
                            >
                              {communityLoading ? 'Loading...' : 'Load Community'}
                            </Button>
                          )}
                        </div>
                      )}
                    </>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="sharing" className="space-y-4">
              {/* Mood Pattern Sharing */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Share className="text-primary" size={20} />
                    Mood Pattern Sharing
                  </CardTitle>
                  <CardDescription>
                    Share and discover anonymized mood insights
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {sharedPatterns.length > 0 ? (
                      sharedPatterns
                        .sort((a, b) => b.timestamp - a.timestamp)
                        .map((pattern, index) => (
                          <motion.div
                            key={pattern.id}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: index * 0.1 }}
                          >
                            <Card className="p-6">
                            <div className="space-y-4">
                              {/* Header */}
                          <div className="flex items-start justify-between">
                            <div className="space-y-2">
                              <div className="flex items-center gap-2">
                                {getPatternIcon(pattern.type)}
                                <h3 className="font-semibold">{pattern.title}</h3>
                                <Badge variant="outline" className="capitalize">
                                  {pattern.type.replace('-', ' ')}
                                </Badge>
                              </div>
                              <p className="text-sm text-muted-foreground">
                                {pattern.description}
                              </p>
                            </div>
                            <div className="flex items-center gap-2 text-sm text-muted-foreground">
                              {pattern.isAnonymous ? (
                                <EyeSlash className="w-4 h-4" />
                              ) : (
                                <Eye className="w-4 h-4" />
                              )}
                              <span>{formatRelativeTime(pattern.timestamp)}</span>
                            </div>
                          </div>

                          {/* Pattern Summary */}
                          <Card className="p-4 bg-muted/50">
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                              <div className="flex items-center gap-2">
                                {getTrendIcon(pattern.anonymizedPattern.weeklyTrend)}
                                <span className="capitalize">
                                  {pattern.anonymizedPattern.weeklyTrend}
                                </span>
                              </div>
                              <div>
                                <span className="text-muted-foreground">Progress: </span>
                                <span className="font-medium">
                                  {pattern.anonymizedPattern.improvementScore}%
                                </span>
                              </div>
                              <div>
                                <span className="text-muted-foreground">Days Tracked: </span>
                                <span className="font-medium">
                                  {pattern.anonymizedPattern.daysTracked}
                                </span>
                              </div>
                              <div>
                                <ChartLine className="w-4 h-4 inline mr-1" />
                                <span className="text-xs">
                                  {pattern.anonymizedPattern.majorWin}
                                </span>
                              </div>
                            </div>
                          </Card>

                          {/* Tags */}
                          {pattern.tags && pattern.tags.length > 0 && (
                            <div className="flex flex-wrap gap-2">
                              {pattern.tags.map(tag => (
                                <Badge key={tag} variant="secondary" className="text-xs">
                                  {tag}
                                </Badge>
                              ))}
                            </div>
                          )}

                          {/* Actions */}
                          <div className="flex items-center justify-between pt-4 border-t">
                            <div className="flex items-center gap-4">
                              <Button
                                variant={hasUserEncouraged(pattern.id) ? "default" : "ghost"}
                                size="sm"
                                onClick={() => giveEncouragement(pattern.id)}
                                className={`flex items-center gap-2 ${
                                  hasUserEncouraged(pattern.id) 
                                    ? 'bg-rose-100 text-rose-700 hover:bg-rose-200' 
                                    : 'hover:bg-gray-100'
                                }`}
                              >
                                <Heart 
                                  className={`w-4 h-4 ${
                                    hasUserEncouraged(pattern.id) ? 'fill-current' : ''
                                  }`} 
                                />
                                {pattern.encouragements} Encouragements
                              </Button>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => setSelectedPattern(pattern)}
                                className="flex items-center gap-2"
                              >
                                <ChatCircle className="w-4 h-4" />
                                {pattern.replies.length} Replies
                              </Button>
                            </div>
                            <div className="flex items-center gap-2">
                              <Shield className="w-4 h-4 text-muted-foreground" />
                              <span className="text-xs text-muted-foreground">
                                Anonymized & Safe
                              </span>
                            </div>
                          </div>

                          {/* Replies Preview */}
                          {pattern.replies.length > 0 && (
                            <div className="space-y-2 pt-2 border-t">
                              {pattern.replies.slice(0, 2).map(reply => (
                                <div key={reply.id} className="p-3 rounded bg-muted/30">
                                  <div className="flex items-start justify-between">
                                    <p className="text-sm">{reply.content}</p>
                                    <button
                                      onClick={() => toggleReplyLike(pattern.id, reply.id)}
                                      className="flex items-center gap-1 text-xs text-muted-foreground hover:text-red-500 transition-colors"
                                    >
                                      <Heart 
                                        className={`w-3 h-3 ${
                                          hasUserLikedReply(reply) ? 'fill-red-500 text-red-500' : ''
                                        }`} 
                                      />
                                      {reply.hearts}
                                    </button>
                                  </div>
                                  {reply.isFromModerator && (
                                    <Badge variant="outline" className="text-xs mt-2">
                                      Community Guide
                                    </Badge>
                                  )}
                                </div>
                              ))}
                              {pattern.replies.length > 2 && (
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={() => setSelectedPattern(pattern)}
                                  className="text-xs"
                                >
                                  View all {pattern.replies.length} replies
                                </Button>
                              )}
                            </div>
                          )}
                        </div>
                      </Card>
                    </motion.div>
                  ))
                    ) : (
                      <div className="text-center py-8 text-muted-foreground">
                        <Share size={48} className="mx-auto mb-4 opacity-50" />
                        <h4 className="font-medium mb-2">No Shared Patterns Yet</h4>
                        <p className="text-sm mb-4">
                          Be the first to share your mood pattern insights with the community!
                        </p>
                        <Button
                          onClick={() => setShowShareDialog(true)}
                          variant="outline"
                        >
                          Share Your Progress
                        </Button>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="my-patterns" className="space-y-4">
              <div className="space-y-4">
                {sharedPatterns
                  .filter(pattern => pattern.userId === 'current_user_anon')
                  .length > 0 ? (
                    sharedPatterns
                      .filter(pattern => pattern.userId === 'current_user_anon')
                      .map(pattern => (
                        <Card key={pattern.id} className="p-4">
                          <div className="flex items-start justify-between">
                            <div>
                              <h4 className="font-semibold">{pattern.title}</h4>
                              <p className="text-sm text-muted-foreground mt-1">
                                {pattern.description}
                              </p>
                              <div className="flex items-center gap-4 mt-3 text-sm">
                                <span className="flex items-center gap-1">
                                  <Heart className="w-4 h-4" />
                                  {pattern.encouragements} encouragements
                                </span>
                                <span className="flex items-center gap-1">
                                  <ChatCircle className="w-4 h-4" />
                                  {pattern.replies.length} replies
                                </span>
                              </div>
                            </div>
                            <Badge className="capitalize">{pattern.type.replace('-', ' ')}</Badge>
                          </div>
                        </Card>
                      ))
                  ) : (
                    <div className="text-center py-8 text-muted-foreground">
                      <Trophy size={48} className="mx-auto mb-4 opacity-50" />
                      <h4 className="font-medium mb-2">No Shared Patterns</h4>
                      <p className="text-sm mb-4">
                        You haven't shared any mood patterns with the community yet.
                      </p>
                      <Button
                        onClick={() => setShowShareDialog(true)}
                        variant="outline"
                      >
                        Share Your First Pattern
                      </Button>
                    </div>
                  )}
              </div>
            </TabsContent>

            <TabsContent value="stats" className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Card className="p-4">
                  <h4 className="font-semibold mb-3">Community Impact</h4>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Patterns Shared</span>
                      <Badge>{userStats.patternsShared}</Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Encouragements Given</span>
                      <Badge>{userStats.encouragementsGiven}</Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Helpful Replies</span>
                      <Badge>{userStats.helpfulReplies}</Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Support Streak</span>
                      <Badge variant={userStats.supportStreak > 7 ? 'default' : 'secondary'}>
                        {userStats.supportStreak} days
                      </Badge>
                    </div>
                  </div>
                </Card>

                <Card className="p-4">
                  <h4 className="font-semibold mb-3">Recognition</h4>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Encouragements Received</span>
                      <Badge>{userStats.encouragementsReceived}</Badge>
                    </div>
                    <div className="p-3 rounded bg-primary/10">
                      <div className="flex items-center gap-2">
                        <Star className="w-4 h-4 text-yellow-500" />
                        <span className="font-medium text-sm">Community Helper</span>
                      </div>
                      <p className="text-xs text-muted-foreground mt-1">
                        Thank you for supporting others in their wellness journey!
                      </p>
                    </div>
                  </div>
                </Card>
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      {/* Share Dialog */}
      <AnimatePresence>
        {showShareDialog && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4"
            onClick={() => setShowShareDialog(false)}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="bg-background p-6 rounded-lg max-w-md w-full max-h-[80vh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              <h3 className="text-lg font-semibold mb-4">Share Your Progress</h3>
              
              <div className="space-y-4">
                <div>
                  <label className="text-sm font-medium">Type of Share</label>
                  <Select
                    value={newShare.type}
                    onValueChange={(value) => setNewShare({ ...newShare, type: value as any })}
                  >
                    <SelectTrigger className="mt-1">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="milestone">🏆 Milestone Achievement</SelectItem>
                      <SelectItem value="breakthrough">✨ Personal Breakthrough</SelectItem>
                      <SelectItem value="support-request">💙 Seeking Support</SelectItem>
                      <SelectItem value="inspiration">🌟 Inspiration Story</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <label className="text-sm font-medium">Title</label>
                  <input
                    type="text"
                    value={newShare.title}
                    onChange={(e) => setNewShare({ ...newShare, title: e.target.value })}
                    placeholder="Give your share a meaningful title..."
                    className="w-full mt-1 p-2 border rounded"
                  />
                </div>

                <div>
                  <label className="text-sm font-medium">Your Story</label>
                  <Textarea
                    value={newShare.description}
                    onChange={(e) => setNewShare({ ...newShare, description: e.target.value })}
                    placeholder="Share your experience, what you learned, or how others can support you..."
                    className="mt-1"
                    rows={4}
                  />
                </div>

                <div className="p-3 rounded bg-muted/50">
                  <h4 className="font-medium text-sm mb-2">Your Anonymized Pattern</h4>
                  <div className="text-sm space-y-1">
                    {(() => {
                      const pattern = generateMyMoodPattern()
                      return (
                        <>
                          <div>Weekly Trend: <span className="capitalize">{pattern.weeklyTrend}</span></div>
                          <div>Progress Score: {pattern.improvementScore}%</div>
                          <div>Days Tracked: {pattern.daysTracked}</div>
                        </>
                      )
                    })()}
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="anonymous"
                    checked={newShare.isAnonymous}
                    onChange={(e) => setNewShare({ ...newShare, isAnonymous: e.target.checked })}
                  />
                  <label htmlFor="anonymous" className="text-sm">
                    Share anonymously (recommended)
                  </label>
                </div>

                <div className="flex gap-3 pt-4">
                  <Button 
                    onClick={() => setShowShareDialog(false)} 
                    variant="outline" 
                    className="flex-1"
                  >
                    Cancel
                  </Button>
                  <Button onClick={sharePattern} className="flex-1">
                    Share with Community
                  </Button>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Pattern Detail Dialog */}
      <AnimatePresence>
        {selectedPattern && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4"
            onClick={() => setSelectedPattern(null)}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="bg-background p-6 rounded-lg max-w-2xl w-full max-h-[80vh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="space-y-4">
                <div className="flex items-start justify-between">
                  <h3 className="text-lg font-semibold">{selectedPattern.title}</h3>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setSelectedPattern(null)}
                  >
                    ×
                  </Button>
                </div>

                <p className="text-muted-foreground">{selectedPattern.description}</p>

                <div className="space-y-3">
                  <h4 className="font-medium">Community Replies</h4>
                  {selectedPattern.replies.map(reply => (
                    <div key={reply.id} className="p-3 rounded border">
                      <p className="text-sm">{reply.content}</p>
                      <div className="flex items-center justify-between mt-2">
                        <span className="text-xs text-muted-foreground">
                          {formatRelativeTime(reply.timestamp)}
                        </span>
                        <button
                          onClick={() => toggleReplyLike(selectedPattern.id, reply.id)}
                          className="flex items-center gap-1 text-xs text-muted-foreground hover:text-red-500 transition-colors"
                        >
                          <Heart 
                            className={`w-3 h-3 ${
                              hasUserLikedReply(reply) ? 'fill-red-500 text-red-500' : ''
                            }`} 
                          />
                          {reply.hearts}
                        </button>
                      </div>
                    </div>
                  ))}

                  <div className="pt-4 border-t">
                    <Textarea
                      placeholder="Add a supportive reply..."
                      onKeyDown={(e) => {
                        if (e.key === 'Enter' && !e.shiftKey) {
                          e.preventDefault()
                          addReply(selectedPattern.id, (e.target as HTMLTextAreaElement).value)
                          ;(e.target as HTMLTextAreaElement).value = ''
                        }
                      }}
                    />
                    <p className="text-xs text-muted-foreground mt-2">
                      Press Enter to send, Shift+Enter for new line
                    </p>
                  </div>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}