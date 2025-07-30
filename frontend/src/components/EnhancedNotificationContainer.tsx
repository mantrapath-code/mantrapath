import { ReactNode } from 'react'
import { motion } from 'framer-motion'
import '../styles/notifications.css'

interface EnhancedNotificationContainerProps {
  children: ReactNode
}

export function EnhancedNotificationContainer({ children }: EnhancedNotificationContainerProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      className="enhanced-notification-container"
    >
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="space-y-3">
          {children}
        </div>
      </div>
    </motion.div>
  )
}
