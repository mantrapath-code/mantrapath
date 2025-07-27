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
  MessageCircle, 
  Trophy, 
  Plus, 
  Search,
  Calendar,
  Star,
  Flag,
  Share,
  Bookmark,
  MoreHorizontal,
  Shield
} from "@phosphor-icons/react"
import { motion, AnimatePresence } from "framer-motion"
import { toast } from "sonner"
import { communityApi } from "@/services/api"
import { useKV } from '@github/spark/hooks'

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
  const [activeTab, setActiveTab] = useState("forums")
  const [forums, setForums] = useState<Forum[]>([])
  const [threads, setThreads] = useState<Thread[]>([])
  const [events, setEvents] = useState<CommunityEvent[]>([])
  const [challenges, setChallenges] = useState<Challenge[]>([])
  const [selectedForum, setSelectedForum] = useState<Forum | null>(null)
  const [selectedThread, setSelectedThread] = useState<Thread | null>(null)
  const [replies, setReplies] = useState<Reply[]>([])
  const [searchQuery, setSearchQuery] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [showCreateDialog, setShowCreateDialog] = useState(false)
  const [showThreadDialog, setShowThreadDialog] = useState(false)
  
  // Persistent state for user's community activity
  const [joinedForums, setJoinedForums] = useKV("joined-forums", [] as string[])
  const [likedThreads, setLikedThreads] = useKV("liked-threads", [] as string[])
  const [bookmarkedThreads, setBookmarkedThreads] = useKV("bookmarked-threads", [] as string[])
  const [userReputation, setUserReputation] = useKV("user-reputation", 0)

  // Load initial data
  useEffect(() => {
    loadForums()
    loadEvents()
    loadChallenges()
  }, [])

  // Load threads when forum is selected
  useEffect(() => {
    if (selectedForum) {
      loadForumThreads(selectedForum.id)
    }
  }, [selectedForum])

  const loadForums = async () => {
    try {
      setIsLoading(true)
      const forumsData = await communityApi.getForums()
      setForums(forumsData || [])
    } catch (error) {
      console.error('Failed to load forums:', error)
      toast.error('Failed to load forums')
      // Use mock data as fallback
      setForums(mockForums)
    } finally {
      setIsLoading(false)
    }
  }

  const loadForumThreads = async (forumId: string) => {
    try {
      const threadsData = await communityApi.getForumThreads(forumId)
      setThreads(threadsData || [])
    } catch (error) {
      console.error('Failed to load threads:', error)
      toast.error('Failed to load threads')
      // Use mock data as fallback
      setThreads(mockThreads)
    }
  }

  const loadEvents = async () => {
    try {
      const eventsData = await communityApi.getEvents()
      setEvents(eventsData || mockEvents)
    } catch (error) {
      console.error('Failed to load events:', error)
      toast.error('Failed to load events')
      setEvents(mockEvents)
    }
  }

  const loadChallenges = async () => {
    try {
      const challengesData = await communityApi.getChallenges()
      setChallenges(challengesData || mockChallenges)
    } catch (error) {
      console.error('Failed to load challenges:', error)
      toast.error('Failed to load challenges')
      setChallenges(mockChallenges)
    }
  }

  const handleJoinEvent = async (eventId: string) => {
    try {
      await communityApi.joinEvent(eventId)
      setEvents(current => current.map(event => 
        event.id === eventId 
          ? { ...event, is_participating: true, participant_count: event.participant_count + 1 }
          : event
      ))
      toast.success('Successfully joined event!')
    } catch (error) {
      console.error('Failed to join event:', error)
      toast.error('Failed to join event')
    }
  }

  const handleLeaveEvent = async (eventId: string) => {
    try {
      await communityApi.leaveEvent(eventId)
      setEvents(current => current.map(event => 
        event.id === eventId 
          ? { ...event, is_participating: false, participant_count: Math.max(0, event.participant_count - 1) }
          : event
      ))
      toast.success('Left event successfully')
    } catch (error) {
      console.error('Failed to leave event:', error)
      toast.error('Failed to leave event')
    }
  }

  const handleJoinChallenge = async (challengeId: string) => {
    try {
      await communityApi.joinChallenge(challengeId)
      setChallenges(current => current.map(challenge => 
        challenge.id === challengeId 
          ? { ...challenge, is_participating: true, participant_count: challenge.participant_count + 1 }
          : challenge
      ))
      toast.success('Successfully joined challenge!')
    } catch (error) {
      console.error('Failed to join challenge:', error)
      toast.error('Failed to join challenge')
    }
  }

  const handleLeaveChallenge = async (challengeId: string) => {
    try {
      await communityApi.leaveChallenge(challengeId)
      setChallenges(current => current.map(challenge => 
        challenge.id === challengeId 
          ? { ...challenge, is_participating: false, participant_count: Math.max(0, challenge.participant_count - 1) }
          : challenge
      ))
      toast.success('Left challenge successfully')
    } catch (error) {
      console.error('Failed to leave challenge:', error)
      toast.error('Failed to leave challenge')
    }
  }

  const handleCreateEvent = async (eventData: Partial<CommunityEvent>) => {
    try {
      const newEvent = await communityApi.createEvent(eventData)
      setEvents(current => [newEvent, ...current])
      toast.success('Event created successfully!')
      return newEvent
    } catch (error) {
      console.error('Failed to create event:', error)
      toast.error('Failed to create event')
      throw error
    }
  }

  const handleCreateChallenge = async (challengeData: Partial<Challenge>) => {
    try {
      const newChallenge = await communityApi.createChallenge(challengeData)
      setChallenges(current => [newChallenge, ...current])
      toast.success('Challenge created successfully!')
      return newChallenge
    } catch (error) {
      console.error('Failed to create challenge:', error)
      toast.error('Failed to create challenge')
      throw error
    }
  }

  const handleJoinForum = async (forumId: string) => {
    try {
      await communityApi.joinForum(forumId)
      setJoinedForums(current => [...current, forumId])
      toast.success('Successfully joined forum!')
      loadForums() // Refresh to update member count
    } catch (error) {
      console.error('Failed to join forum:', error)
      toast.error('Failed to join forum')
    }
  }

  const handleLeaveForum = async (forumId: string) => {
    try {
      await communityApi.leaveForum(forumId)
      setJoinedForums(current => current.filter(id => id !== forumId))
      toast.success('Left forum successfully')
      loadForums() // Refresh to update member count
    } catch (error) {
      console.error('Failed to leave forum:', error)
      toast.error('Failed to leave forum')
    }
  }

  const handleLikeThread = async (threadId: string, contentType: string = 'thread') => {
    try {
      const isLiked = likedThreads.includes(threadId)
      
      if (isLiked) {
        await communityApi.removeLike(contentType, threadId)
        setLikedThreads(current => current.filter(id => id !== threadId))
        toast.success('Like removed')
      } else {
        await communityApi.likeContent({ content_type: contentType, content_id: threadId })
        setLikedThreads(current => [...current, threadId])
        toast.success('Thread liked!')
      }
      
      // Refresh threads to update like count
      if (selectedForum) {
        loadForumThreads(selectedForum.id)
      }
    } catch (error) {
      console.error('Failed to update like:', error)
      toast.error('Failed to update like')
    }
  }

  const handleCreateThread = async (data: { title: string; content: string; forumId: string; tags: string[] }) => {
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

  const handleReplyToThread = async (threadId: string, content: string) => {
    try {
      await communityApi.replyToThread(threadId, { content })
      toast.success('Reply posted!')
      // Refresh thread details or replies
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
          <CardTitle className="flex items-center gap-2">
            <Users className="text-primary" size={24} />
            Community Hub
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsList className="grid grid-cols-4 w-full mb-6">
              <TabsTrigger value="forums">Forums</TabsTrigger>
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
                <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
                  <DialogTrigger asChild>
                    <Button className="flex items-center gap-2">
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

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Forums List */}
                <div className="space-y-4">
                  <h3 className="font-semibold text-lg">Community Forums</h3>
                  <ScrollArea className="h-[500px]">
                    <div className="space-y-3">
                      {forums.map((forum) => (
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
                                  <MessageCircle size={12} />
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
                              {joinedForums.includes(forum.id) ? (
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
                      ))}
                    </div>
                  </ScrollArea>
                </div>

                {/* Threads List */}
                <div className="space-y-4">
                  <h3 className="font-semibold text-lg">
                    {selectedForum ? `${selectedForum.name} Discussions` : 'Select a Forum'}
                  </h3>
                  {selectedForum ? (
                    <ScrollArea className="h-[500px]">
                      <div className="space-y-3">
                        {threads.map((thread) => (
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
                                        likedThreads.includes(thread.id) ? 'text-red-500' : ''
                                      }`}
                                    >
                                      <Heart size={14} />
                                      {thread.like_count}
                                    </button>
                                    <span className="flex items-center gap-1">
                                      <MessageCircle size={14} />
                                      {thread.reply_count}
                                    </span>
                                    <span>{new Date(thread.created_at).toLocaleDateString()}</span>
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
                                      <MessageCircle size={14} />
                                      Reply
                                    </Button>
                                  </div>
                                </div>
                              </div>
                            </div>
                          </motion.div>
                        ))}
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
                likedThreads={likedThreads}
                userReputation={userReputation}
              />
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      {/* Thread Detail Dialog */}
      <Dialog open={showThreadDialog} onOpenChange={setShowThreadDialog}>
        <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
          {selectedThread && (
            <ThreadDetailView 
              thread={selectedThread} 
              onReply={(content) => handleReplyToThread(selectedThread.id, content)}
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
            <MessageCircle size={16} className="text-blue-500" />
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
  onReply 
}: { 
  thread: Thread
  onReply: (content: string) => void 
}) {
  const [replyContent, setReplyContent] = useState("")

  const handleSubmitReply = () => {
    if (!replyContent.trim()) {
      toast.error('Please enter a reply')
      return
    }
    
    onReply(replyContent.trim())
    setReplyContent("")
  }

  return (
    <div className="space-y-6">
      <DialogHeader>
        <DialogTitle className="text-left">{thread.title}</DialogTitle>
        <DialogDescription className="text-left">
          by {thread.author.name} in {thread.forum_name}
        </DialogDescription>
      </DialogHeader>
      
      <div className="space-y-4">
        <div className="p-4 bg-muted/50 rounded-lg">
          <p className="text-sm">{thread.content}</p>
        </div>
        
        <div className="flex items-center gap-4 text-sm text-muted-foreground">
          <span className="flex items-center gap-1">
            <Heart size={14} />
            {thread.like_count} likes
          </span>
          <span className="flex items-center gap-1">
            <MessageCircle size={14} />
            {thread.reply_count} replies
          </span>
          <span>{new Date(thread.created_at).toLocaleDateString()}</span>
        </div>
        
        <div className="space-y-4">
          <h4 className="font-medium">Add a reply</h4>
          <Textarea
            value={replyContent}
            onChange={(e) => setReplyContent(e.target.value)}
            placeholder="Share your thoughts or support..."
            rows={4}
          />
          <div className="flex justify-end">
            <Button onClick={handleSubmitReply}>
              Post Reply
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}

function MyActivitySection({ 
  joinedForums, 
  likedThreads, 
  userReputation 
}: {
  joinedForums: string[]
  likedThreads: string[]
  userReputation: number
}) {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="p-4 text-center">
            <Users size={24} className="mx-auto mb-2 text-primary" />
            <h4 className="font-medium">Forums Joined</h4>
            <p className="text-2xl font-bold">{joinedForums.length}</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4 text-center">
            <Heart size={24} className="mx-auto mb-2 text-red-500" />
            <h4 className="font-medium">Posts Liked</h4>
            <p className="text-2xl font-bold">{likedThreads.length}</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4 text-center">
            <Star size={24} className="mx-auto mb-2 text-yellow-500" />
            <h4 className="font-medium">Reputation</h4>
            <p className="text-2xl font-bold">{userReputation}</p>
          </CardContent>
        </Card>
      </div>
      
      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center text-muted-foreground py-8">
            <MessageCircle size={48} className="mx-auto mb-4 opacity-50" />
            <p>Your community activity will appear here</p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
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
    id: '1',
    name: 'General Support',
    description: 'Share experiences and support each other through daily challenges',
    category: 'support',
    member_count: 1247,
    thread_count: 89,
    is_member: false,
    created_at: new Date().toISOString(),
    tags: ['support', 'general', 'community']
  },
  {
    id: '2',
    name: 'Anxiety & Stress',
    description: 'Discussing anxiety management and stress relief techniques',
    category: 'anxiety',
    member_count: 823,
    thread_count: 156,
    is_member: true,
    created_at: new Date().toISOString(),
    tags: ['anxiety', 'stress', 'coping']
  },
  {
    id: '3',
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

const mockThreads: Thread[] = [
  {
    id: '1',
    title: 'Small wins today! 🌟',
    content: 'I managed to go for a 10-minute walk even though I was feeling anxious. Sometimes the smallest steps matter most.',
    author: {
      id: '1',
      name: 'Sarah',
      badges: ['Community Guide']
    },
    forum_id: '1',
    forum_name: 'General Support',
    created_at: new Date(Date.now() - 3600000).toISOString(),
    updated_at: new Date(Date.now() - 3600000).toISOString(),
    reply_count: 8,
    like_count: 23,
    view_count: 156,
    is_liked: false,
    is_bookmarked: false,
    tags: ['achievement', 'anxiety'],
    category: 'achievements'
  }
]

const mockEvents: CommunityEvent[] = [
  {
    id: '1',
    title: 'Virtual Meditation Circle',
    description: 'Join us for a 30-minute guided meditation session focused on mindfulness and stress relief',
    start_time: new Date(Date.now() + 86400000).toISOString(),
    end_time: new Date(Date.now() + 88200000).toISOString(),
    is_virtual: true,
    participant_count: 23,
    is_participating: false
  },
  {
    id: '2',
    title: 'Anxiety Support Group Meeting',
    description: 'A safe space to share experiences and coping strategies for anxiety management',
    start_time: new Date(Date.now() + 172800000).toISOString(),
    end_time: new Date(Date.now() + 176400000).toISOString(),
    location: 'Community Center Room A',
    is_virtual: false,
    participant_count: 12,
    is_participating: true
  },
  {
    id: '3',
    title: 'Mental Health First Aid Workshop',
    description: 'Learn how to provide initial support to someone experiencing mental health challenges',
    start_time: new Date(Date.now() + 432000000).toISOString(),
    end_time: new Date(Date.now() + 439200000).toISOString(),
    is_virtual: true,
    participant_count: 45,
    is_participating: false
  }
]

const mockChallenges: Challenge[] = [
  {
    id: '1',
    title: '7-Day Gratitude Challenge',
    description: 'Practice daily gratitude by writing down three things you\'re grateful for each day',
    duration_days: 7,
    participant_count: 156,
    is_participating: false,
    start_date: new Date().toISOString(),
    end_date: new Date(Date.now() + 604800000).toISOString(),
    category: 'mindfulness'
  },
  {
    id: '2',
    title: '21-Day Meditation Journey',
    description: 'Build a consistent meditation practice with guided sessions and community support',
    duration_days: 21,
    participant_count: 89,
    is_participating: true,
    start_date: new Date(Date.now() - 432000000).toISOString(),
    end_date: new Date(Date.now() + 1382400000).toISOString(),
    category: 'mindfulness'
  },
  {
    id: '3',
    title: 'Sleep Hygiene Bootcamp',
    description: 'Improve your sleep quality with evidence-based techniques and tracking',
    duration_days: 14,
    participant_count: 67,
    is_participating: false,
    start_date: new Date(Date.now() + 86400000).toISOString(),
    end_date: new Date(Date.now() + 1296000000).toISOString(),
    category: 'sleep'
  },
  {
    id: '4',
    title: 'Daily Movement Challenge',
    description: 'Commit to 30 minutes of physical activity each day, any type of movement counts!',
    duration_days: 30,
    participant_count: 234,
    is_participating: false,
    start_date: new Date().toISOString(),
    end_date: new Date(Date.now() + 2592000000).toISOString(),
    category: 'fitness'
  }
]