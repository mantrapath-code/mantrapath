/**
 * Enhanced Notification Service for MantraPath
 * Provides consistent, accessible, and contextual notifications
 */

import { toast } from 'sonner'
import { processApiError, createSuccessMessage, type UserFriendlyError } from '../utils/errorHandling'

export interface NotificationOptions {
  duration?: number
  dismissible?: boolean
  action?: {
    label: string
    onClick: () => void
  }
  context?: string
}

class NotificationService {
  /**
   * Show success notification with MantraPath branding
   */
  success(action: string, options: NotificationOptions = {}) {
    const successMsg = createSuccessMessage(action, options.context)
    
    toast.success(successMsg.message, {
      description: successMsg.description,
      duration: options.duration || 4000,
      dismissible: options.dismissible !== false,
      action: options.action
    })
  }

  /**
   * Show error notification with enhanced context
   */
  error(error: any, options: NotificationOptions = {}) {
    const userError = processApiError(error)
    
    toast.error(userError.message, {
      description: userError.description,
      duration: this.getDurationBySeverity(userError.severity),
      dismissible: options.dismissible !== false,
      action: options.action || this.getDefaultAction(userError)
    })
  }

  /**
   * Show warning with actionable guidance
   */
  warning(title: string, message: string, options: NotificationOptions = {}) {
    toast.warning(title, {
      description: message,
      duration: options.duration || 6000,
      dismissible: options.dismissible !== false,
      action: options.action
    })
  }

  /**
   * Show informational message
   */
  info(title: string, message: string, options: NotificationOptions = {}) {
    toast.info(title, {
      description: message,
      duration: options.duration || 5000,
      dismissible: options.dismissible !== false,
      action: options.action
    })
  }

  /**
   * Show loading state with progress indication
   */
  loading(message: string, description?: string) {
    return toast.loading(message, {
      description,
      dismissible: false
    })
  }

  /**
   * Update an existing toast (useful for loading states)
   */
  update(toastId: string | number, type: 'success' | 'error' | 'warning' | 'info', message: string, description?: string) {
    toast.dismiss(toastId)
    
    switch (type) {
      case 'success':
        toast.success(message, { description })
        break
      case 'error':
        toast.error(message, { description })
        break
      case 'warning':
        toast.warning(message, { description })
        break
      case 'info':
        toast.info(message, { description })
        break
    }
  }

  /**
   * Dismiss specific toast
   */
  dismiss(toastId?: string | number) {
    toast.dismiss(toastId)
  }

  /**
   * Dismiss all toasts
   */
  dismissAll() {
    toast.dismiss()
  }

  /**
   * Show wellness-specific notifications
   */
  wellness = {
    moodLogged: (score: number) => {
      const emoji = this.getMoodEmoji(score)
      this.success('mood-entry', {
        context: `${emoji} Your emotional check-in helps build self-awareness`
      })
    },

    streakAchieved: (days: number) => {
      toast.success(`🎉 ${days} day streak!`, {
        description: 'Consistency is the key to lasting wellness habits.',
        duration: 6000
      })
    },

    challengeProgress: (completed: number, total: number) => {
      const percentage = Math.round((completed / total) * 100)
      toast.info(`Progress Update: ${percentage}%`, {
        description: `You've completed ${completed} out of ${total} challenge days. Keep going!`,
        duration: 5000
      })
    },

    communitySupport: (type: 'encouragement' | 'reply' | 'like') => {
      const messages = {
        encouragement: 'Your encouragement brightens someone\'s day! 💙',
        reply: 'Thanks for sharing your thoughts with the community! 🤝',
        like: 'Your support means a lot to fellow community members! 👍'
      }
      
      toast.success('Community Impact', {
        description: messages[type],
        duration: 4000
      })
    }
  }

  /**
   * Privacy and data-related notifications
   */
  privacy = {
    dataExported: () => {
      toast.success('Data exported successfully', {
        description: 'Your wellness data has been securely packaged for download.',
        duration: 5000
      })
    },

    dataDeleted: (type: string) => {
      toast.success(`${type} data deleted`, {
        description: 'Your data has been permanently removed as requested.',
        duration: 6000
      })
    },

    privacyUpdated: () => {
      toast.success('Privacy settings updated', {
        description: 'Your data sharing preferences have been saved.',
        duration: 4000
      })
    }
  }

  /**
   * Subscription and upgrade notifications
   */
  subscription = {
    upgraded: (tier: string) => {
      toast.success(`Welcome to ${tier}!`, {
        description: 'You now have access to advanced wellness features.',
        duration: 6000
      })
    },

    featureRestricted: (feature: string, requiredTier: string) => {
      toast.warning('Upgrade Required', {
        description: `${feature} requires ${requiredTier} membership.`,
        action: {
          label: 'Upgrade',
          onClick: () => window.location.href = '/upgrade'
        }
      })
    },

    trialEnding: (daysLeft: number) => {
      toast.warning(`Trial ending in ${daysLeft} days`, {
        description: 'Continue your wellness journey with a subscription.',
        duration: 8000,
        action: {
          label: 'Subscribe',
          onClick: () => window.location.href = '/subscribe'
        }
      })
    }
  }

  private getDurationBySeverity(severity: UserFriendlyError['severity']): number {
    switch (severity) {
      case 'critical': return 10000
      case 'error': return 8000
      case 'warning': return 6000
      case 'info': return 4000
      default: return 5000
    }
  }

  private getDefaultAction(error: UserFriendlyError) {
    if (error.category === 'authentication') {
      return {
        label: 'Sign In',
        onClick: () => window.location.href = '/auth'
      }
    }

    if (error.category === 'network') {
      return {
        label: 'Retry',
        onClick: () => window.location.reload()
      }
    }

    return undefined
  }

  private getMoodEmoji(score: number): string {
    if (score >= 8) return '😊'
    if (score >= 6) return '🙂'
    if (score >= 4) return '😐'
    if (score >= 2) return '😔'
    return '😢'
  }
}

export const notificationService = new NotificationService()

// Convenience exports for common patterns
export const notify = notificationService
export const wellness = notificationService.wellness
export const privacy = notificationService.privacy
export const subscription = notificationService.subscription

export default notificationService
