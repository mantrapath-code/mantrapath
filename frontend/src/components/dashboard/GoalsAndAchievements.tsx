import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { 
  CheckCircle, 
  Circle, 
  Trophy, 
  Star, 
  Target,
  Plus,
  Calendar
} from "lucide-react"
import { motion } from "framer-motion"
import { toast } from "sonner"

interface Goal {
  id: number
  title: string
  completed: boolean
  icon: React.ComponentType<{ className?: string }>
}

interface Achievement {
  title: string
  description: string
  earned: string
  icon: React.ComponentType<{ className?: string }>
}

const todayGoals: Goal[] = [
  { id: 1, title: "Mood Check-in", completed: true, icon: CheckCircle },
  { id: 2, title: "Journal Entry", completed: false, icon: Circle },
  { id: 3, title: "Mindfulness", completed: false, icon: Target },
]

const recentAchievements: Achievement[] = [
  { title: "7-Day Streak", description: "Mood tracking consistency", earned: "2 days ago", icon: Trophy },
  { title: "Mindful Moments", description: "Completed 10 sessions", earned: "1 week ago", icon: Star },
]

interface GoalsAndAchievementsProps {
  onNavigate?: (tab: string) => void
}

export function GoalsAndAchievements({ onNavigate }: GoalsAndAchievementsProps) {
  const handleToggleGoal = (goalId: number, goalTitle: string) => {
    // Handle journal entry goal specifically
    if (goalTitle === "Journal Entry" && onNavigate) {
      onNavigate('journal')
      toast.success('Opening journal to complete your entry!')
      return
    }
    
    // Handle mood check-in goal
    if (goalTitle === "Mood Check-in" && onNavigate) {
      onNavigate('mood')
      toast.success('Opening mood tracker!')
      return
    }
    
    toast.success('Goal updated!', {
      description: 'Great job on your progress!',
    })
  }

  const handleAddGoal = () => {
    toast.info('Add new goal feature coming soon!')
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2 }}
      className="space-y-6"
    >
      {/* Today's Goals */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
          <CardTitle className="flex items-center gap-2 text-lg">
            <Target className="text-blue-500" size={20} />
            Today's Goals
          </CardTitle>
          <Button 
            variant="outline" 
            size="sm"
            onClick={handleAddGoal}
          >
            <Plus size={16} className="mr-1" />
            Add
          </Button>
        </CardHeader>
        <CardContent className="space-y-3">
          {todayGoals.map((goal, index) => {
            const IconComponent = goal.icon
            return (
              <motion.div
                key={goal.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.3 + index * 0.1 }}
                className="flex items-center justify-between p-3 rounded-lg bg-muted/30 hover:bg-muted/50 transition-colors cursor-pointer"
                onClick={() => handleToggleGoal(goal.id, goal.title)}
              >
                <div className="flex items-center gap-3">
                  <IconComponent 
                    className={`w-5 h-5 ${goal.completed ? 'text-green-500' : 'text-muted-foreground'}`}
                  />
                  <span className={`font-medium ${goal.completed ? 'line-through text-muted-foreground' : ''}`}>
                    {goal.title}
                  </span>
                </div>
                {goal.completed && (
                  <Badge variant="secondary" className="text-xs bg-green-100 text-green-800">
                    Completed
                  </Badge>
                )}
              </motion.div>
            )
          })}
        </CardContent>
      </Card>

      {/* Recent Achievements */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg">
            <Trophy className="text-yellow-500" size={20} />
            Recent Achievements
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {recentAchievements.map((achievement, index) => {
            const IconComponent = achievement.icon
            return (
              <motion.div
                key={achievement.title}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.4 + index * 0.1 }}
                className="flex items-start gap-3 p-3 rounded-lg bg-gradient-to-r from-yellow-50 to-orange-50 border border-yellow-200"
              >
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-yellow-400 to-orange-500 flex items-center justify-center shrink-0">
                  <IconComponent className="w-5 h-5 text-white" />
                </div>
                <div className="flex-1 min-w-0">
                  <h4 className="font-medium text-sm">{achievement.title}</h4>
                  <p className="text-xs text-muted-foreground mt-1">{achievement.description}</p>
                  <div className="flex items-center gap-1 mt-2 text-xs text-muted-foreground">
                    <Calendar className="w-3 h-3" />
                    {achievement.earned}
                  </div>
                </div>
              </motion.div>
            )
          })}
        </CardContent>
      </Card>
    </motion.div>
  )
}