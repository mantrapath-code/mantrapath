/**
 * Robust WebSocket Hook - Consolidated Implementation
 * Replaces useWebSocket.ts and useEnhancedWebSocket.ts with a single, robust solution
 */

import { useEffect, useRef, useState, useCallback, useMemo } from 'react'
import { toast } from 'sonner'

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
  socket: WebSocket | null
  status: 'connecting' | 'connected' | 'disconnected' | 'error' | 'closed'
  reconnectAttempts: number
  lastHeartbeat: number
  messageQueue: WebSocketMessage[]
  reconnectTimeout: NodeJS.Timeout | null
  heartbeatInterval: NodeJS.Timeout | null
}

export interface WebSocketHookReturn {
  isConnected: boolean
  connectionError: string | null
  sendMessage: (message: WebSocketMessage, connectionId?: string) => void
  lastMessage: WebSocketMessage | null
  connectionStats: {
    totalConnections: number
    healthyConnections: number
    failedConnections: number
  }
  addEventHandler: (eventType: string, handler: (message: WebSocketMessage) => void) => string
  removeEventHandler: (handlerId: string) => void
  reconnectAll: () => void
  disconnectAll: () => void
  hasAttemptedConnection: boolean
}

// Global connection manager to prevent duplicates
class WebSocketManager {
  private static instance: WebSocketManager
  private connections: Map<string, WebSocketConnection> = new Map()
  private eventHandlers: Map<string, Array<{ id: string; handler: (message: WebSocketMessage) => void }>> = new Map()
  private globalReconnectAttempts = 0
  private maxGlobalReconnectAttempts = 3

  static getInstance(): WebSocketManager {
    if (!WebSocketManager.instance) {
      WebSocketManager.instance = new WebSocketManager()
    }
    return WebSocketManager.instance
  }

  createConnection(url: string, userId: string): WebSocketConnection {
    const connectionId = `ws_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    
    // Check if connection already exists for this URL
    const existingConnection = Array.from(this.connections.values()).find(conn => 
      conn.url === url && conn.status !== 'closed'
    )
    
    if (existingConnection) {
      return existingConnection
    }

    const connection: WebSocketConnection = {
      id: connectionId,
      url,
      socket: null,
      status: 'connecting',
      reconnectAttempts: 0,
      lastHeartbeat: Date.now(),
      messageQueue: [],
      reconnectTimeout: null,
      heartbeatInterval: null
    }

    this.connections.set(connectionId, connection)
    return connection
  }

  getConnection(connectionId: string): WebSocketConnection | undefined {
    return this.connections.get(connectionId)
  }

  getAllConnections(): WebSocketConnection[] {
    return Array.from(this.connections.values())
  }

  removeConnection(connectionId: string): void {
    const connection = this.connections.get(connectionId)
    if (connection) {
      this.cleanupConnection(connection)
      this.connections.delete(connectionId)
    }
  }

  private cleanupConnection(connection: WebSocketConnection): void {
    if (connection.reconnectTimeout) {
      clearTimeout(connection.reconnectTimeout)
      connection.reconnectTimeout = null
    }
    
    if (connection.heartbeatInterval) {
      clearInterval(connection.heartbeatInterval)
      connection.heartbeatInterval = null
    }
    
    if (connection.socket) {
      connection.socket.close(1000, 'Connection cleanup')
      connection.socket = null
    }
    
    connection.status = 'closed'
  }

  addEventHandler(eventType: string, handler: (message: WebSocketMessage) => void): string {
    const handlerId = `handler_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    const handlers = this.eventHandlers.get(eventType) || []
    handlers.push({ id: handlerId, handler })
    this.eventHandlers.set(eventType, handlers)
    return handlerId
  }

  removeEventHandler(handlerId: string): void {
    for (const [eventType, handlers] of this.eventHandlers.entries()) {
      const filteredHandlers = handlers.filter(h => h.id !== handlerId)
      if (filteredHandlers.length === 0) {
        this.eventHandlers.delete(eventType)
      } else {
        this.eventHandlers.set(eventType, filteredHandlers)
      }
    }
  }

  routeEvent(message: WebSocketMessage): void {
    const handlers = this.eventHandlers.get(message.type) || []
    handlers.forEach(({ handler }) => {
      try {
        handler(message)
      } catch (error) {
        console.error('Error in WebSocket event handler:', error)
      }
    })
  }

  cleanup(): void {
    this.connections.forEach(connection => {
      this.cleanupConnection(connection)
    })
    this.connections.clear()
    this.eventHandlers.clear()
    this.globalReconnectAttempts = 0
  }
}

// WebSocket URL configuration (resilient across devices / origins)
const getWebSocketUrls = (userId: string): string[] => {
  // 1. Explicit env variable
  let configured = import.meta.env.VITE_WS_URL as string | undefined

  // 2. Fallback to current origin if not supplied
  if (!configured && typeof window !== 'undefined') {
    const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    configured = `${proto}//${window.location.host}`
  }

  // Avoid hardcoding localhost; if no env provided derive from window origin
  let baseUrl = configured
  if (!baseUrl && typeof window !== 'undefined') {
    const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    baseUrl = `${proto}//${window.location.host}`
  }
  baseUrl = (baseUrl || 'ws://api-gateway:8000').replace(/\/$/, '')

  // Force secure if page is secure
  if (typeof window !== 'undefined' && window.location.protocol === 'https:') {
    baseUrl = baseUrl.replace('ws://', 'wss://')
  }

  const uid = userId || 'anonymous'
  const primary = `${baseUrl}/api/notifications/ws/${uid}`
  const legacy = `${baseUrl}/ws/${uid}` // direct notification service (fallback)

  return [primary, legacy]
}

export function useRobustWebSocket(
  userId?: string,
  options: {
    maxReconnectAttempts?: number
    reconnectDelay?: number
    heartbeatInterval?: number
    enableHeartbeat?: boolean
  } = {}
): WebSocketHookReturn {
  const [isConnected, setIsConnected] = useState(false)
  const [connectionError, setConnectionError] = useState<string | null>(null)
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null)
  const [connectionStats, setConnectionStats] = useState({
    totalConnections: 0,
    healthyConnections: 0,
    failedConnections: 0
  })
  // Track whether we've actually tried to connect (for better UI state handling)
  const [hasAttemptedConnection, setHasAttemptedConnection] = useState(false)

  const managerRef = useRef<WebSocketManager>(WebSocketManager.getInstance())
  const isInitializedRef = useRef(false)

  const maxReconnectAttempts = options.maxReconnectAttempts || 5
  const reconnectDelay = options.reconnectDelay || 1000
  const heartbeatInterval = options.heartbeatInterval || 30000
  const enableHeartbeat = options.enableHeartbeat !== false

  // Update connection stats
  const updateStats = useCallback(() => {
    const connections = managerRef.current.getAllConnections()
    const healthyConnections = connections.filter(conn => 
      conn.status === 'connected' && 
      (Date.now() - conn.lastHeartbeat) < heartbeatInterval * 2
    ).length
    const failedConnections = connections.filter(conn => 
      conn.status === 'error'
    ).length

    setConnectionStats({
      totalConnections: connections.length,
      healthyConnections,
      failedConnections
    })

    setIsConnected(healthyConnections > 0)
  }, [heartbeatInterval])

  // Start heartbeat for a connection
  const startHeartbeat = useCallback((connection: WebSocketConnection) => {
    if (!enableHeartbeat || connection.heartbeatInterval) return

    connection.heartbeatInterval = setInterval(() => {
      if (connection.socket && connection.socket.readyState === WebSocket.OPEN) {
        connection.lastHeartbeat = Date.now()
        try {
          connection.socket.send(JSON.stringify({
            type: 'heartbeat',
            timestamp: new Date().toISOString()
          }))
        } catch (error) {
          console.error('Heartbeat failed:', error)
          connection.status = 'error'
          updateStats()
        }
      }
    }, heartbeatInterval)
  }, [enableHeartbeat, heartbeatInterval, updateStats])

  // Stop heartbeat for a connection
  const stopHeartbeat = useCallback((connection: WebSocketConnection) => {
    if (connection.heartbeatInterval) {
      clearInterval(connection.heartbeatInterval)
      connection.heartbeatInterval = null
    }
  }, [])

  // Connect to a WebSocket
  const connect = useCallback((url: string, userId: string): Promise<WebSocketConnection> => {
    return new Promise((resolve, reject) => {
      const connection = managerRef.current.createConnection(url, userId)
      
      try {
        const socket = new WebSocket(url)
        connection.socket = socket

        const connectionTimeout = setTimeout(() => {
          if (connection.status === 'connecting') {
            connection.status = 'error'
            socket.close()
            reject(new Error(`Connection timeout after 15 seconds for ${url}`))
          }
        }, 15000)

        socket.onopen = () => {
          clearTimeout(connectionTimeout)
          connection.status = 'connected'
          connection.reconnectAttempts = 0
          connection.lastHeartbeat = Date.now()
          startHeartbeat(connection)
          updateStats()
          resolve(connection)
        }

        socket.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data)
            setLastMessage(message)
            managerRef.current.routeEvent(message)
            connection.lastHeartbeat = Date.now()
          } catch (error) {
            console.error('Failed to parse WebSocket message:', error)
          }
        }

        socket.onclose = (event) => {
          clearTimeout(connectionTimeout)
          stopHeartbeat(connection)
          connection.status = 'disconnected'
          
          // Only attempt reconnection for unexpected disconnections
          if (event.code !== 1000 && event.code !== 1001 && connection.reconnectAttempts < maxReconnectAttempts) {
            connection.reconnectAttempts++
            const delay = Math.min(reconnectDelay * Math.pow(2, connection.reconnectAttempts - 1), 30000)
            
            connection.reconnectTimeout = setTimeout(() => {
              connect(url, userId).catch(console.error)
            }, delay)
          } else if (event.code === 1000) {
            // Normal closure - don't treat as error
            connection.status = 'closed'
          } else {
            connection.status = 'error'
          }
          
          updateStats()
        }

        socket.onerror = (error) => {
          clearTimeout(connectionTimeout)
          connection.status = 'error'
          console.error('WebSocket connection error for URL:', url, error)
          console.error('WebSocket readyState:', socket.readyState)
          updateStats()
          reject(error)
        }

      } catch (error) {
        connection.status = 'error'
        reject(error)
      }
    })
  }, [maxReconnectAttempts, reconnectDelay, startHeartbeat, stopHeartbeat, updateStats])

  // Send message
  const sendMessage = useCallback((message: WebSocketMessage, connectionId?: string) => {
    const connections = managerRef.current.getAllConnections()
    const targetConnection = connectionId 
      ? managerRef.current.getConnection(connectionId)
      : connections.find(conn => conn.status === 'connected')

    if (targetConnection && targetConnection.socket && targetConnection.socket.readyState === WebSocket.OPEN) {
      try {
        targetConnection.socket.send(JSON.stringify(message))
      } catch (error) {
        console.error('Failed to send message:', error)
        // Queue message for later
        targetConnection.messageQueue.push(message)
      }
    } else {
      // Queue message if no connection available
      const availableConnection = connections.find(conn => conn.status === 'connected')
      if (availableConnection) {
        availableConnection.messageQueue.push(message)
      }
    }
  }, [])

  // Add event handler
  const addEventHandler = useCallback((eventType: string, handler: (message: WebSocketMessage) => void): string => {
    return managerRef.current.addEventHandler(eventType, handler)
  }, [])

  // Remove event handler
  const removeEventHandler = useCallback((handlerId: string) => {
    managerRef.current.removeEventHandler(handlerId)
  }, [])

  // Reconnect all connections
  const reconnectAll = useCallback(() => {
    const connections = managerRef.current.getAllConnections()
    connections.forEach(connection => {
      if (connection.status !== 'connected' && connection.status !== 'closed') {
        connect(connection.url, 'user').catch(console.error)
      }
    })
  }, [connect])

  // Disconnect all connections
  const disconnectAll = useCallback(() => {
    const connections = managerRef.current.getAllConnections()
    connections.forEach(connection => {
      if (connection.socket) {
        connection.socket.close(1000, 'Manual disconnect')
      }
    })
    managerRef.current.cleanup()
    updateStats()
  }, [updateStats])

  // Initialize connections
  // Keep previous user id to detect changes
  const prevUserIdRef = useRef<string | undefined>(undefined)

  useEffect(() => {
    // Wait until we actually have a user id before initializing.
    if (!userId) {
      console.debug('[WS] No userId yet; postponing WebSocket initialization')
      return
    }

    // If user changed, reset and allow re-init
    if (prevUserIdRef.current && prevUserIdRef.current !== userId) {
      console.debug('[WS] Detected user change from', prevUserIdRef.current, 'to', userId, '— resetting WebSocket connections')
      disconnectAll()
      managerRef.current.cleanup()
      isInitializedRef.current = false
      setIsConnected(false)
      setConnectionError(null)
    }

    prevUserIdRef.current = userId

    if (isInitializedRef.current) {
      return
    }

    isInitializedRef.current = true
    setHasAttemptedConnection(true)

    const effectiveUserId = userId
    const urls = getWebSocketUrls(effectiveUserId)
    console.debug('[WS] Initializing WebSocket connections for user', effectiveUserId, 'URLs:', urls)

    const initializeConnections = async () => {
      try {
        // Ensure full page load (helps on slower devices / secondary tabs)
        if (document.readyState !== 'complete') {
          await new Promise(resolve => {
            if (document.readyState === 'complete') {
              resolve(void 0)
            } else {
              window.addEventListener('load', () => resolve(void 0), { once: true })
            }
          })
        }

        // Small delay to help when backend containers are still warming
        await new Promise(resolve => setTimeout(resolve, 1000))

        for (const url of urls) {
          try {
            console.debug('[WS] Attempting connection to', url)
            await connect(url, effectiveUserId)
            console.debug('[WS] ✅ Connected to', url)
          } catch (error) {
            console.warn('[WS] ❌ Connection failed for', url, error)
            // Continue trying the remaining URLs
          }
        }

        if (!managerRef.current.getAllConnections().some(c => c.status === 'connected')) {
          setConnectionError('All WebSocket connection attempts failed')
        }
      } catch (error) {
        console.error('[WS] Fatal error during WebSocket initialization', error)
        setConnectionError('Failed to establish WebSocket connections')
      }
    }

    initializeConnections()

    return () => {
      // Cleanup only when component unmounts or user changes (handled by effect rerun)
      // We intentionally do not set isInitializedRef to false here unless user changes; unmount will reset state.
    }
  }, [userId, connect, disconnectAll])

  // Add default event handlers
  useEffect(() => {
    const defaultHandlers = [
      {
        eventType: 'notification',
        handler: (message: WebSocketMessage) => {
          if (message.data?.title) {
            toast.info(message.data.title, {
              description: message.data.message
            })
          }
        }
      },
      {
        eventType: 'mood_pattern_alert',
        handler: (message: WebSocketMessage) => {
          toast.warning('Mood Pattern Alert', {
            description: message.data?.message || 'A mood pattern has been detected'
          })
        }
      },
      {
        eventType: 'breathing_reminder',
        handler: (message: WebSocketMessage) => {
          toast('Breathing Exercise Reminder', {
            description: 'Take a moment to breathe and center yourself'
          })
        }
      },
      {
        eventType: 'weekly_report',
        handler: (message: WebSocketMessage) => {
          toast.success('Weekly Report Ready', {
            description: 'Your weekly wellness report is now available'
          })
        }
      }
    ]

    const handlerIds: string[] = []
    defaultHandlers.forEach(({ eventType, handler }) => {
      const handlerId = addEventHandler(eventType, handler)
      handlerIds.push(handlerId)
    })

    return () => {
      handlerIds.forEach(handlerId => removeEventHandler(handlerId))
    }
  }, [addEventHandler, removeEventHandler])

  // Handle visibility change
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible' && !isConnected) {
        reconnectAll()
      }
    }

    document.addEventListener('visibilitychange', handleVisibilityChange)
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange)
    }
  }, [isConnected, reconnectAll])

  return {
    isConnected,
    connectionError,
    sendMessage,
    lastMessage,
    connectionStats,
    addEventHandler,
    removeEventHandler,
    reconnectAll,
    disconnectAll,
    hasAttemptedConnection
  }
}
