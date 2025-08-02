import { useState, useEffect } from "react"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { 
  Trophy,
  Medal,
  Star,
  Sparkle,
  Heart,
  Target,
  Flame,
  Crown,
  Gift,
  ArrowRight,
  X
} from "@phosphor-icons/react"
import { motion, AnimatePresence } from "framer-motion"
import confetti from 'canvas-confetti'
import { apiService } from "@/services/api"

interface Celebration {
  id: string
  type: string
  title: string
  message: string
  achievement_level: string
  reward_type?: string
  reward_data?: any
  created_at: string
}

interface CelebrationModalProps {
  celebrations: Celebration[]
  onClose: () => void
  onCelebrationsSeen: (celebrationIds: string[]) => void
}

export function CelebrationModal({ celebrations, onClose, onCelebrationsSeen }: CelebrationModalProps) {
  const [currentIndex, setCurrentIndex] = useState(0)
  const [hasShownConfetti, setHasShownConfetti] = useState(false)

  useEffect(() => {
    if (celebrations.length > 0 && !hasShownConfetti) {
      // Trigger confetti animation
      const duration = 3000
      const animationEnd = Date.now() + duration
      const defaults = { startVelocity: 30, spread: 360, ticks: 60, zIndex: 0 }

      function randomInRange(min: number, max: number) {
        return Math.random() * (max - min) + min
      }

      const interval = setInterval(function() {
        const timeLeft = animationEnd - Date.now()

        if (timeLeft <= 0) {
          return clearInterval(interval)
        }

        const particleCount = 50 * (timeLeft / duration)
        
        confetti(Object.assign({}, defaults, {
          particleCount,
          origin: { x: randomInRange(0.1, 0.3), y: Math.random() - 0.2 }
        }))
        confetti(Object.assign({}, defaults, {
          particleCount,
          origin: { x: randomInRange(0.7, 0.9), y: Math.random() - 0.2 }
        }))
      }, 250)

      setHasShownConfetti(true)
    }
  }, [celebrations.length, hasShownConfetti])

  const getAchievementIcon = (level: string, type: string) => {
    const iconSize = 48
    const iconProps = { size: iconSize, weight: "fill" as const }

    if (level === "platinum" || level === "gold") {
      return <Crown {...iconProps} className="text-yellow-500" />
    } else if (level === "silver") {
      return <Medal {...iconProps} className="text-gray-400" />
    } else if (type === "improvement_streak") {
      return <Trophy {...iconProps} className="text-blue-500" />
    } else if (type === "consistency_streak") {
      return <Flame {...iconProps} className="text-orange-500" />
    } else if (type === "resilience") {
      return <Heart {...iconProps} className="text-red-500" />
    } else if (type === "stress_management") {
      return <Target {...iconProps} className="text-green-500" />
    } else if (type === "first_week") {
      return <Star {...iconProps} className="text-purple-500" />
    } else {
      return <Sparkle {...iconProps} className="text-pink-500" />
    }
  }

  const getAchievementColor = (level: string) => {
    switch (level) {
      case "platinum":
        return "from-gray-200 to-gray-400"
      case "gold":
        return "from-yellow-200 to-yellow-400"
      case "silver":
        return "from-gray-100 to-gray-300"
      case "bronze":
        return "from-orange-200 to-orange-400"
      default:
        return "from-blue-200 to-blue-400"
    }
  }

  const getLevelBadgeColor = (level: string) => {
    switch (level) {
      case "platinum":
        return "bg-gray-100 text-gray-800 border-gray-300"
      case "gold":
        return "bg-yellow-100 text-yellow-800 border-yellow-300"
      case "silver":
        return "bg-gray-50 text-gray-700 border-gray-200"
      case "bronze":
        return "bg-orange-100 text-orange-800 border-orange-300"
      default:
        return "bg-blue-100 text-blue-800 border-blue-300"
    }
  }

  const getRewardDescription = (rewardType?: string, rewardData?: any) => {
    if (!rewardType) return null

    switch (rewardType) {
      case "insight_unlock":
        return "🔓 New personal insight unlocked!"
      case "feature_unlock":
        return "✨ New feature available to explore!"
      case "weekly_insight":
        return "📊 Weekly pattern insight generated!"
      case "premium_insight":
        return "💎 Premium insight added to your profile!"
      case "master_badge":
        return "👑 Master badge earned!"
      case "resilience_badge":
        return "💪 Resilience badge earned!"
      case "coping_insight":
        return "🧘 Personalized coping strategy insight!"
      case "welcome_insights":
        return "🌱 Welcome package insights unlocked!"
      case "emotion_guide":
        return "🎭 Emotional awareness guide unlocked!"
      case "encouragement":
        return "💜 Special encouragement message!"
      default:
        return "🎁 Special reward unlocked!"
    }
  }

  const handleNext = () => {
    if (currentIndex < celebrations.length - 1) {
      setCurrentIndex(currentIndex + 1)
    } else {
      handleClose()
    }
  }

  const handleClose = () => {
    // Mark all celebrations as seen
    const celebrationIds = celebrations.map(c => c.id)
    onCelebrationsSeen(celebrationIds)
    onClose()
  }

  if (celebrations.length === 0) {
    return null
  }

  const currentCelebration = celebrations[currentIndex]
  const isLastCelebration = currentIndex === celebrations.length - 1

  return (
    <Dialog open={true} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-md">
        <motion.div
          key={currentIndex}
          initial={{ opacity: 0, scale: 0.9, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          transition={{ duration: 0.3 }}
          className="text-center space-y-6"
        >
          {/* Close button */}
          <Button
            variant="ghost"
            size="sm"
            className="absolute right-4 top-4"
            onClick={handleClose}
          >
            <X size={16} />
          </Button>

          {/* Achievement Icon */}
          <div className={`mx-auto w-24 h-24 rounded-full bg-gradient-to-br ${getAchievementColor(currentCelebration.achievement_level)} flex items-center justify-center shadow-lg`}>
            {getAchievementIcon(currentCelebration.achievement_level, currentCelebration.type)}
          </div>

          {/* Achievement Level Badge */}
          <Badge 
            variant="outline" 
            className={`mx-auto ${getLevelBadgeColor(currentCelebration.achievement_level)} font-semibold uppercase tracking-wide`}
          >
            {currentCelebration.achievement_level} Achievement
          </Badge>

          {/* Title and Message */}
          <div className="space-y-3">
            <DialogHeader>
              <DialogTitle className="text-2xl font-bold text-center">
                {currentCelebration.title}
              </DialogTitle>
            </DialogHeader>
            
            <p className="text-muted-foreground leading-relaxed">
              {currentCelebration.message}
            </p>
          </div>

          {/* Reward Description */}
          {currentCelebration.reward_type && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="bg-gradient-to-r from-purple-50 to-pink-50 p-4 rounded-lg border border-purple-200"
            >
              <div className="flex items-center justify-center gap-2 text-purple-700">
                <Gift size={20} />
                <span className="font-medium">
                  {getRewardDescription(currentCelebration.reward_type, currentCelebration.reward_data)}
                </span>
              </div>
            </motion.div>
          )}

          {/* Progress Indicator */}
          {celebrations.length > 1 && (
            <div className="flex justify-center gap-2">
              {celebrations.map((_, index) => (
                <div
                  key={index}
                  className={`w-2 h-2 rounded-full transition-colors ${
                    index === currentIndex ? 'bg-primary' : 'bg-gray-300'
                  }`}
                />
              ))}
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-3 justify-center pt-4">
            {!isLastCelebration ? (
              <>
                <Button variant="outline" onClick={handleClose}>
                  Close
                </Button>
                <Button onClick={handleNext} className="min-w-[120px]">
                  Next <ArrowRight size={16} className="ml-2" />
                </Button>
              </>
            ) : (
              <Button onClick={handleClose} className="min-w-[120px]">
                <Heart size={16} className="mr-2" />
                Awesome!
              </Button>
            )}
          </div>

          {/* Celebration Counter */}
          {celebrations.length > 1 && (
            <p className="text-xs text-muted-foreground">
              Celebration {currentIndex + 1} of {celebrations.length}
            </p>
          )}
        </motion.div>
      </DialogContent>
    </Dialog>
  )
}

// Hook to manage celebrations
export function useCelebrations() {
  const [pendingCelebrations, setPendingCelebrations] = useState<Celebration[]>([])
  const [showCelebrations, setShowCelebrations] = useState(false)

  const checkForCelebrations = async () => {
    try {
      const celebrations = await apiService.getPendingCelebrations()
      if (celebrations.length > 0) {
        setPendingCelebrations(celebrations)
        setShowCelebrations(true)
      }
    } catch (error) {
      console.log('Could not check for celebrations:', error)
    }
  }

  const markCelebrationsAsSeen = async (celebrationIds: string[]) => {
    try {
      await apiService.markCelebrationsAsSeen(celebrationIds)
    } catch (error) {
      console.log('Could not mark celebrations as seen:', error)
    }
  }

  const closeCelebrations = () => {
    setShowCelebrations(false)
    setPendingCelebrations([])
  }

  return {
    pendingCelebrations,
    showCelebrations,
    checkForCelebrations,
    markCelebrationsAsSeen,
    closeCelebrations
  }
}
