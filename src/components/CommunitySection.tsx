import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Avatar } from "@/components/ui/avatar"
import { Users, Heart, MessageCircle, Trophy } from "@phosphor-icons/react"
import { motion } from "framer-motion"

interface CommunityPost {
  id: string
  title: string
  content: string
  author: {
    name: string
    badges: string[]
  }
  timestamp: number
  replies: number
  likes: number
  category: 'general' | 'anxiety' | 'depression' | 'support' | 'achievements'
}

const mockPosts: CommunityPost[] = [
  {
    id: '1',
    title: 'Small wins today! 🌟',
    content: 'I managed to go for a 10-minute walk even though I was feeling anxious. Sometimes the smallest steps matter most.',
    author: { name: 'Sarah', badges: ['Community Guide'] },
    timestamp: Date.now() - 3600000,
    replies: 8,
    likes: 23,
    category: 'achievements'
  },
  {
    id: '2',
    title: 'Dealing with work stress - any tips?',
    content: 'Having a tough week at work and feeling overwhelmed. How do you all manage stress when everything feels urgent?',
    author: { name: 'Alex', badges: ['Supportive Soul'] },
    timestamp: Date.now() - 7200000,
    replies: 12,
    likes: 15,
    category: 'support'
  },
  {
    id: '3',
    title: 'Gratitude practice changed my perspective',
    content: 'Been doing the daily gratitude practice for 2 weeks now. It\'s amazing how it shifts focus to the positive things, even on difficult days.',
    author: { name: 'Maya', badges: ['Resilient Streak'] },
    timestamp: Date.now() - 14400000,
    replies: 6,
    likes: 31,
    category: 'general'
  }
]

export function CommunitySection() {
  const getCategoryColor = (category: CommunityPost['category']) => {
    switch (category) {
      case 'achievements': return 'bg-green-100 text-green-800'
      case 'support': return 'bg-blue-100 text-blue-800'
      case 'anxiety': return 'bg-yellow-100 text-yellow-800'
      case 'depression': return 'bg-purple-100 text-purple-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }
  
  const getBadgeIcon = (badge: string) => {
    switch (badge) {
      case 'Community Guide': return '🧭'
      case 'Supportive Soul': return '💙'
      case 'Resilient Streak': return '🌟'
      default: return '✨'
    }
  }
  
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="text-primary" size={24} />
            Community Support
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <Button variant="outline" className="h-20 flex flex-col gap-1">
              <Trophy size={20} className="text-yellow-500" />
              <span className="text-sm">Achievements</span>
            </Button>
            <Button variant="outline" className="h-20 flex flex-col gap-1">
              <Heart size={20} className="text-red-500" />
              <span className="text-sm">Support</span>
            </Button>
            <Button variant="outline" className="h-20 flex flex-col gap-1">
              <MessageCircle size={20} className="text-blue-500" />
              <span className="text-sm">General</span>
            </Button>
            <Button variant="outline" className="h-20 flex flex-col gap-1">
              <Users size={20} className="text-green-500" />
              <span className="text-sm">Groups</span>
            </Button>
          </div>
          
          <div className="space-y-4">
            {mockPosts.map((post, index) => (
              <motion.div
                key={post.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <Card className="hover:shadow-md transition-shadow">
                  <CardContent className="p-4">
                    <div className="flex items-start gap-3">
                      <Avatar className="w-10 h-10 bg-primary/10 flex items-center justify-center">
                        <span className="text-primary font-medium">
                          {post.author.name[0]}
                        </span>
                      </Avatar>
                      
                      <div className="flex-1 space-y-2">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="font-medium">{post.author.name}</span>
                          {post.author.badges.map((badge) => (
                            <Badge key={badge} variant="secondary" className="text-xs">
                              {getBadgeIcon(badge)} {badge}
                            </Badge>
                          ))}
                          <Badge className={cn("text-xs", getCategoryColor(post.category))}>
                            {post.category}
                          </Badge>
                        </div>
                        
                        <h4 className="font-medium text-foreground">{post.title}</h4>
                        <p className="text-sm text-muted-foreground">{post.content}</p>
                        
                        <div className="flex items-center gap-4 text-sm text-muted-foreground">
                          <span className="flex items-center gap-1">
                            <Heart size={14} />
                            {post.likes}
                          </span>
                          <span className="flex items-center gap-1">
                            <MessageCircle size={14} />
                            {post.replies}
                          </span>
                          <span>{new Date(post.timestamp).toLocaleDateString()}</span>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
          
          <div className="mt-6 text-center">
            <Button>Share Your Story</Button>
          </div>
        </CardContent>
      </Card>
      
      <Card>
        <CardHeader>
          <CardTitle>Community Guidelines</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          <p className="text-sm text-muted-foreground">
            💜 Be kind and supportive to everyone
          </p>
          <p className="text-sm text-muted-foreground">
            🤝 Share experiences, not medical advice
          </p>
          <p className="text-sm text-muted-foreground">
            🔒 Respect privacy and confidentiality
          </p>
          <p className="text-sm text-muted-foreground">
            🌟 Celebrate progress, no matter how small
          </p>
        </CardContent>
      </Card>
    </div>
  )
}

function cn(...classes: string[]) {
  return classes.filter(Boolean).join(' ')
}