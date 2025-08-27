/**
 * Live Dashboard - Sprint 2 Implementation
 * Real-time display of backend service data with mobile-first design
 */

import React from 'react'
import { motion } from 'framer-motion'
import { Heart, Brain, Mic, Activity, AlertTriangle, CheckCircle, Clock } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card'
import { Badge } from '../ui/badge'
import { Progress } from '../ui/progress'
import { useRealtime, useRealtimeActions } from '../../contexts/RealtimeContext'
import { useResponsiveLayout } from '../../hooks/useResponsiveLayout'
import { cn } from '../../lib/utils'

export function LiveDashboard() {
  const {
    userContext,
    currentEmotionState,
    riskScore,
    activeAssistance,
    assistanceHistory,
    voiceActivityLevel,
    currentMoodState,
    moodPatterns,
    connectionStatus,
    serviceHealth,
    crisisAlerts
  } = useRealtime()
  
  const { isConnected, connectionError } = useRealtimeActions()
  const { currentLayout } = useResponsiveLayout()
  
  const isMobile = currentLayout.deviceType === 'mobile'
  
  return (
    <div className="space-y-6 p-4">
      {/* Connection Health Indicator - Fixed position on mobile */}
      <ConnectionHealthIndicator 
        services={connectionStatus}
        serviceHealth={serviceHealth}
        isConnected={isConnected}
        connectionError={connectionError}
        className={cn(
          isMobile ? "fixed top-4 right-4 z-50" : "mb-6"
        )}
      />
      
      {/* Crisis Alerts - High Priority */}
      {crisisAlerts.length > 0 && (
        <CrisisAlertPanel alerts={crisisAlerts} />
      )}
      
      {/* Main Dashboard Grid */}
      <div className={cn(
        "grid gap-6",
        isMobile ? "grid-cols-1" : "grid-cols-1 md:grid-cols-2 lg:grid-cols-3"
      )}>
        
        {/* Live Mood State (from Mood Service Port 8002) */}
        <LiveMoodIndicator 
          emotion={currentEmotionState}
          moodState={currentMoodState}
          patterns={moodPatterns}
          servicePort={8002}
        />
        
        {/* Proactive Assistance Status (from Assistance Engine Port 8018) */}
        <ProactiveAssistancePanel
          activeAssistance={activeAssistance}
          history={assistanceHistory.slice(-5)} // Show last 5
          servicePort={8018}
        />
        
        {/* AI Context Insights (from AI Context Store Port 8013) */}
        <ContextualInsights 
          context={userContext}
          riskScore={riskScore}
          servicePort={8013}
        />
        
        {/* Live Voice Activity (from Voice Processor Port 8015 + Gateway Port 8000) */}
        <VoiceActivityIndicator 
          activityLevel={voiceActivityLevel}
          servicePort={8015}
        />
        
      </div>
    </div>
  )
}

// Connection Health Component
function ConnectionHealthIndicator({ 
  services, 
  serviceHealth,
  isConnected, 
  connectionError,
  className 
}: { 
  services: Record<string, string>
  serviceHealth: Record<string, string>
  isConnected: boolean
  connectionError: string | null
  className?: string 
}) {
  const connectedCount = Object.values(services).filter(status => status === 'connected').length
  const totalServices = Object.keys(services).length
  
  return (
    <Card className={cn("border-none shadow-sm", className)}>
      <CardContent className="p-4">
        <div className="flex items-center justify-between mb-3">
          <h4 className="text-sm font-medium">Backend Services</h4>
          <Badge variant={isConnected ? 'default' : 'destructive'} className="text-xs">
            {connectedCount}/{totalServices} Connected
          </Badge>
        </div>
        
        <div className="space-y-2">
          {Object.entries(services).map(([service, status]) => {
            const health = serviceHealth[service] || 'unknown'
            const port = getServicePort(service)
            
            return (
              <div key={service} className="flex items-center gap-2 text-xs">
                <div className={cn(
                  "w-2 h-2 rounded-full",
                  status === 'connected' ? 'bg-green-500' : 
                  status === 'connecting' ? 'bg-yellow-500 animate-pulse' : 
                  'bg-red-500'
                )} />
                <span className="capitalize flex-1">{service}</span>
                <span className="text-muted-foreground">{port}</span>
                <Badge 
                  variant="outline" 
                  className={cn(
                    "text-xs px-1 py-0",
                    health === 'healthy' ? 'border-green-200 text-green-600' :
                    health === 'degraded' ? 'border-yellow-200 text-yellow-600' :
                    'border-red-200 text-red-600'
                  )}
                >
                  {health}
                </Badge>
              </div>
            )
          })}
        </div>
        
        {connectionError && (
          <div className="mt-2 text-xs text-red-600 bg-red-50 p-2 rounded">
            {connectionError}
          </div>
        )}
      </CardContent>
    </Card>
  )
}

// Crisis Alert Panel
function CrisisAlertPanel({ alerts }: { alerts: any[] }) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="bg-red-50 border border-red-200 rounded-lg p-4"
    >
      <div className="flex items-center gap-2 mb-2">
        <AlertTriangle className="w-5 h-5 text-red-600" />
        <h3 className="font-medium text-red-800">Crisis Alert</h3>
        <Badge variant="destructive">{alerts.length}</Badge>
      </div>
      <div className="space-y-2">
        {alerts.slice(0, 3).map((alert, index) => (
          <div key={index} className="text-sm text-red-700">
            <span className="font-medium">{alert.severity}</span> severity detected
            {alert.immediateActions?.length > 0 && (
              <div className="text-xs mt-1">
                Action: {alert.immediateActions[0]}
              </div>
            )}
          </div>
        ))}
      </div>
    </motion.div>
  )
}

// Live Mood Indicator Component
function LiveMoodIndicator({ 
  emotion, 
  moodState, 
  patterns, 
  servicePort 
}: { 
  emotion: any
  moodState: any
  patterns: any[]
  servicePort: number 
}) {
  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-sm font-medium flex items-center gap-2">
          <Heart className="w-4 h-4 text-red-500" />
          Live Mood State
          <Badge variant="outline" className="text-xs">{servicePort}</Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {emotion && (
          <div>
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm text-muted-foreground">Emotion</span>
              <Badge>{emotion.emotion}</Badge>
            </div>
            <Progress value={emotion.confidence * 100} className="h-2" />
            <div className="text-xs text-muted-foreground mt-1">
              Confidence: {Math.round(emotion.confidence * 100)}%
            </div>
          </div>
        )}
        
        {moodState && (
          <div>
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm text-muted-foreground">Mood Value</span>
              <span className="text-sm font-medium">{moodState.moodValue}/10</span>
            </div>
            <Progress value={moodState.moodValue * 10} className="h-2" />
          </div>
        )}
        
        {patterns.length > 0 && (
          <div>
            <div className="text-sm text-muted-foreground mb-2">Recent Patterns</div>
            <div className="space-y-1">
              {patterns.slice(0, 2).map((pattern, index) => (
                <div key={index} className="text-xs p-2 bg-muted rounded">
                  <div className="font-medium">{pattern.pattern?.type}</div>
                  <div className="text-muted-foreground">{pattern.pattern?.description}</div>
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

// Proactive Assistance Panel
function ProactiveAssistancePanel({ 
  activeAssistance, 
  history, 
  servicePort 
}: { 
  activeAssistance: any
  history: any[]
  servicePort: number 
}) {
  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-sm font-medium flex items-center gap-2">
          <Brain className="w-4 h-4 text-blue-500" />
          Proactive Assistance
          <Badge variant="outline" className="text-xs">{servicePort}</Badge>
          {activeAssistance && (
            <Badge className="text-xs bg-green-100 text-green-700">
              {activeAssistance.responseTimeMs}ms
            </Badge>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {activeAssistance ? (
          <div className="p-3 bg-blue-50 rounded-lg">
            <div className="font-medium text-sm mb-1">
              {activeAssistance.assistanceType} assistance
            </div>
            <div className="text-sm text-muted-foreground mb-2">
              {activeAssistance.suggestion?.message}
            </div>
            <div className="flex gap-2">
              <Badge variant="outline" className="text-xs">
                {activeAssistance.suggestion?.urgency}
              </Badge>
              <Badge variant="outline" className="text-xs">
                Score: {Math.round(activeAssistance.evaluationScore * 100)}%
              </Badge>
            </div>
          </div>
        ) : (
          <div className="text-sm text-muted-foreground text-center py-4">
            No active assistance
          </div>
        )}
        
        {history.length > 0 && (
          <div>
            <div className="text-sm text-muted-foreground mb-2">Recent History</div>
            <div className="space-y-2">
              {history.map((item, index) => (
                <div key={index} className="text-xs p-2 bg-muted rounded flex justify-between items-center">
                  <span>{item.suggestion?.category}</span>
                  <Badge variant="outline" className="text-xs">
                    {item.responseTimeMs}ms
                  </Badge>
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

// Contextual Insights Component
function ContextualInsights({ 
  context, 
  riskScore, 
  servicePort 
}: { 
  context: any
  riskScore: any
  servicePort: number 
}) {
  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-sm font-medium flex items-center gap-2">
          <Activity className="w-4 h-4 text-green-500" />
          AI Context Insights
          <Badge variant="outline" className="text-xs">{servicePort}</Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {context?.context && (
          <div className="grid grid-cols-2 gap-2">
            <div className="text-center">
              <div className="text-lg font-medium">{context.context.mood}</div>
              <div className="text-xs text-muted-foreground">Mood</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-medium">{context.context.energy}</div>
              <div className="text-xs text-muted-foreground">Energy</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-medium">{context.context.stress}</div>
              <div className="text-xs text-muted-foreground">Stress</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-medium">{context.context.engagement}</div>
              <div className="text-xs text-muted-foreground">Engagement</div>
            </div>
          </div>
        )}
        
        {riskScore && (
          <div>
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm text-muted-foreground">Risk Score</span>
              <Badge 
                variant={riskScore.severity === 'high' ? 'destructive' : 
                       riskScore.severity === 'medium' ? 'default' : 'secondary'}
              >
                {riskScore.severity}
              </Badge>
            </div>
            <Progress value={riskScore.riskScore * 100} className="h-2" />
            <div className="text-xs text-muted-foreground mt-1">
              Score: {Math.round(riskScore.riskScore * 100)}%
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

// Voice Activity Indicator
function VoiceActivityIndicator({ 
  activityLevel, 
  servicePort 
}: { 
  activityLevel: number
  servicePort: number 
}) {
  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-sm font-medium flex items-center gap-2">
          <Mic className="w-4 h-4 text-purple-500" />
          Voice Activity
          <Badge variant="outline" className="text-xs">{servicePort}</Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="text-center">
          <div className={cn(
            "w-16 h-16 rounded-full mx-auto mb-2 flex items-center justify-center",
            activityLevel > 0.7 ? "bg-green-100" :
            activityLevel > 0.3 ? "bg-yellow-100" :
            "bg-gray-100"
          )}>
            <Mic className={cn(
              "w-8 h-8",
              activityLevel > 0.7 ? "text-green-600" :
              activityLevel > 0.3 ? "text-yellow-600" :
              "text-gray-400"
            )} />
          </div>
          <div className="text-lg font-medium">{Math.round(activityLevel * 100)}%</div>
          <div className="text-xs text-muted-foreground">Activity Level</div>
        </div>
        
        <Progress value={activityLevel * 100} className="h-2" />
        
        <div className="text-xs text-center text-muted-foreground">
          {activityLevel > 0.7 ? "High activity detected" :
           activityLevel > 0.3 ? "Moderate activity" :
           "Low activity"}
        </div>
      </CardContent>
    </Card>
  )
}

// Helper function to get service port
function getServicePort(service: string): string {
  const ports: Record<string, string> = {
    notifications: ':3001',
    assistance: ':8018',
    aiContext: ':8013',
    aiEvents: ':8014',
    voiceEvents: ':8015',
    voice: ':8000',
    mood: ':8002',
    chat: ':8004'
  }
  return ports[service] || ''
}
