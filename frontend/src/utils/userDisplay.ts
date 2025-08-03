/**
 * User Display Utilities
 * Generates unique 5-character identifiers for users throughout the platform
 */

/**
 * Generates a unique 5-character identifier from a user ID
 * Uses the first 5 characters of the user ID for consistency
 * @param userId - The full user ID
 * @returns A 5-character unique identifier
 */
export function generateUniqueUserDisplay(userId: string): string {
  if (!userId || typeof userId !== 'string') {
    return 'USER1' // Fallback for invalid IDs
  }
  
  // Take first 5 characters and convert to uppercase for consistency
  const uniqueId = userId.substring(0, 5).toUpperCase()
  
  // Ensure we always have 5 characters by padding with numbers if needed
  if (uniqueId.length < 5) {
    const padding = '12345'.substring(0, 5 - uniqueId.length)
    return uniqueId + padding
  }
  
  return uniqueId
}

/**
 * Gets display name for a user - always returns the unique 5-char identifier
 * @param user - User object with id and optional name fields
 * @returns The unique 5-character identifier
 */
export function getUserDisplayName(user: { 
  id: string
  username?: string
  first_name?: string
  last_name?: string
}): string {
  return generateUniqueUserDisplay(user.id)
}

/**
 * Gets initials for avatar display - uses the unique identifier
 * @param user - User object with id
 * @returns 2-character initials from the unique identifier
 */
export function getUserInitials(user: { id: string }): string {
  const uniqueId = generateUniqueUserDisplay(user.id)
  return uniqueId.substring(0, 2)
}

/**
 * Formats user display for different contexts
 * @param user - User object
 * @param context - Display context ('full', 'short', 'initials')
 * @returns Formatted user display string
 */
export function formatUserDisplay(
  user: { id: string; username?: string; first_name?: string; last_name?: string },
  context: 'full' | 'short' | 'initials' = 'full'
): string {
  const uniqueId = generateUniqueUserDisplay(user.id)
  
  switch (context) {
    case 'initials':
      return getUserInitials(user)
    case 'short':
      return uniqueId.substring(0, 3)
    case 'full':
    default:
      return uniqueId
  }
}