import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { 
  ChartLine, 
  WifiHigh, 
  WifiX, 
  ArrowClockwise, 
  Clock,
  Heart,
  Brain,
  Lightning
} from '@phosphor-icons/react'
import { motion, AnimatePresence } from 'framer-motion'

interface RealTimeData {
  timestamp: string
  heartRate?: number
  stressLevel?: number
  aiConfidence?: number
  connectionStatus: 'connected' | 'disconnected' | 'connecting'
  lastUpdate: string
}

interface RealTimeWidgetProps {
  className?: string
}

export function RealTimeWidget({ className = '' }: RealTimeWidgetProps) {
  const [data, setData] = useState<RealTimeData>({
    timestamp: new Date().toISOString(),
    heartRate: 72,
    stressLevel: 3.2,
    aiConfidence: 85,
    connectionStatus: 'connected',
    lastUpdate: 'Just now'
  })
  
  const [isRefreshing, setIsRefreshing] = useState(false)
  
  // Simulate real-time data updates
  useEffect(() => {
    const interval = setInterval(() => {
      setData(prev => ({
        ...prev,
        timestamp: new Date().toISOString(),
        heartRate: Math.floor(Math.random() * 20) + 65, // 65-85 bpm
        stressLevel: Math.random() * 5 + 1, // 1-6 stress level
        aiConfidence: Math.floor(Math.random() * 20) + 75, // 75-95% confidence
        lastUpdate: 'Just now'
      }))
    }, 5000) // Update every 5 seconds
    
    return () => clearInterval(interval)
  }, [])
  
  const handleRefresh = async () => {
    setIsRefreshing(true)
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000))
    setData(prev => ({
      ...prev,
      timestamp: new Date().toISOString(),
      lastUpdate: 'Just now'
    }))
    setIsRefreshing(false)
  }
  
  const getConnectionIcon = () => {
    switch (data.connectionStatus) {
      case 'connected':
        return <WifiHigh className="w-4 h-4 text-green-600" />
      case 'connecting':
        return <ArrowClockwise className="w-4 h-4 text-yellow-600 animate-spin" />
      default:
        return <WifiX className="w-4 h-4 text-red-600" />
    }
  }
  
  const getConnectionColor = () => {
    switch (data.connectionStatus) {
      case 'connected':
        return 'bg-green-100 text-green-800 border-green-200'
      case 'connecting':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      default:
        return 'bg-red-100 text-red-800 border-red-200'
    }
  }
  
  const getStressColor = (level: number) => {
    if (level <= 2) return 'text-green-600'
    if (level <= 4) return 'text-yellow-600'
    return 'text-red-600'
  }
  
  return (
    <Card className={className}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2 text-lg">
            <ChartLine className="w-5 h-5 text-blue-600" />
            Live Metrics
          </CardTitle>
          <div className="flex items-center gap-2">
            <Badge variant="outline" className={`text-xs ${getConnectionColor()}`}>
              {getConnectionIcon()}
              <span className="ml-1 capitalize">{data.connectionStatus}</span>
            </Badge>
            <Button
              onClick={handleRefresh}
              disabled={isRefreshing}
              size="sm"
              variant="ghost"
              className="h-6 w-6 p-0"
            >
              <ArrowClockwise className={`w-3 h-3 ${isRefreshing ? 'animate-spin' : ''}`} />
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Real-time Metrics Grid */}
        <div className="grid grid-cols-1 gap-3">
          {/* Heart Rate */}
          <motion.div
            key={data.heartRate}
            initial={{ scale: 0.95 }}
            animate={{ scale: 1 }}
            className="flex items-center justify-between p-3 bg-red-50 rounded-lg"
          >
            <div className="flex items-center gap-2">
              <Heart className="w-5 h-5 text-red-500" />
              <span className="text-sm font-medium">Heart Rate</span>
            </div>
            <div className="text-right">
              <div className="text-lg font-bold text-red-600">{data.heartRate}</div>
              <div className="text-xs text-muted-foreground">bpm</div>
            </div>
          </motion.div>
          
          {/* Stress Level */}
          <motion.div
            key={data.stressLevel}
            initial={{ scale: 0.95 }}
            animate={{ scale: 1 }}
            className="flex items-center justify-between p-3 bg-orange-50 rounded-lg"
          >
            <div className="flex items-center gap-2">
              <Lightning className="w-5 h-5 text-orange-500" />
              <span className="text-sm font-medium">Stress Level</span>
            </div>
            <div className="text-right">
              <div className={`text-lg font-bold ${getStressColor(data.stressLevel || 0)}`}>
                {data.stressLevel?.toFixed(1)}
              </div>
              <div className="text-xs text-muted-foreground">/10</div>
            </div>
          </motion.div>
          
          {/* AI Confidence */}
          <motion.div
            key={data.aiConfidence}
            initial={{ scale: 0.95 }}
            animate={{ scale: 1 }}
            className="flex items-center justify-between p-3 bg-blue-50 rounded-lg"
          >
            <div className="flex items-center gap-2">
              <Brain className="w-5 h-5 text-blue-500" />
              <span className="text-sm font-medium">AI Confidence</span>
            </div>
            <div className="text-right">
              <div className="text-lg font-bold text-blue-600">{data.aiConfidence}%</div>
              <div className="text-xs text-muted-foreground">accuracy</div>
            </div>
          </motion.div>
        </div>
        
        {/* Last Update */}
        <div className="flex items-center justify-center gap-2 text-xs text-muted-foreground pt-2 border-t">
          <Clock className="w-3 h-3" />
          <span>Last updated: {data.lastUpdate}</span>
        </div>
        
        {/* Live Indicator */}
        <AnimatePresence>
          {data.connectionStatus === 'connected' && (
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
              className="flex items-center justify-center gap-2 p-2 bg-green-50 rounded-lg"
            >
              <motion.div
                animate={{ scale: [1, 1.2, 1] }}
                transition={{ duration: 2, repeat: Infinity }}
                className="w-2 h-2 bg-green-500 rounded-full"
              />
              <span className="text-xs text-green-700 font-medium">LIVE</span>
            </motion.div>
          )}
        </AnimatePresence>
      </CardContent>
    </Card>
  )
}
