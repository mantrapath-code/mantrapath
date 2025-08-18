import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Button } from '@/components/ui/button'
import { 
  ChartLine, 
  HardDrives, 
  Battery, 
  WifiHigh, 
  Warning, 
  CheckCircle, 
  XCircle,
  ArrowClockwise
} from '@phosphor-icons/react'
import { motion, AnimatePresence } from 'framer-motion'
import { PerformanceMetrics, PerformanceAlert } from '@/hooks/usePerformanceMonitor'

interface PerformanceDashboardProps {
  metrics: PerformanceMetrics
  alerts: PerformanceAlert[]
  onRefresh: () => void
  className?: string
}

export function PerformanceDashboard({ 
  metrics, 
  alerts, 
  onRefresh, 
  className = "" 
}: PerformanceDashboardProps) {
  const [isExpanded, setIsExpanded] = useState(false)

  const getPerformanceColor = (score: number) => {
    if (score >= 80) return 'text-green-600'
    if (score >= 60) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getPerformanceStatus = (score: number) => {
    if (score >= 80) return 'Excellent'
    if (score >= 60) return 'Good'
    if (score >= 40) return 'Fair'
    return 'Poor'
  }

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const formatLatency = (ms: number) => {
    if (ms < 100) return `${ms.toFixed(0)}ms`
    if (ms < 1000) return `${ms.toFixed(1)}ms`
    return `${(ms / 1000).toFixed(2)}s`
  }

  const getAlertIcon = (type: PerformanceAlert['type']) => {
    switch (type) {
      case 'warning':
        return <Warning className="w-4 h-4 text-yellow-600" />
      case 'error':
        return <XCircle className="w-4 h-4 text-red-600" />
      case 'critical':
        return <Warning className="w-4 h-4 text-red-800" />
      default:
        return <CheckCircle className="w-4 h-4 text-green-600" />
    }
  }

  const getAlertColor = (type: PerformanceAlert['type']) => {
    switch (type) {
      case 'warning':
        return 'bg-yellow-50 border-yellow-200 text-yellow-800'
      case 'error':
        return 'bg-red-50 border-red-200 text-red-800'
      case 'critical':
        return 'bg-red-100 border-red-300 text-red-900'
      default:
        return 'bg-green-50 border-green-200 text-green-800'
    }
  }

  return (
    <Card className={`${className}`}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2 text-lg">
            <ChartLine className="w-5 h-5" />
            Performance Monitor
          </CardTitle>
          <div className="flex items-center gap-2">
            <Button
              onClick={onRefresh}
              size="sm"
              variant="ghost"
              className="h-8 w-8 p-0"
            >
              <ArrowClockwise className="w-4 h-4" />
            </Button>
            <Button
              onClick={() => setIsExpanded(!isExpanded)}
              size="sm"
              variant="ghost"
              className="h-8 px-2"
            >
              {isExpanded ? 'Collapse' : 'Expand'}
            </Button>
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Performance Score */}
        <div className="text-center p-4 bg-muted/50 rounded-lg">
          <div className="text-2xl font-bold mb-2">
            {Math.round((metrics.renderTime + metrics.memoryUsage / 1024 / 1024 + metrics.networkLatency) / 3)}
          </div>
          <div className="text-sm text-muted-foreground">Performance Score</div>
          <Progress 
            value={Math.max(0, 100 - (metrics.renderTime + metrics.memoryUsage / 1024 / 1024 + metrics.networkLatency) / 3)} 
            className="mt-2" 
          />
        </div>

        {/* Key Metrics Grid */}
        <div className="grid grid-cols-2 gap-4">
          {/* Render Time */}
          <div className="text-center p-3 bg-background border rounded-lg">
            <div className="flex items-center justify-center gap-2 mb-2">
              <ChartLine className="w-4 h-4 text-blue-600" />
              <span className="text-sm font-medium">Render Time</span>
            </div>
            <div className="text-lg font-bold text-blue-600">
              {formatLatency(metrics.renderTime)}
            </div>
            <div className="text-xs text-muted-foreground">Target: &lt;300ms</div>
          </div>

          {/* Memory Usage */}
          <div className="text-center p-3 bg-background border rounded-lg">
            <div className="flex items-center justify-center gap-2 mb-2">
              <ChartLine className="w-4 h-4 text-purple-600" />
              <span className="text-sm font-medium">Memory</span>
            </div>
            <div className="text-lg font-bold text-purple-600">
              {formatBytes(metrics.memoryUsage)}
            </div>
            <div className="text-xs text-muted-foreground">Target: &lt;100MB</div>
          </div>

          {/* FPS */}
          <div className="text-center p-3 bg-background border rounded-lg">
            <div className="flex items-center justify-center gap-2 mb-2">
              <ChartLine className="w-4 h-4 text-green-600" />
              <span className="text-sm font-medium">FPS</span>
            </div>
            <div className="text-lg font-bold text-green-600">
              {metrics.fps}
            </div>
            <div className="text-xs text-muted-foreground">Target: &gt;30</div>
          </div>

          {/* Network Latency */}
          <div className="text-center p-3 bg-background border rounded-lg">
            <div className="flex items-center justify-center gap-2 mb-2">
              <WifiHigh className="w-4 h-4 text-orange-600" />
              <span className="text-sm font-medium">Network</span>
            </div>
            <div className="text-lg font-bold text-orange-600">
              {formatLatency(metrics.networkLatency)}
            </div>
            <div className="text-xs text-muted-foreground">Target: &lt;500ms</div>
          </div>
        </div>

        {/* Alerts */}
        {alerts.length > 0 && (
          <div className="space-y-2">
            <h4 className="text-sm font-medium text-muted-foreground">Performance Alerts</h4>
            <AnimatePresence>
              {alerts.slice(0, isExpanded ? alerts.length : 3).map((alert, index) => (
                <motion.div
                  key={`${alert.metric}-${alert.timestamp}`}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  transition={{ delay: index * 0.1 }}
                  className={`p-3 rounded-lg border ${getAlertColor(alert.type)}`}
                >
                  <div className="flex items-center gap-2">
                    {getAlertIcon(alert.type)}
                    <span className="text-sm font-medium">{alert.metric}</span>
                    <Badge variant="outline" className="ml-auto">
                      {alert.type}
                    </Badge>
                  </div>
                  <p className="text-xs mt-1">{alert.message}</p>
                </motion.div>
              ))}
            </AnimatePresence>
            {alerts.length > 3 && !isExpanded && (
              <Button
                onClick={() => setIsExpanded(true)}
                size="sm"
                variant="ghost"
                className="w-full"
              >
                Show {alerts.length - 3} more alerts
              </Button>
            )}
          </div>
        )}

        {/* Expanded Metrics */}
        {isExpanded && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="space-y-4 pt-4 border-t"
          >
            <h4 className="text-sm font-medium text-muted-foreground">Detailed Metrics</h4>
            
            <div className="grid grid-cols-1 gap-3">
              {/* DOM Nodes */}
              <div className="flex items-center justify-between p-2 bg-muted/30 rounded">
                <span className="text-sm">DOM Nodes</span>
                <span className="text-sm font-mono">{metrics.domNodes.toLocaleString()}</span>
              </div>

              {/* Event Loop Delay */}
              <div className="flex items-center justify-between p-2 bg-muted/30 rounded">
                <span className="text-sm">Event Loop Delay</span>
                <span className="text-sm font-mono">{formatLatency(metrics.eventLoopDelay)}</span>
              </div>

              {/* Real-time Update Latency */}
              <div className="flex items-center justify-between p-2 bg-muted/30 rounded">
                <span className="text-sm">Real-time Updates</span>
                <span className="text-sm font-mono">{formatLatency(metrics.realTimeUpdateLatency)}</span>
              </div>

              {/* WebSocket Latency */}
              <div className="flex items-center justify-between p-2 bg-muted/30 rounded">
                <span className="text-sm">WebSocket Latency</span>
                <span className="text-sm font-mono">{formatLatency(metrics.webSocketLatency)}</span>
              </div>

              {/* UI Response Time */}
              <div className="flex items-center justify-between p-2 bg-muted/30 rounded">
                <span className="text-sm">UI Response Time</span>
                <span className="text-sm font-mono">{formatLatency(metrics.uiResponseTime)}</span>
              </div>
            </div>
          </motion.div>
        )}
      </CardContent>
    </Card>
  )
}
