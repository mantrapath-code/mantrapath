import { useEffect, useState } from 'react'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Bell, BellRing, Check, X, Wifi, WifiSlash } from '@phosphor-icons/react'
import { useWebSocket } from '@/hooks/useWebSocket'
import { motion, AnimatePresence } from 'framer-motion'
import { toast } from 'sonner'

interface Notification {
  id: string
  title: string
  message: string
  notification_type: string
  action_url?: string
  priority: string
  is_read: boolean
  is_sent: boolean
  sent_at?: string
  created_at: string
}

export function RealTimeNotifications() {
  const { isConnected, lastMessage, connectionError } = useWebSocket()
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [unreadCount, setUnreadCount] = useState(0)
  const [showPanel, setShowPanel] = useState(false)

  // Fetch recent notifications on mount
  useEffect(() => {
    fetchNotifications()
  }, [])

  // Handle incoming WebSocket messages
  useEffect(() => {
    if (lastMessage?.type === 'notification') {
      const newNotification = lastMessage.data as Notification
      setNotifications(prev => [newNotification, ...prev.slice(0, 19)]) // Keep latest 20
      setUnreadCount(prev => prev + 1)
    }
  }, [lastMessage])

  const fetchNotifications = async () => {
    try {
      const token = localStorage.getItem('auth_token')
      const apiBaseUrl = process.env.VITE_API_BASE_URL || 'http://localhost:8000'
      const response = await fetch(`${apiBaseUrl}/notify/recent?limit=20`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })

      if (response.ok) {
        const data = await response.json()
        setNotifications(data)
        setUnreadCount(data.filter((n: Notification) => !n.is_read).length)
      }
    } catch (error) {
      console.error('Error fetching notifications:', error)
    }
  }

  const markAsRead = async (notificationId: string) => {
    try {
      const token = localStorage.getItem('auth_token')
      const apiBaseUrl = process.env.VITE_API_BASE_URL || 'http://localhost:8000'
      const response = await fetch(`${apiBaseUrl}/notify/mark-read/${notificationId}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })

      if (response.ok) {
        setNotifications(prev => 
          prev.map(n => 
            n.id === notificationId ? { ...n, is_read: true } : n
          )
        )
        setUnreadCount(prev => Math.max(0, prev - 1))
      }
    } catch (error) {
      console.error('Error marking notification as read:', error)
    }
  }

  const markAllAsRead = async () => {
    try {
      const token = localStorage.getItem('auth_token')
      const apiBaseUrl = process.env.VITE_API_BASE_URL || 'http://localhost:8000'
      const response = await fetch(`${apiBaseUrl}/notify/mark-all-read`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })

      if (response.ok) {
        setNotifications(prev => 
          prev.map(n => ({ ...n, is_read: true }))
        )
        setUnreadCount(0)
        toast.success('All notifications marked as read')
      }
    } catch (error) {
      console.error('Error marking all notifications as read:', error)
    }
  }

  const handleNotificationClick = (notification: Notification) => {
    if (!notification.is_read) {
      markAsRead(notification.id)
    }

    if (notification.action_url) {
      // Navigate to the action URL
      window.location.hash = notification.action_url
      setShowPanel(false)
    }
  }

  const getNotificationIcon = (type: string, priority: string) => {
    const isUrgent = priority === 'urgent' || priority === 'high'
    
    switch (type) {
      case 'mood_pattern':
        return isUrgent ? '⚠️' : '📊'
      case 'weekly_report':
        return '📈'
      case 'intervention':
        return '🤗'
      case 'community':
        return '👥'
      case 'crisis':
        return '🚨'
      default:
        return isUrgent ? '🔔' : '💬'
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent':
        return 'destructive'
      case 'high':
        return 'destructive'
      case 'normal':
        return 'secondary'
      case 'low':
        return 'outline'
      default:
        return 'secondary'
    }
  }

  const formatTimeAgo = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60))

    if (diffInMinutes < 1) return 'Just now'
    if (diffInMinutes < 60) return `${diffInMinutes}m ago`
    if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)}h ago`
    return `${Math.floor(diffInMinutes / 1440)}d ago`
  }

  return (
    <div className="relative">
      {/* Notification Bell Button */}
      <Button
        variant={showPanel ? "default" : "ghost"}
        size="sm"
        onClick={() => setShowPanel(!showPanel)}
        className="relative"
      >
        {isConnected ? (
          <BellRing className={`h-4 w-4 ${unreadCount > 0 ? 'text-primary' : ''}`} />
        ) : (
          <Bell className="h-4 w-4 text-muted-foreground" />
        )}
        {unreadCount > 0 && (
          <Badge 
            variant="destructive" 
            className="absolute -top-1 -right-1 h-5 w-5 p-0 text-xs flex items-center justify-center"
          >
            {unreadCount > 99 ? '99+' : unreadCount}
          </Badge>
        )}
      </Button>

      {/* Connection Status Indicator */}
      <div className="absolute -bottom-1 -right-1">
        {isConnected ? (
          <Wifi className="h-3 w-3 text-green-500" />
        ) : (
          <WifiSlash className="h-3 w-3 text-red-500" />
        )}
      </div>

      {/* Notifications Panel */}
      <AnimatePresence>
        {showPanel && (
          <>
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 z-40 lg:hidden"
              onClick={() => setShowPanel(false)}
            />

            {/* Panel */}
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: -10 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: -10 }}
              className="absolute right-0 top-12 z-50 w-80 max-w-[90vw]"
            >
              <Card className="p-4 shadow-lg border">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2">
                    <BellRing className="h-5 w-5" />
                    <h3 className="font-semibold">Notifications</h3>
                    {!isConnected && (
                      <Badge variant="destructive">Offline</Badge>
                    )}
                  </div>
                  <div className="flex items-center gap-2">
                    {unreadCount > 0 && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={markAllAsRead}
                        className="text-xs"
                      >
                        <Check className="h-3 w-3 mr-1" />
                        Mark all read
                      </Button>
                    )}
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setShowPanel(false)}
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  </div>
                </div>

                {connectionError && (
                  <div className="mb-3 p-2 bg-destructive/10 border border-destructive/20 rounded text-sm text-destructive">
                    Connection error: {connectionError}
                  </div>
                )}

                <div className="max-h-96 overflow-y-auto space-y-3">
                  {notifications.length === 0 ? (
                    <div className="text-center py-8 text-muted-foreground">
                      <Bell className="h-8 w-8 mx-auto mb-2 opacity-50" />
                      <p>No notifications yet</p>
                    </div>
                  ) : (
                    notifications.map((notification) => (
                      <motion.div
                        key={notification.id}
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        className={`
                          p-3 rounded-lg border cursor-pointer transition-all
                          ${!notification.is_read 
                            ? 'bg-primary/5 border-primary/20' 
                            : 'bg-muted/50 border-border'
                          }
                          hover:bg-primary/10
                        `}
                        onClick={() => handleNotificationClick(notification)}
                      >
                        <div className="flex items-start gap-3">
                          <div className="text-lg">
                            {getNotificationIcon(notification.notification_type, notification.priority)}
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 mb-1">
                              <h4 className="font-medium text-sm truncate">
                                {notification.title}
                              </h4>
                              <Badge 
                                variant={getPriorityColor(notification.priority)}
                                className="text-xs"
                              >
                                {notification.priority}
                              </Badge>
                            </div>
                            <p className="text-sm text-muted-foreground line-clamp-2">
                              {notification.message}
                            </p>
                            <div className="flex items-center justify-between mt-2">
                              <span className="text-xs text-muted-foreground">
                                {formatTimeAgo(notification.created_at)}
                              </span>
                              {!notification.is_read && (
                                <div className="w-2 h-2 bg-primary rounded-full" />
                              )}
                            </div>
                          </div>
                        </div>
                      </motion.div>
                    ))
                  )}
                </div>

                {notifications.length > 0 && (
                  <div className="mt-4 pt-3 border-t">
                    <Button
                      variant="ghost"
                      className="w-full text-sm"
                      onClick={() => {
                        window.location.hash = '/notifications'
                        setShowPanel(false)
                      }}
                    >
                      View all notifications
                    </Button>
                  </div>
                )}
              </Card>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  )
}