import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { TrendingUp, TrendingDown, Activity } from 'lucide-react'
import { motion } from 'framer-motion'

interface MoodTrendChartProps {
  data: Array<{
    date: string
    mood: number
    timestamp: string
  }>
  trend: 'improving' | 'declining' | 'stable'
  className?: string
}

export function MoodTrendChart({ data, trend, className = '' }: MoodTrendChartProps) {
  const maxMood = Math.max(...data.map(d => d.mood), 1)
  const minMood = Math.min(...data.map(d => d.mood), 0)
  const avgMood = data.length > 0 ? data.reduce((sum, d) => sum + d.mood, 0) / data.length : 0
  
  const getTrendIcon = () => {
    switch (trend) {
      case 'improving':
        return <TrendingUp className="w-4 h-4 text-green-600" />
      case 'declining':
        return <TrendingDown className="w-4 h-4 text-red-600" />
      default:
        return <Activity className="w-4 h-4 text-blue-600" />
    }
  }
  
  const getTrendColor = () => {
    switch (trend) {
      case 'improving':
        return 'text-green-600 bg-green-50 border-green-200'
      case 'declining':
        return 'text-red-600 bg-red-50 border-red-200'
      default:
        return 'text-blue-600 bg-blue-50 border-blue-200'
    }
  }
  
  return (
    <Card className={className}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2 text-lg">
            📈 Mood Trend
          </CardTitle>
          <Badge variant="outline" className={`text-xs ${getTrendColor()}`}>
            {getTrendIcon()}
            <span className="ml-1 capitalize">{trend}</span>
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {data.length > 0 ? (
          <>
            {/* Simple Chart Visualization */}
            <div className="relative h-24 bg-gradient-to-r from-muted/20 to-muted/10 rounded-lg p-3">
              <div className="flex items-end justify-between h-full">
                {data.slice(-7).map((entry, index) => (
                  <motion.div
                    key={entry.date}
                    initial={{ height: 0 }}
                    animate={{ height: `${(entry.mood / 10) * 100}%` }}
                    transition={{ delay: index * 0.1 }}
                    className="flex-1 mx-0.5"
                  >
                    <div 
                      className={`w-full rounded-t-sm ${
                        entry.mood >= 7 ? 'bg-green-500' :
                        entry.mood >= 5 ? 'bg-yellow-500' :
                        entry.mood >= 3 ? 'bg-orange-500' : 'bg-red-500'
                      }`}
                      style={{ height: '100%' }}
                    />
                  </motion.div>
                ))}
              </div>
            </div>
            
            {/* Stats Summary */}
            <div className="grid grid-cols-3 gap-4 text-center">
              <div>
                <div className="text-lg font-bold text-green-600">{maxMood.toFixed(1)}</div>
                <div className="text-xs text-muted-foreground">Peak</div>
              </div>
              <div>
                <div className="text-lg font-bold text-primary">{avgMood.toFixed(1)}</div>
                <div className="text-xs text-muted-foreground">Average</div>
              </div>
              <div>
                <div className="text-lg font-bold text-orange-600">{minMood.toFixed(1)}</div>
                <div className="text-xs text-muted-foreground">Low</div>
              </div>
            </div>
            
            {/* Progress Indicator */}
            <div className="space-y-2">
              <div className="flex justify-between text-xs text-muted-foreground">
                <span>This week's progress</span>
                <span>{Math.round((avgMood / 10) * 100)}%</span>
              </div>
              <Progress value={(avgMood / 10) * 100} className="h-2" />
            </div>
            
            {/* Last 7 Days Labels */}
            <div className="flex justify-between text-xs text-muted-foreground">
              {data.slice(-7).map((entry) => (
                <span key={entry.date}>
                  {new Date(entry.timestamp).toLocaleDateString('en-US', { weekday: 'short' })}
                </span>
              ))}
            </div>
          </>
        ) : (
          <div className="text-center py-8">
            <Activity className="w-12 h-12 mx-auto text-muted-foreground mb-3" />
            <div className="text-sm text-muted-foreground">No trend data available</div>
            <div className="text-xs text-muted-foreground mt-1">
              Start tracking your mood to see trends
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}




