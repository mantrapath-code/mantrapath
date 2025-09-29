import React, { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { 
  Brain, 
  Star, 
  TrendingUp, 
  TrendingDown,
  ArrowRight,
  CheckCircle,
  AlertCircle,
  Lightbulb,
  Target
} from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

interface Insight {
  id: string
  type: 'recommendation' | 'pattern' | 'achievement' | 'warning'
  title: string
  description: string
  confidence: number
  priority: 'high' | 'medium' | 'low'
  actionable?: boolean
  icon?: React.ReactNode
}

interface PersonalizedInsightsProps {
  className?: string
}

export function PersonalizedInsights({ className = '' }: PersonalizedInsightsProps) {
  const [selectedInsight, setSelectedInsight] = useState<string | null>(null)
  
  // Mock personalized insights data
  const insights: Insight[] = [
    {
      id: '1',
      type: 'pattern',
      title: 'Morning Mood Pattern',
      description: 'You tend to feel more positive in the mornings. Consider scheduling important tasks early.',
      confidence: 87,
      priority: 'high',
      actionable: true,
      icon: <TrendingUp className="w-4 h-4" />
    },
    {
      id: '2',
      type: 'recommendation',
      title: 'Stress Management',
      description: 'Based on your recent patterns, try 5-minute breathing exercises when stress levels peak.',
      confidence: 92,
      priority: 'high',
      actionable: true,
      icon: <Lightbulb className="w-4 h-4" />
    },
    {
      id: '3',
      type: 'achievement',
      title: 'Consistency Milestone',
      description: 'You\'ve maintained regular mood tracking for 2 weeks! This builds self-awareness.',
      confidence: 100,
      priority: 'medium',
      icon: <Star className="w-4 h-4" />
    },
    {
      id: '4',
      type: 'warning',
      title: 'Sleep Impact',
      description: 'Your mood dips correlate with shorter sleep duration. Prioritize 7-8 hours of sleep.',
      confidence: 78,
      priority: 'high',
      actionable: true,
      icon: <AlertCircle className="w-4 h-4" />
    }
  ]
  
  const getInsightColor = (type: Insight['type']) => {
    switch (type) {
      case 'recommendation':
        return 'bg-blue-50 border-blue-200 text-blue-800'
      case 'pattern':
        return 'bg-purple-50 border-purple-200 text-purple-800'
      case 'achievement':
        return 'bg-green-50 border-green-200 text-green-800'
      case 'warning':
        return 'bg-orange-50 border-orange-200 text-orange-800'
      default:
        return 'bg-gray-50 border-gray-200 text-gray-800'
    }
  }
  
  const getPriorityBadge = (priority: Insight['priority']) => {
    switch (priority) {
      case 'high':
        return <Badge variant="destructive" className="text-xs">High</Badge>
      case 'medium':
        return <Badge variant="default" className="text-xs">Medium</Badge>
      case 'low':
        return <Badge variant="secondary" className="text-xs">Low</Badge>
    }
  }
  
  const handleInsightAction = (insightId: string) => {
    const insight = insights.find(i => i.id === insightId)
    if (insight) {
      // Here you would implement the actual action
      console.log(`Taking action for insight: ${insight.title}`)
    }
  }
  
  return (
    <Card className={className}>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-lg">
          <Brain className="w-5 h-5 text-purple-600" />
          AI Insights
        </CardTitle>
        <p className="text-sm text-muted-foreground">
          Personalized recommendations based on your wellness data
        </p>
      </CardHeader>
      <CardContent className="space-y-3">
        <AnimatePresence>
          {insights.map((insight, index) => (
            <motion.div
              key={insight.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ delay: index * 0.1 }}
              className={`p-4 rounded-lg border cursor-pointer transition-all duration-200 ${getInsightColor(insight.type)} ${
                selectedInsight === insight.id ? 'ring-2 ring-primary/20' : ''
              }`}
              onClick={() => setSelectedInsight(selectedInsight === insight.id ? null : insight.id)}
            >
              <div className="flex items-start gap-3">
                <div className="flex-shrink-0 p-1.5 bg-white/60 rounded-full">
                  {insight.icon}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between mb-1">
                    <h4 className="font-medium text-sm truncate">{insight.title}</h4>
                    <div className="flex items-center gap-2 ml-2">
                      {getPriorityBadge(insight.priority)}
                      <Badge variant="outline" className="text-xs">
                        {insight.confidence}% confidence
                      </Badge>
                    </div>
                  </div>
                  <p className="text-xs leading-relaxed mb-2">{insight.description}</p>
                  
                  <AnimatePresence>
                    {selectedInsight === insight.id && (
                      <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        className="mt-3 pt-3 border-t border-white/40"
                      >
                        <div className="flex items-center justify-between">
                          <div className="text-xs text-muted-foreground">
                            Based on {Math.floor(Math.random() * 30) + 7} days of data
                          </div>
                          {insight.actionable && (
                            <Button
                              size="sm"
                              variant="outline"
                              className="h-7 text-xs"
                              onClick={(e) => {
                                e.stopPropagation()
                                handleInsightAction(insight.id)
                              }}
                            >
                              Take Action
                              <ArrowRight className="w-3 h-3 ml-1" />
                            </Button>
                          )}
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
        
        {/* Summary Stats */}
        <div className="pt-3 border-t">
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <div className="text-lg font-bold text-blue-600">
                {insights.filter(i => i.type === 'recommendation').length}
              </div>
              <div className="text-xs text-muted-foreground">Recommendations</div>
            </div>
            <div>
              <div className="text-lg font-bold text-purple-600">
                {insights.filter(i => i.type === 'pattern').length}
              </div>
              <div className="text-xs text-muted-foreground">Patterns</div>
            </div>
            <div>
              <div className="text-lg font-bold text-green-600">
                {insights.filter(i => i.type === 'achievement').length}
              </div>
              <div className="text-xs text-muted-foreground">Achievements</div>
            </div>
          </div>
        </div>
        
        {/* AI Confidence Indicator */}
        <div className="flex items-center justify-center gap-2 pt-2">
          <div className="flex items-center gap-1">
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 8, repeat: Infinity, ease: "linear" }}
              className="w-3 h-3 border-2 border-purple-600 border-t-transparent rounded-full"
            />
            <span className="text-xs text-muted-foreground">AI analyzing your patterns</span>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}




