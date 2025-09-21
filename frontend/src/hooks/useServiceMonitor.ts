/**
 * Sprint 2 Real-Ti  const baseUrl = import.meta.env.VITE_API_GATEWAY_URL || import.meta.env.VITE_API_URL || 'http://localhost:8000'
  const services = [
    { name: 'API Gateway', port: 8000, url: baseUrl },
    { name: 'Auth Service', port: 8001, url: 'http://localhost:8001' },
    { name: 'Profile Service', port: 8002, url: 'http://localhost:8002' },
    { name: 'Mood Service', port: 8003, url: 'http://localhost:8003' },
    { name: 'Chatbot Service', port: 8004, url: 'http://localhost:8004' },
    { name: 'Content Service', port: 8005, url: 'http://localhost:8005' },
    { name: 'Community Service', port: 8006, url: 'http://localhost:8006' },
    { name: 'Notification Service', port: 8007, url: 'http://localhost:8007' },
    { name: 'ML Service', port: 8008, url: 'http://localhost:8008' },
    { name: 'AI Event Processor', port: 8014, url: 'http://localhost:8014' },
    { name: 'Assistance Engine', port: 8018, url: 'http://localhost:8018' }
  ]; Monitor
 * Monitors backend services via HTTP health checks since WebSocket may not be available
 */

import { useState, useEffect, useCallback } from 'react'
import { sprint2ApiService } from '@/services/sprint2-api'
import { useAuth } from '@/hooks/useAuth'

interface ServiceStatus {
  name: string
  port: number
  status: 'healthy' | 'degraded' | 'error' | 'connecting'
  lastCheck: string
  responseTime: number
  errorMessage?: string
}

export function useServiceMonitor() {
  const [services, setServices] = useState<ServiceStatus[]>([])
  const [isMonitoring, setIsMonitoring] = useState(false)
  const { user } = useAuth()

  const baseUrl = import.meta.env.VITE_API_GATEWAY_URL || import.meta.env.VITE_API_URL || 'http://localhost:8000'
  const serviceEndpoints = [
    { name: 'API Gateway', port: 8000, key: 'gateway', healthUrl: `${baseUrl}/health` },
    { name: 'AI Context Store', port: 8013, key: 'context', healthUrl: 'http://localhost:8013/health' },
    { name: 'AI Event Processor', port: 8014, key: 'aiEvents', healthUrl: 'http://localhost:8014/health' },
    { name: 'Voice Processor', port: 8015, key: 'voiceEvents', healthUrl: 'http://localhost:8015/health' },
    { name: 'Assistance Engine', port: 8018, key: 'assistance', healthUrl: 'http://localhost:8018/health' },
    { name: 'Notifications', port: 8007, key: 'notifications', healthUrl: 'http://localhost:8007/health' },
    { name: 'Mood Service', port: 8002, key: 'mood', healthUrl: 'http://localhost:8002/health' },
    { name: 'Chatbot Service', port: 8004, key: 'chatbot', healthUrl: 'http://localhost:8004/health' }
  ]

  const checkServiceHealth = useCallback(async (endpoint: typeof serviceEndpoints[0]): Promise<ServiceStatus> => {
    const startTime = Date.now()
    
    try {
      const response = await fetch(endpoint.healthUrl, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
        },
        // Add timeout
        signal: AbortSignal.timeout(5000)
      })
      
      const responseTime = Date.now() - startTime
      
      if (response.ok) {
        const data = await response.json()
        return {
          name: endpoint.name,
          port: endpoint.port,
          status: data.status === 'healthy' ? 'healthy' : 'degraded',
          lastCheck: new Date().toISOString(),
          responseTime,
        }
      } else {
        return {
          name: endpoint.name,
          port: endpoint.port,
          status: 'error',
          lastCheck: new Date().toISOString(),
          responseTime,
          errorMessage: `HTTP ${response.status}`
        }
      }
    } catch (error) {
      return {
        name: endpoint.name,
        port: endpoint.port,
        status: 'error',
        lastCheck: new Date().toISOString(),
        responseTime: Date.now() - startTime,
        errorMessage: error instanceof Error ? error.message : 'Connection failed'
      }
    }
  }, [])

  const checkAllServices = useCallback(async () => {
    setIsMonitoring(true)
    
    const statusPromises = serviceEndpoints.map(endpoint => 
      checkServiceHealth(endpoint)
    )
    
    try {
      const statuses = await Promise.all(statusPromises)
      setServices(statuses)
    } catch (error) {
      console.error('Failed to check services:', error)
    } finally {
      setIsMonitoring(false)
    }
  }, [checkServiceHealth])

  // Initial check and periodic monitoring
  useEffect(() => {
    checkAllServices()
    
    // Check every 30 seconds
    const interval = setInterval(checkAllServices, 30000)
    return () => clearInterval(interval)
  }, [checkAllServices])

  const getConnectionStatus = useCallback(() => {
    const statusMap: Record<string, 'connected' | 'connecting' | 'disconnected'> = {}
    
    serviceEndpoints.forEach(endpoint => {
      const service = services.find(s => s.port === endpoint.port)
      if (service) {
        statusMap[endpoint.key] = service.status === 'healthy' ? 'connected' : 'disconnected'
      } else {
        statusMap[endpoint.key] = 'connecting'
      }
    })
    
    return statusMap
  }, [services])

  const getHealthyCount = useCallback(() => {
    return services.filter(s => s.status === 'healthy').length
  }, [services])

  const getTotalCount = useCallback(() => {
    return serviceEndpoints.length
  }, [])

  return {
    services,
    isMonitoring,
    checkAllServices,
    connectionStatus: getConnectionStatus(),
    healthyCount: getHealthyCount(),
    totalCount: getTotalCount(),
    isAllHealthy: getHealthyCount() === getTotalCount()
  }
}
