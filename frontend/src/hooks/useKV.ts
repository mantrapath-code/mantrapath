import { useState, useEffect } from 'react'

/**
 * Utility function to safely check if localStorage is available
 */
const isLocalStorageAvailable = (): boolean => {
  try {
    const test = '__localStorage_test__'
    window.localStorage.setItem(test, test)
    window.localStorage.removeItem(test)
    return true
  } catch {
    return false
  }
}

/**
 * Custom hook to replace @github/spark/hooks useKV
 * Uses localStorage for persistence with enhanced error handling
 */
/**
 * Utility function to clean up corrupted localStorage entries
 * Can be called manually if needed
 */
export const cleanupLocalStorage = (keys?: string[]): void => {
  if (!isLocalStorageAvailable()) {
    console.warn('localStorage is not available for cleanup')
    return
  }

  try {
    const keysToCheck = keys || Object.keys(window.localStorage)
    
    keysToCheck.forEach(key => {
      try {
        const item = window.localStorage.getItem(key)
        if (item && item !== 'undefined' && item !== 'null' && item.trim() !== '') {
          JSON.parse(item) // Test if it's valid JSON
        }
      } catch (error) {
        console.warn(`Removing corrupted localStorage key: ${key}`)
        window.localStorage.removeItem(key)
      }
    })
  } catch (error) {
    console.error('Error during localStorage cleanup:', error)
  }
}

export function useKV<T>(key: string, defaultValue: T): [T, (value: T) => void] {
  const [storedValue, setStoredValue] = useState<T>(() => {
    // Check if localStorage is available
    if (!isLocalStorageAvailable()) {
      console.warn('localStorage is not available, using default value for key:', key)
      return defaultValue
    }

    try {
      const item = window.localStorage.getItem(key)
      
      // Handle null, undefined, or empty string cases
      if (!item || item === 'undefined' || item === 'null' || item.trim() === '') {
        return defaultValue
      }
      
      // Try to parse the JSON
      const parsed = JSON.parse(item)
      return parsed
    } catch (error) {
      console.error(`Error reading localStorage key "${key}":`, error)
      
      // Clear the corrupted data and return default value
      try {
        window.localStorage.removeItem(key)
        console.log(`Cleared corrupted localStorage key "${key}"`)
      } catch (clearError) {
        console.error(`Error clearing localStorage key "${key}":`, clearError)
      }
      
      return defaultValue
    }
  })

  const setValue = (value: T) => {
    try {
      // Update state first
      setStoredValue(value)
      
      // Check if localStorage is available before trying to use it
      if (!isLocalStorageAvailable()) {
        console.warn('localStorage is not available, value only stored in memory for key:', key)
        return
      }
      
      // Validate that the value can be stringified
      const stringifiedValue = JSON.stringify(value)
      
      // Then update localStorage
      window.localStorage.setItem(key, stringifiedValue)
    } catch (error) {
      console.error(`Error setting localStorage key "${key}":`, error)
      
      // State is already updated above, so the hook will still work in memory
    }
  }

  return [storedValue, setValue]
}
