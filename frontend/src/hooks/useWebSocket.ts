import { useEffect, useRef, useState, useCallback, useMemo } from 'react'
import { toast } from 'sonner'

export interface WebSocketMessage {
  type: string
  data: any
  timestamp: string
}

export interface WebSocketHookReturn {
  isConnected: boolean
  connectionError: string | null
  sendMessage: (message: any) => void
  lastMessage: WebSocketMessage | null
}

/**
 * WebSocket hook for real-time notifications and updates
 * Connects to the backend WebSocket endpoint for live features
 */
export function useWebSocket(url?: string): WebSocketHookReturn {
  const [isConnected, setIsConnected] = useState(false)
  const [connectionError, setConnectionError] = useState<string | null>(null)
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null)
  
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const reconnectAttempts = useRef(0)
  const maxReconnectAttempts = 5

  // Memoize the WebSocket URL to prevent unnecessary re-connections
  const wsUrl = useMemo(() => {
    // If running in development, use the proxy through Vite dev server
    if (import.meta.env.DEV) {
      return url || import.meta.env.VITE_WS_URL || `ws://localhost:5173/api/notifications/ws`
    }
    // In production, use the actual backend URL
    return url || import.meta.env.VITE_WS_URL || `ws://localhost:8007`
  }, [url])

  const connect = useCallback(() => {
    try {
      // Get auth token and user data for WebSocket connection
      const token = localStorage.getItem('authToken') || localStorage.getItem('mantrapath_token')
      const userData = localStorage.getItem('user') || localStorage.getItem('user_data')
      
      // For now, use a demo user ID if not authenticated
      let userId = 'demo-user'
      
      if (token && userData) {
        try {
          const user = JSON.parse(userData)
          userId = user.id || 'demo-user'
        } catch (e) {
          console.warn('Failed to parse user data, using demo user')
        }
      } else {
        console.log('🔌 No authentication data available, using demo user for WebSocket connection')
      }

      // Use the correct WebSocket endpoint format: /ws/{user_id}
      const wsUrlWithPath = `${wsUrl}/ws/${userId}`

      console.log('🔌 Connecting to WebSocket:', wsUrlWithPath)
      wsRef.current = new WebSocket(wsUrlWithPath)

      wsRef.current.onopen = () => {
        console.log('🔗 WebSocket connected')
        setIsConnected(true)
        setConnectionError(null)
        reconnectAttempts.current = 0
      }

      wsRef.current.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data)
          setLastMessage(message)
          
          // Handle different message types
          switch (message.type) {
            case 'notification':
              toast.info(message.data.title, {
                description: message.data.message
              })
              break
            case 'mood_pattern_alert':
              toast.warning('Mood Pattern Alert', {
                description: message.data.message
              })
              break
            case 'breathing_reminder':
              toast('Breathing Exercise Reminder', {
                description: 'Take a moment to breathe and center yourself'
              })
              break
            case 'weekly_report':
              toast.success('Weekly Report Ready', {
                description: 'Your weekly wellness report is now available'
              })
              break
            default:
              console.log('📥 Received WebSocket message:', message)
          }
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error)
        }
      }

      wsRef.current.onclose = (event) => {
        console.log('🔌 WebSocket disconnected:', event.code, event.reason)
        setIsConnected(false)
        
        // Attempt to reconnect if not a manual close and backend might be available
        if (event.code !== 1000 && event.code !== 1006 && reconnectAttempts.current < maxReconnectAttempts) {
          const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 30000)
          
          console.log(`🔄 Attempting to reconnect in ${delay}ms (attempt ${reconnectAttempts.current + 1}/${maxReconnectAttempts})`)
          
          reconnectTimeoutRef.current = setTimeout(() => {
            reconnectAttempts.current++
            connect()
          }, delay)
        } else if (event.code === 1006) {
          // Connection failed (likely backend not running)
          setConnectionError('Real-time features unavailable (backend service not running)')
        } else if (reconnectAttempts.current >= maxReconnectAttempts) {
          setConnectionError('Failed to establish WebSocket connection after multiple attempts')
        }
      }

      wsRef.current.onerror = (error) => {
        // Only log error if we haven't already shown a connection error
        if (!connectionError) {
          console.warn('⚠️  WebSocket connection failed - backend service may not be running')
          setConnectionError('Real-time features unavailable (backend service not running)')
        }
      }

    } catch (error) {
      console.error('Failed to create WebSocket connection:', error)
      setConnectionError('Failed to create WebSocket connection')
    }
  }, [wsUrl]) // Keep wsUrl dependency but ensure it's stable

  const sendMessage = useCallback((message: any) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message))
    } else {
      console.warn('WebSocket is not connected. Message not sent:', message)
    }
  }, [])

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
      reconnectTimeoutRef.current = null
    }
    
    if (wsRef.current) {
      wsRef.current.close(1000, 'Component unmounting')
      wsRef.current = null
    }
    
    setIsConnected(false)
    setConnectionError(null)
  }, [])

  useEffect(() => {
    connect()
    
    return () => {
      disconnect()
    }
  }, [connect, disconnect]) // Use stable callbacks

  // Handle visibility change to reconnect when tab becomes active
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible' && !isConnected && !connectionError) {
        connect()
      }
    }

    document.addEventListener('visibilitychange', handleVisibilityChange)
    
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange)
    }
  }, [isConnected, connectionError, connect]) // Include connect dependency

  return {
    isConnected,
    connectionError,
    sendMessage,
    lastMessage
  }
}