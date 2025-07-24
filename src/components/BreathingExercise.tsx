import { useState, useEffect, useRef } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Play, Pause, RotateClockwise } from "@phosphor-icons/react"
import { motion, AnimatePresence } from "framer-motion"

interface BreathingExerciseProps {
  onComplete?: () => void
  className?: string
}

export function BreathingExercise({ onComplete, className }: BreathingExerciseProps) {
  const [isActive, setIsActive] = useState(false)
  const [phase, setPhase] = useState<'inhale' | 'hold' | 'exhale' | 'pause'>('inhale')
  const [cycleCount, setCycleCount] = useState(0)
  const [timeRemaining, setTimeRemaining] = useState(0)
  const [exerciseType, setExerciseType] = useState<'4-7-8' | '4-4-4-4' | 'box'>('4-7-8')
  const intervalRef = useRef<NodeJS.Timeout | null>(null)

  const exercises = {
    '4-7-8': {
      name: '4-7-8 Relaxing Breath',
      description: 'Calming technique for anxiety and stress',
      phases: { inhale: 4, hold: 7, exhale: 8, pause: 2 },
      totalCycles: 4
    },
    '4-4-4-4': {
      name: 'Box Breathing',
      description: 'Balanced breathing for focus and clarity',
      phases: { inhale: 4, hold: 4, exhale: 4, pause: 4 },
      totalCycles: 5
    },
    'box': {
      name: 'Equal Breathing',
      description: 'Simple technique for general relaxation',
      phases: { inhale: 4, hold: 0, exhale: 4, pause: 1 },
      totalCycles: 6
    }
  }

  const currentExercise = exercises[exerciseType]

  useEffect(() => {
    if (isActive) {
      startBreathing()
    } else {
      stopBreathing()
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
    }
  }, [isActive, exerciseType])

  const startBreathing = () => {
    setCycleCount(0)
    setPhase('inhale')
    setTimeRemaining(currentExercise.phases.inhale)
    
    intervalRef.current = setInterval(() => {
      setTimeRemaining(prev => {
        if (prev <= 1) {
          moveToNextPhase()
          return getNextPhaseDuration()
        }
        return prev - 1
      })
    }, 1000)
  }

  const stopBreathing = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
      intervalRef.current = null
    }
  }

  const moveToNextPhase = () => {
    setPhase(currentPhase => {
      let nextPhase: typeof phase
      let newCycleCount = cycleCount

      switch (currentPhase) {
        case 'inhale':
          nextPhase = currentExercise.phases.hold > 0 ? 'hold' : 'exhale'
          break
        case 'hold':
          nextPhase = 'exhale'
          break
        case 'exhale':
          nextPhase = 'pause'
          break
        case 'pause':
          newCycleCount += 1
          if (newCycleCount >= currentExercise.totalCycles) {
            setIsActive(false)
            onComplete?.()
            return 'inhale'
          }
          nextPhase = 'inhale'
          break
        default:
          nextPhase = 'inhale'
      }

      setCycleCount(newCycleCount)
      return nextPhase
    })
  }

  const getNextPhaseDuration = () => {
    return currentExercise.phases[getNextPhaseType()]
  }

  const getNextPhaseType = (): keyof typeof currentExercise.phases => {
    switch (phase) {
      case 'inhale':
        return currentExercise.phases.hold > 0 ? 'hold' : 'exhale'
      case 'hold':
        return 'exhale'
      case 'exhale':
        return 'pause'
      case 'pause':
        return 'inhale'
      default:
        return 'inhale'
    }
  }

  const getPhaseInstruction = () => {
    switch (phase) {
      case 'inhale': return 'Breathe in slowly'
      case 'hold': return 'Hold your breath'
      case 'exhale': return 'Breathe out slowly'
      case 'pause': return 'Pause naturally'
      default: return 'Get ready'
    }
  }

  const getPhaseColor = () => {
    switch (phase) {
      case 'inhale': return 'from-blue-400 to-cyan-400'
      case 'hold': return 'from-purple-400 to-pink-400'
      case 'exhale': return 'from-green-400 to-emerald-400'
      case 'pause': return 'from-yellow-400 to-orange-400'
      default: return 'from-gray-400 to-gray-500'
    }
  }

  const resetExercise = () => {
    setIsActive(false)
    setCycleCount(0)
    setPhase('inhale')
    setTimeRemaining(0)
  }

  return (
    <Card className={className}>
      <CardHeader className="text-center pb-4">
        <CardTitle className="flex items-center justify-center gap-2">
          <div className="w-6 h-6 rounded-full bg-gradient-to-r from-blue-400 to-purple-400" />
          Breathing Exercise
        </CardTitle>
        <div className="space-y-2">
          <div className="flex gap-2 justify-center">
            {Object.entries(exercises).map(([key, exercise]) => (
              <Button
                key={key}
                variant={exerciseType === key ? "default" : "outline"}
                size="sm"
                onClick={() => {
                  setExerciseType(key as keyof typeof exercises)
                  resetExercise()
                }}
                disabled={isActive}
                className="text-xs"
              >
                {exercise.name}
              </Button>
            ))}
          </div>
          <p className="text-sm text-muted-foreground">
            {currentExercise.description}
          </p>
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        {/* Breathing Circle */}
        <div className="flex justify-center">
          <div className="relative">
            <motion.div
              className={`w-32 h-32 rounded-full bg-gradient-to-r ${getPhaseColor()} opacity-20`}
              animate={{
                scale: isActive ? (phase === 'inhale' ? 1.3 : phase === 'exhale' ? 0.7 : 1) : 1
              }}
              transition={{
                duration: isActive ? timeRemaining : 0.5,
                ease: "easeInOut"
              }}
            />
            <motion.div
              className={`absolute inset-4 rounded-full bg-gradient-to-r ${getPhaseColor()}`}
              animate={{
                scale: isActive ? (phase === 'inhale' ? 1.2 : phase === 'exhale' ? 0.8 : 1) : 1
              }}
              transition={{
                duration: isActive ? timeRemaining : 0.5,
                ease: "easeInOut"
              }}
            />
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-center text-white">
                <div className="text-2xl font-bold">{timeRemaining}</div>
                {isActive && (
                  <div className="text-xs opacity-75">
                    {phase.charAt(0).toUpperCase() + phase.slice(1)}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Instructions */}
        <div className="text-center space-y-2">
          <AnimatePresence mode="wait">
            <motion.div
              key={phase + isActive}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="space-y-1"
            >
              <p className="text-lg font-medium">{getPhaseInstruction()}</p>
              {isActive && (
                <div className="flex items-center justify-center gap-2">
                  <Badge variant="outline" className="text-xs">
                    Cycle {cycleCount + 1} of {currentExercise.totalCycles}
                  </Badge>
                </div>
              )}
            </motion.div>
          </AnimatePresence>
        </div>

        {/* Controls */}
        <div className="flex justify-center gap-2">
          <Button
            onClick={() => setIsActive(!isActive)}
            variant={isActive ? "secondary" : "default"}
            size="lg"
            className="min-w-24"
          >
            {isActive ? (
              <>
                <Pause size={16} className="mr-2" />
                Pause
              </>
            ) : (
              <>
                <Play size={16} className="mr-2" />
                Start
              </>
            )}
          </Button>
          
          <Button
            onClick={resetExercise}
            variant="outline"
            size="lg"
            disabled={!isActive && cycleCount === 0}
          >
            <RotateClockwise size={16} />
          </Button>
        </div>

        {/* Progress */}
        {cycleCount > 0 && (
          <div className="space-y-2">
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>Progress</span>
              <span>{cycleCount} / {currentExercise.totalCycles} cycles</span>
            </div>
            <div className="w-full bg-muted rounded-full h-2">
              <motion.div
                className="bg-primary h-2 rounded-full"
                initial={{ width: 0 }}
                animate={{ width: `${(cycleCount / currentExercise.totalCycles) * 100}%` }}
                transition={{ duration: 0.5 }}
              />
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}