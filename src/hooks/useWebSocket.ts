import { useEffect, useRef, useState, useCallback } from 'react'
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

  const wsUrl = url || `ws://localhost:8000/ws`

  const connect = useCallback(() => {
    try {
      // Get auth token for WebSocket connection
      const token = localStorage.getItem('mantrapath_token')
      const wsUrlWithAuth = token ? `${wsUrl}?token=${token}` : wsUrl

      wsRef.current = new WebSocket(wsUrlWithAuth)

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
        
        // Attempt to reconnect if not a manual close
        if (event.code !== 1000 && reconnectAttempts.current < maxReconnectAttempts) {
          const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 30000)
          
          console.log(`🔄 Attempting to reconnect in ${delay}ms (attempt ${reconnectAttempts.current + 1}/${maxReconnectAttempts})`)
          
          reconnectTimeoutRef.current = setTimeout(() => {
            reconnectAttempts.current++
            connect()
          }, delay)
        } else if (reconnectAttempts.current >= maxReconnectAttempts) {
          setConnectionError('Failed to establish WebSocket connection after multiple attempts')
        }
      }

      wsRef.current.onerror = (error) => {
        console.error('❌ WebSocket error:', error)
        setConnectionError('WebSocket connection error')
      }

    } catch (error) {
      console.error('Failed to create WebSocket connection:', error)
      setConnectionError('Failed to create WebSocket connection')
    }
  }, [wsUrl])

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
  }, [connect, disconnect])

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
  }, [isConnected, connectionError, connect])

  return {
    isConnected,
    connectionError,
    sendMessage,
    lastMessage
  }
}