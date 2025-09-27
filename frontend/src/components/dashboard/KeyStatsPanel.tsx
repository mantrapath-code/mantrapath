import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { 
  Heart, 
  BookOpen, 
  Calendar, 
  Trophy, 
  BarChart3,
  TrendingUp
} from "lucide-react"
import { motion } from "framer-motion"
import { useUserStats } from "@/hooks/useWellness"
import { useJournal } from "@/hooks/useJournal"

interface StatItem {
  label: string
  value: number | string
  icon: React.ComponentType<{ className?: string }>
  color: string
  trend?: 'up' | 'down' | 'stable'
}

export function KeyStatsPanel() {
  const { stats } = useUserStats()
  const { entries } = useJournal()

  // Mock data - replace with real data when available
  const statsData: StatItem[] = [
    {
      label: "Day Streak",
      value: stats?.currentStreak || 7,
      icon: Heart,
      color: "text-red-500",
      trend: 'up'
    },
    {
      label: "Journals",
      value: entries?.length || 12,
      icon: BookOpen,
      color: "text-blue-500",
      trend: 'up'
    },
    {
      label: "Sessions",
      value: stats?.totalSessions || 24,
      icon: Calendar,
      color: "text-green-500",
      trend: 'stable'
    },
    {
      label: "Achievements",
      value: stats?.achievements || 8,
      icon: Trophy,
      color: "text-yellow-500",
      trend: 'up'
    },
  ]

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3 }}
    >
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg">
            <BarChart3 className="text-primary" size={20} />
            Key Stats
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4">
            {statsData.map((stat, index) => {
              const IconComponent = stat.icon
              return (
                <motion.div
                  key={stat.label}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.4 + index * 0.1 }}
                  className="text-center p-4 rounded-lg bg-gradient-to-br from-muted/30 to-muted/10 hover:from-muted/40 hover:to-muted/20 transition-all duration-200"
                >
                  <div className="flex items-center justify-center mb-2">
                    <div className="relative">
                      <IconComponent className={`w-8 h-8 ${stat.color}`} />
                      {stat.trend === 'up' && (
                        <TrendingUp className="w-3 h-3 text-green-500 absolute -top-1 -right-1" />
                      )}
                    </div>
                  </div>
                  
                  <div className="space-y-1">
                    <div className="text-2xl font-bold">
                      {typeof stat.value === 'number' && stat.value > 999 
                        ? `${(stat.value / 1000).toFixed(1)}k` 
                        : stat.value}
                    </div>
                    <div className="text-xs text-muted-foreground font-medium">
                      {stat.label}
                    </div>
                  </div>
                  
                  {stat.trend && (
                    <Badge 
                      variant="secondary" 
                      className={`text-xs mt-2 ${
                        stat.trend === 'up' 
                          ? 'bg-green-100 text-green-700' 
                          : stat.trend === 'down'
                          ? 'bg-red-100 text-red-700'
                          : 'bg-blue-100 text-blue-700'
                      }`}
                    >
                      {stat.trend === 'up' ? '+12%' : stat.trend === 'down' ? '-5%' : 'Stable'}
                    </Badge>
                  )}
                </motion.div>
              )
            })}
          </div>
          
          {/* Summary */}
          <div className="mt-6 p-3 bg-primary/5 rounded-lg border">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">This Week</span>
              <Badge className="bg-primary/10 text-primary border-primary/20">
                Excellent Progress
              </Badge>
            </div>
            <p className="text-xs text-muted-foreground mt-2">
              You're maintaining a great wellness routine. Keep it up!
            </p>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}