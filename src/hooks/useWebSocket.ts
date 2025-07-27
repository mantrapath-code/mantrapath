import { useEffect, useRef, useState, useCallback } from 'react'
import { useAuth } from './useAuth'
import { toast } from 'sonner'

interface WebSocketMessage {
  type: string
  data: any
  timestamp: string
}

interface NotificationData {
  id: string
  title: string
  message: string
  notification_type: string
  action_url?: string
  priority: string
  created_at: string
}

interface UseWebSocketReturn {
  isConnected: boolean
  sendMessage: (message: any) => void
  lastMessage: WebSocketMessage | null
  connectionError: string | null
}

export function useWebSocket(): UseWebSocketReturn {
  const { user, isAuthenticated } = useAuth()
  const [isConnected, setIsConnected] = useState(false)
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null)
  const [connectionError, setConnectionError] = useState<string | null>(null)
  const ws = useRef<WebSocket | null>(null)
  const reconnectAttempts = useRef(0)
  const maxReconnectAttempts = 5
  const reconnectDelay = useRef(1000)

  const connect = useCallback(() => {
    if (!isAuthenticated || !user?.id) {
      return
    }

    try {
      const wsBaseUrl = process.env.VITE_WS_BASE_URL || 'ws://localhost:8007'
      const wsUrl = `${wsBaseUrl}/ws/${user.id}`
      ws.current = new WebSocket(wsUrl)

      ws.current.onopen = () => {
        console.log('WebSocket connected')
        setIsConnected(true)
        setConnectionError(null)
        reconnectAttempts.current = 0
        reconnectDelay.current = 1000

        // Send heartbeat every 30 seconds
        const heartbeatInterval = setInterval(() => {
          if (ws.current?.readyState === WebSocket.OPEN) {
            sendMessage({ type: 'heartbeat' })
          } else {
            clearInterval(heartbeatInterval)
          }
        }, 30000)
      }

      ws.current.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data)
          setLastMessage(message)
          handleMessage(message)
        } catch (error) {
          console.error('Error parsing WebSocket message:', error)
        }
      }

      ws.current.onclose = () => {
        console.log('WebSocket disconnected')
        setIsConnected(false)
        
        // Attempt to reconnect
        if (reconnectAttempts.current < maxReconnectAttempts) {
          reconnectAttempts.current++
          console.log(`Attempting to reconnect... (${reconnectAttempts.current}/${maxReconnectAttempts})`)
          
          setTimeout(() => {
            connect()
          }, reconnectDelay.current)
          
          // Exponential backoff
          reconnectDelay.current = Math.min(reconnectDelay.current * 2, 30000)
        } else {
          setConnectionError('Failed to maintain WebSocket connection')
        }
      }

      ws.current.onerror = (error) => {
        console.error('WebSocket error:', error)
        setConnectionError('WebSocket connection error')
      }

    } catch (error) {
      console.error('Error creating WebSocket connection:', error)
      setConnectionError('Failed to create WebSocket connection')
    }
  }, [isAuthenticated, user?.id])

  const disconnect = useCallback(() => {
    if (ws.current) {
      ws.current.close()
      ws.current = null
    }
    setIsConnected(false)
  }, [])

  const sendMessage = useCallback((message: any) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(message))
    }
  }, [])

  const handleMessage = (message: WebSocketMessage) => {
    switch (message.type) {
      case 'notification':
        handleNotification(message.data as NotificationData)
        break
      case 'notification_read':
        // Handle notification read confirmation
        console.log('Notification marked as read:', message.data)
        break
      case 'heartbeat_ack':
        // Handle heartbeat acknowledgment
        break
      case 'connection':
        console.log('WebSocket connection established:', message.data.message)
        break
      default:
        console.log('Unknown message type:', message.type)
    }
  }

  const handleNotification = (notification: NotificationData) => {
    // Show toast notification
    const toastProps = {
      duration: notification.priority === 'urgent' ? 10000 : 5000,
      action: notification.action_url ? {
        label: 'View',
        onClick: () => {
          // Navigate to action URL
          if (notification.action_url) {
            window.location.hash = notification.action_url
          }
          // Mark as read
          markNotificationAsRead(notification.id)
        }
      } : undefined
    }

    switch (notification.notification_type) {
      case 'mood_pattern':
        toast.warning(notification.message, {
          ...toastProps,
          description: notification.title
        })
        break
      case 'weekly_report':
        toast.info(notification.message, {
          ...toastProps,
          description: notification.title
        })
        break
      case 'intervention':
        toast.error(notification.message, {
          ...toastProps,
          description: notification.title
        })
        break
      case 'community':
        toast.success(notification.message, {
          ...toastProps,
          description: notification.title
        })
        break
      default:
        toast(notification.message, {
          ...toastProps,
          description: notification.title
        })
    }

    // Play notification sound for urgent notifications
    if (notification.priority === 'urgent') {
      playNotificationSound()
    }
  }

  const markNotificationAsRead = (notificationId: string) => {
    sendMessage({
      type: 'mark_read',
      notification_id: notificationId
    })
  }

  const playNotificationSound = () => {
    // Create a simple notification sound
    try {
      const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)()
      const oscillator = audioContext.createOscillator()
      const gainNode = audioContext.createGain()
      
      oscillator.connect(gainNode)
      gainNode.connect(audioContext.destination)
      
      oscillator.frequency.setValueAtTime(800, audioContext.currentTime)
      oscillator.frequency.setValueAtTime(600, audioContext.currentTime + 0.1)
      
      gainNode.gain.setValueAtTime(0.3, audioContext.currentTime)
      gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.3)
      
      oscillator.start(audioContext.currentTime)
      oscillator.stop(audioContext.currentTime + 0.3)
    } catch (error) {
      console.warn('Could not play notification sound:', error)
    }
  }

  useEffect(() => {
    if (isAuthenticated && user?.id) {
      connect()
    }

    return () => {
      disconnect()
    }
  }, [isAuthenticated, user?.id, connect, disconnect])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (ws.current) {
        ws.current.close()
      }
    }
  }, [])

  return {
    isConnected,
    sendMessage,
    lastMessage,
    connectionError
  }
}