/**
 * Sprint 2 Proactive Assistance Panel
 * Displays contextual assistance triggered by backend events
 */

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { 
  Heart, 
  Brain, 
  Clock, 
  X, 
  CheckCircle, 
  Warning,
  Lightbulb,
  User,
  Chat,
  ArrowRight
} from '@phosphor-icons/react'
import { useRealtime } from '@/contexts/RealtimeContext'
import { sprint2ApiService } from '@/services/sprint2-api'
import { useAuth } from '@/hooks/useAuth'
import { toast } from 'sonner'

interface AssistanceType {
  id: string
  type: 'wellness_check' | 'mood_support' | 'crisis_prevention' | 'mindfulness_reminder' | 'social_connection'
  title: string
  message: string
  priority: 'low' | 'medium' | 'high' | 'critical'
  culturalContext?: string
  suggestedActions: Array<{
    id: string
    label: string
    action: 'navigate' | 'api_call' | 'external_link'
    target: string
  }>
  estimatedHelpfulness: number
  timestamp: string
}

export function ProactiveAssistancePanel() {
  const [activeAssistance, setActiveAssistance] = useState<AssistanceType | null>(null)
  const [isVisible, setIsVisible] = useState(false)
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false)
  const { user } = useAuth()
  
  // Get real-time assistance data from context
  const { 
    activeAssistance: realtimeAssistance,
    assistanceHistory,
    connectionStatus 
  } = useRealtime()

  // Monitor for new assistance triggers
  useEffect(() => {
    if (realtimeAssistance && !activeAssistance) {
      // Transform backend assistance data to UI format
      const assistanceUI: AssistanceType = {
        id: `assistance-${Date.now()}`,
        type: realtimeAssistance.assistanceType === 'proactive' ? 'wellness_check' : 'mood_support',
        title: getAssistanceTitle(realtimeAssistance.assistanceType),
        message: realtimeAssistance.suggestion?.message || 'We notice you might benefit from some support right now.',
        priority: realtimeAssistance.suggestion?.urgency || 'medium',
        culturalContext: realtimeAssistance.suggestion?.culturalTone,
        suggestedActions: [], // Will be populated from backend
        estimatedHelpfulness: realtimeAssistance.evaluationScore || 0.7,
        timestamp: realtimeAssistance.timestamp || new Date().toISOString()
      }
      
      setActiveAssistance(assistanceUI)
      setIsVisible(true)
      setFeedbackSubmitted(false)
      
      // Show toast notification
      toast.info('💜 Proactive assistance available', {
        description: 'We have some personalized support ready for you',
        action: {
          label: 'View',
          onClick: () => setIsVisible(true)
        }
      })
    }
  }, [realtimeAssistance, activeAssistance])

  const getAssistanceTitle = (type: string): string => {
    const titles = {
      wellness_check: '💜 Wellness Check-in',
      mood_support: '🌈 Mood Support',
      crisis_prevention: '🚨 Immediate Support',
      mindfulness_reminder: '🧘 Mindfulness Moment',
      social_connection: '👥 Connect & Share'
    }
    return titles[type as keyof typeof titles] || '💡 Personalized Support'
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical': return 'bg-red-500 text-white'
      case 'high': return 'bg-orange-500 text-white'
      case 'medium': return 'bg-blue-500 text-white'
      case 'low': return 'bg-green-500 text-white'
      default: return 'bg-gray-500 text-white'
    }
  }

  const handleAcceptAssistance = async () => {
    if (!activeAssistance || !user) return
    
    try {
      // For now, use the evaluate API to record feedback
      await sprint2ApiService.evaluateAssistance(user.id, {
        assistance_id: activeAssistance.id,
        feedback_type: 'accepted',
        helpful: true,
        timestamp: new Date().toISOString()
      })
      
      setFeedbackSubmitted(true)
      toast.success('Thank you for accepting the assistance! 💜')
      
      // Keep panel open to show actions
    } catch (error) {
      console.error('Failed to send acceptance feedback:', error)
      toast.error('Failed to record feedback')
    }
  }

  const handleDeclineAssistance = async (reason?: string) => {
    if (!activeAssistance || !user) return
    
    try {
      // For now, use the evaluate API to record feedback
      await sprint2ApiService.evaluateAssistance(user.id, {
        assistance_id: activeAssistance.id,
        feedback_type: 'declined',
        helpful: false,
        reason,
        timestamp: new Date().toISOString()
      })
      
      setFeedbackSubmitted(true)
      toast.info('Understood. We\'ll adjust future suggestions.')
      
      // Close panel after decline
      setTimeout(() => {
        setIsVisible(false)
        setActiveAssistance(null)
      }, 2000)
    } catch (error) {
      console.error('Failed to send decline feedback:', error)
      toast.error('Failed to record feedback')
    }
  }

  const handleActionClick = (action: AssistanceType['suggestedActions'][0]) => {
    switch (action.action) {
      case 'navigate':
        // Would integrate with router for navigation
        console.log('Navigate to:', action.target)
        break
      case 'api_call':
        // Make API call
        console.log('API call to:', action.target)
        break
      case 'external_link':
        window.open(action.target, '_blank')
        break
    }
  }

  const handleDismiss = () => {
    setIsVisible(false)
    setTimeout(() => setActiveAssistance(null), 300)
  }

  if (!activeAssistance || !isVisible) {
    return null
  }

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: 50, scale: 0.95 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        exit={{ opacity: 0, y: 50, scale: 0.95 }}
        className="fixed bottom-6 right-6 z-50 max-w-sm"
      >
        <Card className="shadow-2xl border-2 border-purple-200 bg-gradient-to-br from-purple-50 to-pink-50">
          <CardHeader className="pb-3">
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-2">
                <Brain className="text-purple-600" size={20} />
                <CardTitle className="text-sm font-semibold text-purple-900">
                  {activeAssistance.title}
                </CardTitle>
              </div>
              <div className="flex items-center gap-2">
                <Badge className={`text-xs ${getPriorityColor(activeAssistance.priority)}`}>
                  {activeAssistance.priority}
                </Badge>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleDismiss}
                  className="h-6 w-6 p-0 hover:bg-purple-100"
                >
                  <X size={14} />
                </Button>
              </div>
            </div>
          </CardHeader>
          
          <CardContent className="space-y-4">
            <p className="text-sm text-gray-700 leading-relaxed">
              {activeAssistance.message}
            </p>
            
            {activeAssistance.culturalContext && (
              <div className="bg-purple-100 rounded-lg p-3">
                <p className="text-xs text-purple-800">
                  <User className="inline mr-1" size={12} />
                  Cultural Context: {activeAssistance.culturalContext}
                </p>
              </div>
            )}

            <div className="flex items-center gap-1 text-xs text-gray-500">
              <Clock size={12} />
              Estimated helpfulness: {Math.round(activeAssistance.estimatedHelpfulness * 100)}%
            </div>

            {!feedbackSubmitted ? (
              <div className="flex gap-2">
                <Button
                  onClick={handleAcceptAssistance}
                  size="sm"
                  className="flex-1 bg-purple-600 hover:bg-purple-700"
                >
                  <CheckCircle size={14} className="mr-1" />
                  Accept
                </Button>
                <Button
                  onClick={() => handleDeclineAssistance()}
                  variant="outline"
                  size="sm"
                  className="flex-1"
                >
                  <X size={14} className="mr-1" />
                  Not now
                </Button>
              </div>
            ) : (
              <div className="space-y-3">
                <div className="text-green-600 text-sm flex items-center gap-1">
                  <CheckCircle size={14} />
                  Thank you for your feedback!
                </div>
                
                {activeAssistance.suggestedActions.length > 0 && (
                  <div className="space-y-2">
                    <p className="text-xs font-medium text-gray-600">Suggested actions:</p>
                    {activeAssistance.suggestedActions.map((action) => (
                      <Button
                        key={action.id}
                        onClick={() => handleActionClick(action)}
                        variant="outline"
                        size="sm"
                        className="w-full justify-between text-xs"
                      >
                        {action.label}
                        <ArrowRight size={12} />
                      </Button>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Connection status indicator */}
            <div className="flex items-center gap-1 text-xs text-gray-400 pt-2 border-t">
              <div className={`w-2 h-2 rounded-full ${
                connectionStatus?.['assistance'] === 'connected' 
                  ? 'bg-green-400' 
                  : 'bg-orange-400'
              }`} />
              {connectionStatus?.['assistance'] === 'connected' ? 'Live assistance' : 'Cached assistance'}
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </AnimatePresence>
  )
}
