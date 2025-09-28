import { Card, CardContent } from "@/components/ui/card"
import { 
  Heart, 
  BookOpen, 
  Brain, 
  Mic,
  MessageCircle,
  Plus
} from "lucide-react"
import { motion } from "framer-motion"
import { toast } from "sonner"

interface QuickAction {
  title: string
  icon: React.ComponentType<{ className?: string }>
  action: string
  color: string
}

const quickActions: QuickAction[] = [
  { title: "Quick Mood Entry", icon: Heart, action: "mood", color: "text-pink-500" },
  { title: "Voice Note", icon: Mic, action: "voice", color: "text-blue-500" },
  { title: "New Journal", icon: BookOpen, action: "journal", color: "text-green-500" },
  { title: "Chat with AI", icon: MessageCircle, action: "chat", color: "text-purple-500" },
]

interface QuickActionsGridProps {
  onActionClick?: (actionType: string) => void
}

export function QuickActionsGrid({ onActionClick }: QuickActionsGridProps) {
  
  const handleQuickAction = (actionType: string) => {
    if (onActionClick) {
      onActionClick(actionType)
      return
    }
    
    // Default behavior if no custom handler
    switch (actionType) {
      case 'mood':
        toast.info('Opening mood tracker...')
        break
      case 'voice':
        toast.info('Starting voice note...')
        break
      case 'journal':
        toast.info('Opening new journal entry...')
        break
      case 'chat':
        toast.info('Opening AI chat...')
        break
      default:
        toast.info(`${actionType} feature coming soon!`)
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.1 }}
      className="mb-8"
    >
      <div className="mb-4">
        <h2 className="text-lg font-semibold text-foreground mb-1">Quick Actions</h2>
        <p className="text-sm text-muted-foreground">Start your wellness journey with these tools</p>
      </div>
      
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4">
        {quickActions.map((action, index) => {
          const IconComponent = action.icon
          return (
            <motion.div
              key={action.action}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.1 + index * 0.05 }}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <Card 
                className="cursor-pointer hover:shadow-lg transition-all duration-200 border hover:border-primary/20 bg-gradient-to-br from-background to-muted/20 group h-full"
                onClick={() => handleQuickAction(action.action)}
              >
                <CardContent className="p-4 text-center space-y-3 h-full flex flex-col justify-center">
                  <div className="w-12 h-12 rounded-full bg-gradient-to-br from-primary/10 to-secondary/10 flex items-center justify-center mx-auto group-hover:scale-110 transition-transform duration-200">
                    <IconComponent className={`w-6 h-6 ${action.color}`} />
                  </div>
                  <div className="space-y-1">
                    <h3 className="font-medium text-sm leading-tight">{action.title}</h3>
                    <p className="text-xs text-muted-foreground leading-tight">
                      {action.action === 'mood' && 'Track your current mood'}
                      {action.action === 'voice' && 'Record a voice memo'}
                      {action.action === 'journal' && 'Write your thoughts'}
                      {action.action === 'chat' && 'Talk to your AI companion'}
                    </p>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )
        })}
      </div>
    </motion.div>
  )
}