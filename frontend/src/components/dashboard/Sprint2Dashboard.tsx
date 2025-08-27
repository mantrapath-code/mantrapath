/**
 * Sprint 2 Real-Time Dashboard Enhancement
 * Shows live data from backend services with real-time updates
 */

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { 
  Pulse, 
  Brain, 
  Heart, 
  WifiHigh, 
  WifiSlash,
  Clock,
  Lightning,
  Users,
  Chat,
  ArrowClockwise,
  CheckCircle,
  Warning
} from '@phosphor-icons/react'
import { motion, AnimatePresence } from 'framer-motion'
import { useServiceMonitor } from '@/hooks/useServiceMonitor'
import { useRealtime } from '@/contexts/RealtimeContext'
import { sprint2ApiService } from '@/services/sprint2-api'
import { useAuth } from '@/hooks/useAuth'
import { toast } from 'sonner'
import ServiceDebugPanel from '@/components/debug/ServiceDebugPanel'
import { apiService } from '@/services/api'
import { Sprint2TestControls } from '@/components/testing'

interface ServiceStatus {
  name: string
  port: number
  status: 'healthy' | 'degraded' | 'error'
  lastPing: string
  responseTime: number
}

export function Sprint2Dashboard() {
  const [assistanceData, setAssistanceData] = useState<any>(null)
  const [contextData, setContextData] = useState<any>(null)
  const { user } = useAuth()
  
  // Use service monitor for real connection status
  const {
    services,
    isMonitoring,
    checkAllServices,
    connectionStatus,
    healthyCount,
    totalCount,
    isAllHealthy
  } = useServiceMonitor()
  
  // Get real-time data from context (may be mock data)
  const { 
    userContext,
    currentEmotionState,
    riskScore,
    activeAssistance,
    voiceSession,
    currentMoodState
  } = useRealtime()

  // Fetch some real data from services
  useEffect(() => {
    const fetchLiveData = async () => {
      if (!user) return
      
      try {
        // Get real AI insights
        const insights = await apiService.getAIInsights()
        console.log('📊 AI Insights loaded:', insights)
        
        // Get current mood context
        const moodContext = await apiService.getCurrentMoodContext()
        console.log('🎭 Mood context loaded:', moodContext)
        
        // Get proactive assistance
        const assistance = await apiService.getProactiveAssistance()
        setAssistanceData(assistance)
        console.log('🤝 Assistance data loaded:', assistance)
        
        // Get user achievements/stats
        const achievements = await apiService.getCelebrationStats()
        console.log('🏆 Achievement stats loaded:', achievements)
        
      } catch (error) {
        console.error('Failed to fetch live data:', error)
      }
    }
    
    fetchLiveData()
    const interval = setInterval(fetchLiveData, 60000) // Every minute
    return () => clearInterval(interval)
  }, [user])

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'text-green-500'
      case 'degraded': return 'text-yellow-500'
      case 'error': return 'text-red-500'
      default: return 'text-gray-500'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy': return <CheckCircle className="text-green-500" size={16} />
      case 'degraded': return <Warning className="text-yellow-500" size={16} />
      case 'error': return <Warning className="text-red-500" size={16} />
      case 'connecting': return <Clock className="text-blue-500 animate-pulse" size={16} />
      default: return <Clock className="text-gray-500" size={16} />
    }
  }

  return (
    <div className="space-y-6">
      {/* Real-time connection status */}
      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg flex items-center gap-2">
              <Pulse className="text-purple-600" size={20} />
              Sprint 2 Live Status
            </CardTitle>
            <div className="flex items-center gap-2">
              {isAllHealthy ? (
                <WifiHigh className="text-green-500" size={16} />
              ) : (
                <WifiSlash className="text-red-500" size={16} />
              )}
              <Badge variant="outline" className="text-xs">
                {healthyCount}/{totalCount} healthy
              </Badge>
              <Button
                onClick={checkAllServices}
                disabled={isMonitoring}
                size="sm"
                variant="outline"
              >
                <ArrowClockwise 
                  className={isMonitoring ? 'animate-spin' : ''} 
                  size={14} 
                />
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {services.map((service) => {
              const isConnected = service.status === 'healthy'
              
              return (
                <motion.div
                  key={service.name}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="bg-gray-50 rounded-lg p-3"
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium">{service.name}</span>
                    {getStatusIcon(service.status)}
                  </div>
                  <div className="text-xs text-gray-500 space-y-1">
                    <div>Port: {service.port}</div>
                    <div className="flex items-center gap-1">
                      <div className={`w-2 h-2 rounded-full ${
                        isConnected ? 'bg-green-400' : 'bg-red-400'
                      }`} />
                      {isConnected ? 'Connected' : 'Disconnected'}
                    </div>
                    <div>
                      Response: {service.responseTime}ms
                    </div>
                    {service.errorMessage && (
                      <div className="text-red-500 text-xs">
                        {service.errorMessage}
                      </div>
                    )}
                  </div>
                </motion.div>
              )
            })}
          </div>
        </CardContent>
      </Card>

      {/* Live AI Insights */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        
        {/* Current Emotion State */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-base flex items-center gap-2">
              <Brain className="text-blue-500" size={18} />
              AI Emotion Detection
            </CardTitle>
          </CardHeader>
          <CardContent>
            {currentEmotionState || assistanceData ? (
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm">Current State</span>
                  <Badge variant="outline">
                    {currentEmotionState?.emotion || assistanceData?.mood || 'Neutral'}
                  </Badge>
                </div>
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span>Confidence</span>
                    <span>{Math.round((currentEmotionState?.confidence || assistanceData?.confidence || 0.75) * 100)}%</span>
                  </div>
                  <Progress value={(currentEmotionState?.confidence || assistanceData?.confidence || 0.75) * 100} className="h-2" />
                </div>
                <p className="text-xs text-gray-600">
                  Last updated: {new Date().toLocaleTimeString()}
                </p>
              </div>
            ) : (
              <div className="text-sm text-gray-500 text-center py-4">
                <div className="animate-pulse space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="h-4 bg-gray-200 rounded w-20"></div>
                    <div className="h-6 bg-gray-200 rounded-full w-16"></div>
                  </div>
                  <div className="h-2 bg-gray-200 rounded w-full"></div>
                  <div className="h-3 bg-gray-200 rounded w-32"></div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Active Assistance */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-base flex items-center gap-2">
              <Heart className="text-purple-500" size={18} />
              Proactive Assistance
            </CardTitle>
          </CardHeader>
          <CardContent>
            {activeAssistance || assistanceData ? (
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm">Status</span>
                  <Badge className="bg-purple-100 text-purple-700">
                    {activeAssistance?.assistanceType || assistanceData?.status || 'Ready'}
                  </Badge>
                </div>
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span>Evaluation Score</span>
                    <span>{Math.round((activeAssistance?.evaluationScore || assistanceData?.evaluation_score || 0.8) * 100)}%</span>
                  </div>
                  <Progress 
                    value={(activeAssistance?.evaluationScore || assistanceData?.evaluation_score || 0.8) * 100} 
                    className="h-2" 
                  />
                </div>
                <p className="text-xs text-gray-600">
                  Ready to provide personalized support
                </p>
              </div>
            ) : (
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm">Status</span>
                  <Badge variant="outline">Standby</Badge>
                </div>
                <div className="text-xs text-gray-600">
                  AI assistance is monitoring and ready to help when needed
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Service Health Summary */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-base flex items-center gap-2">
              <Lightning className="text-orange-500" size={18} />
              System Health
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm">Overall Status</span>
                <Badge variant={isAllHealthy ? "default" : "destructive"}>
                  {isAllHealthy ? 'Healthy' : 'Degraded'}
                </Badge>
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Services Online</span>
                  <span>{healthyCount}/{totalCount}</span>
                </div>
                <Progress value={(healthyCount / totalCount) * 100} className="h-2" />
              </div>
              <div className="text-xs text-gray-600">
                Average response: {services.length > 0 ? Math.round(services.reduce((sum, s) => sum + s.responseTime, 0) / services.length) : 0}ms
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Context Intelligence Summary */}
      {userContext && (
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-base flex items-center gap-2">
              <Lightning className="text-orange-500" size={18} />
              User Context Intelligence
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
              <div>
                <span className="font-medium">Engagement Level:</span>
                <div className="mt-1">
                  <Progress value={(userContext.context?.engagement || 0.5) * 100} className="h-2" />
                </div>
              </div>
              <div>
                <span className="font-medium">Recent Activity:</span>
                <p className="text-gray-600 mt-1">
                  {userContext.context?.recentActivities?.[0] || 'Analyzing...'}
                </p>
              </div>
              <div>
                <span className="font-medium">Last Context Update:</span>
                <p className="text-gray-600 mt-1">
                  {new Date(userContext.timestamp).toLocaleTimeString()}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Development Test Controls */}
      {import.meta.env.DEV && (
        <Sprint2TestControls />
      )}
      
      {/* Debug Panel for Development */}
      {import.meta.env.DEV && (
        <ServiceDebugPanel />
      )}
    </div>
  )
}
