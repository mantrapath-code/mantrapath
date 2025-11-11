/**
 * Service Monitor Hook
 * Monitors backend services via HTTP health checks using centralized service endpoints
 */

import { useState, useEffect, useCallback } from 'react'
import { sprint2ApiService } from '@/services/sprint2-api'
import { useAuth } from '@/hooks/useAuth'
import { SERVICE_ENDPOINTS, serviceHealthUrl } from '@/config/serviceEndpoints'
import { getApiBaseUrl } from '@/config/api-config'

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

  const baseUrl = getApiBaseUrl() || 'http://api-gateway:8000'
  const monitoredKeys = [
    { key: 'api_gateway', name: 'API Gateway', port: 8000 },
    { key: 'ai_context', name: 'AI Context Store', port: 8013 },
    { key: 'ai_events', name: 'AI Event Processor', port: 8014 },
    { key: 'voice_events', name: 'Voice Processor', port: 8015 },
    { key: 'assistance', name: 'Assistance Engine', port: 8018 },
    { key: 'notification', name: 'Notifications', port: 8007 },
    { key: 'mood', name: 'Mood Service', port: 8003 },
    { key: 'chatbot', name: 'Chatbot Service', port: 8004 },
  ] as const

  const serviceEndpoints = monitoredKeys.map(m => ({
    name: m.name,
    port: m.port,
    key: m.key,
    healthUrl: m.key === 'api_gateway' ? `${baseUrl}/health` : serviceHealthUrl(m.key)
  }))

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
    
    const statusPromises = serviceEndpoints.map(endpoint => checkServiceHealth(endpoint))
    
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
