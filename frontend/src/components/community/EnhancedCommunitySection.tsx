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
  Shield
} from "@phosphor-icons/react"
import { motion, AnimatePresence } from "framer-motion"
import { toast } from "sonner"
import { communityApi } from "@/services/api"
import { useCommunityData } from "@/hooks/useCommunityData"
import { formatRelativeTime as formatTime } from "@/utils/timeFormat"
import { useAuth } from "@/hooks/useAuth"
import { MoodPatternSharing } from "../mood/MoodPatternSharing"
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
    try {
      await communityApi.joinEvent(eventId)
      toast.success('Successfully joined event!')
      await loadEvents() // Refresh events list
    } catch (error) {
      console.error('Failed to join event:', error)
      toast.error('Failed to join event')
    }
  }

  const handleLeaveEvent = async (eventId: string) => {
    try {
      await communityApi.leaveEvent(eventId)
      toast.success('Successfully left event')
      await loadEvents() // Refresh events list
    } catch (error) {
      console.error('Failed to leave event:', error)
      toast.error('Failed to leave event')
    }
  }

  const handleJoinChallenge = async (challengeId: string) => {
    try {
      await communityApi.joinChallenge(challengeId)
      toast.success('Successfully joined challenge!')
      await loadChallenges() // Refresh challenges list
    } catch (error) {
      console.error('Failed to join challenge:', error)
      toast.error('Failed to join challenge')
    }
  }

  const handleLeaveChallenge = async (challengeId: string) => {
    try {
      await communityApi.leaveChallenge(challengeId)
      toast.success('Successfully left challenge')
      await loadChallenges() // Refresh challenges list
    } catch (error) {
      console.error('Failed to leave challenge:', error)
      toast.error('Failed to leave challenge')
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
        end_date: challengeData.end_date!
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

  const handleReplyToThread = async (threadId: string, content: string, parentId?: string) => {
    if (!isAuthenticated) {
      toast.error('Please log in to reply to discussions')
      return
    }
    
    try {
      await replyToThreadAction(threadId, content, parentId)
      
      toast.success('Reply posted!')
      setShowThreadDialog(false)
      
      // Refresh threads to get latest data
      if (selectedForum) {
        loadThreads(selectedForum.id)
      }
    } catch (error) {
      console.error('Failed to post reply:', error)
      toast.error('Failed to post reply')
    }
  }

  const getCategoryColor = (category: string) => {
    switch (category.toLowerCase()) {
      case 'achievements': return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
      case 'support': return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
      case 'anxiety': return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
      case 'depression': return 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200'
      case 'general': return 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200'
      case 'wellness': return 'bg-pink-100 text-pink-800 dark:bg-pink-900 dark:text-pink-200'
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
                Welcome, {user.username}!
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
                                  {thread.author.name[0]}
                                </span>
                              </Avatar>
                              
                              <div className="flex-1 space-y-2">
                                <div className="flex items-center gap-2 flex-wrap">
                                  <span className="font-medium">{thread.author.name}</span>
                                  {thread.author.badges?.map((badge) => (
                                    <Badge key={badge} variant="secondary" className="text-xs">
                                      {getBadgeIcon(badge)} {badge}
                                    </Badge>
                                  ))}
                                  <Badge className={getCategoryColor(thread.category)}>
                                    {thread.category}
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
                  <EventCard 
                    key={event.id} 
                    event={event}
                    onJoin={() => handleJoinEvent(event.id)}
                    onLeave={() => handleLeaveEvent(event.id)}
                  />
                ))}
              </div>
            </TabsContent>

            <TabsContent value="challenges" className="space-y-4">
              <div className="flex items-center justify-between mb-6">
                <h3 className="font-semibold text-lg">Wellness Challenges</h3>
                <Dialog>
                  <DialogTrigger asChild>
                    <Button size="sm" className="flex items-center gap-2">
                      <Plus size={16} />
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
                    <CreateChallengeForm onSubmit={handleCreateChallenge} />
                  </DialogContent>
                </Dialog>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {challenges.map((challenge) => (
                  <ChallengeCard 
                    key={challenge.id} 
                    challenge={challenge}
                    onJoin={() => handleJoinChallenge(challenge.id)}
                    onLeave={() => handleLeaveChallenge(challenge.id)}
                  />
                ))}
              </div>
            </TabsContent>

            <TabsContent value="my-activity" className="space-y-4">
              <MyActivitySection 
                joinedForums={joinedForums}
                userReputation={userReputation}
                communityStats={communityStats}
                enhancedStats={enhancedStats}
                forums={forums}
                threads={threads}
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
  isAuthenticated
}: { 
  thread: Thread
  onReply: (content: string, parentId?: string) => void 
  isAuthenticated: boolean
}) {
  const [replyContent, setReplyContent] = useState("")
  const [replies, setReplies] = useState<Reply[]>([])
  const [loadingReplies, setLoadingReplies] = useState(false)
  const [replyingTo, setReplyingTo] = useState<{id: string, name: string} | null>(null)

  // Load replies when component mounts or thread changes
  useEffect(() => {
    if (!isAuthenticated) {
      return // Don't load replies if not authenticated
    }
    
    const loadReplies = async () => {
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

    loadReplies()
  }, [thread.id, isAuthenticated])

  // Handle liking a reply
  const handleLikeReply = async (replyId: string) => {
    try {
      const response = await communityApi.likeContent('reply', replyId)
      
      // Update the reply in local state
      setReplies(prevReplies => 
        prevReplies.map(reply => 
          reply.id === replyId 
            ? { 
                ...reply, 
                is_liked: response.liked,
                like_count: response.like_count
              }
            : reply
        )
      )
    } catch (error) {
      console.error('Failed to like reply:', error)
      toast.error('Failed to update like')
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
              {reply.author.name.charAt(0).toUpperCase()}
            </span>
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 text-xs text-muted-foreground mb-1">
              <span className="font-medium text-foreground">{reply.author.name}</span>
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
                  onClick={() => handleReplyToReply(reply.id, reply.author.name)}
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
        <p className="text-sm text-muted-foreground">by {thread.author.name} in {thread.forum_name}</p>
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

function MyActivitySection({ 
  joinedForums, 
  userReputation,
  communityStats,
  enhancedStats,
  forums,
  threads
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
}) {
  // Calculate user's shares (threads they've created)
  const userShares = threads.filter(thread => thread.author.id === 'current_user') // This would be the actual user ID
  
  // Use enhanced stats if available, otherwise calculate locally
  const stats = enhancedStats || {
    reputation: userReputation,
    forums_joined: joinedForums.length,
    threads_liked: communityStats.threadsLiked,
    threads_created: userShares.length,
    replies_posted: communityStats.repliesPosted,
    likes_received: 0,
    help_score: Math.min(10, userReputation / 10)
  }
  
  // Calculate enhanced reputation based on activity
  const enhancedReputation = {
    base: stats.reputation,
    fromLikes: stats.threads_liked * 2,
    fromShares: stats.threads_created * 5,
    fromReplies: stats.replies_posted * 3,
    fromReceived: stats.likes_received * 2,
    total: stats.reputation
  }

  // Get joined forum details
  const joinedForumDetails = forums.filter(forum => joinedForums.includes(forum.id))

  return (
    <div className="space-y-6">
      {/* Enhanced Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4 text-center">
            <Users size={24} className="mx-auto mb-2 text-primary" />
            <h4 className="font-medium">Forums Joined</h4>
            <p className="text-2xl font-bold">{stats.forums_joined}</p>
            <p className="text-xs text-muted-foreground">
              {joinedForumDetails.length > 0 ? 'Active member' : 'Join forums to connect'}
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4 text-center">
            <Heart size={24} className="mx-auto mb-2 text-red-500" />
            <h4 className="font-medium">Posts Liked</h4>
            <p className="text-2xl font-bold">{stats.threads_liked}</p>
            <p className="text-xs text-muted-foreground">
              +{stats.threads_liked * 2} reputation
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4 text-center">
            <Share size={24} className="mx-auto mb-2 text-blue-500" />
            <h4 className="font-medium">My Shares</h4>
            <p className="text-2xl font-bold">{stats.threads_created}</p>
            <p className="text-xs text-muted-foreground">
              {stats.threads_created > 0 ? 'Helping others' : 'Share your journey'}
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4 text-center">
            <Star size={24} className="mx-auto mb-2 text-yellow-500" />
            <h4 className="font-medium">Reputation</h4>
            <p className="text-2xl font-bold">{enhancedReputation.total}</p>
            <p className="text-xs text-muted-foreground">
              Community helper
            </p>
          </CardContent>
        </Card>
      </div>

      {/* My Impact Section */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Trophy className="text-yellow-500" size={20} />
              My Impact
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm">Support Given</span>
                <Badge variant="secondary">{stats.threads_liked} likes</Badge>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm">Stories Shared</span>
                <Badge variant={stats.threads_created > 0 ? "default" : "secondary"}>
                  {stats.threads_created} posts
                </Badge>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm">Community Replies</span>
                <Badge variant={stats.replies_posted > 0 ? "default" : "secondary"}>
                  {stats.replies_posted} replies
                </Badge>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm">Likes Received</span>
                <Badge variant={stats.likes_received > 0 ? "default" : "secondary"}>
                  {stats.likes_received} hearts
                </Badge>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm">Help Score</span>
                <Badge variant="outline" className="font-bold">
                  {stats.help_score}/10
                </Badge>
              </div>
            </div>
            
            {enhancedReputation.total > 50 && (
              <div className="bg-gradient-to-r from-yellow-50 to-orange-50 dark:from-yellow-900/20 dark:to-orange-900/20 p-3 rounded-lg border">
                <div className="flex items-center gap-2">
                  <Star className="text-yellow-500" size={16} />
                  <span className="text-sm font-medium">
                    {stats.help_score >= 7 ? 'Community Champion' : 
                     stats.help_score >= 5 ? 'Community Helper' : 
                     'Community Member'}
                  </span>
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  You're making a positive impact in the community! 🌟
                </p>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <ChatCircle className="text-blue-500" size={20} />
              Joined Forums
            </CardTitle>
          </CardHeader>
          <CardContent>
            {joinedForumDetails.length > 0 ? (
              <div className="space-y-3">
                {joinedForumDetails.slice(0, 5).map((forum) => (
                  <div key={forum.id} className="flex items-center justify-between p-3 rounded-lg border">
                    <div>
                      <h4 className="font-medium text-sm">{forum.name}</h4>
                      <p className="text-xs text-muted-foreground">{forum.member_count} members</p>
                    </div>
                    <Badge variant="outline" className="text-xs">
                      {forum.category}
                    </Badge>
                  </div>
                ))}
                {joinedForumDetails.length > 5 && (
                  <p className="text-xs text-muted-foreground text-center">
                    +{joinedForumDetails.length - 5} more forums
                  </p>
                )}
              </div>
            ) : (
              <div className="text-center text-muted-foreground py-6">
                <Users size={32} className="mx-auto mb-3 opacity-50" />
                <p className="text-sm">Join forums to connect with others</p>
                <p className="text-xs">Share experiences and get support</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity / My Shares */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Share className="text-green-500" size={20} />
            My Recent Shares
          </CardTitle>
        </CardHeader>
        <CardContent>
          {userShares.length > 0 ? (
            <div className="space-y-4">
              {userShares.slice(0, 3).map((share) => (
                <div key={share.id} className="p-4 rounded-lg border">
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
              {userShares.length > 3 && (
                <p className="text-xs text-muted-foreground text-center">
                  +{userShares.length - 3} more shares
                </p>
              )}
            </div>
          ) : (
            <div className="text-center text-muted-foreground py-8">
              <Share size={48} className="mx-auto mb-4 opacity-50" />
              <p className="mb-2">No shared stories yet</p>
              <p className="text-sm">Share your wellness journey to inspire others</p>
              <Button variant="outline" size="sm" className="mt-4">
                <Plus size={16} className="mr-2" />
                Share Your Story
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )

  // Helper function for relative time (should be moved to utils)
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

// Mock data for fallback
const mockForums: Forum[] = [
  {
    id: 'forum_1',
    name: 'General Support',
    description: 'Share experiences and support each other through daily challenges',
    category: 'support',
    member_count: 1247,
    thread_count: 89,
    is_member: false,  // Changed from false to ensure consistency
    created_at: new Date().toISOString(),
    tags: ['support', 'general', 'community']
  },
  {
    id: 'forum_2',
    name: 'Anxiety & Stress',
    description: 'Discussing anxiety management and stress relief techniques',
    category: 'anxiety',
    member_count: 823,
    thread_count: 156,
    is_member: false,  // Changed from true to false for new users
    created_at: new Date().toISOString(),
    tags: ['anxiety', 'stress', 'coping']
  },
  {
    id: 'forum_3',
    name: 'Achievements & Milestones',
    description: 'Celebrate your progress and inspire others with your journey',
    category: 'achievements',
    member_count: 567,
    thread_count: 234,
    is_member: false,
    created_at: new Date().toISOString(),
    tags: ['achievements', 'progress', 'celebration']
  }
]