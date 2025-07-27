import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import { 
  Bell, 
  BellRinging, 
  X, 
  Heart, 
  Brain, 
  Users, 
  Trophy,
  Clock
} from '@phosphor-icons/react'
import { motion, AnimatePresence } from 'framer-motion'
import { useWebSocket } from '@/hooks/useWebSocket'
import { apiService } from '@/services/api'

interface Notification {
  id: string
  title: string
  message: string
  type: 'info' | 'warning' | 'achievement' | 'reminder' | 'mood_alert'
  timestamp: string
  read: boolean
  actionUrl?: string
}

export function RealTimeNotifications() {
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [showDropdown, setShowDropdown] = useState(false)
  const [unreadCount, setUnreadCount] = useState(0)
  
  const { isConnected, lastMessage } = useWebSocket()

  // Load initial notifications
  useEffect(() => {
    const loadNotifications = async () => {
      try {
        // This would be connected to the notification service
        // For now, using mock data but ready for backend
        const mockNotifications: Notification[] = [
          {
            id: '1',
            title: 'Weekly Report Ready',
            message: 'Your weekly wellness report is now available',
            type: 'info',
            timestamp: new Date().toISOString(),
            read: false
          }
        ]
        setNotifications(mockNotifications)
        setUnreadCount(mockNotifications.filter(n => !n.read).length)
      } catch (error) {
        console.error('Failed to load notifications:', error)
      }
    }

    loadNotifications()
  }, [])

  // Handle new WebSocket messages
  useEffect(() => {
    if (lastMessage) {
      const newNotification: Notification = {
        id: Date.now().toString(),
        title: lastMessage.data.title || 'New Notification',
        message: lastMessage.data.message || '',
        type: mapMessageTypeToNotificationType(lastMessage.type),
        timestamp: lastMessage.timestamp,
        read: false
      }

      setNotifications(prev => [newNotification, ...prev.slice(0, 9)]) // Keep last 10
      setUnreadCount(prev => prev + 1)
    }
  }, [lastMessage])

  const mapMessageTypeToNotificationType = (wsType: string): Notification['type'] => {
    switch (wsType) {
      case 'mood_pattern_alert':
        return 'mood_alert'
      case 'breathing_reminder':
        return 'reminder'
      case 'weekly_report':
        return 'achievement'
      default:
        return 'info'
    }
  }

  const getNotificationIcon = (type: Notification['type']) => {
    switch (type) {
      case 'mood_alert':
        return <Heart className="text-red-500" size={16} />
      case 'reminder':
        return <Clock className="text-blue-500" size={16} />
      case 'achievement':
        return <Trophy className="text-yellow-500" size={16} />
      case 'warning':
        return <Brain className="text-orange-500" size={16} />
      default:
        return <Bell className="text-gray-500" size={16} />
    }
  }

  const markAsRead = async (notificationId: string) => {
    setNotifications(prev => 
      prev.map(n => 
        n.id === notificationId ? { ...n, read: true } : n
      )
    )
    setUnreadCount(prev => Math.max(0, prev - 1))

    try {
      // This would call the notification service to mark as read
      // await apiService.markNotificationAsRead(notificationId)
    } catch (error) {
      console.error('Failed to mark notification as read:', error)
    }
  }

  const markAllAsRead = async () => {
    setNotifications(prev => prev.map(n => ({ ...n, read: true })))
    setUnreadCount(0)

    try {
      // This would call the notification service
      // await apiService.markAllNotificationsAsRead()
    } catch (error) {
      console.error('Failed to mark all notifications as read:', error)
    }
  }

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / (1000 * 60))
    const diffHours = Math.floor(diffMins / 60)
    const diffDays = Math.floor(diffHours / 24)

    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins}m ago`
    if (diffHours < 24) return `${diffHours}h ago`
    if (diffDays < 7) return `${diffDays}d ago`
    return date.toLocaleDateString()
  }

  return (
    <div className="relative">
      {/* Notification Bell Button */}
      <Button
        variant="ghost"
        size="sm"
        onClick={() => setShowDropdown(!showDropdown)}
        className="relative"
      >
        {unreadCount > 0 ? (
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            className="relative"
          >
            <BellRinging size={20} className="text-primary" />
            <Badge 
              variant="destructive" 
              className="absolute -top-2 -right-2 h-5 w-5 p-0 flex items-center justify-center text-xs"
            >
              {unreadCount > 9 ? '9+' : unreadCount}
            </Badge>
          </motion.div>
        ) : (
          <Bell size={20} className={isConnected ? 'text-primary' : 'text-muted-foreground'} />
        )}
      </Button>

      {/* Notifications Dropdown */}
      <AnimatePresence>
        {showDropdown && (
          <>
            {/* Backdrop */}
            <div 
              className="fixed inset-0 z-40"
              onClick={() => setShowDropdown(false)}
            />
            
            {/* Dropdown */}
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="absolute top-full right-0 z-50 w-80 mt-2"
            >
              <Card className="shadow-lg border">
                <CardContent className="p-0">
                  {/* Header */}
                  <div className="flex items-center justify-between p-4 border-b">
                    <h3 className="font-semibold text-foreground">Notifications</h3>
                    <div className="flex items-center gap-2">
                      {!isConnected && (
                        <Badge variant="secondary" className="text-xs">
                          Offline
                        </Badge>
                      )}
                      {unreadCount > 0 && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={markAllAsRead}
                          className="text-xs"
                        >
                          Mark all read
                        </Button>
                      )}
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setShowDropdown(false)}
                      >
                        <X size={16} />
                      </Button>
                    </div>
                  </div>

                  {/* Notifications List */}
                  <div className="max-h-80 overflow-y-auto">
                    {notifications.length === 0 ? (
                      <div className="p-8 text-center text-muted-foreground">
                        <Bell size={32} className="mx-auto mb-2" />
                        <p>No notifications yet</p>
                        <p className="text-xs mt-1">We'll notify you about important updates</p>
                      </div>
                    ) : (
                      notifications.map((notification) => (
                        <motion.div
                          key={notification.id}
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          className={`p-4 border-b last:border-b-0 cursor-pointer hover:bg-muted/50 transition-colors ${
                            !notification.read ? 'bg-primary/5' : ''
                          }`}
                          onClick={() => markAsRead(notification.id)}
                        >
                          <div className="flex items-start gap-3">
                            <div className="flex-shrink-0 mt-0.5">
                              {getNotificationIcon(notification.type)}
                            </div>
                            
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center justify-between">
                                <h4 className={`text-sm font-medium truncate ${
                                  !notification.read ? 'text-foreground' : 'text-muted-foreground'
                                }`}>
                                  {notification.title}
                                </h4>
                                {!notification.read && (
                                  <div className="w-2 h-2 bg-primary rounded-full flex-shrink-0 ml-2" />
                                )}
                              </div>
                              
                              <p className="text-xs text-muted-foreground mt-1 line-clamp-2">
                                {notification.message}
                              </p>
                              
                              <span className="text-xs text-muted-foreground mt-1 block">
                                {formatTime(notification.timestamp)}
                              </span>
                            </div>
                          </div>
                        </motion.div>
                      ))
                    )}
                  </div>

                  {/* Footer */}
                  {notifications.length > 0 && (
                    <div className="p-3 border-t bg-muted/20">
                      <Button 
                        variant="ghost" 
                        size="sm" 
                        className="w-full text-xs"
                        onClick={() => {
                          setShowDropdown(false)
                          // Navigate to notifications page
                        }}
                      >
                        View all notifications
                      </Button>
                    </div>
                  )}
                </CardContent>
              </Card>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  )
}