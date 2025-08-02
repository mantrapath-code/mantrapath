/**
 * Achievements Page - Phase 2 Enhancement
 * Dedicated page for viewing achievements, milestones, and celebration history
 */

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  Trophy,
  Medal,
  Star,
  Crown,
  Target,
  Flame,
  ArrowLeft,
  Calendar,
  Gift,
  Sparkle
} from '@phosphor-icons/react'
import { motion } from 'framer-motion'
import { useMoods } from '@/hooks/useMoods'
import { apiService } from '@/services/api'

interface Achievement {
  id: string
  title: string
  description: string
  category: string
  level: 'bronze' | 'silver' | 'gold' | 'platinum'
  progress: number
  maxProgress: number
  isUnlocked: boolean
  unlockedAt?: string
  icon: string
}

interface AchievementsPageProps {
  onBack?: () => void
}

export function AchievementsPage({ onBack }: AchievementsPageProps) {
  const { moods } = useMoods()
  const [achievements, setAchievements] = useState<Achievement[]>([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('overview')

  useEffect(() => {
    loadAchievements()
  }, [])

  const loadAchievements = async () => {
    try {
      setLoading(true)
      // Mock achievements for now - in real implementation, this would come from API
      const mockAchievements: Achievement[] = [
        {
          id: '1',
          title: 'First Steps',
          description: 'Log your first mood entry',
          category: 'getting-started',
          level: 'bronze',
          progress: moods.length > 0 ? 1 : 0,
          maxProgress: 1,
          isUnlocked: moods.length > 0,
          unlockedAt: moods.length > 0 ? new Date(moods[0].timestamp).toISOString() : undefined,
          icon: '🎯'
        },
        {
          id: '2',
          title: 'Week Warrior',
          description: 'Log moods for 7 consecutive days',
          category: 'consistency',
          level: 'silver',
          progress: Math.min(7, moods.length),
          maxProgress: 7,
          isUnlocked: moods.length >= 7,
          icon: '🔥'
        },
        {
          id: '3',
          title: 'Mood Master',
          description: 'Reach 30 total mood entries',
          category: 'milestone',
          level: 'gold',
          progress: Math.min(30, moods.length),
          maxProgress: 30,
          isUnlocked: moods.length >= 30,
          icon: '👑'
        },
        {
          id: '4',
          title: 'Positive Vibes',
          description: 'Log 5 excellent moods in a row',
          category: 'positivity',
          level: 'silver',
          progress: 0, // Would need to calculate streak
          maxProgress: 5,
          isUnlocked: false,
          icon: '✨'
        }
      ]
      
      setAchievements(mockAchievements)
    } catch (error) {
      console.error('Failed to load achievements:', error)
    } finally {
      setLoading(false)
    }
  }

  const getAchievementColor = (level: Achievement['level']) => {
    switch (level) {
      case 'bronze': return 'text-amber-600 bg-amber-50'
      case 'silver': return 'text-gray-600 bg-gray-50'
      case 'gold': return 'text-yellow-600 bg-yellow-50'
      case 'platinum': return 'text-purple-600 bg-purple-50'
    }
  }

  const getAchievementIcon = (level: Achievement['level']) => {
    switch (level) {
      case 'bronze': return <Medal className="text-amber-600" size={24} />
      case 'silver': return <Medal className="text-gray-600" size={24} />
      case 'gold': return <Trophy className="text-yellow-600" size={24} />
      case 'platinum': return <Crown className="text-purple-600" size={24} />
    }
  }

  const unlockedAchievements = achievements.filter(a => a.isUnlocked)
  const lockedAchievements = achievements.filter(a => !a.isUnlocked)
  const totalProgress = achievements.reduce((sum, a) => sum + (a.progress / a.maxProgress), 0)
  const averageProgress = achievements.length > 0 ? (totalProgress / achievements.length) * 100 : 0

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div className="flex items-center gap-3">
          {onBack && (
            <Button variant="ghost" size="sm" onClick={onBack}>
              <ArrowLeft size={16} />
            </Button>
          )}
          <div>
            <h1 className="text-2xl font-bold flex items-center gap-2">
              <Trophy className="text-primary" size={28} />
              Achievements
            </h1>
            <p className="text-muted-foreground">
              Track your wellness journey milestones and celebrate your progress
            </p>
          </div>
        </div>
        <Badge variant="secondary" className="text-sm">
          {unlockedAchievements.length}/{achievements.length} Unlocked
        </Badge>
      </motion.div>

      {/* Progress Overview */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <Card className="bg-gradient-to-r from-primary/5 to-accent/5">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Target className="text-primary" size={20} />
              Overall Progress
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Achievement Progress</span>
                <span className="text-sm text-muted-foreground">{averageProgress.toFixed(0)}%</span>
              </div>
              <Progress value={averageProgress} className="h-3" />
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-primary">{unlockedAchievements.length}</div>
                  <div className="text-xs text-muted-foreground">Unlocked</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-muted-foreground">{lockedAchievements.length}</div>
                  <div className="text-xs text-muted-foreground">In Progress</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-amber-600">
                    {unlockedAchievements.filter(a => a.level === 'gold' || a.level === 'platinum').length}
                  </div>
                  <div className="text-xs text-muted-foreground">Premium</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">{moods.length}</div>
                  <div className="text-xs text-muted-foreground">Total Entries</div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Achievement Tabs */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="overview" className="flex items-center gap-2">
              <Star size={16} />
              All Achievements
            </TabsTrigger>
            <TabsTrigger value="unlocked" className="flex items-center gap-2">
              <Gift size={16} />
              Unlocked ({unlockedAchievements.length})
            </TabsTrigger>
            <TabsTrigger value="progress" className="flex items-center gap-2">
              <Flame size={16} />
              In Progress ({lockedAchievements.length})
            </TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-4 mt-6">
            <div className="grid gap-4">
              {achievements.map((achievement, index) => (
                <motion.div
                  key={achievement.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <Card className={achievement.isUnlocked ? 'border-primary/20 bg-primary/5' : ''}>
                    <CardContent className="p-6">
                      <div className="flex items-center gap-4">
                        <div className={`p-3 rounded-full ${getAchievementColor(achievement.level)}`}>
                          {achievement.isUnlocked ? getAchievementIcon(achievement.level) : 
                            <span className="text-2xl opacity-50">{achievement.icon}</span>
                          }
                        </div>
                        
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <h3 className="font-semibold">{achievement.title}</h3>
                            <Badge variant="outline" className="text-xs capitalize">
                              {achievement.level}
                            </Badge>
                            {achievement.isUnlocked && (
                              <Badge variant="default" className="text-xs">
                                <Sparkle size={12} className="mr-1" />
                                Unlocked
                              </Badge>
                            )}
                          </div>
                          <p className="text-sm text-muted-foreground mb-2">{achievement.description}</p>
                          
                          <div className="space-y-2">
                            <div className="flex items-center justify-between text-xs">
                              <span>Progress</span>
                              <span>{achievement.progress}/{achievement.maxProgress}</span>
                            </div>
                            <Progress 
                              value={(achievement.progress / achievement.maxProgress) * 100} 
                              className="h-2"
                            />
                          </div>
                          
                          {achievement.unlockedAt && (
                            <div className="flex items-center gap-1 mt-2 text-xs text-muted-foreground">
                              <Calendar size={12} />
                              Unlocked {new Date(achievement.unlockedAt).toLocaleDateString()}
                            </div>
                          )}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="unlocked" className="space-y-4 mt-6">
            {unlockedAchievements.length > 0 ? (
              <div className="grid gap-4">
                {unlockedAchievements.map((achievement) => (
                  <Card key={achievement.id} className="border-primary/20 bg-primary/5">
                    <CardContent className="p-6">
                      <div className="flex items-center gap-4">
                        <div className={`p-3 rounded-full ${getAchievementColor(achievement.level)}`}>
                          {getAchievementIcon(achievement.level)}
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <h3 className="font-semibold">{achievement.title}</h3>
                            <Badge variant="default" className="text-xs">
                              <Sparkle size={12} className="mr-1" />
                              Unlocked
                            </Badge>
                          </div>
                          <p className="text-sm text-muted-foreground">{achievement.description}</p>
                          {achievement.unlockedAt && (
                            <div className="flex items-center gap-1 mt-2 text-xs text-muted-foreground">
                              <Calendar size={12} />
                              {new Date(achievement.unlockedAt).toLocaleDateString()}
                            </div>
                          )}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : (
              <Card>
                <CardContent className="p-12 text-center">
                  <Trophy className="mx-auto text-muted-foreground mb-4" size={48} />
                  <h3 className="text-lg font-semibold mb-2">No Achievements Unlocked Yet</h3>
                  <p className="text-muted-foreground">
                    Keep logging your moods and you'll start unlocking achievements!
                  </p>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          <TabsContent value="progress" className="space-y-4 mt-6">
            {lockedAchievements.length > 0 ? (
              <div className="grid gap-4">
                {lockedAchievements.map((achievement) => (
                  <Card key={achievement.id}>
                    <CardContent className="p-6">
                      <div className="flex items-center gap-4">
                        <div className="p-3 rounded-full bg-muted">
                          <span className="text-2xl opacity-50">{achievement.icon}</span>
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <h3 className="font-semibold">{achievement.title}</h3>
                            <Badge variant="outline" className="text-xs capitalize">
                              {achievement.level}
                            </Badge>
                          </div>
                          <p className="text-sm text-muted-foreground mb-2">{achievement.description}</p>
                          
                          <div className="space-y-2">
                            <div className="flex items-center justify-between text-xs">
                              <span>Progress</span>
                              <span>{achievement.progress}/{achievement.maxProgress}</span>
                            </div>
                            <Progress 
                              value={(achievement.progress / achievement.maxProgress) * 100} 
                              className="h-2"
                            />
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : (
              <Card>
                <CardContent className="p-12 text-center">
                  <Sparkle className="mx-auto text-muted-foreground mb-4" size={48} />
                  <h3 className="text-lg font-semibold mb-2">All Caught Up!</h3>
                  <p className="text-muted-foreground">
                    You've unlocked all available achievements. More coming soon!
                  </p>
                </CardContent>
              </Card>
            )}
          </TabsContent>
        </Tabs>
      </motion.div>
    </div>
  )
}
