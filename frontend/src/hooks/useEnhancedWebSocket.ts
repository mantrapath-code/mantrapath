import { useEffect, useRef, useState, useCallback } from 'react'
import { toast } from 'sonner'
import { usePerformanceMonitor } from './usePerformanceMonitor'

export interface WebSocketMessage {
  type: string
  data: any
  timestamp: string
  id?: string
  priority?: 'low' | 'normal' | 'high' | 'critical'
}

export interface WebSocketConnection {
  id: string
  url: string
  socket: WebSocket
  status: 'connecting' | 'connected' | 'disconnected' | 'error'
  lastHeartbeat: number
  reconnectAttempts: number
  messageQueue: WebSocketMessage[]
}

export interface WebSocketManager {
  connections: Map<string, WebSocketConnection>
  connectionPool: ConnectionPool
  healthMonitor: HealthMonitor
  eventRouter: EventRouter
  reconnectStrategy: ReconnectStrategy
}

export interface ConnectionPool {
  maxConnections: number
  activeConnections: number
  connectionQueue: ConnectionRequest[]
  createConnection: (endpoint: string) => Promise<WebSocketConnection>
  releaseConnection: (connectionId: string) => void
}

export interface ConnectionRequest {
  endpoint: string
  priority: number
  timestamp: number
}

export interface HealthMonitor {
  checkConnectionHealth: (connectionId: string) => boolean
  sendHeartbeat: (connectionId: string) => void
  getConnectionStats: () => ConnectionStats
}

export interface ConnectionStats {
  totalConnections: number
  healthyConnections: number
  failedConnections: number
  averageLatency: number
}

export interface EventRouter {
  routes: Map<string, EventHandler[]>
  addRoute: (eventType: string, handler: EventHandler) => void
  removeRoute: (eventType: string, handler: EventHandler) => void
  routeEvent: (message: WebSocketMessage) => void
}

export interface EventHandler {
  id: string
  handler: (message: WebSocketMessage) => void
  priority: number
}

export interface ReconnectStrategy {
  maxAttempts: number
  baseDelay: number
  maxDelay: number
  backoffMultiplier: number
  shouldReconnect: (connection: WebSocketConnection) => boolean
  calculateDelay: (attempt: number) => number
}

export interface WebSocketHookReturn {
  isConnected: boolean
  connectionError: string | null
  sendMessage: (message: WebSocketMessage, connectionId?: string) => void
  lastMessage: WebSocketMessage | null
  connectionStats: ConnectionStats
  addEventHandler: (eventType: string, handler: EventHandler) => void
  removeEventHandler: (eventType: string, handlerId: string) => void
  reconnectAll: () => void
  getConnectionHealth: (connectionId: string) => boolean
}

const DEFAULT_RECONNECT_STRATEGY: ReconnectStrategy = {
  maxAttempts: 5,
  baseDelay: 1000,
  maxDelay: 30000,
  backoffMultiplier: 2,
  shouldReconnect: (connection) => connection.reconnectAttempts < 5,
  calculateDelay: (attempt) => Math.min(
    1000 * Math.pow(2, attempt),
    30000
  )
}

export function useEnhancedWebSocket(
  urls: string[] = [],
  options: {
    maxConnections?: number
    heartbeatInterval?: number
    reconnectStrategy?: Partial<ReconnectStrategy>
  } = {}
): WebSocketHookReturn {
  const [isConnected, setIsConnected] = useState(false)
  const [connectionError, setConnectionError] = useState<string | null>(null)
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null)
  const [connectionStats, setConnectionStats] = useState<ConnectionStats>({
    totalConnections: 0,
    healthyConnections: 0,
    failedConnections: 0,
    averageLatency: 0
  })

  const connectionsRef = useRef<Map<string, WebSocketConnection>>(new Map())
  const eventHandlersRef = useRef<Map<string, EventHandler[]>>(new Map())
  const reconnectTimeoutsRef = useRef<Map<string, NodeJS.Timeout>>(new Map())
  const heartbeatIntervalsRef = useRef<Map<string, NodeJS.Timeout>>(new Map())
  
  const { recordMetric } = usePerformanceMonitor()
  
  const maxConnections = options.maxConnections || 3
  const heartbeatInterval = options.heartbeatInterval || 30000
  const reconnectStrategy = { ...DEFAULT_RECONNECT_STRATEGY, ...options.reconnectStrategy }

  // Connection Pool Management
  const createConnection = useCallback(async (endpoint: string): Promise<WebSocketConnection> => {
    const connectionId = `ws_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    
    return new Promise((resolve, reject) => {
      try {
        // Construct proper WebSocket URL with user ID and authentication
        let wsUrl = endpoint
        
        // Get auth token and user data for WebSocket connection
        const token = localStorage.getItem('authToken') || localStorage.getItem('mantrapath_token')
        const userData = localStorage.getItem('user') || localStorage.getItem('user_data')
        
        if (!token || !userData) {
          // Silently skip connection when no authentication is available
          reject(new Error('No authentication data available'))
          return
        }
        
        let userId = 'anonymous'
        try {
          const user = JSON.parse(userData)
          userId = user.id || 'anonymous'
        } catch (e) {
          // Silently handle invalid user data
          reject(new Error('Invalid user data for WebSocket connection'))
          return
        }
        
        // Construct proper WebSocket URL: ws://host:port/ws/{user_id}?token={token}
        const wsUrlWithPath = `${endpoint}/ws/${userId}`
        const wsUrlWithAuth = `${wsUrlWithPath}?token=${token}`
        
        const socket = new WebSocket(wsUrlWithAuth)
        const connection: WebSocketConnection = {
          id: connectionId,
          url: wsUrlWithAuth,
          socket,
          status: 'connecting',
          lastHeartbeat: Date.now(),
          reconnectAttempts: 0,
          messageQueue: []
        }

        // Set a connection timeout
        const connectionTimeout = setTimeout(() => {
          if (connection.status === 'connecting') {
            connection.status = 'error'
            socket.close()
            reject(new Error('Connection timeout'))
          }
        }, 10000) // 10 second timeout

        socket.onopen = () => {
          clearTimeout(connectionTimeout)
          connection.status = 'connected'
          setIsConnected(true)
          setConnectionError(null)
          startHeartbeat(connectionId)
          updateConnectionStats()
          resolve(connection)
        }

        socket.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data)
            setLastMessage(message)
            routeEvent(message)
            recordMetric('webSocketLatency', Date.now() - new Date(message.timestamp).getTime())
          } catch (error) {
            console.error('Failed to parse WebSocket message:', error)
          }
        }

        socket.onclose = (event) => {
          clearTimeout(connectionTimeout)
          connection.status = 'disconnected'
          stopHeartbeat(connectionId)
          
          if (event.code !== 1000 && reconnectStrategy.shouldReconnect(connection)) {
            scheduleReconnect(connection)
          }
          
          updateConnectionStats()
        }

        socket.onerror = (error) => {
          clearTimeout(connectionTimeout)
          connection.status = 'error'
          console.warn(`WebSocket connection error to ${endpoint}:`, error)
          updateConnectionStats()
          reject(error)
        }

        connectionsRef.current.set(connectionId, connection)
        
      } catch (error) {
        reject(error)
      }
    })
  }, [reconnectStrategy])

  const releaseConnection = useCallback((connectionId: string) => {
    const connection = connectionsRef.current.get(connectionId)
    if (connection) {
      connection.socket.close(1000, 'Connection released')
      connectionsRef.current.delete(connectionId)
      stopHeartbeat(connectionId)
      clearReconnectTimeout(connectionId)
      updateConnectionStats()
    }
  }, [])

  // Health Monitoring
  const startHeartbeat = useCallback((connectionId: string) => {
    const interval = setInterval(() => {
      const connection = connectionsRef.current.get(connectionId)
      if (connection && connection.status === 'connected') {
        connection.lastHeartbeat = Date.now()
        try {
          connection.socket.send(JSON.stringify({
            type: 'heartbeat',
            timestamp: new Date().toISOString()
          }))
        } catch (error) {
          console.error('Heartbeat failed:', error)
          connection.status = 'error'
        }
      }
    }, heartbeatInterval)
    
    heartbeatIntervalsRef.current.set(connectionId, interval)
  }, [heartbeatInterval])

  const stopHeartbeat = useCallback((connectionId: string) => {
    const interval = heartbeatIntervalsRef.current.get(connectionId)
    if (interval) {
      clearInterval(interval)
      heartbeatIntervalsRef.current.delete(connectionId)
    }
  }, [])

  const checkConnectionHealth = useCallback((connectionId: string): boolean => {
    const connection = connectionsRef.current.get(connectionId)
    if (!connection) return false
    
    const timeSinceHeartbeat = Date.now() - connection.lastHeartbeat
    return connection.status === 'connected' && timeSinceHeartbeat < heartbeatInterval * 2
  }, [heartbeatInterval])

  // Reconnection Strategy
  const scheduleReconnect = useCallback((connection: WebSocketConnection) => {
    if (connection.reconnectAttempts >= reconnectStrategy.maxAttempts) {
      console.log(`Max reconnection attempts reached for ${connection.id}`)
      return
    }

    const delay = reconnectStrategy.calculateDelay(connection.reconnectAttempts)
    const timeout = setTimeout(() => {
      reconnectConnection(connection)
    }, delay)

    reconnectTimeoutsRef.current.set(connection.id, timeout)
  }, [reconnectStrategy])

  const reconnectConnection = useCallback(async (connection: WebSocketConnection) => {
    try {
      connection.reconnectAttempts++
      connection.status = 'connecting'
      
      const newSocket = new WebSocket(connection.url)
      connection.socket = newSocket
      
      // Re-attach event handlers
      newSocket.onopen = () => {
        connection.status = 'connected'
        connection.reconnectAttempts = 0
        setIsConnected(true)
        setConnectionError(null)
        startHeartbeat(connection.id)
        updateConnectionStats()
        
        // Re-send queued messages
        connection.messageQueue.forEach(message => {
          try {
            newSocket.send(JSON.stringify(message))
          } catch (error) {
            console.error('Failed to re-send queued message:', error)
          }
        })
        connection.messageQueue = []
      }
      
      // Re-attach other event handlers...
      newSocket.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data)
          setLastMessage(message)
          routeEvent(message)
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error)
        }
      }
      
      newSocket.onclose = (event) => {
        connection.status = 'disconnected'
        stopHeartbeat(connection.id)
        
        if (event.code !== 1000 && reconnectStrategy.shouldReconnect(connection)) {
          scheduleReconnect(connection)
        }
        
        updateConnectionStats()
      }
      
      newSocket.onerror = (error) => {
        connection.status = 'error'
        setConnectionError(`Reconnection error: ${error}`)
        updateConnectionStats()
      }
      
    } catch (error) {
      console.error('Reconnection failed:', error)
      connection.status = 'error'
      updateConnectionStats()
    }
  }, [reconnectStrategy, startHeartbeat, stopHeartbeat])

  const clearReconnectTimeout = useCallback((connectionId: string) => {
    const timeout = reconnectTimeoutsRef.current.get(connectionId)
    if (timeout) {
      clearTimeout(timeout)
      reconnectTimeoutsRef.current.delete(connectionId)
    }
  }, [])

  // Event Routing
  const routeEvent = useCallback((message: WebSocketMessage) => {
    const handlers = eventHandlersRef.current.get(message.type) || []
    const sortedHandlers = handlers.sort((a, b) => b.priority - a.priority)
    
    sortedHandlers.forEach(handler => {
      try {
        handler.handler(message)
      } catch (error) {
        console.error(`Error in event handler ${handler.id}:`, error)
      }
    })
  }, [])

  const addEventHandler = useCallback((eventType: string, handler: EventHandler) => {
    const handlers = eventHandlersRef.current.get(eventType) || []
    handlers.push(handler)
    eventHandlersRef.current.set(eventType, handlers)
  }, [])

  const removeEventHandler = useCallback((eventType: string, handlerId: string) => {
    const handlers = eventHandlersRef.current.get(eventType) || []
    const filteredHandlers = handlers.filter(h => h.id !== handlerId)
    eventHandlersRef.current.set(eventType, filteredHandlers)
  }, [])

  // Message Sending
  const sendMessage = useCallback((message: WebSocketMessage, connectionId?: string) => {
    const targetConnection = connectionId 
      ? connectionsRef.current.get(connectionId)
      : Array.from(connectionsRef.current.values()).find(c => c.status === 'connected')
    
    if (targetConnection && targetConnection.status === 'connected') {
      try {
        targetConnection.socket.send(JSON.stringify(message))
      } catch (error) {
        console.error('Failed to send message:', error)
        // Queue message for later if connection fails
        targetConnection.messageQueue.push(message)
      }
    } else {
      // Queue message if no connection available
      const availableConnection = Array.from(connectionsRef.current.values())[0]
      if (availableConnection) {
        availableConnection.messageQueue.push(message)
      }
    }
  }, [])

  // Statistics and Health
  const updateConnectionStats = useCallback(() => {
    const connections = Array.from(connectionsRef.current.values())
    const healthyConnections = connections.filter(c => checkConnectionHealth(c.id)).length
    const failedConnections = connections.filter(c => c.status === 'error').length
    
    setConnectionStats({
      totalConnections: connections.length,
      healthyConnections,
      failedConnections,
      averageLatency: 0 // TODO: Calculate from actual measurements
    })
    
    setIsConnected(healthyConnections > 0)
  }, [checkConnectionHealth])

  const reconnectAll = useCallback(() => {
    connectionsRef.current.forEach(connection => {
      if (connection.status !== 'connected') {
        scheduleReconnect(connection)
      }
    })
  }, [scheduleReconnect])

  const getConnectionHealth = useCallback((connectionId: string): boolean => {
    return checkConnectionHealth(connectionId)
  }, [checkConnectionHealth])

  // Initialize connections
  useEffect(() => {
    const initializeConnections = async () => {
      if (urls.length === 0) {
        return
      }

      // Check if authentication data is available before attempting connections
      const token = localStorage.getItem('authToken') || localStorage.getItem('mantrapath_token')
      const userData = localStorage.getItem('user') || localStorage.getItem('user_data')
      
      if (!token || !userData) {
        // Silently skip WebSocket initialization when no authentication is available
        return
      }

      try {
        for (const url of urls) {
          if (connectionsRef.current.size < maxConnections) {
            try {
              await createConnection(url)
            } catch (connectionError) {
              // Silently handle connection failures without logging
              // This prevents console spam when authentication is missing
            }
          }
        }
      } catch (error) {
        // Silently handle initialization failures
      }
    }

    initializeConnections()

    return () => {
      // Cleanup all connections
      connectionsRef.current.forEach(connection => {
        releaseConnection(connection.id)
      })
    }
  }, [urls, maxConnections, createConnection, releaseConnection])

  // Add default event handlers for common message types
  useEffect(() => {
    const defaultHandlers: EventHandler[] = [
      {
        id: 'default_notification',
        handler: (message) => {
          if (message.type === 'notification') {
            toast.info(message.data.title, {
              description: message.data.message
            })
          }
        },
        priority: 1
      },
      {
        id: 'default_mood_alert',
        handler: (message) => {
          if (message.type === 'mood_pattern_alert') {
            toast.warning('Mood Pattern Alert', {
              description: message.data.message
            })
          }
        },
        priority: 1
      },
      {
        id: 'default_breathing_reminder',
        handler: (message) => {
          if (message.type === 'breathing_reminder') {
            toast('Breathing Exercise Reminder', {
              description: 'Take a moment to breathe and center yourself'
            })
          }
        },
        priority: 1
      }
    ]

    defaultHandlers.forEach(handler => {
      addEventHandler('notification', handler)
      addEventHandler('mood_pattern_alert', handler)
      addEventHandler('breathing_reminder', handler)
    })
  }, [addEventHandler])

  return {
    isConnected,
    connectionError,
    sendMessage,
    lastMessage,
    connectionStats,
    addEventHandler,
    removeEventHandler,
    reconnectAll,
    getConnectionHealth
  }
}
