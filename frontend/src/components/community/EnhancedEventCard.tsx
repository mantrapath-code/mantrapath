import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Textarea } from "@/components/ui/textarea"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Calendar, ChatCircle, MapPin, Share, Clock, Users, Star } from "@phosphor-icons/react"
import { motion } from "framer-motion"
import { toast } from "sonner"
import { communityApi } from "@/services/api"
import { useAuth } from "@/hooks/useAuth"

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

interface EnhancedEventCardProps {
  event: {
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
    // Enhanced fields
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
  onJoin: () => void
  onLeave: () => void
  onRefresh?: () => void
}

export function EnhancedEventCard({ event, onJoin, onLeave, onRefresh }: EnhancedEventCardProps) {
  const { isAuthenticated } = useAuth()
  const [isLoading, setIsLoading] = useState(false)
  const [showComments, setShowComments] = useState(false)
  const [comments, setComments] = useState<Comment[]>([])
  const [newComment, setNewComment] = useState('')

  const eventStartTime = new Date(event.start_time)
  const eventEndTime = new Date(event.end_time)
  const now = new Date()
  const isUpcoming = eventStartTime > now
  const isOngoing = eventStartTime <= now && eventEndTime > now
  const isCompleted = eventEndTime <= now

  useEffect(() => {
    if (showComments) {
      loadComments()
    }
  }, [showComments, event.id])

  const loadComments = async () => {
    try {
      const data = await communityApi.getEventComments(event.id)
      setComments(data)
    } catch (error) {
      console.error('Failed to load comments:', error)
    }
  }

  const handleAddComment = async () => {
    if (!newComment.trim()) return

    try {
      const response = await communityApi.addEventComment(event.id, {
        content: newComment.trim()
      })
      toast.success('Comment added!')
      setNewComment('')
      await loadComments()
      
      // Call onRefresh to update the parent event data with new comment count
      if (onRefresh) {
        onRefresh()
      }
    } catch (error) {
      console.error('Failed to add comment:', error)
      toast.error('Failed to add comment')
    }
  }

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

  const formatEventTime = (startTime: string, endTime: string) => {
    const start = new Date(startTime)
    const end = new Date(endTime)
    const startDate = start.toLocaleDateString()
    const startTimeStr = start.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    const endTimeStr = end.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    
    if (start.toDateString() === end.toDateString()) {
      return `${startDate} from ${startTimeStr} to ${endTimeStr}`
    } else {
      return `${startDate} ${startTimeStr} - ${end.toLocaleDateString()} ${endTimeStr}`
    }
  }

  const getEventStatus = () => {
    if (isUpcoming) return { label: 'Upcoming', color: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200' }
    if (isOngoing) return { label: 'Live Now', color: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' }
    if (isCompleted) return { label: 'Completed', color: 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200' }
    return { label: 'Unknown', color: 'bg-gray-100 text-gray-800' }
  }

  const status = getEventStatus()

  return (
    <Card className="enhanced-event-card hover:shadow-lg transition-shadow">
      <CardHeader>
        <div className="flex justify-between items-start">
          <div className="space-y-2">
            <CardTitle className="text-lg">{event.title}</CardTitle>
            {event.organizer && (
              <p className="text-sm text-muted-foreground">
                Organized by {event.organizer.name}
              </p>
            )}
            <div className="flex gap-2 items-center flex-wrap">
              <Badge className={status.color}>
                {status.label}
              </Badge>
              {event.is_virtual ? (
                <Badge variant="outline">Virtual</Badge>
              ) : (
                <Badge variant="outline">In-Person</Badge>
              )}
              <Badge variant="outline">
                {event.participant_count} joined
              </Badge>
              {event.average_rating && (
                <Badge variant="secondary">
                  <Star className="w-3 h-3 mr-1" />
                  {event.average_rating.toFixed(1)}
                </Badge>
              )}
            </div>
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="space-y-4">
        <p className="text-sm text-muted-foreground">{event.description}</p>
        
        {/* Event timing and location */}
        <div className="space-y-3">
          <div className="flex items-start gap-3">
            <Calendar className="w-4 h-4 mt-0.5 text-muted-foreground" />
            <div className="text-sm">
              <div className="font-medium">When</div>
              <div className="text-muted-foreground">
                {formatEventTime(event.start_time, event.end_time)}
              </div>
            </div>
          </div>
          
          {event.location && (
            <div className="flex items-start gap-3">
              <MapPin className="w-4 h-4 mt-0.5 text-muted-foreground" />
              <div className="text-sm">
                <div className="font-medium">Where</div>
                <div className="text-muted-foreground">{event.location}</div>
              </div>
            </div>
          )}
        </div>
        
        {/* Time until event */}
        {isUpcoming && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="p-3 bg-blue-50 dark:bg-blue-950 rounded-lg"
          >
            <div className="flex items-center gap-2 text-blue-700 dark:text-blue-300">
              <Clock className="w-4 h-4" />
              <span className="text-sm font-medium">
                Starts in {Math.ceil((eventStartTime.getTime() - now.getTime()) / (1000 * 60 * 60 * 24))} days
              </span>
            </div>
          </motion.div>
        )}
        
        {isOngoing && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="p-3 bg-green-50 dark:bg-green-950 rounded-lg"
          >
            <div className="flex items-center gap-2 text-green-700 dark:text-green-300">
              <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
              <span className="text-sm font-medium">Event is live now!</span>
            </div>
          </motion.div>
        )}
        
        {/* Tags */}
        {event.tags && event.tags.length > 0 && (
          <div className="flex gap-1 flex-wrap">
            {event.tags.map((tag) => (
              <Badge key={tag} variant="outline" className="text-xs">
                {tag}
              </Badge>
            ))}
          </div>
        )}
        
        {/* Action buttons */}
        <div className="flex flex-wrap gap-2">
          {event.is_participating ? (
            <Button variant="outline" onClick={handleAction} disabled={isLoading}>
              {isLoading ? 'Loading...' : 'Leave Event'}
            </Button>
          ) : (
            <Button 
              onClick={handleAction} 
              disabled={isLoading || !isAuthenticated || isCompleted}
            >
              {isLoading ? 'Loading...' : 'Join Event'}
            </Button>
          )}
          
          <Dialog open={showComments} onOpenChange={setShowComments}>
            <DialogTrigger asChild>
              <Button variant="outline">
                <ChatCircle className="w-4 h-4 mr-2" />
                {event.comment_count || comments.length} Comments
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>Event Discussion</DialogTitle>
                <DialogDescription>
                  Share your thoughts about this event
                </DialogDescription>
              </DialogHeader>
              
              {isAuthenticated && (
                <div className="space-y-2">
                  <Textarea
                    placeholder="Share your thoughts about this event..."
                    value={newComment}
                    onChange={(e) => setNewComment(e.target.value)}
                  />
                  <Button onClick={handleAddComment} disabled={!newComment.trim()}>
                    Add Comment
                  </Button>
                </div>
              )}
              
              <ScrollArea className="max-h-80">
                <div className="space-y-3">
                  {comments.length === 0 ? (
                    <div className="text-center text-muted-foreground py-4">
                      No comments yet. Be the first to share your thoughts!
                    </div>
                  ) : (
                    comments.map((comment) => (
                      <div key={comment.id} className="p-3 border rounded">
                        <div className="flex items-center gap-2 mb-2">
                          <div className="font-medium">{comment.author.name}</div>
                          <div className="text-sm text-muted-foreground">
                            {new Date(comment.created_at).toLocaleDateString()}
                          </div>
                          {comment.author.badges.map((badge) => (
                            <Badge key={badge} variant="outline" className="text-xs">
                              {badge}
                            </Badge>
                          ))}
                        </div>
                        <div className="text-sm">{comment.content}</div>
                        {comment.like_count > 0 && (
                          <div className="mt-2 text-xs text-muted-foreground">
                            {comment.like_count} likes
                          </div>
                        )}
                      </div>
                    ))
                  )}
                </div>
              </ScrollArea>
            </DialogContent>
          </Dialog>
          
          <Button variant="outline">
            <Share className="w-4 h-4 mr-2" />
            Share
          </Button>
        </div>
        
        {/* Event feedback section for completed events */}
        {isCompleted && event.is_participating && (
          <motion.div 
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            className="mt-4 p-4 bg-muted/50 rounded-lg"
          >
            <h4 className="font-medium mb-2">How was this event?</h4>
            <p className="text-sm text-muted-foreground mb-3">
              Your feedback helps improve future events
            </p>
            <Button variant="outline" size="sm">
              Leave Feedback
            </Button>
          </motion.div>
        )}
      </CardContent>
    </Card>
  )
}
