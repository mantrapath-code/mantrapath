import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Avatar } from "@/components/ui/avatar"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { ScrollArea } from "@/components/ui/scroll-area"
import { 
  Users, 
  Heart, 
  ChatCircle, 
  Trophy, 
  Plus, 
  MagnifyingGlass,
  Calendar,
  Star,
  Flag,
  Share,
  Bookmark,
  DotsThree,
  Shield,
  Target,
  TrendUp,
  ArrowBendUpLeft
} from "@phosphor-icons/react"
import { motion, AnimatePresence } from "framer-motion"
import { toast } from "sonner"
import { communityApi } from "@/services/api"
import { useCommunityData } from "@/hooks/useCommunityData"
import { EnhancedChallengeCard } from "./EnhancedChallengeCard"
import { EnhancedEventCard } from "./EnhancedEventCard"
import { formatRelativeTime as formatTime } from "@/utils/timeFormat"
import { useAuth } from "@/hooks/useAuth"
import { MoodPatternSharing } from "../mood/MoodPatternSharing"
import { getUserDisplayName, getUserInitials } from "@/utils/userDisplay"
import type { CommunityStats } from "@/hooks/useCommunityData"

// Types for community data structures
interface Forum {
  id: string
  name: string
  description: string
  category: string
  member_count: number
  thread_count: number
  is_member: boolean
  created_at: string
  tags: string[]
}

interface Thread {
  id: string
  title: string
  content: string
  author: {
    id: string
    name: string
    avatar_url?: string
    badges: string[]
  }
  forum_id: string
  forum_name: string
  created_at: string
  updated_at: string
  reply_count: number
  like_count: number
  view_count: number
  is_liked: boolean
  is_bookmarked: boolean
  tags: string[]
  category: string
}

interface Reply {
  id: string
  content: string
  author: {
    id: string
    name: string
    avatar_url?: string
    badges: string[]
  }
  thread_id: string
  parent_id?: string // Add parent_id for nested replies
  created_at: string
  like_count: number
  is_liked: boolean
}

interface CommunityEvent {
  id: string
  title: string
  description: string
  start_time: string
  end_time: string
  location?: string
  is_virtual: boolean
  participant_count: number
  is_participating: boolean
  created_at: string
  // Enhanced fields for better interaction
  comment_count?: number
  average_rating?: number
  feedback_count?: number
  tags?: string[]
  organizer?: {
    id: string
    name: string
    avatar_url?: string
  }
}

interface Challenge {
  id: string
  title: string
  description: string
  duration_days: number
  participant_count: number
  is_participating: boolean
  start_date: string
  end_date: string
  category: string
  created_at: string
  // Enhanced fields for progress tracking
  progress_percentage?: number
  current_streak?: number
  total_completions?: number
  leaderboard_position?: number
  comments_count?: number
  comment_count?: number
  // Additional fields for creation
  goal_type?: string
  visibility?: string
  challenge_type?: string
  difficulty_level?: string
}

export function EnhancedCommunitySection() {
  const { isAuthenticated, user } = useAuth()
  const [activeTab, setActiveTab] = useState("forums")
  const [events, setEvents] = useState<CommunityEvent[]>([])
  const [challenges, setChallenges] = useState<Challenge[]>([])
  const [selectedForum, setSelectedForum] = useState<Forum | null>(null)
  const [selectedThread, setSelectedThread] = useState<Thread | null>(null)
  const [replies, setReplies] = useState<Reply[]>([])
  const [searchQuery, setSearchQuery] = useState("")
  const [forumFilter, setForumFilter] = useState<'all' | 'joined'>('joined')
  const [isLoading, setIsLoading] = useState(false)
  const [showCreateDialog, setShowCreateDialog] = useState(false)
  const [showThreadDialog, setShowThreadDialog] = useState(false)
  
  // Utility function to format relative time
  const formatRelativeTime = formatTime
  
  // Use shared community data
  const {
    forums,
    threads,
    joinedForums,
    bookmarkedThreads,
    userReputation,
    communityStats,
    enhancedStats,
    loading: communityLoading,
    loadForums,
    loadThreads,
    loadUserStats,
    joinForum: joinForumAction,
    leaveForum: leaveForumAction,
    likeContent,
    unlikeContent,
    replyToThread: replyToThreadAction,
    isForumJoined,
    isThreadLiked
  } = useCommunityData()

  // Refresh all statistics
  const refreshStats = async () => {
    if (isAuthenticated) {
      try {
        await loadUserStats()
      } catch (error) {
        console.error('Failed to refresh stats:', error)
      }
    }
  }

  // Load initial data
  useEffect(() => {
    loadForums()
    if (isAuthenticated) {
      loadUserStats() // Only load stats if user is authenticated
    }
    loadEvents()
    loadChallenges()
  }, [isAuthenticated]) // Only depend on authentication status

  // Load threads when forum is selected
  useEffect(() => {
    if (selectedForum) {
      loadForumThreads(selectedForum.id)
    }
  }, [selectedForum])

  const loadForumThreads = async (forumId: string) => {
    try {
      setIsLoading(true)
      await loadThreads(forumId)
    } catch (error: any) {
      console.error('Failed to load threads:', error)
      
      // The useCommunityData hook already handles the error appropriately
      // No need to show additional toast messages here
    } finally {
      setIsLoading(false)
    }
  }

  const loadEvents = async () => {
    try {
      const eventsData = await communityApi.getEvents()
      setEvents(eventsData)
    } catch (error) {
      console.error('Failed to load events:', error)
      toast.error('Failed to load events')
      setEvents([])
    }
  }

  const loadChallenges = async () => {
    try {
      const challengesData = await communityApi.getChallenges()
      setChallenges(challengesData)
    } catch (error) {
      console.error('Failed to load challenges:', error)
      toast.error('Failed to load challenges')
      setChallenges([])
    }
  }

  const handleJoinEvent = async (eventId: string) => {
    if (!isAuthenticated) {
      toast.error('Please log in to join events')
      return
    }
    
    try {
      await communityApi.joinEvent(eventId)
      toast.success('Great! You\'re now registered for this event.')
      
      // Update local state immediately for better UX
      setEvents(prev => prev.map(event => 
        event.id === eventId 
          ? { ...event, is_participating: true, participant_count: event.participant_count + 1 }
          : event
      ))
      
      // Refresh events list and stats
      await Promise.all([loadEvents(), refreshStats()])
    } catch (error) {
      console.error('Failed to join event:', error)
      toast.error('Failed to join event. Please try again.')
    }
  }

  const handleLeaveEvent = async (eventId: string) => {
    try {
      await communityApi.leaveEvent(eventId)
      toast.success('You have left the event.')
      
      // Update local state immediately for better UX
      setEvents(prev => prev.map(event => 
        event.id === eventId 
          ? { ...event, is_participating: false, participant_count: Math.max(0, event.participant_count - 1) }
          : event
      ))
      
      // Refresh events list and stats
      await Promise.all([loadEvents(), refreshStats()])
    } catch (error) {
      console.error('Failed to leave event:', error)
      toast.error('Failed to leave event. Please try again.')
    }
  }

  const handleJoinChallenge = async (challengeId: string) => {
    if (!isAuthenticated) {
      toast.error('Please log in to join challenges')
      return
    }
    
    try {
      await communityApi.joinChallenge(challengeId)
      toast.success('Welcome to the challenge! Let\'s build healthy habits together.')
      
      // Update local state immediately for better UX
      setChallenges(prev => prev.map(challenge => 
        challenge.id === challengeId 
          ? { ...challenge, is_participating: true, participant_count: challenge.participant_count + 1 }
          : challenge
      ))
      
      // Refresh challenges list and stats
      await Promise.all([loadChallenges(), refreshStats()])
    } catch (error) {
      console.error('Failed to join challenge:', error)
      toast.error('Failed to join challenge. Please try again.')
    }
  }

  const handleLeaveChallenge = async (challengeId: string) => {
    try {
      await communityApi.leaveChallenge(challengeId)
      toast.success('You have left the challenge.')
      
      // Update local state immediately for better UX
      setChallenges(prev => prev.map(challenge => 
        challenge.id === challengeId 
          ? { ...challenge, is_participating: false, participant_count: Math.max(0, challenge.participant_count - 1) }
          : challenge
      ))
      
      // Refresh challenges list and stats
      await Promise.all([loadChallenges(), refreshStats()])
    } catch (error) {
      console.error('Failed to leave challenge:', error)
      toast.error('Failed to leave challenge. Please try again.')
    }
  }

  const handleCreateEvent = async (eventData: Partial<CommunityEvent>) => {
    try {
      await communityApi.createEvent({
        title: eventData.title!,
        description: eventData.description!,
        start_time: eventData.start_time!,
        end_time: eventData.end_time!,
        location: eventData.location,
        is_virtual: eventData.is_virtual!
      })
      toast.success('Event created successfully!')
      await loadEvents() // Refresh events list
      return null
    } catch (error) {
      console.error('Failed to create event:', error)
      toast.error('Failed to create event')
      throw error
    }
  }

  const handleCreateChallenge = async (challengeData: Partial<Challenge>) => {
    try {
      await communityApi.createChallenge({
        title: challengeData.title!,
        description: challengeData.description!,
        category: challengeData.category!,
        duration_days: challengeData.duration_days!,
        start_date: challengeData.start_date!,
        end_date: challengeData.end_date!,
        goal_type: challengeData.goal_type || 'daily',
        visibility: challengeData.visibility || 'public',
        challenge_type: challengeData.challenge_type || 'custom',
        difficulty_level: challengeData.difficulty_level || 'beginner'
      })
      toast.success('Challenge created successfully!')
      await loadChallenges() // Refresh challenges list
      return null
    } catch (error) {
      console.error('Failed to create challenge:', error)
      toast.error('Failed to create challenge')
      throw error
    }
  }

  const handleJoinForum = async (forumId: string) => {
    if (!isAuthenticated) {
      toast.error('Please log in to join forums')
      return
    }
    
    try {
      await joinForumAction(forumId)
      loadForums() // Refresh to update member count
    } catch (error) {
      console.error('Failed to join forum:', error)
      toast.error('Failed to join forum')
    }
  }

  const handleLeaveForum = async (forumId: string) => {
    if (!isAuthenticated) {
      toast.error('Please log in to manage forum membership')
      return
    }
    
    try {
      await leaveForumAction(forumId)
      loadForums() // Refresh to update member count
    } catch (error) {
      console.error('Failed to leave forum:', error)
      toast.error('Failed to leave forum')
    }
  }

  const handleLikeThread = async (threadId: string, contentType: string = 'thread') => {
    if (!isAuthenticated) {
      toast.error('Please log in to like posts')
      return
    }
    
    try {
      const isLiked = isThreadLiked(threadId)
      
      if (isLiked) {
        await unlikeContent(contentType, threadId)
      } else {
        await likeContent(contentType, threadId)
      }
      
      // No need to refresh threads - the hook updates the state automatically
    } catch (error) {
      console.error('Failed to update like:', error)
      // Error handling is done in the hook
    }
  }

  const handleCreateThread = async (data: { title: string; content: string; forumId: string; tags: string[] }) => {
    if (!isAuthenticated) {
      toast.error('Please log in to create discussions')
      return
    }
    
    try {
      await communityApi.createThread({
        title: data.title,
        content: data.content,
        forum_id: data.forumId,
        tags: data.tags
      })
      toast.success('Thread created successfully!')
      setShowCreateDialog(false)
      if (selectedForum) {
        loadForumThreads(selectedForum.id)
      }
    } catch (error) {
      console.error('Failed to create thread:', error)
      toast.error('Failed to create thread')
    }
  }

  // Add a reply trigger to force reload of replies in thread dialog
  const [replyTrigger, setReplyTrigger] = useState(0)

  const handleReplyToThread = async (threadId: string, content: string, parentId?: string) => {
    if (!isAuthenticated) {
      toast.error('Please log in to reply to discussions')
      return
    }
    
    try {
      const result = await replyToThreadAction(threadId, content, parentId)
      
      if (result?.success) {
        toast.success('Reply posted!')
        
        // Trigger reply reload in ThreadDetailView
        setReplyTrigger(prev => prev + 1)
        
        // Refresh threads to get latest data
        if (selectedForum) {
          loadThreads(selectedForum.id)
        }
      }
    } catch (error) {
      console.error('Failed to post reply:', error)
      toast.error('Failed to post reply')
    }
  }

  const getCategoryColor = (category: string) => {
    if (!category) return 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200'
    
    switch (category.toLowerCase()) {
      case 'achievements': return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
      case 'support': return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
      case 'anxiety': return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
      case 'depression': return 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200'
      case 'general': return 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200'
      case 'wellness': return 'bg-pink-100 text-pink-800 dark:bg-pink-900 dark:text-pink-200'
      case 'mindfulness': return 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200'
      case 'challenges': return 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200'
      case 'mental-health': return 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200'
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200'
    }
  }

  const getBadgeIcon = (badge: string) => {
    switch (badge.toLowerCase()) {
      case 'community guide': return '🧭'
      case 'supportive soul': return '💙'
      case 'resilient streak': return '🌟'
      case 'helper': return '🤝'
      case 'mentor': return '🎓'
      case 'moderator': return '🛡️'
      default: return '✨'
    }
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Users className="text-primary" size={24} />
              Community Hub
            </div>
            {user && (
              <div className="text-sm text-muted-foreground">
                Welcome, {getUserDisplayName(user)}!
              </div>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsList className="grid grid-cols-5 w-full mb-6">
              <TabsTrigger value="forums">Forums</TabsTrigger>
              <TabsTrigger value="mood-sharing">Mood Sharing</TabsTrigger>
              <TabsTrigger value="events">Events</TabsTrigger>
              <TabsTrigger value="challenges">Challenges</TabsTrigger>
              <TabsTrigger value="my-activity">My Activity</TabsTrigger>
            </TabsList>

            <TabsContent value="forums" className="space-y-4">
              <div className="flex flex-col sm:flex-row gap-4 mb-6">
                <div className="flex-1">
                  <Input
                    placeholder="Search forums and discussions..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full"
                  />
                </div>
                <div className="flex items-center gap-2">
                  <Select value={forumFilter} onValueChange={(value: 'all' | 'joined') => setForumFilter(value)}>
                    <SelectTrigger className="w-32">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="joined">My Forums</SelectItem>
                      <SelectItem value="all">All Forums</SelectItem>
                    </SelectContent>
                  </Select>
                  <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
                    <DialogTrigger asChild>
                      <Button 
                        className="flex items-center gap-2"
                        disabled={!isAuthenticated}
                        title={!isAuthenticated ? "Please log in to create discussions" : ""}
                      >
                        <Plus size={16} />
                        New Discussion
                      </Button>
                    </DialogTrigger>
                    <DialogContent className="max-w-2xl">
                      <DialogHeader>
                        <DialogTitle>Start a New Discussion</DialogTitle>
                        <DialogDescription>
                          Share your thoughts, ask for support, or celebrate achievements with the community.
                        </DialogDescription>
                      </DialogHeader>
                      <CreateThreadForm onSubmit={handleCreateThread} forums={forums} />
                    </DialogContent>
                  </Dialog>
                </div>
              </div>

              <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
                {/* Forums List */}
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="font-semibold text-lg">
                      {forumFilter === 'joined' ? 'My Forums' : 'Community Forums'}
                    </h3>
                    {forumFilter === 'joined' && (
                      <Badge variant="outline">
                        {joinedForums.length} joined
                      </Badge>
                    )}
                  </div>
                  <ScrollArea className="h-[600px]">
                    <div className="space-y-3">
                      {(() => {
                        const filteredForums = forumFilter === 'joined' 
                          ? forums.filter(forum => joinedForums.includes(forum.id))
                          : forums
                        
                        const searchFilteredForums = searchQuery 
                          ? filteredForums.filter(forum => 
                              forum.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                              forum.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
                              forum.category.toLowerCase().includes(searchQuery.toLowerCase())
                            )
                          : filteredForums

                        if (searchFilteredForums.length === 0) {
                          return (
                            <div className="text-center text-muted-foreground py-8">
                              <Users size={48} className="mx-auto mb-4 opacity-50" />
                              <p className="mb-2">
                                {forumFilter === 'joined' ? 'No joined forums yet' : 'No forums found'}
                              </p>
                              <p className="text-sm">
                                {forumFilter === 'joined' 
                                  ? 'Join forums to connect with like-minded people'
                                  : 'Try adjusting your search terms'
                                }
                              </p>
                              {forumFilter === 'joined' && (
                                <Button 
                                  variant="outline" 
                                  size="sm" 
                                  className="mt-4"
                                  onClick={() => setForumFilter('all')}
                                >
                                  Browse All Forums
                                </Button>
                              )}
                            </div>
                          )
                        }

                        return searchFilteredForums.map((forum) => (
                        <motion.div
                          key={forum.id}
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          className={`p-4 rounded-lg border cursor-pointer transition-all hover:shadow-md ${
                            selectedForum?.id === forum.id ? 'border-primary bg-primary/5' : 'border-border'
                          }`}
                          onClick={() => setSelectedForum(forum)}
                        >
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <h4 className="font-medium">{forum.name}</h4>
                              <p className="text-sm text-muted-foreground mt-1">{forum.description}</p>
                              <div className="flex items-center gap-4 mt-3 text-xs text-muted-foreground">
                                <span className="flex items-center gap-1">
                                  <Users size={12} />
                                  {forum.member_count} members
                                </span>
                                <span className="flex items-center gap-1">
                                  <ChatCircle size={12} />
                                  {forum.thread_count} discussions
                                </span>
                              </div>
                              <div className="flex flex-wrap gap-1 mt-2">
                                {forum.tags?.map((tag) => (
                                  <Badge key={tag} variant="outline" className="text-xs">
                                    {tag}
                                  </Badge>
                                ))}
                              </div>
                            </div>
                            <div className="flex flex-col items-end gap-2">
                              <Badge className={getCategoryColor(forum.category)}>
                                {forum.category}
                              </Badge>
                              {isForumJoined(forum.id) ? (
                                <Button 
                                  size="sm" 
                                  variant="outline"
                                  onClick={(e) => {
                                    e.stopPropagation()
                                    handleLeaveForum(forum.id)
                                  }}
                                >
                                  Leave
                                </Button>
                              ) : (
                                <Button 
                                  size="sm"
                                  onClick={(e) => {
                                    e.stopPropagation()
                                    handleJoinForum(forum.id)
                                  }}
                                >
                                  Join
                                </Button>
                              )}
                            </div>
                          </div>
                        </motion.div>
                        ))
                      })()}
                    </div>
                  </ScrollArea>
                </div>

                {/* Threads List */}
                <div className="space-y-4">
                  <h3 className="font-semibold text-lg">
                    {selectedForum ? `${selectedForum.name} Discussions` : 'Select a Forum'}
                  </h3>
                  {selectedForum ? (
                    <ScrollArea className="h-[600px]">
                      <div className="space-y-3">
                        {isLoading ? (
                          <div className="flex items-center justify-center h-[200px] text-muted-foreground">
                            <div className="text-center">
                              <div className="animate-spin w-8 h-8 border-2 border-primary border-t-transparent rounded-full mx-auto mb-4"></div>
                              <p>Loading discussions...</p>
                            </div>
                          </div>
                        ) : threads.length === 0 ? (
                          <div className="flex items-center justify-center h-[200px] text-muted-foreground">
                            <div className="text-center">
                              <ChatCircle size={48} className="mx-auto mb-4 opacity-50" />
                              {!isForumJoined(selectedForum.id) ? (
                                <div>
                                  <p>Join this forum to view discussions</p>
                                  <p className="text-sm mt-2">Click "Join" to participate in this community</p>
                                </div>
                              ) : (
                                <div>
                                  <p>No discussions yet</p>
                                  {isAuthenticated && (
                                    <p className="text-sm mt-2">Be the first to start a conversation!</p>
                                  )}
                                </div>
                              )}
                            </div>
                          </div>
                        ) : (
                          threads.map((thread) => (
                          <motion.div
                            key={thread.id}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="p-4 rounded-lg border border-border hover:shadow-md transition-all"
                          >
                            <div className="flex items-start gap-3">
                              <Avatar className="w-10 h-10 bg-primary/10 flex items-center justify-center">
                                <span className="text-primary font-medium">
                                  {getUserInitials({ id: thread.author.id || thread.author.name })}
                                </span>
                              </Avatar>
                              
                              <div className="flex-1 space-y-2">
                                <div className="flex items-center gap-2 flex-wrap">
                                  <span className="font-medium">{getUserDisplayName({ id: thread.author.id || thread.author.name })}</span>
                                  {thread.author.badges?.map((badge) => (
                                    <Badge key={badge} variant="secondary" className="text-xs">
                                      {getBadgeIcon(badge)} {badge}
                                    </Badge>
                                  ))}
                                  <Badge className={getCategoryColor(thread.category)}>
                                    {thread.category || 'general'}
                                  </Badge>
                                </div>
                                
                                <h4 className="font-medium text-foreground hover:text-primary cursor-pointer">
                                  {thread.title}
                                </h4>
                                <p className="text-sm text-muted-foreground line-clamp-2">
                                  {thread.content}
                                </p>
                                
                                <div className="flex items-center justify-between">
                                  <div className="flex items-center gap-4 text-sm text-muted-foreground">
                                    <button 
                                      onClick={() => handleLikeThread(thread.id)}
                                      className={`flex items-center gap-1 hover:text-red-500 transition-colors ${
                                        isThreadLiked(thread.id) ? 'text-red-500' : ''
                                      }`}
                                    >
                                      <Heart size={14} />
                                      {thread.like_count}
                                    </button>
                                    <span className="flex items-center gap-1">
                                      <ChatCircle size={14} />
                                      {thread.reply_count}
                                    </span>
                                    <span>{formatRelativeTime(thread.created_at)}</span>
                                  </div>
                                  <div className="flex items-center gap-2">
                                    <Button 
                                      size="sm" 
                                      variant="ghost"
                                      onClick={() => {
                                        setSelectedThread(thread)
                                        setShowThreadDialog(true)
                                      }}
                                    >
                                      <ChatCircle size={14} />
                                      Reply
                                    </Button>
                                  </div>
                                </div>
                              </div>
                            </div>
                          </motion.div>
                        ))
                        )}
                      </div>
                    </ScrollArea>
                  ) : (
                    <div className="flex items-center justify-center h-[400px] text-muted-foreground">
                      <div className="text-center">
                        <Users size={48} className="mx-auto mb-4 opacity-50" />
                        <p>Select a forum to view discussions</p>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </TabsContent>

            <TabsContent value="mood-sharing" className="space-y-4">
              <div className="mb-6">
                <h3 className="font-semibold text-lg mb-2">Mood Pattern Sharing</h3>
                <p className="text-muted-foreground text-sm">
                  Share your wellness journey anonymously and connect with others who understand your experience.
                </p>
              </div>
              <MoodPatternSharing />
            </TabsContent>

            <TabsContent value="events" className="space-y-4">
              <div className="flex items-center justify-between mb-6">
                <h3 className="font-semibold text-lg">Community Events</h3>
                <Dialog>
                  <DialogTrigger asChild>
                    <Button size="sm" className="flex items-center gap-2">
                      <Plus size={16} />
                      Create Event
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="max-w-2xl">
                    <DialogHeader>
                      <DialogTitle>Create Community Event</DialogTitle>
                      <DialogDescription>
                        Organize a virtual or in-person wellness event for the community.
                      </DialogDescription>
                    </DialogHeader>
                    <CreateEventForm onSubmit={handleCreateEvent} />
                  </DialogContent>
                </Dialog>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {events.map((event) => (
                  <EnhancedEventCard 
                    key={event.id} 
                    event={event}
                    onJoin={() => handleJoinEvent(event.id)}
                    onLeave={() => handleLeaveEvent(event.id)}
                    onRefresh={loadEvents}
                  />
                ))}
              </div>
            </TabsContent>

            <TabsContent value="challenges" className="space-y-6">
              <ChallengesSection 
                challenges={challenges}
                onJoinChallenge={(challengeId) => handleJoinChallenge(challengeId)}
                onLeaveChallenge={(challengeId) => handleLeaveChallenge(challengeId)}
                onCreateChallenge={handleCreateChallenge}
                onRefresh={loadChallenges}
              />
            </TabsContent>

            <TabsContent value="my-activity" className="space-y-4">
              <EnhancedActivitySection 
                joinedForums={joinedForums}
                userReputation={userReputation}
                communityStats={communityStats}
                enhancedStats={enhancedStats}
                forums={forums}
                threads={threads}
                events={events}
                challenges={challenges}
              />
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      {/* Thread Detail Dialog */}
      <Dialog open={showThreadDialog} onOpenChange={setShowThreadDialog}>
        <DialogContent className="max-w-2xl max-h-[80vh] overflow-hidden p-0">
          {selectedThread && (
            <ThreadDetailView 
              thread={selectedThread} 
              onReply={(content, parentId) => handleReplyToThread(selectedThread.id, content, parentId)}
              isAuthenticated={isAuthenticated}
              replyTrigger={replyTrigger}
            />
          )}
        </DialogContent>
      </Dialog>

      {/* Community Guidelines Card */}
      <Card>
        <CardHeader>
          <CardTitle>Community Guidelines</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          <p className="text-sm text-muted-foreground flex items-center gap-2">
            <Heart size={16} className="text-red-500" />
            Be kind and supportive to everyone
          </p>
          <p className="text-sm text-muted-foreground flex items-center gap-2">
            <ChatCircle size={16} className="text-blue-500" />
            Share experiences, not medical advice
          </p>
          <p className="text-sm text-muted-foreground flex items-center gap-2">
            <Shield size={16} className="text-green-500" />
            Respect privacy and confidentiality
          </p>
          <p className="text-sm text-muted-foreground flex items-center gap-2">
            <Star size={16} className="text-yellow-500" />
            Celebrate progress, no matter how small
          </p>
        </CardContent>
      </Card>
    </div>
  )
}

// Challenges Section Component
function ChallengesSection({ 
  challenges, 
  onJoinChallenge, 
  onLeaveChallenge, 
  onCreateChallenge, 
  onRefresh 
}: {
  challenges: Challenge[]
  onJoinChallenge: (challengeId: string) => void
  onLeaveChallenge: (challengeId: string) => void
  onCreateChallenge: (data: any) => Promise<any>
  onRefresh: () => void
}) {
  const [searchTerm, setSearchTerm] = useState("")
  const [selectedCategory, setSelectedCategory] = useState("all")
  const [challengeTab, setChallengeTab] = useState("browse")

  // Filter challenges based on search and category
  const filteredChallenges = challenges.filter(challenge => {
    const matchesSearch = challenge.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         challenge.description.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesCategory = selectedCategory === "all" || challenge.category === selectedCategory
    
    if (challengeTab === "browse") {
      return matchesSearch && matchesCategory
    } else {
      return matchesSearch && matchesCategory && challenge.is_participating
    }
  })

  // Calculate tab counts
  const allChallengesCount = challenges.length
  const joinedChallengesCount = challenges.filter(c => c.is_participating).length

  const categories = ["all", ...Array.from(new Set(challenges.map(c => c.category)))]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h3 className="font-semibold text-xl text-foreground">Wellness Challenges</h3>
          <p className="text-sm text-muted-foreground">Join challenges to build healthy habits together</p>
        </div>
        <Dialog>
          <DialogTrigger asChild>
            <Button className="bg-primary hover:bg-primary/90 text-primary-foreground">
              <Plus size={16} className="mr-2" />
              Create Challenge
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Create Wellness Challenge</DialogTitle>
              <DialogDescription>
                Start a new wellness challenge to motivate and engage the community.
              </DialogDescription>
            </DialogHeader>
            <CreateChallengeForm onSubmit={onCreateChallenge} />
          </DialogContent>
        </Dialog>
      </div>

      {/* Tabs for Browse All vs My Challenges */}
      <div className="border-b border-border">
        <div className="flex space-x-1 bg-muted/30 p-1 rounded-lg w-fit">
          <button
            onClick={() => setChallengeTab("browse")}
            className={`py-2 px-4 rounded-md font-medium text-sm transition-all duration-200 flex items-center gap-2 ${
              challengeTab === "browse"
                ? "bg-background text-primary shadow-sm border border-primary/20"
                : "text-muted-foreground hover:text-foreground hover:bg-background/50"
            }`}
          >
            Browse All
            <span className="bg-primary/10 text-primary px-2 py-0.5 rounded-full text-xs font-bold">
              {allChallengesCount}
            </span>
          </button>
          <button
            onClick={() => setChallengeTab("joined")}
            className={`py-2 px-4 rounded-md font-medium text-sm transition-all duration-200 flex items-center gap-2 ${
              challengeTab === "joined"
                ? "bg-background text-primary shadow-sm border border-primary/20"
                : "text-muted-foreground hover:text-foreground hover:bg-background/50"
            }`}
          >
            My Challenges
            <span className="bg-primary/10 text-primary px-2 py-0.5 rounded-full text-xs font-bold">
              {joinedChallengesCount}
            </span>
          </button>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="flex flex-col sm:flex-row gap-4 p-4 bg-muted/20 rounded-lg border border-border/50">
        <div className="relative flex-1">
          <MagnifyingGlass size={20} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search challenges..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-3 border border-border rounded-lg bg-background focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all duration-200 shadow-sm"
          />
        </div>
        <select
          value={selectedCategory}
          onChange={(e) => setSelectedCategory(e.target.value)}
          className="px-4 py-3 border border-border rounded-lg bg-background focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all duration-200 shadow-sm min-w-[160px]"
        >
          {categories.map(category => (
            <option key={category} value={category}>
              {category === "all" ? "All Categories" : category.charAt(0).toUpperCase() + category.slice(1)}
            </option>
          ))}
        </select>
      </div>

      {/* Challenge Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 sm:gap-6">
        <AnimatePresence>
          {filteredChallenges.map((challenge) => (
            <motion.div
              key={challenge.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              className="h-full"
            >
              <CleanChallengeCard 
                challenge={challenge}
                onJoin={() => onJoinChallenge(challenge.id)}
                onLeave={() => onLeaveChallenge(challenge.id)}
                onRefresh={onRefresh}
              />
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      {/* Empty State */}
      {filteredChallenges.length === 0 && (
        <div className="text-center py-12 px-4">
          <div className="max-w-md mx-auto">
            <div className="w-16 h-16 mx-auto mb-4 bg-muted/30 rounded-full flex items-center justify-center">
              <span className="text-2xl">🎯</span>
            </div>
            <h4 className="text-lg font-medium text-foreground mb-2">
              {challengeTab === "joined" ? "No joined challenges yet" : "No challenges found"}
            </h4>
            <p className="text-muted-foreground text-sm">
              {challengeTab === "joined" 
                ? "Join challenges to start building healthy habits and track your progress"
                : searchTerm || selectedCategory !== "all"
                  ? "Try adjusting your search filters or browse all challenges"
                  : "Be the first to create a wellness challenge for the community"
              }
            </p>
            {challengeTab === "joined" && (
              <Button 
                variant="outline" 
                size="sm" 
                className="mt-4"
                onClick={() => setChallengeTab("browse")}
              >
                Browse All Challenges
              </Button>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

// Clean Challenge Card Component
function CleanChallengeCard({ 
  challenge, 
  onJoin, 
  onLeave, 
  onRefresh 
}: {
  challenge: Challenge
  onJoin: () => void
  onLeave: () => void
  onRefresh: () => void
}) {
  const [isLoading, setIsLoading] = useState(false)
  
  const isActive = new Date(challenge.end_date) > new Date()
  const daysRemaining = Math.ceil((new Date(challenge.end_date).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24))
  
  const handleAction = async () => {
    setIsLoading(true)
    try {
      if (challenge.is_participating) {
        await onLeave()
      } else {
        await onJoin()
      }
      onRefresh()
    } finally {
      setIsLoading(false)
    }
  }

  const getCategoryColor = (category: string) => {
    switch (category.toLowerCase()) {
      case 'mindfulness': return 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300'
      case 'fitness': return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300'
      case 'nutrition': return 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300'
      case 'sleep': return 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300'
      case 'stress': return 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300'
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300'
    }
  }

  return (
    <Card className={`h-full flex flex-col relative overflow-hidden hover:shadow-lg transition-all duration-300 border ${
      challenge.is_participating 
        ? 'border-primary/40 bg-gradient-to-br from-primary/8 to-primary/12 shadow-md' 
        : 'border-border hover:border-primary/30'
    }`}>
      
      <CardHeader className="pb-4 flex-shrink-0">
        <div className="space-y-3">
          {/* Category and Status */}
          <div className="flex items-center justify-between">
            <Badge className={`${getCategoryColor(challenge.category)} text-xs font-medium`}>
              {challenge.category.charAt(0).toUpperCase() + challenge.category.slice(1)}
            </Badge>
            {challenge.is_participating && (
              <Badge variant="secondary" className="bg-primary/15 text-primary border-primary/30">
                Joined
              </Badge>
            )}
          </div>
          
          {/* Title */}
          <CardTitle className="text-base sm:text-lg font-semibold text-foreground leading-tight min-h-[2.5rem] flex items-start">
            <span className="line-clamp-2">
              {challenge.title}
            </span>
          </CardTitle>
          
          {/* Description */}
          <p className="text-sm text-muted-foreground line-clamp-2 leading-relaxed min-h-[2.5rem]">
            {challenge.description}
          </p>
        </div>
      </CardHeader>
      
      <CardContent className="pt-0 flex-1 flex flex-col justify-between">
        <div className="space-y-4">
          {/* Challenge Stats - Responsive Grid */}
          <div className="grid grid-cols-3 gap-2 sm:gap-3">
            <div className="text-center p-2 sm:p-3 bg-muted/40 rounded-lg border border-border/30">
              <div className="text-lg sm:text-xl font-bold text-foreground">{challenge.duration_days}</div>
              <div className="text-xs text-muted-foreground font-medium">Days</div>
            </div>
            <div className="text-center p-2 sm:p-3 bg-muted/40 rounded-lg border border-border/30">
              <div className="text-lg sm:text-xl font-bold text-foreground">{challenge.participant_count}</div>
              <div className="text-xs text-muted-foreground font-medium">People</div>
            </div>
            <div className="text-center p-2 sm:p-3 bg-muted/40 rounded-lg border border-border/30">
              <div className="text-lg sm:text-xl font-bold text-foreground">{isActive ? Math.max(daysRemaining, 0) : 0}</div>
              <div className="text-xs text-muted-foreground font-medium">Left</div>
            </div>
          </div>

          {/* Action Button */}
          <Button 
            onClick={handleAction}
            disabled={isLoading || !isActive}
            size="sm"
            className={`w-full font-medium transition-all duration-200 ${
              challenge.is_participating 
                ? 'bg-destructive hover:bg-destructive/90 text-destructive-foreground' 
                : 'bg-primary hover:bg-primary/90 text-primary-foreground hover:scale-[1.02]'
            }`}
          >
            {isLoading ? (
              <div className="flex items-center gap-2">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-current" />
                Processing...
              </div>
            ) : challenge.is_participating ? (
              <span className="flex items-center gap-2">
                <span>×</span>
                Leave Challenge
              </span>
            ) : (
              <span className="flex items-center gap-2">
                <span>+</span>
                Join Challenge
              </span>
            )}
          </Button>

          {/* Additional Actions for Joined Challenges - Only on larger screens */}
          {challenge.is_participating && (
            <div className="hidden sm:flex gap-2">
              <Button variant="outline" size="sm" className="flex-1 text-xs">
                Progress
              </Button>
              <Button variant="outline" size="sm" className="flex-1 text-xs">
                Comments ({challenge.comment_count || 0})
              </Button>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}

// Helper components
function CreateThreadForm({ 
  onSubmit, 
  forums 
}: { 
  onSubmit: (data: any) => void
  forums: Forum[]
}) {
  const [title, setTitle] = useState("")
  const [content, setContent] = useState("")
  const [selectedForumId, setSelectedForumId] = useState("")
  const [tags, setTags] = useState("")

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!title.trim() || !content.trim() || !selectedForumId) {
      toast.error('Please fill in all required fields')
      return
    }

    onSubmit({
      title: title.trim(),
      content: content.trim(),
      forumId: selectedForumId,
      tags: tags.split(',').map(tag => tag.trim()).filter(Boolean)
    })
    
    // Reset form
    setTitle("")
    setContent("")
    setSelectedForumId("")
    setTags("")
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="text-sm font-medium">Forum</label>
        <Select value={selectedForumId} onValueChange={setSelectedForumId} required>
          <SelectTrigger>
            <SelectValue placeholder="Select a forum" />
          </SelectTrigger>
          <SelectContent>
            {forums.map((forum) => (
              <SelectItem key={forum.id} value={forum.id}>
                {forum.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      
      <div>
        <label className="text-sm font-medium">Title</label>
        <Input
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="What's on your mind?"
          required
        />
      </div>
      
      <div>
        <label className="text-sm font-medium">Content</label>
        <Textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="Share your thoughts, ask for support, or celebrate achievements..."
          rows={6}
          required
        />
      </div>
      
      <div>
        <label className="text-sm font-medium">Tags (optional)</label>
        <Input
          value={tags}
          onChange={(e) => setTags(e.target.value)}
          placeholder="mental-health, support, anxiety (comma-separated)"
        />
      </div>
      
      <div className="flex justify-end gap-2">
        <Button type="button" variant="outline">
          Cancel
        </Button>
        <Button type="submit">
          Post Discussion
        </Button>
      </div>
    </form>
  )
}

function EventCard({ 
  event, 
  onJoin, 
  onLeave 
}: { 
  event: CommunityEvent
  onJoin: () => void
  onLeave: () => void
}) {
  const [isLoading, setIsLoading] = useState(false)

  const handleAction = async () => {
    setIsLoading(true)
    try {
      if (event.is_participating) {
        await onLeave()
      } else {
        await onJoin()
      }
    } finally {
      setIsLoading(false)
    }
  }

  const formatDateTime = (dateString: string) => {
    const date = new Date(dateString)
    return {
      date: date.toLocaleDateString(),
      time: date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  }

  const { date, time } = formatDateTime(event.start_time)
  const isUpcoming = new Date(event.start_time) > new Date()

  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardContent className="p-4">
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h4 className="font-medium">{event.title}</h4>
            <div className="flex items-center gap-2">
              <Badge variant={event.is_virtual ? "secondary" : "default"}>
                {event.is_virtual ? "Virtual" : "In-Person"}
              </Badge>
              {!isUpcoming && (
                <Badge variant="outline" className="text-xs">
                  Past Event
                </Badge>
              )}
            </div>
          </div>
          
          <p className="text-sm text-muted-foreground">{event.description}</p>
          
          <div className="flex items-center gap-4 text-sm text-muted-foreground">
            <span className="flex items-center gap-1">
              <Calendar size={14} />
              {date} at {time}
            </span>
            <span className="flex items-center gap-1">
              <Users size={14} />
              {event.participant_count} participants
            </span>
          </div>

          {event.location && !event.is_virtual && (
            <div className="text-sm text-muted-foreground">
              📍 {event.location}
            </div>
          )}
          
          <Button 
            size="sm" 
            variant={event.is_participating ? "outline" : "default"}
            className="w-full"
            onClick={handleAction}
            disabled={isLoading || !isUpcoming}
          >
            {isLoading ? 'Loading...' : (
              event.is_participating ? "Leave Event" : "Join Event"
            )}
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}

function ChallengeCard({ 
  challenge, 
  onJoin, 
  onLeave 
}: { 
  challenge: Challenge
  onJoin: () => void
  onLeave: () => void
}) {
  const [isLoading, setIsLoading] = useState(false)

  const handleAction = async () => {
    setIsLoading(true)
    try {
      if (challenge.is_participating) {
        await onLeave()
      } else {
        await onJoin()
      }
    } finally {
      setIsLoading(false)
    }
  }

  const isActive = new Date(challenge.end_date) > new Date()
  const daysRemaining = Math.ceil((new Date(challenge.end_date).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24))

  const getCategoryColor = (category: string) => {
    switch (category.toLowerCase()) {
      case 'mindfulness': return 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200'
      case 'fitness': return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
      case 'nutrition': return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
      case 'sleep': return 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200'
      default: return 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200'
    }
  }

  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardContent className="p-4">
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h4 className="font-medium">{challenge.title}</h4>
            <div className="flex items-center gap-2">
              <Badge className={getCategoryColor(challenge.category)}>
                {challenge.category}
              </Badge>
              {!isActive && (
                <Badge variant="outline" className="text-xs">
                  Ended
                </Badge>
              )}
            </div>
          </div>
          
          <p className="text-sm text-muted-foreground">{challenge.description}</p>
          
          <div className="flex items-center gap-4 text-sm text-muted-foreground">
            <span className="flex items-center gap-1">
              <Trophy size={14} />
              {challenge.participant_count} participants
            </span>
            <span className="flex items-center gap-1">
              <Calendar size={14} />
              {isActive ? `${daysRemaining} days left` : 'Challenge ended'}
            </span>
          </div>

          <div className="text-xs text-muted-foreground">
            Duration: {challenge.duration_days} days
          </div>
          
          <Button 
            size="sm" 
            variant={challenge.is_participating ? "outline" : "default"}
            className="w-full"
            onClick={handleAction}
            disabled={isLoading || !isActive}
          >
            {isLoading ? 'Loading...' : (
              challenge.is_participating ? "Leave Challenge" : "Join Challenge"
            )}
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}

function ThreadDetailView({ 
  thread, 
  onReply,
  isAuthenticated,
  replyTrigger
}: { 
  thread: Thread
  onReply: (content: string, parentId?: string) => void 
  isAuthenticated: boolean
  replyTrigger: number
}) {
  const [replyContent, setReplyContent] = useState("")
  const [replies, setReplies] = useState<Reply[]>([])
  const [loadingReplies, setLoadingReplies] = useState(false)
  const [replyingTo, setReplyingTo] = useState<{id: string, name: string} | null>(null)

  // Load replies function
  const loadReplies = async () => {
    if (!isAuthenticated) {
      return // Don't load replies if not authenticated
    }
    
    try {
      setLoadingReplies(true)
      const repliesData = await communityApi.getThreadReplies(thread.id)
      setReplies(repliesData || [])
    } catch (error: any) {
      console.error('Failed to load replies:', error)
      
      // Handle authentication errors gracefully
      if (error.status === 401 || error.status === 403) {
        console.log('Not authenticated for replies - skipping')
        return
      }
      
      toast.error('Failed to load replies')
    } finally {
      setLoadingReplies(false)
    }
  }

  // Load replies when component mounts, thread changes, or reply trigger changes
  useEffect(() => {
    loadReplies()
  }, [thread.id, isAuthenticated, replyTrigger])

  // Handle liking a reply
  const handleLikeReply = async (replyId: string) => {
    if (!isAuthenticated) {
      toast.error('Please log in to like replies')
      return
    }
    
    try {
      // Optimistically update the UI first
      setReplies(prevReplies => 
        prevReplies.map(reply => 
          reply.id === replyId 
            ? { 
                ...reply, 
                is_liked: !reply.is_liked,
                like_count: reply.is_liked 
                  ? Math.max((reply.like_count || 0) - 1, 0)
                  : (reply.like_count || 0) + 1
              }
            : reply
        )
      )
      
      const response = await communityApi.likeContent('reply', replyId)
      
      // Get the updated like count from backend to ensure accuracy
      const likeInfo = await communityApi.getContentLikes('reply', replyId)
      
      // Update with the actual backend state
      setReplies(prevReplies => 
        prevReplies.map(reply => 
          reply.id === replyId 
            ? { 
                ...reply, 
                is_liked: likeInfo.is_liked,
                like_count: likeInfo.like_count
              }
            : reply
        )
      )
      
      if (response.liked) {
        toast.success('Reply liked!')
      } else {
        toast.success('Reply unliked!')
      }
    } catch (error) {
      console.error('Failed to like reply:', error)
      toast.error('Failed to update like')
      
      // Revert optimistic update on error
      loadReplies()
    }
  }

  // Handle replying to a specific reply
  const handleReplyToReply = (replyId: string, authorName: string) => {
    setReplyingTo({ id: replyId, name: authorName })
    setReplyContent(`@${authorName} `)
  }

  // Organize replies into hierarchical structure
  const organizeReplies = (replies: Reply[]): (Reply & { children?: Reply[] })[] => {
    const replyMap = new Map<string, Reply & { children?: Reply[] }>()
    const rootReplies: (Reply & { children?: Reply[] })[] = []

    // First pass: create map of all replies
    replies.forEach(reply => {
      replyMap.set(reply.id, { ...reply, children: [] })
    })

    // Second pass: organize into hierarchy
    replies.forEach(reply => {
      const replyWithChildren = replyMap.get(reply.id)!
      
      if (reply.parent_id && replyMap.has(reply.parent_id)) {
        // This is a nested reply, add to parent's children
        const parent = replyMap.get(reply.parent_id)!
        parent.children = parent.children || []
        parent.children.push(replyWithChildren)
      } else {
        // This is a top-level reply
        rootReplies.push(replyWithChildren)
      }
    })

    return rootReplies
  }

  // Compact Reply Component
  const CompactReply = ({ reply, depth = 0 }: { reply: Reply & { children?: Reply[] }, depth?: number }) => {
    const maxDepth = 1 // Very limited nesting for compact design
    const actualDepth = Math.min(depth, maxDepth)
    
    return (
      <div className={`${actualDepth > 0 ? 'ml-4 pl-2 border-l-2 border-muted' : ''}`}>
        <div className="flex gap-2 p-2 hover:bg-muted/20 rounded">
          <div className="w-6 h-6 bg-primary/10 rounded-full flex items-center justify-center flex-shrink-0">
            <span className="text-xs font-medium text-primary">
              {getUserInitials({ id: reply.author.id || reply.author.name })}
            </span>
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 text-xs text-muted-foreground mb-1">
              <span className="font-medium text-foreground">{getUserDisplayName({ id: reply.author.id || reply.author.name })}</span>
              <span>{formatRelativeTime(reply.created_at)}</span>
            </div>
            <p className="text-sm mb-1">{reply.content}</p>
            <div className="flex items-center gap-3 text-xs">
              <button 
                className={`flex items-center gap-1 hover:text-red-500 transition-colors ${
                  reply.is_liked ? 'text-red-500' : 'text-muted-foreground'
                }`}
                onClick={() => handleLikeReply(reply.id)}
              >
                <Heart size={10} className={reply.is_liked ? 'fill-current' : ''} />
                {reply.like_count}
              </button>
              {actualDepth < maxDepth && (
                <button 
                  className="text-muted-foreground hover:text-primary transition-colors"
                  onClick={() => handleReplyToReply(reply.id, getUserDisplayName({ id: reply.author.id || reply.author.name }))}
                >
                  Reply
                </button>
              )}
            </div>
          </div>
        </div>
        
        {/* Render nested replies */}
        {reply.children && reply.children.length > 0 && actualDepth < maxDepth && (
          <div className="mt-1">
            {reply.children
              .sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime())
              .map(childReply => (
                <CompactReply 
                  key={childReply.id} 
                  reply={childReply} 
                  depth={depth + 1}
                />
              ))}
          </div>
        )}
        
        {/* Show indicator for deeply nested replies */}
        {reply.children && reply.children.length > 0 && actualDepth >= maxDepth && (
          <div className="ml-4 pl-2 border-l-2 border-muted">
            <p className="text-xs text-muted-foreground italic py-1">
              {reply.children.length} more replies...
            </p>
          </div>
        )}
      </div>
    )
  }

  // Utility function to format relative time
  const formatRelativeTime = (dateString: string): string => {
    const now = new Date()
    
    // Handle different date string formats and ensure proper UTC parsing
    let date: Date
    if (dateString.includes('T') && !dateString.includes('Z') && !dateString.includes('+')) {
      // If it's an ISO string without timezone info, assume it's UTC
      date = new Date(dateString + 'Z')
    } else {
      // Otherwise parse normally
      date = new Date(dateString)
    }
    
    // If date parsing failed, return original string
    if (isNaN(date.getTime())) {
      return dateString
    }
    
    const diffInMs = now.getTime() - date.getTime()
    const diffInSeconds = Math.floor(diffInMs / 1000)
    const diffInMinutes = Math.floor(diffInSeconds / 60)
    const diffInHours = Math.floor(diffInMinutes / 60)
    const diffInDays = Math.floor(diffInHours / 24)
    const diffInWeeks = Math.floor(diffInDays / 7)
    const diffInMonths = Math.floor(diffInDays / 30)
    const diffInYears = Math.floor(diffInDays / 365)

    if (diffInSeconds < 60) {
      return diffInSeconds <= 1 ? 'now' : `${diffInSeconds}s`
    } else if (diffInMinutes < 60) {
      return `${diffInMinutes}m`
    } else if (diffInHours < 24) {
      return `${diffInHours}h`
    } else if (diffInDays < 7) {
      return `${diffInDays}d`
    } else if (diffInWeeks < 4) {
      return `${diffInWeeks}w`
    } else if (diffInMonths < 12) {
      return `${diffInMonths}mo`
    } else {
      return `${diffInYears}y`
    }
  }

  const handleSubmitReply = async () => {
    if (!replyContent.trim()) {
      toast.error('Please enter a reply')
      return
    }
    
    try {
      // If replying to a specific reply, pass the parent_id
      const parentId = replyingTo?.id || undefined
      await onReply(replyContent.trim(), parentId)
      setReplyContent("")
      setReplyingTo(null) // Clear reply target
      
      // Reload replies to show the new one
      const repliesData = await communityApi.getThreadReplies(thread.id)
      setReplies(repliesData || [])
    } catch (error) {
      console.error('Failed to submit reply:', error)
    }
  }

  return (
    <div className="max-w-full">
      {/* Compact Header */}
      <div className="px-4 py-3 border-b">
        <h3 className="font-semibold text-lg">{thread.title}</h3>
        <p className="text-sm text-muted-foreground">by {getUserDisplayName({ id: thread.author.id || thread.author.name })} in {thread.forum_name}</p>
      </div>
      
      {/* Thread Content */}
      <div className="px-4 py-3 border-b bg-muted/20">
        <p className="text-sm">{thread.content}</p>
        <div className="flex items-center gap-3 text-sm text-muted-foreground mt-2">
          <span className="flex items-center gap-1">
            <Heart size={12} />
            {thread.like_count}
          </span>
          <span className="flex items-center gap-1">
            <ChatCircle size={12} />
            {thread.reply_count}
          </span>
          <span>{formatRelativeTime(thread.created_at)}</span>
        </div>
      </div>
      
      {/* Replies Section */}
      <div className="max-h-[400px] overflow-y-auto">
        <div className="px-4 py-3">
          <h4 className="font-medium text-sm mb-3">Replies ({replies.length})</h4>
          {loadingReplies ? (
            <div className="text-center py-4">
              <div className="inline-block animate-spin rounded-full h-4 w-4 border-b-2 border-primary"></div>
              <p className="text-xs text-muted-foreground mt-1">Loading...</p>
            </div>
          ) : replies.length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-4">No replies yet</p>
          ) : (
            <div className="space-y-1">
              {organizeReplies(replies)
                .sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime())
                .map((reply) => (
                  <CompactReply key={reply.id} reply={reply} depth={0} />
                ))}
            </div>
          )}
        </div>
      </div>
      
      {/* Reply Form */}
      <div className="border-t p-4 bg-background">
        {replyingTo && (
          <div className="mb-2 flex items-center justify-between">
            <Badge variant="outline" className="text-xs">Replying to {replyingTo.name}</Badge>
            <button 
              onClick={() => {
                setReplyingTo(null)
                setReplyContent('')
              }}
              className="text-xs text-muted-foreground hover:text-foreground"
            >
              ✕
            </button>
          </div>
        )}
        <div className="flex gap-2">
          <Textarea
            value={replyContent}
            onChange={(e) => setReplyContent(e.target.value)}
            placeholder="Add a reply..."
            className="flex-1 min-h-[60px] resize-none text-sm"
            maxLength={500}
          />
          <div className="flex flex-col justify-between">
            <Button 
              onClick={handleSubmitReply}
              size="sm"
              disabled={!replyContent.trim()}
              className="mb-1"
            >
              Post
            </Button>
            <span className="text-xs text-muted-foreground">
              {replyContent.length}/500
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}

// Enhanced Activity Section with sophisticated badge system and insights
function EnhancedActivitySection({ 
  joinedForums, 
  userReputation,
  communityStats,
  enhancedStats,
  forums,
  threads,
  events,
  challenges
}: {
  joinedForums: string[]
  userReputation: number
  communityStats: CommunityStats
  enhancedStats: {
    reputation: number
    forums_joined: number
    threads_liked: number
    threads_created: number
    replies_posted: number
    likes_received: number
    help_score: number
  } | null
  forums: Forum[]
  threads: Thread[]
  events: CommunityEvent[]
  challenges: Challenge[]
}) {
  const { user } = useAuth()
  const [activeInsightTab, setActiveInsightTab] = useState("overview")
  
  // Calculate comprehensive user activity using REAL data
  const userShares = threads.filter(thread => 
    thread.author.id === user?.id || thread.author.name === user?.username
  )
  const joinedEvents = events.filter(event => event.is_participating)
  const joinedChallenges = challenges.filter(challenge => challenge.is_participating)
  const completedChallenges = challenges.filter(challenge => 
    challenge.is_participating && new Date(challenge.end_date) < new Date()
  )
  
  // Use REAL backend stats when available, with intelligent fallbacks
  const stats = {
    reputation: enhancedStats?.reputation || userReputation || 0,
    forums_joined: enhancedStats?.forums_joined || joinedForums.length,
    threads_liked: enhancedStats?.threads_liked || communityStats.threadsLiked || threads.filter(t => t.is_liked).length,
    threads_created: enhancedStats?.threads_created || userShares.length,
    replies_posted: enhancedStats?.replies_posted || communityStats.repliesPosted || 0,
    likes_received: enhancedStats?.likes_received || userShares.reduce((sum, thread) => sum + thread.like_count, 0),
    help_score: enhancedStats?.help_score || Math.min(10, (userReputation || 0) / 10)
  }

  // Intelligent Badge System with Real Activity Logic
  const calculateBadges = () => {
    const badges: Array<{ name: string; icon: string; description: string; tier: string }> = []
    const now = new Date()
    
    // Starter Badges - Easy to achieve
    if (stats.forums_joined >= 1) badges.push({ name: "First Steps", icon: "👶", description: "Joined your first forum", tier: "bronze" })
    if (stats.threads_liked >= 1) badges.push({ name: "Kind Heart", icon: "💝", description: "Liked your first post", tier: "bronze" })
    if (stats.threads_created >= 1) badges.push({ name: "Voice Found", icon: "🗣️", description: "Shared your first story", tier: "bronze" })
    if (stats.replies_posted >= 1) badges.push({ name: "Conversation Starter", icon: "💭", description: "Posted your first reply", tier: "bronze" })
    
    // Community Engagement Badges - Progressive
    if (stats.forums_joined >= 3) badges.push({ name: "Community Explorer", icon: "🗺️", description: "Joined 3+ forums", tier: "bronze" })
    if (stats.forums_joined >= 7) badges.push({ name: "Forum Navigator", icon: "🧭", description: "Joined 7+ forums", tier: "silver" })
    if (stats.forums_joined >= 15) badges.push({ name: "Community Ambassador", icon: "🌟", description: "Joined 15+ forums", tier: "gold" })
    
    // Support & Kindness Badges - Based on real likes given
    if (stats.threads_liked >= 5) badges.push({ name: "Supportive Soul", icon: "💙", description: "Liked 5+ posts", tier: "bronze" })
    if (stats.threads_liked >= 25) badges.push({ name: "Heart of Gold", icon: "💛", description: "Liked 25+ posts", tier: "silver" })
    if (stats.threads_liked >= 75) badges.push({ name: "Beacon of Support", icon: "✨", description: "Liked 75+ posts", tier: "gold" })
    if (stats.threads_liked >= 150) badges.push({ name: "Love Spreader", icon: "💖", description: "Liked 150+ posts", tier: "platinum" })
    
    // Content Creation Badges - Based on actual posts
    if (stats.threads_created >= 2) badges.push({ name: "Story Teller", icon: "📖", description: "Shared 2+ stories", tier: "bronze" })
    if (stats.threads_created >= 5) badges.push({ name: "Wisdom Sharer", icon: "🎭", description: "Shared 5+ stories", tier: "silver" })
    if (stats.threads_created >= 15) badges.push({ name: "Community Voice", icon: "📢", description: "Shared 15+ stories", tier: "gold" })
    if (stats.threads_created >= 30) badges.push({ name: "Thought Leader", icon: "🧠", description: "Shared 30+ stories", tier: "platinum" })
    
    // Conversation Badges - Based on real replies
    if (stats.replies_posted >= 3) badges.push({ name: "Conversationalist", icon: "💬", description: "Posted 3+ replies", tier: "bronze" })
    if (stats.replies_posted >= 10) badges.push({ name: "Discussion Leader", icon: "🎤", description: "Posted 10+ replies", tier: "silver" })
    if (stats.replies_posted >= 25) badges.push({ name: "Community Catalyst", icon: "⚡", description: "Posted 25+ replies", tier: "gold" })
    if (stats.replies_posted >= 50) badges.push({ name: "Master Communicator", icon: "🗨️", description: "Posted 50+ replies", tier: "platinum" })
    
    // Challenge & Event Badges - Real participation
    if (joinedChallenges.length >= 1) badges.push({ name: "Challenge Seeker", icon: "🎯", description: "Joined first challenge", tier: "bronze" })
    if (joinedChallenges.length >= 3) badges.push({ name: "Growth Minded", icon: "🌱", description: "Joined 3+ challenges", tier: "silver" })
    if (completedChallenges.length >= 1) badges.push({ name: "Challenge Conqueror", icon: "🏆", description: "Completed first challenge", tier: "gold" })
    if (completedChallenges.length >= 3) badges.push({ name: "Habit Master", icon: "👑", description: "Completed 3+ challenges", tier: "platinum" })
    
    if (joinedEvents.length >= 1) badges.push({ name: "Event Enthusiast", icon: "🎪", description: "Joined first event", tier: "bronze" })
    if (joinedEvents.length >= 3) badges.push({ name: "Community Connector", icon: "🤝", description: "Joined 3+ events", tier: "silver" })
    
    // Impact Badges - Based on likes received (real engagement)
    if (stats.likes_received >= 5) badges.push({ name: "Inspiring Voice", icon: "🌟", description: "Received 5+ likes", tier: "silver" })
    if (stats.likes_received >= 20) badges.push({ name: "Community Inspiration", icon: "💫", description: "Received 20+ likes", tier: "gold" })
    if (stats.likes_received >= 50) badges.push({ name: "Beacon of Hope", icon: "🕯️", description: "Received 50+ likes", tier: "platinum" })
    
    // Activity Level Badges - Combined real activity
    const totalActivity = stats.threads_created + stats.replies_posted + Math.floor(stats.threads_liked / 3)
    if (totalActivity >= 10) badges.push({ name: "Active Member", icon: "🔥", description: "High community activity", tier: "silver" })
    if (totalActivity >= 25) badges.push({ name: "Super Active", icon: "⚡", description: "Very high activity", tier: "gold" })
    if (totalActivity >= 50) badges.push({ name: "Community Powerhouse", icon: "💪", description: "Exceptional activity", tier: "platinum" })
    
    // Reputation-based Badges - Real reputation points
    if (stats.reputation >= 50) badges.push({ name: "Trusted Member", icon: "🛡️", description: "50+ reputation", tier: "silver" })
    if (stats.reputation >= 150) badges.push({ name: "Community Pillar", icon: "🏛️", description: "150+ reputation", tier: "gold" })
    if (stats.reputation >= 300) badges.push({ name: "Legend", icon: "👑", description: "300+ reputation", tier: "platinum" })
    
    // Help Score Badges - Calculated from real activity
    if (stats.help_score >= 3) badges.push({ name: "Helper", icon: "🤲", description: "Help score 3+", tier: "bronze" })
    if (stats.help_score >= 6) badges.push({ name: "Guardian Angel", icon: "😇", description: "Help score 6+", tier: "silver" })
    if (stats.help_score >= 8) badges.push({ name: "Community Saint", icon: "🕊️", description: "Help score 8+", tier: "gold" })
    if (stats.help_score >= 10) badges.push({ name: "Divine Helper", icon: "✨", description: "Perfect help score", tier: "platinum" })
    
    // Special Combination Badges - Require multiple activities
    if (stats.threads_created >= 3 && stats.replies_posted >= 5 && stats.threads_liked >= 10) {
      badges.push({ name: "Well Rounded", icon: "🎨", description: "Active in all areas", tier: "gold" })
    }
    if (stats.forums_joined >= 5 && totalActivity >= 20) {
      badges.push({ name: "Community Champion", icon: "🏅", description: "Broad engagement", tier: "platinum" })
    }
    
    return badges.sort((a, b) => {
      const tierOrder = { "platinum": 4, "gold": 3, "silver": 2, "bronze": 1 }
      return tierOrder[b.tier] - tierOrder[a.tier]
    })
  }

  const userBadges = calculateBadges()
  const joinedForumDetails = forums.filter(forum => joinedForums.includes(forum.id))
  
  // Calculate progress towards next badges with real targets
  const getNextBadgeProgress = () => {
    const progress: Array<{ badge: string; current: number; target: number; percentage: number }> = []
    
    // Support badges progress
    if (stats.threads_liked < 150) {
      const targets = [1, 5, 25, 75, 150]
      const nextTarget = targets.find(t => t > stats.threads_liked) || 150
      progress.push({
        badge: "Support Badge",
        current: stats.threads_liked,
        target: nextTarget,
        percentage: (stats.threads_liked / nextTarget) * 100
      })
    }
    
    // Content creation progress
    if (stats.threads_created < 30) {
      const targets = [1, 2, 5, 15, 30]
      const nextTarget = targets.find(t => t > stats.threads_created) || 30
      progress.push({
        badge: "Creator Badge",
        current: stats.threads_created,
        target: nextTarget,
        percentage: (stats.threads_created / nextTarget) * 100
      })
    }
    
    // Challenge completion progress
    if (completedChallenges.length < 3) {
      const nextTarget = completedChallenges.length < 1 ? 1 : 3
      progress.push({
        badge: "Challenge Badge",
        current: completedChallenges.length,
        target: nextTarget,
        percentage: (completedChallenges.length / nextTarget) * 100
      })
    }
    
    // Reputation progress
    if (stats.reputation < 300) {
      const targets = [50, 150, 300]
      const nextTarget = targets.find(t => t > stats.reputation) || 300
      progress.push({
        badge: "Reputation Badge",
        current: stats.reputation,
        target: nextTarget,
        percentage: (stats.reputation / nextTarget) * 100
      })
    }
    
    return progress.slice(0, 3)
  }

  const nextBadgeProgress = getNextBadgeProgress()

  return (
    <div className="space-y-6">
      {/* Activity Overview Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card className="hover:shadow-md transition-shadow">
          <CardContent className="p-4 text-center">
            <div className="w-12 h-12 mx-auto mb-2 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
              <Users size={20} className="text-white" />
            </div>
            <h4 className="font-medium text-sm">Community Reach</h4>
            <p className="text-2xl font-bold">{stats.forums_joined}</p>
            <p className="text-xs text-muted-foreground">Forums joined</p>
          </CardContent>
        </Card>
        
        <Card className="hover:shadow-md transition-shadow">
          <CardContent className="p-4 text-center">
            <div className="w-12 h-12 mx-auto mb-2 bg-gradient-to-br from-red-500 to-pink-600 rounded-full flex items-center justify-center">
              <Heart size={20} className="text-white" />
            </div>
            <h4 className="font-medium text-sm">Support Given</h4>
            <p className="text-2xl font-bold">{stats.threads_liked}</p>
            <p className="text-xs text-muted-foreground">Posts liked</p>
          </CardContent>
        </Card>
        
        <Card className="hover:shadow-md transition-shadow">
          <CardContent className="p-4 text-center">
            <div className="w-12 h-12 mx-auto mb-2 bg-gradient-to-br from-green-500 to-emerald-600 rounded-full flex items-center justify-center">
              <Target size={20} className="text-white" />
            </div>
            <h4 className="font-medium text-sm">Challenges</h4>
            <p className="text-2xl font-bold">{completedChallenges.length}/{joinedChallenges.length}</p>
            <p className="text-xs text-muted-foreground">Completed</p>
          </CardContent>
        </Card>
        
        <Card className="hover:shadow-md transition-shadow">
          <CardContent className="p-4 text-center">
            <div className="w-12 h-12 mx-auto mb-2 bg-gradient-to-br from-yellow-500 to-orange-600 rounded-full flex items-center justify-center">
              <Trophy size={20} className="text-white" />
            </div>
            <h4 className="font-medium text-sm">Badges Earned</h4>
            <p className="text-2xl font-bold">{userBadges.length}</p>
            <p className="text-xs text-muted-foreground">Achievements</p>
          </CardContent>
        </Card>
      </div>

      {/* Insights Tabs */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendUp className="text-primary" size={20} />
            Community Insights
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Tabs value={activeInsightTab} onValueChange={setActiveInsightTab}>
            <TabsList className="grid grid-cols-4 w-full mb-6">
              <TabsTrigger value="overview">Overview</TabsTrigger>
              <TabsTrigger value="badges">Badges</TabsTrigger>
              <TabsTrigger value="progress">Progress</TabsTrigger>
              <TabsTrigger value="impact">Impact</TabsTrigger>
            </TabsList>

            <TabsContent value="overview" className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Activity Summary */}
                <div className="space-y-4">
                  <h4 className="font-semibold flex items-center gap-2">
                    <Star className="text-yellow-500" size={16} />
                    Activity Summary
                  </h4>
                  <div className="space-y-3">
                    <div className="flex justify-between items-center p-3 bg-muted/30 rounded-lg">
                      <span className="text-sm font-medium">Stories Shared</span>
                      <Badge variant={stats.threads_created > 0 ? "default" : "secondary"}>
                        {stats.threads_created}
                      </Badge>
                    </div>
                    <div className="flex justify-between items-center p-3 bg-muted/30 rounded-lg">
                      <span className="text-sm font-medium">Replies Posted</span>
                      <Badge variant={stats.replies_posted > 0 ? "default" : "secondary"}>
                        {stats.replies_posted}
                      </Badge>
                    </div>
                    <div className="flex justify-between items-center p-3 bg-muted/30 rounded-lg">
                      <span className="text-sm font-medium">Events Joined</span>
                      <Badge variant={joinedEvents.length > 0 ? "default" : "secondary"}>
                        {joinedEvents.length}
                      </Badge>
                    </div>
                    <div className="flex justify-between items-center p-3 bg-muted/30 rounded-lg">
                      <span className="text-sm font-medium">Active Challenges</span>
                      <Badge variant={joinedChallenges.length > 0 ? "default" : "secondary"}>
                        {joinedChallenges.length}
                      </Badge>
                    </div>
                  </div>
                </div>

                {/* Community Standing */}
                <div className="space-y-4">
                  <h4 className="font-semibold flex items-center gap-2">
                    <Shield className="text-blue-500" size={16} />
                    Community Standing
                  </h4>
                  <div className="p-4 bg-gradient-to-br from-primary/10 to-primary/5 rounded-lg border">
                    <div className="text-center mb-4">
                      <div className="text-3xl font-bold text-primary">{stats.reputation}</div>
                      <div className="text-sm text-muted-foreground">Reputation Points</div>
                    </div>
                    <div className="space-y-2">
                      <div className="flex justify-between text-xs">
                        <span>Help Score</span>
                        <span className="font-medium">{stats.help_score}/10</span>
                      </div>
                      <div className="w-full bg-muted rounded-full h-2">
                        <div 
                          className="bg-gradient-to-r from-green-500 to-emerald-600 h-2 rounded-full transition-all duration-500"
                          style={{ width: `${(stats.help_score / 10) * 100}%` }}
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </TabsContent>

            <TabsContent value="badges" className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {userBadges.map((badge, index) => (
                  <motion.div
                    key={badge.name}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                  >
                    <Card className={`hover:shadow-lg transition-all duration-300 border-2 ${
                      badge.tier === 'platinum' ? 'border-purple-300 bg-gradient-to-br from-purple-50 to-indigo-50 dark:from-purple-900/20 dark:to-indigo-900/20' :
                      badge.tier === 'gold' ? 'border-yellow-300 bg-gradient-to-br from-yellow-50 to-orange-50 dark:from-yellow-900/20 dark:to-orange-900/20' :
                      badge.tier === 'silver' ? 'border-gray-300 bg-gradient-to-br from-gray-50 to-slate-50 dark:from-gray-900/20 dark:to-slate-900/20' :
                      'border-amber-300 bg-gradient-to-br from-amber-50 to-yellow-50 dark:from-amber-900/20 dark:to-yellow-900/20'
                    }`}>
                      <CardContent className="p-4 text-center">
                        <div className="text-3xl mb-2">{badge.icon}</div>
                        <h4 className="font-semibold text-sm mb-1">{badge.name}</h4>
                        <p className="text-xs text-muted-foreground mb-2">{badge.description}</p>
                        <Badge 
                          variant="outline" 
                          className={`text-xs ${
                            badge.tier === 'platinum' ? 'border-purple-400 text-purple-700 dark:text-purple-300' :
                            badge.tier === 'gold' ? 'border-yellow-400 text-yellow-700 dark:text-yellow-300' :
                            badge.tier === 'silver' ? 'border-gray-400 text-gray-700 dark:text-gray-300' :
                            'border-amber-400 text-amber-700 dark:text-amber-300'
                          }`}
                        >
                          {badge.tier.toUpperCase()}
                        </Badge>
                      </CardContent>
                    </Card>
                  </motion.div>
                ))}
                
                {userBadges.length === 0 && (
                  <div className="col-span-full text-center py-8">
                    <Trophy size={48} className="mx-auto mb-4 opacity-50 text-muted-foreground" />
                    <p className="text-muted-foreground mb-2">No badges earned yet</p>
                    <p className="text-sm text-muted-foreground">Start participating to earn your first badge!</p>
                  </div>
                )}
              </div>
            </TabsContent>

            <TabsContent value="progress" className="space-y-4">
              <div className="space-y-6">
                <h4 className="font-semibold">Next Badge Progress</h4>
                {nextBadgeProgress.map((progress, index) => (
                  <div key={index} className="p-4 bg-muted/30 rounded-lg">
                    <div className="flex justify-between items-center mb-2">
                      <span className="font-medium text-sm">{progress.badge}</span>
                      <span className="text-sm text-muted-foreground">
                        {progress.current}/{progress.target}
                      </span>
                    </div>
                    <div className="w-full bg-muted rounded-full h-3">
                      <div 
                        className="bg-gradient-to-r from-primary to-primary/80 h-3 rounded-full transition-all duration-500"
                        style={{ width: `${Math.min(progress.percentage, 100)}%` }}
                      />
                    </div>
                    <p className="text-xs text-muted-foreground mt-1">
                      {Math.round(progress.percentage)}% complete
                    </p>
                  </div>
                ))}
                
                {nextBadgeProgress.length === 0 && (
                  <div className="text-center py-8">
                    <Star size={48} className="mx-auto mb-4 opacity-50 text-muted-foreground" />
                    <p className="text-muted-foreground mb-2">All available badges earned!</p>
                    <p className="text-sm text-muted-foreground">You're a true community champion! 🏆</p>
                  </div>
                )}
              </div>
            </TabsContent>

            <TabsContent value="impact" className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Community Impact - Real Data */}
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Community Impact</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="text-center p-4 bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 rounded-lg">
                      <div className="text-2xl font-bold text-green-600 dark:text-green-400">
                        {Math.max(stats.likes_received + stats.threads_created * 2 + stats.replies_posted, 0)}
                      </div>
                      <div className="text-sm text-muted-foreground">Estimated Reach</div>
                      <p className="text-xs text-muted-foreground mt-1">
                        Based on your real activity
                      </p>
                    </div>
                    
                    <div className="space-y-3">
                      <div className="flex justify-between">
                        <span className="text-sm">Likes on Your Posts</span>
                        <span className="font-medium">{stats.likes_received}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm">Stories Shared</span>
                        <span className="font-medium">{stats.threads_created}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm">Support Given</span>
                        <span className="font-medium">{stats.threads_liked}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm">Replies Posted</span>
                        <span className="font-medium">{stats.replies_posted}</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Personal Growth */}
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Personal Growth</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="text-center p-4 bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-lg">
                      <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                        {Math.round((completedChallenges.length / Math.max(joinedChallenges.length, 1)) * 100)}%
                      </div>
                      <div className="text-sm text-muted-foreground">Challenge Success Rate</div>
                    </div>
                    
                    <div className="space-y-3">
                      <div className="flex justify-between">
                        <span className="text-sm">Challenges Completed</span>
                        <span className="font-medium">{completedChallenges.length}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm">Active Challenges</span>
                        <span className="font-medium">{joinedChallenges.length - completedChallenges.length}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm">Events Attended</span>
                        <span className="font-medium">{joinedEvents.length}</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      {/* Recent Activity Feed */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Share className="text-green-500" size={20} />
            Recent Activity
          </CardTitle>
        </CardHeader>
        <CardContent>
          {userShares.length > 0 || joinedEvents.length > 0 || joinedChallenges.length > 0 ? (
            <div className="space-y-4">
              {/* Recent shares */}
              {userShares.slice(0, 2).map((share) => (
                <div key={share.id} className="p-4 rounded-lg border hover:shadow-sm transition-shadow">
                  <div className="flex items-start justify-between mb-2">
                    <h4 className="font-medium text-sm">{share.title}</h4>
                    <span className="text-xs text-muted-foreground">{formatRelativeTime(share.created_at)}</span>
                  </div>
                  <p className="text-sm text-muted-foreground mb-3 line-clamp-2">{share.content}</p>
                  <div className="flex items-center gap-4 text-xs">
                    <span className="flex items-center gap-1">
                      <Heart size={12} className="text-red-500" />
                      {share.like_count}
                    </span>
                    <span className="flex items-center gap-1">
                      <ChatCircle size={12} className="text-blue-500" />
                      {share.reply_count}
                    </span>
                    <Badge variant="outline" className="text-xs">{share.category}</Badge>
                  </div>
                </div>
              ))}
              
              {/* Recent events */}
              {joinedEvents.slice(0, 1).map((event) => (
                <div key={event.id} className="p-4 rounded-lg border bg-blue-50/50 dark:bg-blue-900/10">
                  <div className="flex items-center gap-2 mb-2">
                    <Calendar size={16} className="text-blue-500" />
                    <span className="font-medium text-sm">Joined Event</span>
                  </div>
                  <h4 className="font-medium text-sm mb-1">{event.title}</h4>
                  <p className="text-xs text-muted-foreground">
                    {new Date(event.start_time).toLocaleDateString()}
                  </p>
                </div>
              ))}
              
              {/* Recent challenges */}
              {joinedChallenges.slice(0, 1).map((challenge) => (
                <div key={challenge.id} className="p-4 rounded-lg border bg-green-50/50 dark:bg-green-900/10">
                  <div className="flex items-center gap-2 mb-2">
                    <Target size={16} className="text-green-500" />
                    <span className="font-medium text-sm">Joined Challenge</span>
                  </div>
                  <h4 className="font-medium text-sm mb-1">{challenge.title}</h4>
                  <p className="text-xs text-muted-foreground">
                    {challenge.duration_days} days • {challenge.category}
                  </p>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center text-muted-foreground py-8">
              <Share size={48} className="mx-auto mb-4 opacity-50" />
              <p className="mb-2">No recent activity</p>
              <p className="text-sm">Start participating to see your activity here</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )

  // Helper function for relative time
  function formatRelativeTime(dateString: string): string {
    const now = new Date()
    const date = new Date(dateString)
    const diffInMs = now.getTime() - date.getTime()
    const diffInSeconds = Math.floor(diffInMs / 1000)
    const diffInMinutes = Math.floor(diffInSeconds / 60)
    const diffInHours = Math.floor(diffInMinutes / 60)
    const diffInDays = Math.floor(diffInHours / 24)

    if (diffInSeconds < 60) {
      return diffInSeconds <= 1 ? 'now' : `${diffInSeconds}s`
    } else if (diffInMinutes < 60) {
      return `${diffInMinutes}m`
    } else if (diffInHours < 24) {
      return `${diffInHours}h`
    } else {
      return `${diffInDays}d`
    }
  }
}

function CreateEventForm({ 
  onSubmit 
}: { 
  onSubmit: (data: any) => Promise<any>
}) {
  const [title, setTitle] = useState("")
  const [description, setDescription] = useState("")
  const [startDate, setStartDate] = useState("")
  const [startTime, setStartTime] = useState("")
  const [endDate, setEndDate] = useState("")
  const [endTime, setEndTime] = useState("")
  const [location, setLocation] = useState("")
  const [isVirtual, setIsVirtual] = useState(true)
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!title.trim() || !description.trim() || !startDate || !startTime) {
      toast.error('Please fill in all required fields')
      return
    }

    const startDateTime = new Date(`${startDate}T${startTime}`).toISOString()
    const endDateTime = endDate && endTime 
      ? new Date(`${endDate}T${endTime}`).toISOString()
      : new Date(new Date(`${startDate}T${startTime}`).getTime() + 2 * 60 * 60 * 1000).toISOString() // Default 2 hours

    setIsLoading(true)
    try {
      await onSubmit({
        title: title.trim(),
        description: description.trim(),
        start_time: startDateTime,
        end_time: endDateTime,
        location: isVirtual ? null : location.trim(),
        is_virtual: isVirtual
      })
      
      // Reset form
      setTitle("")
      setDescription("")
      setStartDate("")
      setStartTime("")
      setEndDate("")
      setEndTime("")
      setLocation("")
      setIsVirtual(true)
    } catch (error) {
      // Error is handled in the parent component
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="text-sm font-medium">Event Title *</label>
        <Input
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="e.g., Weekly Meditation Circle"
          required
        />
      </div>
      
      <div>
        <label className="text-sm font-medium">Description *</label>
        <Textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Describe what the event is about..."
          rows={3}
          required
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="text-sm font-medium">Start Date *</label>
          <Input
            type="date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            min={new Date().toISOString().split('T')[0]}
            required
          />
        </div>
        <div>
          <label className="text-sm font-medium">Start Time *</label>
          <Input
            type="time"
            value={startTime}
            onChange={(e) => setStartTime(e.target.value)}
            required
          />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="text-sm font-medium">End Date (optional)</label>
          <Input
            type="date"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
            min={startDate || new Date().toISOString().split('T')[0]}
          />
        </div>
        <div>
          <label className="text-sm font-medium">End Time (optional)</label>
          <Input
            type="time"
            value={endTime}
            onChange={(e) => setEndTime(e.target.value)}
          />
        </div>
      </div>

      <div className="space-y-3">
        <div className="flex items-center space-x-2">
          <input
            type="checkbox"
            id="isVirtual"
            checked={isVirtual}
            onChange={(e) => setIsVirtual(e.target.checked)}
            className="rounded"
          />
          <label htmlFor="isVirtual" className="text-sm font-medium">
            Virtual Event
          </label>
        </div>

        {!isVirtual && (
          <div>
            <label className="text-sm font-medium">Location</label>
            <Input
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              placeholder="Enter event location"
            />
          </div>
        )}
      </div>
      
      <div className="flex justify-end gap-2 pt-4">
        <Button type="button" variant="outline" disabled={isLoading}>
          Cancel
        </Button>
        <Button type="submit" disabled={isLoading}>
          {isLoading ? 'Creating...' : 'Create Event'}
        </Button>
      </div>
    </form>
  )
}

function CreateChallengeForm({ 
  onSubmit 
}: { 
  onSubmit: (data: any) => Promise<any>
}) {
  const [title, setTitle] = useState("")
  const [description, setDescription] = useState("")
  const [category, setCategory] = useState("")
  const [durationDays, setDurationDays] = useState(7)
  const [isLoading, setIsLoading] = useState(false)

  const categories = [
    'mindfulness',
    'fitness', 
    'nutrition',
    'sleep',
    'mental-health',
    'social',
    'habits'
  ]

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!title.trim() || !description.trim() || !category) {
      toast.error('Please fill in all required fields')
      return
    }

    const startDate = new Date().toISOString()
    const endDate = new Date(Date.now() + durationDays * 24 * 60 * 60 * 1000).toISOString()

    setIsLoading(true)
    try {
      await onSubmit({
        title: title.trim(),
        description: description.trim(),
        category,
        duration_days: durationDays,
        start_date: startDate,
        end_date: endDate
      })
      
      // Reset form
      setTitle("")
      setDescription("")
      setCategory("")
      setDurationDays(7)
    } catch (error) {
      // Error is handled in the parent component
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="text-sm font-medium">Challenge Title *</label>
        <Input
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="e.g., 7-Day Gratitude Challenge"
          required
        />
      </div>
      
      <div>
        <label className="text-sm font-medium">Description *</label>
        <Textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Describe the challenge goals and activities..."
          rows={4}
          required
        />
      </div>

      <div>
        <label className="text-sm font-medium">Category *</label>
        <Select value={category} onValueChange={setCategory} required>
          <SelectTrigger>
            <SelectValue placeholder="Select a category" />
          </SelectTrigger>
          <SelectContent>
            {categories.map((cat) => (
              <SelectItem key={cat} value={cat}>
                {cat.charAt(0).toUpperCase() + cat.slice(1).replace('-', ' ')}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div>
        <label className="text-sm font-medium">Duration (days) *</label>
        <Select 
          value={durationDays.toString()} 
          onValueChange={(value) => setDurationDays(parseInt(value))}
        >
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="3">3 days</SelectItem>
            <SelectItem value="7">7 days</SelectItem>
            <SelectItem value="14">14 days</SelectItem>
            <SelectItem value="21">21 days</SelectItem>
            <SelectItem value="30">30 days</SelectItem>
          </SelectContent>
        </Select>
      </div>
      
      <div className="flex justify-end gap-2 pt-4">
        <Button type="button" variant="outline" disabled={isLoading}>
          Cancel
        </Button>
        <Button type="submit" disabled={isLoading}>
          {isLoading ? 'Creating...' : 'Create Challenge'}
        </Button>
      </div>
    </form>
  )
}

export default EnhancedCommunitySection