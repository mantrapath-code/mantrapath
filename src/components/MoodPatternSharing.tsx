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
  MessageCircle,
  Trophy,
  Sparkles,
  Eye,
  EyeSlash,
  HandHeart
} from '@phosphor-icons/react'
import { motion, AnimatePresence } from 'framer-motion'
import { toast } from 'sonner'
import { useMoods } from "@/hooks/useWellness"
import { useMoodAnalytics } from "@/hooks/useWellness"
import { useKV } from '@github/spark/hooks'

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
  const [activeTab, setActiveTab] = useState('community')
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
    // Initialize with some sample community patterns for demonstration
    if (sharedPatterns.length === 0) {
      initializeSamplePatterns()
    }
  }, [])

  const initializeSamplePatterns = () => {
    const samplePatterns: SharedMoodPattern[] = [
      {
        id: '1',
        userId: 'anon_user_1',
        type: 'milestone',
        title: '30 Days of Consistent Mood Tracking! 🎉',
        description: 'I\'ve been tracking my mood daily for a month now and the insights have been incredible. Seeing my patterns helped me identify that Monday mornings were consistently my lowest point, so I started doing meditation before work. Game changer!',
        anonymizedPattern: {
          weeklyTrend: 'improving',
          majorWin: 'Found Monday morning pattern and created intervention',
          daysTracked: 30,
          improvementScore: 75
        },
        tags: ['milestone', 'self-care', 'meditation'],
        timestamp: Date.now() - (2 * 24 * 60 * 60 * 1000),
        encouragements: 24,
        replies: [
          {
            id: 'r1',
            userId: 'anon_user_2',
            content: 'This is so inspiring! I struggle with Monday mornings too. What kind of meditation do you do?',
            timestamp: Date.now() - (24 * 60 * 60 * 1000),
            hearts: 8
          },
          {
            id: 'r2',
            userId: 'anon_user_3',
            content: 'Amazing progress! 30 days is such an achievement. Keep going! 💪',
            timestamp: Date.now() - (12 * 60 * 60 * 1000),
            hearts: 5,
            isFromModerator: true
          }
        ],
        isAnonymous: true
      },
      {
        id: '2',
        userId: 'anon_user_4',
        type: 'breakthrough',
        title: 'Finally Understanding My Anxiety Triggers',
        description: 'After weeks of tracking, I realized my anxiety spikes happen when I have back-to-back meetings. MantraPath helped me see this pattern clearly. Now I schedule 10-minute breathing breaks between meetings.',
        anonymizedPattern: {
          weeklyTrend: 'improving',
          majorWin: 'Identified meeting-related anxiety pattern',
          daysTracked: 21,
          improvementScore: 60
        },
        tags: ['anxiety', 'workplace', 'breathing'],
        timestamp: Date.now() - (24 * 60 * 60 * 1000),
        encouragements: 18,
        replies: [
          {
            id: 'r3',
            userId: 'anon_user_5',
            content: 'Thank you for sharing this! I have the same issue with back-to-back meetings. Definitely going to try the breathing breaks.',
            timestamp: Date.now() - (6 * 60 * 60 * 1000),
            hearts: 12
          }
        ],
        isAnonymous: true
      },
      {
        id: '3',
        userId: 'anon_user_6',
        type: 'support-request',
        title: 'Having a Tough Week - Could Use Some Encouragement',
        description: 'My mood has been consistently low this week. I know it happens to everyone, but seeing the downward trend in my chart is discouraging. Has anyone else gone through something similar? How did you get through it?',
        anonymizedPattern: {
          weeklyTrend: 'challenging',
          majorWin: 'Still tracking even when feeling low',
          daysTracked: 45,
          improvementScore: 35
        },
        tags: ['support', 'tough-times', 'encouragement-needed'],
        timestamp: Date.now() - (8 * 60 * 60 * 1000),
        encouragements: 31,
        replies: [
          {
            id: 'r4',
            userId: 'anon_user_7',
            content: 'You\'re not alone in this. Tough weeks happen to all of us. The fact that you\'re still tracking shows incredible strength. Be gentle with yourself. 💙',
            timestamp: Date.now() - (4 * 60 * 60 * 1000),
            hearts: 15
          },
          {
            id: 'r5',
            userId: 'anon_user_8',
            content: 'I had a similar week last month. What helped me was focusing on just one small positive thing each day. Sometimes it was just having a warm cup of tea. Small wins count! ☕',
            timestamp: Date.now() - (2 * 60 * 60 * 1000),
            hearts: 9
          }
        ],
        isAnonymous: true
      }
    ]
    
    setSharedPatterns(samplePatterns)
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
    
    const trend = avgMood > 3.5 ? 'improving' : avgMood < 2.5 ? 'challenging' : 'stable'
    const majorWin = recentInsights.length > 0 
      ? recentInsights[0].insight 
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
      replies: [],
      isAnonymous: newShare.isAnonymous
    }

    setSharedPatterns(current => [pattern, ...current])
    setUserStats(current => ({ 
      ...current, 
      patternsShared: current.patternsShared + 1 
    }))

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
    setSharedPatterns(current => 
      current.map(pattern => 
        pattern.id === patternId 
          ? { ...pattern, encouragements: pattern.encouragements + 1 }
          : pattern
      )
    )
    
    setUserStats(current => ({
      ...current,
      encouragementsGiven: current.encouragementsGiven + 1,
      supportStreak: current.supportStreak + 1
    }))

    toast.success('Encouragement sent! 💙')
  }

  const addReply = (patternId: string, content: string) => {
    if (!content.trim()) return

    const reply: CommunityReply = {
      id: Date.now().toString(),
      userId: 'current_user_anon',
      content,
      timestamp: Date.now(),
      hearts: 0
    }

    setSharedPatterns(current => 
      current.map(pattern => 
        pattern.id === patternId 
          ? { ...pattern, replies: [...pattern.replies, reply] }
          : pattern
      )
    )

    setUserStats(current => ({
      ...current,
      helpfulReplies: current.helpfulReplies + 1
    }))

    toast.success('Reply added!')
  }

  const getPatternIcon = (type: SharedMoodPattern['type']) => {
    switch (type) {
      case 'milestone': return <Trophy className="w-4 h-4 text-yellow-500" />
      case 'breakthrough': return <Sparkles className="w-4 h-4 text-purple-500" />
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
            <Button onClick={() => setShowShareDialog(true)}>
              <Share className="w-4 h-4 mr-2" />
              Share Progress
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="community">Community Feed</TabsTrigger>
              <TabsTrigger value="my-patterns">My Shares</TabsTrigger>
              <TabsTrigger value="stats">My Impact</TabsTrigger>
            </TabsList>

            <TabsContent value="community" className="space-y-4">
              <div className="space-y-4">
                {sharedPatterns
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
                              <span>{new Date(pattern.timestamp).toLocaleDateString()}</span>
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
                          {pattern.tags.length > 0 && (
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
                                variant="ghost"
                                size="sm"
                                onClick={() => giveEncouragement(pattern.id)}
                                className="flex items-center gap-2"
                              >
                                <Heart className="w-4 h-4" />
                                {pattern.encouragements} Encouragements
                              </Button>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => setSelectedPattern(pattern)}
                                className="flex items-center gap-2"
                              >
                                <MessageCircle className="w-4 h-4" />
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
                                    <div className="flex items-center gap-1 text-xs text-muted-foreground">
                                      <Heart className="w-3 h-3" />
                                      {reply.hearts}
                                    </div>
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
                  ))}
              </div>
            </TabsContent>

            <TabsContent value="my-patterns" className="space-y-4">
              <div className="space-y-4">
                {sharedPatterns
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
                              <MessageCircle className="w-4 h-4" />
                              {pattern.replies.length} replies
                            </span>
                          </div>
                        </div>
                        <Badge className="capitalize">{pattern.type.replace('-', ' ')}</Badge>
                      </div>
                    </Card>
                  ))}
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
                          {new Date(reply.timestamp).toLocaleString()}
                        </span>
                        <div className="flex items-center gap-1 text-xs">
                          <Heart className="w-3 h-3" />
                          {reply.hearts}
                        </div>
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