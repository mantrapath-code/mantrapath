/**
 * Time formatting utilities for community features
 */

/**
 * Convert a date string to relative time format (1m, 1h, 1d, etc.)
 */
export function getRelativeTime(dateString: string): string {
  try {
    const date = new Date(dateString)
    const now = new Date()
    const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000)

    if (diffInSeconds < 60) {
      return 'now'
    } else if (diffInSeconds < 3600) {
      const minutes = Math.floor(diffInSeconds / 60)
      return `${minutes}m`
    } else if (diffInSeconds < 86400) {
      const hours = Math.floor(diffInSeconds / 3600)
      return `${hours}h`
    } else if (diffInSeconds < 604800) {
      const days = Math.floor(diffInSeconds / 86400)
      return `${days}d`
    } else if (diffInSeconds < 2592000) {
      const weeks = Math.floor(diffInSeconds / 604800)
      return `${weeks}w`
    } else {
      const months = Math.floor(diffInSeconds / 2592000)
      return `${months}mo`
    }
  } catch (error) {
    console.error('Error calculating relative time:', error)
    return 'now'
  }
}

/**
 * Get a readable username from user data
 */
export function getDisplayName(user: { 
  name?: string; 
  username?: string; 
  id?: string 
}): string {
  return user.name || user.username || `User${user.id || 'Unknown'}`
}

/**
 * Format date for full display (fallback)
 */
export function formatFullDate(dateString: string): string {
  try {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch (error) {
    return 'Unknown date'
  }
}
