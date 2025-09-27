/**
 * Comprehensive time formatting utilities
 * Consolidated from timeFormat.ts and timeUtils.ts for better maintainability
 */

/**
 * Time formatting utilities for community features
 */

/**
 * Convert a date string to relative time format (1m, 1h, 1d, etc.)
 * Enhanced version with better UTC handling
 */
export function formatRelativeTime(dateString: string): string {
  const now = new Date()
  
  // Handle different date string formats and ensure proper UTC parsing
  let date: Date
  if (dateString.includes('T') && !dateString.includes('Z') && !dateString.includes('+')) {
    // If it's an ISO string without timezone info, assume it's UTC
    date = new Date(dateString + 'Z')
  } else {
    // Otherwise parse normally
    date = new Date(dateString)
  }
  
  // If date parsing failed, return original string
  if (isNaN(date.getTime())) {
    return dateString
  }
  
  const diffInMs = now.getTime() - date.getTime()
  const diffInSeconds = Math.floor(diffInMs / 1000)
  const diffInMinutes = Math.floor(diffInSeconds / 60)
  const diffInHours = Math.floor(diffInMinutes / 60)
  const diffInDays = Math.floor(diffInHours / 24)
  const diffInWeeks = Math.floor(diffInDays / 7)
  const diffInMonths = Math.floor(diffInDays / 30)
  const diffInYears = Math.floor(diffInDays / 365)

  if (diffInSeconds < 60) {
    return diffInSeconds <= 1 ? 'now' : `${diffInSeconds}s`
  } else if (diffInMinutes < 60) {
    return `${diffInMinutes}m`
  } else if (diffInHours < 24) {
    return `${diffInHours}h`
  } else if (diffInDays < 7) {
    return `${diffInDays}d`
  } else if (diffInWeeks < 4) {
    return `${diffInWeeks}w`
  } else if (diffInMonths < 12) {
    return `${diffInMonths}mo`
  } else {
    return `${diffInYears}y`
  }
}

// Removed deprecated alias getRelativeTime (use formatRelativeTime directly)

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
