/**
 * Time formatting utilities for consistent date/time display across the app
 */

/**
 * Formats a timestamp to relative time (e.g., "1m", "2h", "3d")
 * Works with user's timezone automatically
 */
export function formatRelativeTime(timestamp: number | string | Date): string {
  const now = new Date()
  
  // Handle different input types
  let date: Date
  if (typeof timestamp === 'number') {
    date = new Date(timestamp)
  } else if (typeof timestamp === 'string') {
    // Handle different date string formats
    if (timestamp.includes('T') && !timestamp.includes('Z') && !timestamp.includes('+')) {
      // If it's an ISO string without timezone info, assume it's UTC
      date = new Date(timestamp + 'Z')
    } else {
      date = new Date(timestamp)
    }
  } else {
    date = timestamp
  }
  
  // If date parsing failed, return fallback
  if (isNaN(date.getTime())) {
    return 'unknown'
  }
  
  const diffInMs = now.getTime() - date.getTime()
  const diffInSeconds = Math.floor(diffInMs / 1000)
  const diffInMinutes = Math.floor(diffInSeconds / 60)
  const diffInHours = Math.floor(diffInMinutes / 60)
  const diffInDays = Math.floor(diffInHours / 24)
  const diffInWeeks = Math.floor(diffInDays / 7)
  const diffInMonths = Math.floor(diffInDays / 30)
  const diffInYears = Math.floor(diffInDays / 365)

  // Return relative time in the format: 1s, 1m, 1h, 1d, 1w, 1mo, 1y
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

/**
 * Formats a timestamp to a more descriptive relative time (e.g., "2 minutes ago", "1 hour ago")
 */
export function formatRelativeTimeDescriptive(timestamp: number | string | Date): string {
  const now = new Date()
  
  // Handle different input types
  let date: Date
  if (typeof timestamp === 'number') {
    date = new Date(timestamp)
  } else if (typeof timestamp === 'string') {
    if (timestamp.includes('T') && !timestamp.includes('Z') && !timestamp.includes('+')) {
      date = new Date(timestamp + 'Z')
    } else {
      date = new Date(timestamp)
    }
  } else {
    date = timestamp
  }
  
  if (isNaN(date.getTime())) {
    return 'unknown time'
  }
  
  const diffInMs = now.getTime() - date.getTime()
  const diffInSeconds = Math.floor(diffInMs / 1000)
  const diffInMinutes = Math.floor(diffInSeconds / 60)
  const diffInHours = Math.floor(diffInMinutes / 60)
  const diffInDays = Math.floor(diffInHours / 24)
  const diffInWeeks = Math.floor(diffInDays / 7)
  const diffInMonths = Math.floor(diffInDays / 30)

  if (diffInSeconds < 60) {
    return diffInSeconds <= 1 ? 'just now' : `${diffInSeconds} second${diffInSeconds === 1 ? '' : 's'} ago`
  } else if (diffInMinutes < 60) {
    return `${diffInMinutes} minute${diffInMinutes === 1 ? '' : 's'} ago`
  } else if (diffInHours < 24) {
    return `${diffInHours} hour${diffInHours === 1 ? '' : 's'} ago`
  } else if (diffInDays < 7) {
    return `${diffInDays} day${diffInDays === 1 ? '' : 's'} ago`
  } else if (diffInWeeks < 4) {
    return `${diffInWeeks} week${diffInWeeks === 1 ? '' : 's'} ago`
  } else if (diffInMonths < 12) {
    return `${diffInMonths} month${diffInMonths === 1 ? '' : 's'} ago`
  } else {
    const diffInYears = Math.floor(diffInDays / 365)
    return `${diffInYears} year${diffInYears === 1 ? '' : 's'} ago`
  }
}

/**
 * Formats a date to a localized date string based on user's timezone
 */
export function formatLocalDate(timestamp: number | string | Date, options?: Intl.DateTimeFormatOptions): string {
  let date: Date
  if (typeof timestamp === 'number') {
    date = new Date(timestamp)
  } else if (typeof timestamp === 'string') {
    if (timestamp.includes('T') && !timestamp.includes('Z') && !timestamp.includes('+')) {
      date = new Date(timestamp + 'Z')
    } else {
      date = new Date(timestamp)
    }
  } else {
    date = timestamp
  }
  
  if (isNaN(date.getTime())) {
    return 'Invalid date'
  }
  
  const defaultOptions: Intl.DateTimeFormatOptions = {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    ...options
  }
  
  return date.toLocaleDateString(undefined, defaultOptions)
}

/**
 * Formats a date to include time based on user's timezone
 */
export function formatLocalDateTime(timestamp: number | string | Date): string {
  let date: Date
  if (typeof timestamp === 'number') {
    date = new Date(timestamp)
  } else if (typeof timestamp === 'string') {
    if (timestamp.includes('T') && !timestamp.includes('Z') && !timestamp.includes('+')) {
      date = new Date(timestamp + 'Z')
    } else {
      date = new Date(timestamp)
    }
  } else {
    date = timestamp
  }
  
  if (isNaN(date.getTime())) {
    return 'Invalid date'
  }
  
  return date.toLocaleString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}
