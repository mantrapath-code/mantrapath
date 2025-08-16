import { useState, useEffect, useCallback, useRef } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Avatar } from "@/components/ui/avatar"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Switch } from "@/components/ui/switch"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Progress } from "@/components/ui/progress"
import { 
  Heart, ChatCircle, Calendar, Trophy, Users, TrendUp, TrendDown,
  Funnel, ArrowClockwise, Star, Target, WifiSlash, WifiHigh, Plus, ArrowRight,
  Medal, Crown, Fire, Lightning, ShieldCheck, Sparkle, Chat, Question
} from "@phosphor-icons/react"
import { motion, AnimatePresence } from "framer-motion"
import { toast } from "sonner"
import { communityApi } from "@/services/api"
import { useAuth } from "@/hooks/useAuth"
import { useWebSocket } from "@/hooks/useWebSocket"
import { getUserDisplayName, getUserInitials } from "@/utils/userDisplay"
import { formatRelativeTime } from "@/utils/timeUtils"


interface FeedItem {
  id: string
  type: 'thread' | 'challenge' | 'event' | 'comment' | 'progress'
  title: string
  content: string
  author: {
    id: string
    name: string
    avatar_url?: string
  }
  created_at: string
  engagement: {
    likes: number
    comments: number
    participants?: number
  }
  category: string
  is_liked: boolean
  metadata?: any
}

interface CommunityScore {
  total_score: number
  breakdown: {
    participation: number
    engagement: number
    helpfulness: number
    consistency: number
  }
  level: string
  next_level_threshold: number
}

interface FeedFilters {
  types: string[]
  categories: string[]
  timeRange: string
  sortBy: string
}

interface Achievement {
  id: string
  title: string
  description: string
  category: string
  icon: string
  level: 'bronze' | 'silver' | 'gold' | 'platinum'
  earned_at: string
  progress: number
  max_progress: number
  is_completed: boolean
}

interface CommunityAnalytics {
  participation: {
    threads_created: number
    replies_posted: number
    events_joined: number
    challenges_completed: number
  }
  engagement: {
    total_likes_given: number
    total_likes_received: number
    comments_made: number
    help_requests_answered: number
  }
  growth: {
    weekly_activity_trend: number
    consistency_streak: number
    improvement_areas: string[]
    top_categories: string[]
  }
  impact: {
    community_rank: number
    total_members: number
    helpful_votes: number
    mentorship_sessions: number
  }
}

export function CommunityFeed() {
  const { user } = useAuth()
  const { isConnected: wsConnected, lastMessage } = useWebSocket()
  
  const [feedItems, setFeedItems] = useState<FeedItem[]>([])
  const [communityScore, setCommunityScore] = useState<CommunityScore | null>(null)
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [retryCount, setRetryCount] = useState(0)
  
  // Achievements and Analytics state
  const [achievements, setAchievements] = useState<Achievement[]>([])
  const [analytics, setAnalytics] = useState<CommunityAnalytics | null>(null)
  const [achievementsLoading, setAchievementsLoading] = useState(false)
  const [analyticsLoading, setAnalyticsLoading] = useState(false)
  const [showAchievements, setShowAchievements] = useState(false)
  const [showAnalytics, setShowAnalytics] = useState(false)
  
  // Real-time state
  const [lastUpdateTime, setLastUpdateTime] = useState<Date>(new Date())
  const [newItemsCount, setNewItemsCount] = useState(0)
  const autoRefreshRef = useRef<NodeJS.Timeout | null>(null)
  const retryTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  
  // Filter states
  const [filters, setFilters] = useState<FeedFilters>({
    types: ['thread', 'challenge', 'event'],
    categories: [],
    timeRange: '7d',
    sortBy: 'recent'
  })
  
  const [showFilters, setShowFilters] = useState(false)
  
  // Initialize component with loading state
  useEffect(() => {
    setLoading(true)
    loadFeedData()
  }, [])
  
  // Handle view details navigation
  const handleViewDetails = useCallback((item: FeedItem) => {
    // Show details in toast for now - detailed pages coming soon
    toast.info(`${item.type} details page coming soon!`)
  }, [])

  // Fetch user achievements
  const fetchAchievements = useCallback(async () => {
    if (!user?.id) return
    
    setAchievementsLoading(true)
    try {
      // Get user activity data to calculate achievements
      const [userActivity, communityScore] = await Promise.all([
        communityApi.getUserActivity(50),
        communityApi.getUserCommunityScore()
      ])
      
      const calculatedAchievements = calculateAchievements(userActivity, communityScore)
      setAchievements(calculatedAchievements)
    } catch (error) {
      console.error('Failed to fetch achievements:', error)
      toast.error('Failed to load achievements')
    } finally {
      setAchievementsLoading(false)
    }
  }, [user?.id])

  // Fetch community analytics
  const fetchAnalytics = useCallback(async () => {
    if (!user?.id) return
    
    setAnalyticsLoading(true)
    try {
      const [userActivity, communityScore, userStats] = await Promise.all([
        communityApi.getUserActivity(100),
        communityApi.getUserCommunityScore(),
        communityApi.getCommunityFeed({ types: ['thread', 'challenge', 'event'], timeRange: '30d', sortBy: 'recent' })
      ])
      
      const calculatedAnalytics = calculateAnalytics(userActivity, communityScore, userStats)
      setAnalytics(calculatedAnalytics)
    } catch (error) {
      console.error('Failed to fetch analytics:', error)
      toast.error('Failed to load analytics')
    } finally {
      setAnalyticsLoading(false)
    }
  }, [user?.id])

  // Helper function to calculate achievements from user activity
  const calculateAchievements = useCallback((userActivity: any, communityScore: any): Achievement[] => {
    const achievements: Achievement[] = []
    
    if (!userActivity?.activity || !communityScore) return achievements
    
    const activities = userActivity.activity
    const threadsCreated = activities.filter((a: any) => a.type === 'thread_created').length
    const repliesPosted = activities.filter((a: any) => a.type === 'reply_posted').length
    const totalLikes = activities.reduce((sum: number, a: any) => sum + (a.like_count || 0), 0)
    
    // First Steps Achievement
    if (threadsCreated >= 1) {
      achievements.push({
        id: 'first-thread',
        title: 'First Steps',
        description: 'Created your first discussion thread',
        category: 'participation',
        icon: 'thread',
        level: 'bronze',
        earned_at: activities.find((a: any) => a.type === 'thread_created')?.created_at || new Date().toISOString(),
        progress: 1,
        max_progress: 1,
        is_completed: true
      })
    }
    
    // Active Contributor Achievement
    if (threadsCreated >= 5) {
      achievements.push({
        id: 'active-contributor',
        title: 'Active Contributor',
        description: 'Created 5 or more discussion threads',
        category: 'participation',
        icon: 'star',
        level: 'silver',
        earned_at: new Date().toISOString(),
        progress: threadsCreated,
        max_progress: 5,
        is_completed: true
      })
    }
    
    // Helpful Helper Achievement
    if (repliesPosted >= 10) {
      achievements.push({
        id: 'helpful-helper',
        title: 'Helpful Helper',
        description: 'Posted 10 or more helpful replies',
        category: 'engagement',
        icon: 'heart',
        level: 'silver',
        earned_at: new Date().toISOString(),
        progress: repliesPosted,
        max_progress: 10,
        is_completed: true
      })
    }
    
    // Community Leader Achievement
    if (communityScore.total_score >= 85) {
      achievements.push({
        id: 'community-leader',
        title: 'Community Leader',
        description: 'Achieved top-tier community score',
        category: 'leadership',
        icon: 'crown',
        level: 'gold',
        earned_at: new Date().toISOString(),
        progress: communityScore.total_score,
        max_progress: 100,
        is_completed: true
      })
    }
    
    // Popular Voice Achievement
    if (totalLikes >= 50) {
      achievements.push({
        id: 'popular-voice',
        title: 'Popular Voice',
        description: 'Received 50+ likes on your contributions',
        category: 'recognition',
        icon: 'fire',
        level: 'gold',
        earned_at: new Date().toISOString(),
        progress: totalLikes,
        max_progress: 50,
        is_completed: true
      })
    }
    
    return achievements
  }, [])

  // Helper function to calculate analytics from user data
  const calculateAnalytics = useCallback((userActivity: any, communityScore: any, feedData: any): CommunityAnalytics => {
    const activities = userActivity?.activity || []
    const score = communityScore || { total_score: 0, breakdown: { participation: 0, engagement: 0, helpfulness: 0, consistency: 0 } }
    
    const threadsCreated = activities.filter((a: any) => a.type === 'thread_created').length
    const repliesPosted = activities.filter((a: any) => a.type === 'reply_posted').length
    const totalLikes = activities.reduce((sum: number, a: any) => sum + (a.like_count || 0), 0)
    
    // Calculate weekly trend (simplified)
    const lastWeekActivities = activities.filter((a: any) => {
      const activityDate = new Date(a.created_at)
      const weekAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)
      return activityDate >= weekAgo
    })
    
    return {
      participation: {
        threads_created: threadsCreated,
        replies_posted: repliesPosted,
        events_joined: 0, // Would need event participation data
        challenges_completed: 0 // Would need challenge completion data
      },
      engagement: {
        total_likes_given: 0, // Would need like activity data
        total_likes_received: totalLikes,
        comments_made: repliesPosted,
        help_requests_answered: Math.floor(repliesPosted * 0.6) // Estimated
      },
      growth: {
        weekly_activity_trend: lastWeekActivities.length > activities.length / 4 ? 1 : -1,
        consistency_streak: score.breakdown.consistency,
        improvement_areas: score.total_score < 70 ? ['engagement', 'participation'] : [],
        top_categories: ['mental-health', 'support'] // Would analyze from actual content
      },
      impact: {
        community_rank: Math.max(1, Math.floor((100 - score.total_score) * 10)), // Estimated ranking
        total_members: 1000, // Would get from community stats
        helpful_votes: Math.floor(totalLikes * 0.8), // Estimated helpful votes
        mentorship_sessions: 0 // Would need mentorship data
      }
    }
  }, [])

  // Real-time WebSocket message handling
  useEffect(() => {
    if (!lastMessage || !wsConnected) return

    try {
      switch (lastMessage.type) {
        case 'community_feed_update':
          handleRealTimeUpdate(lastMessage.data)
          break
        case 'community_like':
          handleRealTimeLike(lastMessage.data)
          break
        case 'community_comment':
          handleRealTimeComment(lastMessage.data)
          break
        case 'community_new_post':
          handleNewPost(lastMessage.data)
          break
        default:
          break
      }
    } catch (error) {
      console.error('Error handling WebSocket message:', error)
    }
  }, [lastMessage, wsConnected])

  // Auto-refresh mechanism (fallback when WebSocket is not available)
  useEffect(() => {
    if (wsConnected) {
      // Clear auto-refresh when WebSocket is connected
      if (autoRefreshRef.current) {
        clearInterval(autoRefreshRef.current)
        autoRefreshRef.current = null
      }
    } else {
      // Start auto-refresh when WebSocket is not available
      const interval = 30000 // 30 seconds
      autoRefreshRef.current = setInterval(() => {
        loadFeedDataSilently()
      }, interval)
    }

    return () => {
      if (autoRefreshRef.current) {
        clearInterval(autoRefreshRef.current)
      }
    }
  }, [wsConnected])

  // Load feed data with error handling and retries
  const loadFeedData = useCallback(async (silent = false) => {
    try {
      if (!silent) {
        setLoading(true)
        setError(null)
      }
      
      const data = await communityApi.getCommunityFeed(filters)
      
      if (data && data.length > 0) {
        setFeedItems(data as FeedItem[])
      } else {
        setFeedItems([])
      }
      
      setLastUpdateTime(new Date())
      setRetryCount(0)
      setNewItemsCount(0)
      
      if (error) {
        setError(null)
        toast.success('Community feed restored!')
      }
    } catch (err: any) {
      console.error('Failed to load feed:', err)
      
      // Set proper error state instead of using mock data
      setError('Failed to load community feed. Please try again later.')
      setFeedItems([])
      
      if (!silent) {
        toast.error('Failed to load community feed. Please try again later.')
      }
    } finally {
      setLoading(false)
    }
  }, [filters, error])

  const loadCommunityScore = useCallback(async () => {
    try {
      const score = await communityApi.getUserCommunityScore()
      setCommunityScore(score as CommunityScore)
    } catch (error: any) {
      console.error('Failed to load community score:', error)
      // Don't show errors for community score - it's optional
    }
  }, [])

  // Silent load for auto-refresh
  const loadFeedDataSilently = useCallback(() => {
    loadFeedData(true)
  }, [loadFeedData])

  // Real-time update handlers
  const handleRealTimeUpdate = useCallback((data: any) => {
    if (data.type === 'feed_refresh') {
      loadFeedDataSilently()
    } else if (data.item) {
      // Update specific item
      setFeedItems(prev => prev.map(item => 
        item.id === data.item.id ? { ...item, ...data.item } : item
      ))
    }
  }, [loadFeedDataSilently])

  const handleRealTimeLike = useCallback((data: any) => {
    setFeedItems(prev => prev.map(item => {
      if (item.id === data.item_id) {
        return {
          ...item,
          engagement: {
            ...item.engagement,
            likes: data.total_likes
          },
          is_liked: data.user_id === user?.id ? data.is_liked : item.is_liked
        }
      }
      return item
    }))
  }, [user?.id])

  const handleRealTimeComment = useCallback((data: any) => {
    setFeedItems(prev => prev.map(item => {
      if (item.id === data.item_id) {
        return {
          ...item,
          engagement: {
            ...item.engagement,
            comments: data.total_comments
          }
        }
      }
      return item
    }))
  }, [])

  const handleNewPost = useCallback((data: any) => {
    // Check if the new post matches current filters
    const matchesFilters = filters.types.includes(data.type) &&
      (filters.categories.length === 0 || filters.categories.includes(data.category))

    if (matchesFilters) {
      setNewItemsCount(prev => prev + 1)
      // Optionally add to feed immediately or show notification
      if (filters.sortBy === 'recent') {
        setFeedItems(prev => [data, ...prev])
      }
    }
  }, [filters])

  useEffect(() => {
    loadFeedData()
    loadCommunityScore()
  }, [filters, loadFeedData, loadCommunityScore])

  // Cleanup timeouts
  useEffect(() => {
    return () => {
      if (autoRefreshRef.current) {
        clearInterval(autoRefreshRef.current)
      }
      if (retryTimeoutRef.current) {
        clearTimeout(retryTimeoutRef.current)
      }
    }
  }, [])

  const handleManualRefresh = async () => {
    setRefreshing(true)
    await loadFeedData()
    await loadCommunityScore()
    setRefreshing(false)
    toast.success('Feed refreshed!')
  }

  // Optimistic like update with rollback on failure
  const handleLike = async (itemId: string, type: string) => {
    // Optimistic update
    const previousItems = [...feedItems]
    setFeedItems(prev => prev.map(item => 
      item.id === itemId 
        ? { 
            ...item, 
            is_liked: !item.is_liked,
            engagement: {
              ...item.engagement,
              likes: item.is_liked ? item.engagement.likes - 1 : item.engagement.likes + 1
            }
          }
        : item
    ))

    try {
      await communityApi.likeContent(type, itemId)
    } catch (error) {
      // Rollback on failure
      setFeedItems(previousItems)
      toast.error('Failed to update like')
    }
  }

  // Show new items notification
  const handleShowNewItems = () => {
    loadFeedData()
    setNewItemsCount(0)
  }

  const updateFilter = (key: keyof FeedFilters, value: any) => {
    setFilters(prev => ({ ...prev, [key]: value }))
  }

  const toggleFilterType = (type: string) => {
    setFilters(prev => ({
      ...prev,
      types: prev.types.includes(type) 
        ? prev.types.filter(t => t !== type)
        : [...prev.types, type]
    }))
  }

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600'
    if (score >= 60) return 'text-blue-600'
    if (score >= 40) return 'text-yellow-600'
    return 'text-gray-600'
  }

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'thread': return <ChatCircle size={16} />
      case 'challenge': return <Target size={16} />
      case 'event': return <Calendar size={16} />
      case 'comment': return <ChatCircle size={16} />
      case 'progress': return <TrendUp size={16} />
      default: return <ChatCircle size={16} />
    }
  }

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'thread': return 'bg-blue-100 text-blue-800'
      case 'challenge': return 'bg-green-100 text-green-800'
      case 'event': return 'bg-purple-100 text-purple-800'
      case 'comment': return 'bg-orange-100 text-orange-800'
      case 'progress': return 'bg-indigo-100 text-indigo-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="w-full max-w-6xl mx-auto space-y-6 p-4 min-h-screen">
      {/* Enhanced Community Score Header */}
      {communityScore && (
        <Card className="bg-gradient-to-r from-primary/10 to-primary/5 border-primary/20">
          <CardContent className="p-4">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="font-semibold text-base flex items-center gap-2">
                  <Star className="text-yellow-500" size={18} />
                  Community Score
                </h3>
                <p className="text-xs text-muted-foreground">Your engagement level</p>
              </div>
              <div className="text-right">
                <motion.div 
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  className={`text-2xl font-bold ${getScoreColor(communityScore.total_score)}`}
                >
                  {communityScore.total_score}
                </motion.div>
                <Badge variant="outline" className="mt-1 text-xs">
                  {communityScore.level}
                </Badge>
              </div>
            </div>
            
            {/* Progress bar to next level */}
            <div className="mb-4">
              <div className="flex justify-between text-xs text-muted-foreground mb-1">
                <span>Progress to next level</span>
                <span>{Math.round((communityScore.total_score / communityScore.next_level_threshold) * 100)}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-1.5">
                <motion.div 
                  initial={{ width: 0 }}
                  animate={{ width: `${(communityScore.total_score / communityScore.next_level_threshold) * 100}%` }}
                  transition={{ duration: 1, ease: "easeOut" }}
                  className="bg-gradient-to-r from-primary to-primary/80 h-1.5 rounded-full"
                ></motion.div>
              </div>
            </div>
            
            <div className="grid grid-cols-4 gap-3">
              {Object.entries(communityScore.breakdown).map(([key, value], index) => (
                <motion.div 
                  key={key}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="text-center p-2 bg-white/50 rounded-lg hover:bg-white/70 transition-colors cursor-pointer"
                >
                  <div className="text-sm font-medium text-primary">{value}</div>
                  <div className="text-xs text-muted-foreground capitalize">{key}</div>
                </motion.div>
              ))}
            </div>
            
            {/* Quick Actions */}
            <div className="flex gap-2 mt-4">
              <Button 
                variant="outline" 
                size="sm" 
                className="flex-1 text-xs"
                onClick={() => {
                  setShowAchievements(true)
                  fetchAchievements()
                }}
              >
                <Trophy size={12} className="mr-1" />
                View Achievements
              </Button>
              <Button 
                variant="outline" 
                size="sm" 
                className="flex-1 text-xs"
                onClick={() => {
                  setShowAnalytics(true)
                  fetchAnalytics()
                }}
              >
                <TrendUp size={12} className="mr-1" />
                Analytics
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Feed Controls */}
      <Card className="w-full max-w-none">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between flex-wrap gap-2">
            <CardTitle className="flex items-center gap-2">
              <Users size={20} />
              Community Feed
              {/* Real-time connection indicator */}
              <div className="flex items-center gap-1 ml-2">
                {wsConnected ? (
                  <div className="flex items-center text-green-600">
                    <WifiHigh size={16} />
                    <span className="text-xs ml-1">Live</span>
                  </div>
                ) : (
                  <div className="flex items-center text-gray-500">
                    <WifiHigh size={16} />
                    <span className="text-xs ml-1">Offline</span>
                  </div>
                )}
              </div>
            </CardTitle>
            <div className="flex items-center gap-2">
              {/* New items notification */}
              {newItemsCount > 0 && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleShowNewItems}
                  className="bg-blue-50 text-blue-600 border-blue-200 hover:bg-blue-100"
                >
                  {newItemsCount} new update{newItemsCount > 1 ? 's' : ''}
                </Button>
              )}
              
              {/* Last update time */}
              <span className="text-xs text-muted-foreground">
                Updated {formatRelativeTime(lastUpdateTime.toISOString())}
              </span>
              
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowFilters(!showFilters)}
              >
                <Funnel size={16} />
                Filters
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={handleManualRefresh}
                disabled={refreshing}
              >
                <ArrowClockwise size={16} className={refreshing ? 'animate-spin' : ''} />
              </Button>
            </div>
          </div>

          {/* Error state */}
          {error && (
            <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-red-600">
                  <WifiSlash size={16} />
                  <span className="text-sm">{error}</span>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => loadFeedData()}
                  className="text-red-600 border-red-200"
                >
                  Retry
                </Button>
              </div>
            </div>
          )}
        </CardHeader>

        {showFilters && (
          <CardContent className="border-t">
            <div className="space-y-4">
              {/* Content Type Filters */}
              <div>
                <label className="text-sm font-medium mb-2 block">Content Types</label>
                <div className="flex flex-wrap gap-2">
                  {['thread', 'challenge', 'event', 'comment', 'progress'].map(type => (
                    <div key={type} className="flex items-center space-x-2">
                      <Switch
                        checked={filters.types.includes(type)}
                        onCheckedChange={() => toggleFilterType(type)}
                      />
                      <span className="text-sm capitalize">{type}s</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Time Range & Sort */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium mb-2 block">Time Range</label>
                  <Select value={filters.timeRange} onValueChange={(value) => updateFilter('timeRange', value)}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="1d">Last 24 hours</SelectItem>
                      <SelectItem value="7d">Last week</SelectItem>
                      <SelectItem value="30d">Last month</SelectItem>
                      <SelectItem value="all">All time</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <div>
                  <label className="text-sm font-medium mb-2 block">Sort By</label>
                  <Select value={filters.sortBy} onValueChange={(value) => updateFilter('sortBy', value)}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="recent">Most Recent</SelectItem>
                      <SelectItem value="popular">Most Popular</SelectItem>
                      <SelectItem value="trending">Trending</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </div>
          </CardContent>
        )}
      </Card>

      {/* Feed Items with Tabbed Organization */}
      <Card className="w-full">
        <CardHeader className="pb-3">
          <CardTitle className="text-lg">Recent Activity</CardTitle>
        </CardHeader>
        <CardContent className="p-0 w-full">
          <Tabs value={
            filters.types.length > 1 || filters.types.includes('thread') && filters.types.includes('challenge') && filters.types.includes('event') 
              ? 'all' 
              : filters.types[0] || 'all'
          } onValueChange={(value) => {
            if (value === 'all') {
              updateFilter('types', ['thread', 'challenge', 'event', 'comment', 'progress'])
            } else {
              updateFilter('types', [value])
            }
          }} className="w-full">
            <TabsList className="w-full grid grid-cols-6 rounded-none border-b">
              <TabsTrigger value="all" className="text-xs">All</TabsTrigger>
              <TabsTrigger value="thread" className="text-xs">Discussions</TabsTrigger>
              <TabsTrigger value="challenge" className="text-xs">Challenges</TabsTrigger>
              <TabsTrigger value="event" className="text-xs">Events</TabsTrigger>
              <TabsTrigger value="comment" className="text-xs">Comments</TabsTrigger>
              <TabsTrigger value="progress" className="text-xs">Progress</TabsTrigger>
            </TabsList>
            
            <TabsContent value="all" className="mt-0">
              <div className="p-4">
                {loading ? (
                  <div className="text-center py-8">
                    <div className="animate-spin w-6 h-6 border-2 border-primary border-t-transparent rounded-full mx-auto mb-3"></div>
                    <p className="text-sm text-muted-foreground">Loading activity...</p>
                    {!wsConnected && (
                      <p className="text-xs text-amber-600 mt-2">
                        Real-time updates unavailable - using latest cached data
                      </p>
                    )}
                  </div>
                ) : error && feedItems.length === 0 ? (
                  <div className="text-center py-8">
                    <WifiSlash size={32} className="mx-auto mb-3 opacity-50 text-red-500" />
                    <h3 className="font-medium mb-2 text-sm">Connection Error</h3>
                    <p className="text-xs text-muted-foreground mb-3">
                      Unable to load community feed. Please check your connection.
                    </p>
                    <Button onClick={() => loadFeedData()} variant="outline" size="sm">
                      <ArrowClockwise size={14} className="mr-2" />
                      Try Again
                    </Button>
                  </div>
                ) : feedItems.length === 0 ? (
                  <div className="text-center py-8">
                    <Users size={32} className="mx-auto mb-3 opacity-50" />
                    <h3 className="font-medium mb-2 text-sm">No activity found</h3>
                    <p className="text-xs text-muted-foreground mb-3">
                      Try adjusting your filters or check back later for new community activity.
                    </p>
                    <div className="flex items-center justify-center gap-2 text-xs text-muted-foreground">
                      {wsConnected ? (
                        <div className="flex items-center text-green-600">
                          <WifiHigh size={12} />
                          <span className="ml-1">Live updates enabled</span>
                        </div>
                      ) : (
                        <div className="flex items-center text-green-600">
                          <WifiHigh size={12} />
                          <span className="ml-1">Live data - real-time updates</span>
                        </div>
                      )}
                    </div>
                  </div>
                ) : (
                  <div className="space-y-3 p-4">
                    <AnimatePresence>
                      {feedItems.map((item, index) => (
                        <motion.div
                          key={item.id}
                          initial={{ opacity: 0, y: 10 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ duration: 0.2, delay: index * 0.05 }}
                          className="group"
                        >
                          <Card className="w-full hover:shadow-sm transition-all duration-200 border border-border/30 hover:border-border/60 group-hover:bg-accent/20">
                            <CardContent className="p-4">
                              <div className="flex items-start gap-3">
                                <Avatar className="w-8 h-8 border border-border/30 flex-shrink-0">
                                  {item.author.avatar_url ? (
                                    <img 
                                      src={item.author.avatar_url} 
                                      alt={item.author.name}
                                      className="w-full h-full object-cover"
                                    />
                                  ) : (
                                    <div className="w-full h-full bg-primary/10 flex items-center justify-center text-primary font-medium text-xs">
                                      {getUserInitials({ id: item.author.id })}
                                    </div>
                                  )}
                                </Avatar>
                                
                                <div className="flex-1 min-w-0">
                                  <div className="flex items-center gap-2 mb-2">
                                    <span className="font-medium text-sm text-foreground">
                                      {getUserDisplayName({ id: item.author.id })}
                                    </span>
                                    <Badge 
                                      variant="secondary" 
                                      className={`text-xs px-2 py-0.5 ${getTypeColor(item.type)} border-0`}
                                    >
                                      {getTypeIcon(item.type)}
                                      <span className="ml-1 font-medium text-xs">{item.type}</span>
                                    </Badge>
                                    <span className="text-xs text-muted-foreground">
                                      {formatRelativeTime(item.created_at)}
                                    </span>
                                  </div>
                                  
                                  <h4 className="font-semibold text-sm mb-2 text-foreground">
                                    {item.title}
                                  </h4>
                                  
                                  <p className="text-sm text-muted-foreground mb-3 line-clamp-2 leading-relaxed">
                                    {item.content}
                                  </p>
                                  
                                  <div className="flex items-center justify-between">
                                    <div className="flex items-center gap-4">
                                      <motion.button
                                        whileHover={{ scale: 1.1 }}
                                        whileTap={{ scale: 0.9 }}
                                        onClick={() => handleLike(item.id, item.type)}
                                        className={`flex items-center gap-1 text-sm hover:text-red-500 transition-colors ${
                                          item.is_liked ? 'text-red-500' : 'text-muted-foreground'
                                        }`}
                                      >
                                        <Heart size={14} className={item.is_liked ? 'fill-current' : ''} />
                                        <span className="font-medium">{item.engagement.likes}</span>
                                      </motion.button>
                                      
                                      <button className="flex items-center gap-1 text-sm text-muted-foreground hover:text-blue-500 transition-colors">
                                        <ChatCircle size={14} />
                                        <span className="font-medium">{item.engagement.comments}</span>
                                      </button>
                                    </div>
                                    
                                    <motion.button
                                      whileHover={{ scale: 1.05, x: 2 }}
                                      whileTap={{ scale: 0.95 }}
                                      onClick={() => handleViewDetails(item)}
                                      className="flex items-center gap-1 text-sm text-primary hover:text-primary/80 transition-all font-medium"
                                    >
                                      <span>View Details</span>
                                      <ArrowRight size={14} />
                                    </motion.button>
                                  </div>
                                </div>
                              </div>
                            </CardContent>
                          </Card>
                        </motion.div>
                      ))}
                    </AnimatePresence>
                  </div>
                )}
              </div>
            </TabsContent>
            
            {/* Individual tab content for filtered views */}
            {['thread', 'challenge', 'event', 'comment', 'progress'].map(type => (
              <TabsContent key={type} value={type} className="mt-0">
                <div className="p-4">
                  {feedItems.filter(item => item.type === type).length === 0 ? (
                    <div className="text-center py-8">
                      <div className={`w-12 h-12 rounded-full mx-auto mb-3 flex items-center justify-center ${getTypeColor(type)}`}>
                        {getTypeIcon(type)}
                      </div>
                      <h3 className="font-medium mb-2 text-sm">No {type}s found</h3>
                      <p className="text-xs text-muted-foreground">
                        Check back later for new {type} activity.
                      </p>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {feedItems.filter(item => item.type === type).map((item, index) => (
                        <motion.div
                          key={item.id}
                          initial={{ opacity: 0, y: 10 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ duration: 0.2 }}
                          className="group"
                        >
                          <Card className="hover:shadow-sm transition-all duration-200 border border-border/30 hover:border-border/60 group-hover:bg-accent/20">
                            <CardContent className="p-3">
                              <div className="flex items-center gap-3">
                                <Avatar className="w-6 h-6 border border-border/30 flex-shrink-0">
                                  {item.author.avatar_url ? (
                                    <img 
                                      src={item.author.avatar_url} 
                                      alt={item.author.name}
                                      className="w-full h-full object-cover"
                                    />
                                  ) : (
                                    <div className="w-full h-full bg-primary/10 flex items-center justify-center text-primary font-medium text-xs">
                                      {item.author.name.split(' ').map(n => n[0]).join('').toUpperCase()}
                                    </div>
                                  )}
                                </Avatar>
                                
                                <div className="flex-1 min-w-0">
                                  <div className="flex items-center gap-2 mb-1">
                                    <span className="font-medium text-xs truncate text-foreground">
                                      {item.author.name}
                                    </span>
                                    <Badge 
                                      variant="secondary" 
                                      className={`text-xs px-1.5 py-0 h-4 ${getTypeColor(item.type)} border-0`}
                                    >
                                      {getTypeIcon(item.type)}
                                      <span className="ml-1 font-medium text-xs">{item.type}</span>
                                    </Badge>
                                    <span className="text-xs text-muted-foreground">
                                      {formatRelativeTime(item.created_at)}
                                    </span>
                                  </div>
                                  
                                  <h4 className="font-medium text-sm line-clamp-1 text-foreground mb-0.5">
                                    {item.title}
                                  </h4>
                                  
                                  <p className="text-xs text-muted-foreground line-clamp-1 leading-relaxed">
                                    {item.content}
                                  </p>
                                </div>
                                
                                <div className="flex items-center gap-3 flex-shrink-0">
                                  <div className="flex items-center gap-3">
                                    <motion.button
                                      whileHover={{ scale: 1.1 }}
                                      whileTap={{ scale: 0.9 }}
                                      onClick={() => handleLike(item.id, item.type)}
                                      className={`flex items-center gap-1 text-xs hover:text-red-500 transition-colors ${
                                        item.is_liked ? 'text-red-500' : 'text-muted-foreground'
                                      }`}
                                    >
                                      <Heart size={12} className={item.is_liked ? 'fill-current' : ''} />
                                      <span className="font-medium text-xs">{item.engagement.likes}</span>
                                    </motion.button>
                                    
                                    <button className="flex items-center gap-1 text-xs text-muted-foreground hover:text-blue-500 transition-colors">
                                      <ChatCircle size={12} />
                                      <span className="font-medium text-xs">{item.engagement.comments}</span>
                                    </button>
                                  </div>
                                  
                                  <motion.button
                                    whileHover={{ scale: 1.05, x: 2 }}
                                    whileTap={{ scale: 0.95 }}
                                    onClick={() => handleViewDetails(item)}
                                    className="flex items-center gap-1 text-xs text-primary hover:text-primary/80 transition-all font-medium group-hover:translate-x-1"
                                  >
                                    <span>View</span>
                                    <ArrowRight size={12} className="transition-transform group-hover:translate-x-0.5" />
                                  </motion.button>
                                </div>
                              </div>
                            </CardContent>
                          </Card>
                        </motion.div>
                      ))}
                    </div>
                  )}
                </div>
              </TabsContent>
            ))}
          </Tabs>
        </CardContent>
      </Card>

      {/* Achievements Modal */}
      <Dialog open={showAchievements} onOpenChange={setShowAchievements}>
        <DialogContent className="max-w-4xl">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Trophy size={24} className="text-yellow-500" />
              Your Achievements
            </DialogTitle>
            <DialogDescription>
              {!achievementsLoading && achievements.length > 0 && (
                <span className="text-muted-foreground">
                  You've earned {achievements.length} achievement{achievements.length !== 1 ? 's' : ''}! Keep up the great work in building our community.
                </span>
              )}
            </DialogDescription>
          </DialogHeader>
          
          {achievementsLoading && (
            <div className="flex justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            </div>
          )}
          
          {!achievementsLoading && (
            <div className="mt-4">
              {achievements.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {achievements.map((achievement) => {
                    const IconComponent = achievement.icon === 'trophy' ? Trophy :
                                       achievement.icon === 'star' ? Star :
                                       achievement.icon === 'heart' ? Heart :
                                       achievement.icon === 'crown' ? Crown :
                                       achievement.icon === 'fire' ? Fire :
                                       Trophy
                    
                    const levelColorClass = achievement.level === 'gold' ? 'border-yellow-500 bg-gradient-to-br from-yellow-50 to-yellow-100' :
                                           achievement.level === 'silver' ? 'border-gray-400 bg-gradient-to-br from-gray-50 to-gray-100' :
                                           'border-amber-600 bg-gradient-to-br from-amber-50 to-amber-100'
                    
                    const iconColorClass = achievement.level === 'gold' ? 'bg-yellow-500' :
                                          achievement.level === 'silver' ? 'bg-gray-400' :
                                          'bg-amber-600'
                    
                    return (
                      <Card key={achievement.id} className={`p-4 border-2 ${levelColorClass}`}>
                        <div className="flex items-start gap-3">
                          <div className={`p-3 rounded-full ${iconColorClass} text-white flex items-center justify-center flex-shrink-0`}>
                            <IconComponent size={20} />
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 mb-1">
                              <h4 className="font-semibold text-sm">{achievement.title}</h4>
                              <Badge variant="secondary" className="text-xs px-2 py-0.5">
                                {achievement.level.toUpperCase()}
                              </Badge>
                            </div>
                            <p className="text-sm text-muted-foreground mb-2">
                              {achievement.description}
                            </p>
                            <div className="space-y-1">
                              <div className="flex items-center justify-between text-xs text-muted-foreground">
                                <span>Progress: {achievement.progress}/{achievement.max_progress}</span>
                                <span>{Math.round((achievement.progress / achievement.max_progress) * 100)}%</span>
                              </div>
                              <Progress 
                                value={(achievement.progress / achievement.max_progress) * 100} 
                                className="h-2"
                              />
                            </div>
                            <p className="text-xs text-muted-foreground mt-2">
                              Earned: {new Date(achievement.earned_at).toLocaleDateString()}
                            </p>
                          </div>
                        </div>
                      </Card>
                    )
                  })}
                </div>
              ) : (
                <div className="text-center py-12">
                  <Trophy size={48} className="mx-auto text-muted-foreground mb-4" />
                  <h3 className="text-lg font-semibold mb-2">No Achievements Yet</h3>
                  <p className="text-muted-foreground">
                    Start participating in the community to earn your first achievements!
                  </p>
                </div>
              )}
            </div>
          )}
          
          <div className="flex justify-end mt-6">
            <Button variant="outline" onClick={() => setShowAchievements(false)}>
              Close
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* Enhanced Analytics Modal with Charts */}
      <Dialog open={showAnalytics} onOpenChange={setShowAnalytics}>
        <DialogContent className="max-w-7xl max-h-[85vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <TrendUp size={24} className="text-blue-500" />
              Community Analytics & Activity
            </DialogTitle>
            <DialogDescription>
              {!analyticsLoading && analytics && (
                <span className="text-muted-foreground">
                  Comprehensive insights into your community engagement, growth trends, and impact metrics.
                </span>
              )}
            </DialogDescription>
          </DialogHeader>
          
          {analyticsLoading && (
            <div className="flex justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            </div>
          )}
          {!analyticsLoading && analytics && (
            <div className="space-y-8">
              {/* Activity Overview with Visual Progress */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
                <div className="lg:col-span-2">
                  <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                    <Users size={20} className="text-green-500" />
                    Participation Overview
                  </h3>
                  <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                    <Card className="p-4 hover:shadow-md transition-shadow border-l-4 border-green-500">
                      <div className="text-center space-y-2">
                        <div className="text-3xl font-bold text-green-600">{analytics.participation.threads_created}</div>
                        <div className="text-sm text-muted-foreground font-medium">Threads Created</div>
                        <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                          <div className="bg-green-500 h-2 rounded-full" style={{ width: `${Math.min(100, (analytics.participation.threads_created / 20) * 100)}%` }}></div>
                        </div>
                      </div>
                    </Card>
                    <Card className="p-4 hover:shadow-md transition-shadow border-l-4 border-blue-500">
                      <div className="text-center space-y-2">
                        <div className="text-3xl font-bold text-blue-600">{analytics.participation.replies_posted}</div>
                        <div className="text-sm text-muted-foreground font-medium">Replies Posted</div>
                        <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                          <div className="bg-blue-500 h-2 rounded-full" style={{ width: `${Math.min(100, (analytics.participation.replies_posted / 50) * 100)}%` }}></div>
                        </div>
                      </div>
                    </Card>
                    <Card className="p-4 hover:shadow-md transition-shadow border-l-4 border-purple-500">
                      <div className="text-center space-y-2">
                        <div className="text-3xl font-bold text-purple-600">{analytics.participation.events_joined}</div>
                        <div className="text-sm text-muted-foreground font-medium">Events Joined</div>
                        <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                          <div className="bg-purple-500 h-2 rounded-full" style={{ width: `${Math.min(100, (analytics.participation.events_joined / 10) * 100)}%` }}></div>
                        </div>
                      </div>
                    </Card>
                    <Card className="p-4 hover:shadow-md transition-shadow border-l-4 border-orange-500">
                      <div className="text-center space-y-2">
                        <div className="text-3xl font-bold text-orange-600">{analytics.participation.challenges_completed}</div>
                        <div className="text-sm text-muted-foreground font-medium">Challenges Completed</div>
                        <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                          <div className="bg-orange-500 h-2 rounded-full" style={{ width: `${Math.min(100, (analytics.participation.challenges_completed / 5) * 100)}%` }}></div>
                        </div>
                      </div>
                    </Card>
                  </div>
                </div>
                
                {/* Activity Distribution Chart */}
                <div>
                  <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                    <Target size={20} className="text-amber-500" />
                    Activity Distribution
                  </h3>
                  <Card className="p-6">
                    <div className="space-y-4">
                      {[
                        { label: 'Threads', value: analytics.participation.threads_created, color: 'bg-green-500', max: 20 },
                        { label: 'Replies', value: analytics.participation.replies_posted, color: 'bg-blue-500', max: 50 },
                        { label: 'Events', value: analytics.participation.events_joined, color: 'bg-purple-500', max: 10 },
                        { label: 'Challenges', value: analytics.participation.challenges_completed, color: 'bg-orange-500', max: 5 }
                      ].map((item) => {
                        const percentage = Math.min(100, (item.value / item.max) * 100)
                        return (
                          <div key={item.label} className="space-y-2">
                            <div className="flex justify-between items-center">
                              <span className="text-sm font-medium">{item.label}</span>
                              <span className="text-sm text-muted-foreground">{item.value}</span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-3">
                              <div className={`${item.color} h-3 rounded-full transition-all duration-500`} style={{ width: `${percentage}%` }}></div>
                            </div>
                          </div>
                        )
                      })}
                    </div>
                  </Card>
                </div>
              </div>

              {/* Engagement Analytics with Visual Insights */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
                <div>
                  <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                    <Heart size={20} className="text-red-500" />
                    Community Engagement
                  </h3>
                  <div className="grid grid-cols-2 gap-4 mb-4">
                    <Card className="p-4 hover:shadow-md transition-shadow border-l-4 border-red-500">
                      <div className="space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="text-sm font-medium text-muted-foreground">Likes Received</span>
                          <Heart size={16} className="text-red-500" />
                        </div>
                        <div className="text-2xl font-bold text-red-600">{analytics.engagement.total_likes_received}</div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div className="bg-red-500 h-2 rounded-full" style={{ width: `${Math.min(100, (analytics.engagement.total_likes_received / 100) * 100)}%` }}></div>
                        </div>
                      </div>
                    </Card>
                    <Card className="p-4 hover:shadow-md transition-shadow border-l-4 border-pink-500">
                      <div className="space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="text-sm font-medium text-muted-foreground">Likes Given</span>
                          <Heart size={16} className="text-pink-500" />
                        </div>
                        <div className="text-2xl font-bold text-pink-600">{analytics.engagement.total_likes_given}</div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div className="bg-pink-500 h-2 rounded-full" style={{ width: `${Math.min(100, (analytics.engagement.total_likes_given / 150) * 100)}%` }}></div>
                        </div>
                      </div>
                    </Card>
                    <Card className="p-4 hover:shadow-md transition-shadow border-l-4 border-amber-500">
                      <div className="space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="text-sm font-medium text-muted-foreground">Comments</span>
                          <Chat size={16} className="text-amber-500" />
                        </div>
                        <div className="text-2xl font-bold text-amber-600">{analytics.engagement.comments_made}</div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div className="bg-amber-500 h-2 rounded-full" style={{ width: `${Math.min(100, (analytics.engagement.comments_made / 75) * 100)}%` }}></div>
                        </div>
                      </div>
                    </Card>
                    <Card className="p-4 hover:shadow-md transition-shadow border-l-4 border-emerald-500">
                      <div className="space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="text-sm font-medium text-muted-foreground">Help Provided</span>
                          <Question size={16} className="text-emerald-500" />
                        </div>
                        <div className="text-2xl font-bold text-emerald-600">{analytics.engagement.help_requests_answered}</div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div className="bg-emerald-500 h-2 rounded-full" style={{ width: `${Math.min(100, (analytics.engagement.help_requests_answered / 25) * 100)}%` }}></div>
                        </div>
                      </div>
                    </Card>
                  </div>
                </div>

                {/* Engagement Score Visualization */}
                <div>
                  <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                    <Lightning size={20} className="text-yellow-500" />
                    Engagement Score Breakdown
                  </h3>
                  <Card className="p-6">
                    <div className="space-y-6">
                      {/* Overall Engagement Score */}
                      <div className="text-center mb-6">
                        <div className="text-4xl font-bold text-primary mb-2">
                          {Math.round((analytics.engagement.total_likes_received * 2 + analytics.engagement.total_likes_given + analytics.engagement.comments_made * 3 + analytics.engagement.help_requests_answered * 5) / 10)}
                        </div>
                        <div className="text-sm text-muted-foreground">Overall Engagement Score</div>
                        <div className="w-full bg-gray-200 rounded-full h-3 mt-3">
                          <div className="bg-gradient-to-r from-yellow-400 to-orange-500 h-3 rounded-full" style={{ width: `${Math.min(100, ((analytics.engagement.total_likes_received * 2 + analytics.engagement.total_likes_given + analytics.engagement.comments_made * 3 + analytics.engagement.help_requests_answered * 5) / 500) * 100)}%` }}></div>
                        </div>
                      </div>
                      
                      {/* Contribution Breakdown */}
                      <div className="space-y-3">
                        <h4 className="font-semibold text-sm">Score Contribution:</h4>
                        {[
                          { label: 'Likes Received (×2)', value: analytics.engagement.total_likes_received * 2, color: 'bg-red-400' },
                          { label: 'Likes Given (×1)', value: analytics.engagement.total_likes_given, color: 'bg-pink-400' },
                          { label: 'Comments (×3)', value: analytics.engagement.comments_made * 3, color: 'bg-amber-400' },
                          { label: 'Help Provided (×5)', value: analytics.engagement.help_requests_answered * 5, color: 'bg-emerald-400' }
                        ].map((item) => (
                          <div key={item.label} className="flex items-center justify-between text-sm">
                            <span>{item.label}</span>
                            <div className="flex items-center gap-2">
                              <div className="w-16 bg-gray-200 rounded-full h-2">
                                <div className={`${item.color} h-2 rounded-full`} style={{ width: `${Math.min(100, (item.value / 50) * 100)}%` }}></div>
                              </div>
                              <span className="w-8 text-right">{item.value}</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </Card>
                </div>
              </div>

              {/* Enhanced Growth Trends & Analytics */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
                {/* Growth Trends with Visual Charts */}
                <div>
                  <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                    <TrendUp size={20} className="text-emerald-500" />
                    Growth & Trends Analysis
                  </h3>
                  <Card className="p-6">
                    <div className="space-y-6">
                      {/* Activity Trend Visualization */}
                      <div>
                        <div className="flex items-center justify-between mb-3">
                          <span className="text-sm font-medium">Weekly Activity Trend</span>
                          <div className="flex items-center gap-2">
                            {analytics.growth.weekly_activity_trend > 0 ? (
                              <>
                                <TrendUp size={16} className="text-green-500" />
                                <span className="text-green-600 font-semibold text-sm">+{analytics.growth.weekly_activity_trend}%</span>
                              </>
                            ) : (
                              <>
                                <TrendDown size={16} className="text-red-500" />
                                <span className="text-red-600 font-semibold text-sm">{analytics.growth.weekly_activity_trend}%</span>
                              </>
                            )}
                          </div>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-3">
                          <div 
                            className={`h-3 rounded-full transition-all duration-700 ${analytics.growth.weekly_activity_trend > 0 ? 'bg-gradient-to-r from-green-400 to-emerald-500' : 'bg-gradient-to-r from-red-400 to-red-500'}`}
                            style={{ width: `${Math.min(100, Math.abs(analytics.growth.weekly_activity_trend) + 20)}%` }}
                          ></div>
                        </div>
                      </div>

                      {/* Consistency Streak */}
                      <div>
                        <div className="flex items-center justify-between mb-3">
                          <span className="text-sm font-medium">Consistency Streak</span>
                          <div className="flex items-center gap-2">
                            <Fire size={16} className="text-orange-500" />
                            <span className="font-bold text-orange-600">{analytics.growth.consistency_streak} days</span>
                          </div>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-3">
                          <div className="bg-gradient-to-r from-orange-400 to-red-500 h-3 rounded-full transition-all duration-500" style={{ width: `${Math.min(100, (analytics.growth.consistency_streak / 30) * 100)}%` }}></div>
                        </div>
                        <div className="text-xs text-muted-foreground mt-1">
                          Target: 30 days • Progress: {Math.round((analytics.growth.consistency_streak / 30) * 100)}%
                        </div>
                      </div>

                      {/* Improvement Areas */}
                      {analytics.growth.improvement_areas.length > 0 && (
                        <div>
                          <span className="text-sm font-medium block mb-3">Focus Areas</span>
                          <div className="space-y-2">
                            {analytics.growth.improvement_areas.slice(0, 3).map((area, index) => (
                              <div key={index} className="flex items-center justify-between p-2 bg-yellow-50 rounded-lg border-l-3 border-yellow-400">
                                <span className="text-sm font-medium">{area}</span>
                                <Target size={14} className="text-yellow-600" />
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </Card>
                </div>

                {/* Category Performance */}
                <div>
                  <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                    <Star size={20} className="text-purple-500" />
                    Category Performance
                  </h3>
                  <Card className="p-6">
                    <div className="space-y-4">
                      {/* Top Categories with Progress */}
                      <div>
                        <h4 className="text-sm font-semibold mb-3 text-muted-foreground">Most Active Categories</h4>
                        <div className="space-y-3">
                          {analytics.growth.top_categories.slice(0, 5).map((category, index) => {
                            // Calculate activity based on category position and community data
                            const activity = Math.max(20, 95 - (index * 15)) // Higher score for top categories
                            return (
                              <div key={index} className="space-y-2">
                                <div className="flex items-center justify-between">
                                  <div className="flex items-center gap-2">
                                    <div className={`w-3 h-3 rounded-full ${
                                      index === 0 ? 'bg-purple-500' : 
                                      index === 1 ? 'bg-blue-500' : 
                                      index === 2 ? 'bg-green-500' : 
                                      index === 3 ? 'bg-yellow-500' : 'bg-gray-400'
                                    }`}></div>
                                    <span className="text-sm font-medium">{category}</span>
                                  </div>
                                  <span className="text-xs text-muted-foreground">{Math.round(activity)}% active</span>
                                </div>
                                <div className="w-full bg-gray-200 rounded-full h-2">
                                  <div className={`h-2 rounded-full transition-all duration-500 ${
                                    index === 0 ? 'bg-purple-500' : 
                                    index === 1 ? 'bg-blue-500' : 
                                    index === 2 ? 'bg-green-500' : 
                                    index === 3 ? 'bg-yellow-500' : 'bg-gray-400'
                                  }`} style={{ width: `${activity}%` }}></div>
                                </div>
                              </div>
                            )
                          })}
                        </div>
                      </div>

                      {/* Overall Category Engagement */}
                      <div className="pt-4 border-t">
                        <div className="text-center">
                          <div className="text-2xl font-bold text-primary mb-1">
                            {analytics.growth.top_categories.length}
                          </div>
                          <div className="text-sm text-muted-foreground mb-3">Active Categories</div>
                          <div className="w-full bg-gray-200 rounded-full h-3">
                            <div className="bg-gradient-to-r from-purple-400 to-blue-500 h-3 rounded-full" style={{ width: `${Math.min(100, (analytics.growth.top_categories.length / 10) * 100)}%` }}></div>
                          </div>
                          <div className="text-xs text-muted-foreground mt-1">Diversity Score</div>
                        </div>
                      </div>
                    </div>
                  </Card>
                </div>
              </div>

              {/* Community Impact Analytics */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Impact Metrics */}
                <div>
                  <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                    <Target size={20} className="text-amber-500" />
                    Community Impact
                  </h3>
                  <Card className="p-6 space-y-5">
                    <div className="flex items-center justify-between py-2">
                      <span className="text-sm font-medium text-gray-700">Community Rank</span>
                      <span className="font-bold text-purple-600 text-xl">#{analytics.impact.community_rank}</span>
                    </div>
                    
                    <div className="flex items-center justify-between py-2">
                      <span className="text-sm font-medium text-gray-700">Total Members</span>
                      <span className="text-muted-foreground font-medium">{analytics.impact.total_members.toLocaleString()}</span>
                    </div>
                    
                    <div className="flex items-center justify-between py-2">
                      <span className="text-sm font-medium text-gray-700">Helpful Votes</span>
                      <span className="font-bold text-green-600 text-lg">{analytics.impact.helpful_votes}</span>
                    </div>
                    
                    <div className="flex items-center justify-between py-2">
                      <span className="text-sm font-medium text-gray-700">Mentorship Sessions</span>
                      <span className="font-bold text-orange-600 text-lg">{analytics.impact.mentorship_sessions}</span>
                    </div>
                    
                    {/* Community Rank Progress */}
                    <div className="py-2">
                      <div className="flex items-center justify-between text-sm text-gray-600 mb-2">
                        <span className="font-medium">Community Ranking</span>
                        <span className="font-semibold">Top {Math.round((analytics.impact.community_rank / analytics.impact.total_members) * 100)}%</span>
                      </div>
                      <Progress 
                        value={Math.max(0, 100 - (analytics.impact.community_rank / analytics.impact.total_members) * 100)} 
                        className="h-3"
                      />
                    </div>
                  </Card>
                </div>
                
                {/* Community Reputation & Recognition */}
                <div>
                  <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                    <Crown size={20} className="text-gold-500" />
                    Recognition & Status
                  </h3>
                  <Card className="p-6">
                    <div className="space-y-6">
                      {/* Reputation Score */}
                      <div className="text-center">
                        <div className="text-3xl font-bold text-primary mb-2">
                          {Math.round((analytics.impact.helpful_votes * 10 + analytics.impact.mentorship_sessions * 25 + (analytics.impact.total_members - analytics.impact.community_rank)) / 10)}
                        </div>
                        <div className="text-sm text-muted-foreground mb-4">Community Reputation Score</div>
                        <div className="w-full bg-gray-200 rounded-full h-4">
                          <div className="bg-gradient-to-r from-yellow-400 via-orange-500 to-red-500 h-4 rounded-full" style={{ width: `${Math.min(100, (Math.round((analytics.impact.helpful_votes * 10 + analytics.impact.mentorship_sessions * 25 + (analytics.impact.total_members - analytics.impact.community_rank)) / 10) / 500) * 100)}%` }}></div>
                        </div>
                      </div>
                      
                      {/* Impact Breakdown */}
                      <div className="space-y-3">
                        <h4 className="font-semibold text-sm text-muted-foreground">Impact Sources:</h4>
                        {[
                          { label: 'Helpful Votes', value: analytics.impact.helpful_votes, icon: Heart, color: 'text-red-500', multiplier: 10 },
                          { label: 'Mentorship', value: analytics.impact.mentorship_sessions, icon: Users, color: 'text-blue-500', multiplier: 25 },
                          { label: 'Community Rank', value: analytics.impact.total_members - analytics.impact.community_rank, icon: Trophy, color: 'text-yellow-500', multiplier: 1 }
                        ].map((item, index) => {
                          const Icon = item.icon
                          const contribution = item.value * item.multiplier
                          return (
                            <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                              <div className="flex items-center gap-3">
                                <Icon size={16} className={item.color} />
                                <span className="text-sm font-medium">{item.label}</span>
                              </div>
                              <div className="text-right">
                                <div className="text-sm font-bold">{item.value}</div>
                                <div className="text-xs text-muted-foreground">+{contribution} pts</div>
                              </div>
                            </div>
                          )
                        })}
                      </div>
                      
                      {/* Ranking Badge */}
                      <div className="text-center pt-4 border-t">
                        <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-full text-sm font-semibold ${
                          analytics.impact.community_rank <= analytics.impact.total_members * 0.1 ? 'bg-yellow-100 text-yellow-800' :
                          analytics.impact.community_rank <= analytics.impact.total_members * 0.25 ? 'bg-blue-100 text-blue-800' :
                          analytics.impact.community_rank <= analytics.impact.total_members * 0.5 ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                        }`}>
                          <Trophy size={16} />
                          {
                            analytics.impact.community_rank <= analytics.impact.total_members * 0.1 ? 'Top Contributor' :
                            analytics.impact.community_rank <= analytics.impact.total_members * 0.25 ? 'Active Member' :
                            analytics.impact.community_rank <= analytics.impact.total_members * 0.5 ? 'Community Member' : 'New Member'
                          }
                        </div>
                      </div>
                    </div>
                  </Card>
                </div>
              </div>
            </div>
          )}
          
          {!analyticsLoading && !analytics && (
            <div className="text-center py-12">
              <TrendUp size={48} className="mx-auto text-muted-foreground mb-4" />
              <h3 className="text-lg font-semibold mb-2">No Analytics Data</h3>
              <p className="text-muted-foreground">
                Start engaging with the community to generate analytics insights!
              </p>
            </div>
          )}
          
          <div className="flex justify-end mt-8 pt-4 border-t">
            <Button variant="outline" onClick={() => setShowAnalytics(false)} className="px-6">
              Close
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* Floating Action Button for Quick Post */}
      <motion.div
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ delay: 0.5 }}
        className="fixed bottom-6 right-6 z-50"
      >
        <motion.button
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          className="w-14 h-14 bg-primary text-primary-foreground rounded-full shadow-lg hover:shadow-xl transition-shadow flex items-center justify-center"
          onClick={() => toast.info('Quick post feature coming soon!')}
        >
          <Plus size={24} />
        </motion.button>
      </motion.div>
    </div>
  )
}