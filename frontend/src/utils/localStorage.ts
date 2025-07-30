/**
 * LocalStorage utilities for debugging and maintenance
 */

/**
 * Common localStorage keys used in the application
 */
export const STORAGE_KEYS = {
  COMMUNITY_MOOD_PATTERNS: 'community-mood-patterns',
  COMMUNITY_STATS: 'community-stats',
  DISMISSED_PATTERNS: 'dismissed-patterns',
  LAST_PATTERN_CHECK: 'last-pattern-check',
  USER_MOODS: 'user-moods',
  JOINED_FORUMS: 'joined-forums',
  LIKED_THREADS: 'liked-threads',
  BOOKMARKED_THREADS: 'bookmarked-threads',
  USER_REPUTATION: 'user-reputation',
  NOTIFICATION_SCHEDULES: 'notification-schedules',
  NOTIFICATION_PREFERENCES: 'notification-preferences',
} as const

/**
 * Debug function to inspect localStorage values
 */
export const inspectLocalStorage = (): void => {
  console.group('LocalStorage Inspection')
  
  Object.values(STORAGE_KEYS).forEach(key => {
    try {
      const value = localStorage.getItem(key)
      if (value !== null) {
        const parsed = JSON.parse(value)
        console.log(`✅ ${key}:`, parsed)
      } else {
        console.log(`❌ ${key}: not found`)
      }
    } catch (error) {
      console.error(`🔥 ${key}: corrupted data -`, error)
      console.log(`   Raw value:`, localStorage.getItem(key))
    }
  })
  
  console.groupEnd()
}

/**
 * Clear specific corrupted keys
 */
export const clearCorruptedKeys = (): number => {
  let clearedCount = 0
  
  Object.values(STORAGE_KEYS).forEach(key => {
    try {
      const value = localStorage.getItem(key)
      if (value && value !== 'undefined' && value !== 'null' && value.trim() !== '') {
        JSON.parse(value) // Test parsing
      }
    } catch (error) {
      console.warn(`Clearing corrupted key: ${key}`)
      localStorage.removeItem(key)
      clearedCount++
    }
  })
  
  console.log(`Cleared ${clearedCount} corrupted localStorage keys`)
  return clearedCount
}

/**
 * Reset all application localStorage data
 */
export const resetAllLocalStorage = (): void => {
  Object.values(STORAGE_KEYS).forEach(key => {
    localStorage.removeItem(key)
  })
  console.log('All application localStorage data has been reset')
}

/**
 * Initialize default values for all keys
 */
export const initializeDefaults = (): void => {
  const defaults = {
    [STORAGE_KEYS.COMMUNITY_MOOD_PATTERNS]: [],
    [STORAGE_KEYS.COMMUNITY_STATS]: {
      patternsShared: 0,
      encouragementsGiven: 0,
      encouragementsReceived: 0,
      supportStreak: 0,
      helpfulReplies: 0
    },
    [STORAGE_KEYS.DISMISSED_PATTERNS]: [],
    [STORAGE_KEYS.LAST_PATTERN_CHECK]: 0,
    [STORAGE_KEYS.USER_MOODS]: [],
    [STORAGE_KEYS.JOINED_FORUMS]: [],
    [STORAGE_KEYS.LIKED_THREADS]: [],
    [STORAGE_KEYS.BOOKMARKED_THREADS]: [],
    [STORAGE_KEYS.USER_REPUTATION]: 0,
    [STORAGE_KEYS.NOTIFICATION_SCHEDULES]: [],
    [STORAGE_KEYS.NOTIFICATION_PREFERENCES]: {
      enabled: true,
      types: ['mood-reminders', 'pattern-alerts', 'wellness-tips'],
      quietHours: { start: 22, end: 8 },
      frequency: 'smart'
    }
  }
  
  Object.entries(defaults).forEach(([key, value]) => {
    if (!localStorage.getItem(key)) {
      localStorage.setItem(key, JSON.stringify(value))
    }
  })
  
  console.log('Default values initialized for missing localStorage keys')
}

// Expose utilities on window for debugging
if (typeof window !== 'undefined') {
  (window as any).localStorageUtils = {
    inspect: inspectLocalStorage,
    clearCorrupted: clearCorruptedKeys,
    reset: resetAllLocalStorage,
    initialize: initializeDefaults
  }
}
