/**
 * Enhanced Error Handling Utilities for MantraPath
 * Provides meaningful, user-friendly error messages with MantraPath context
 */

export interface ApiError {
  message: string
  status: number
  code?: string
  field?: string
  details?: any
}

export interface UserFriendlyError {
  title: string
  message: string
  description?: string
  actionable?: string
  severity: 'info' | 'warning' | 'error' | 'critical'
  category: 'network' | 'validation' | 'authentication' | 'authorization' | 'server' | 'unknown'
}

/**
 * Converts API errors into user-friendly messages with MantraPath context
 */
export function processApiError(error: any): UserFriendlyError {
  const apiError = error as ApiError

  // Handle specific status codes
  switch (apiError.status) {
    case 400:
      return handleBadRequestError(apiError)
    case 401:
      return handleAuthenticationError(apiError)
    case 403:
      return handleAuthorizationError(apiError)
    case 404:
      return handleNotFoundError(apiError)
    case 409:
      return handleConflictError(apiError)
    case 422:
      return handleValidationError(apiError)
    case 429:
      return handleRateLimitError(apiError)
    case 500:
    case 502:
    case 503:
    case 504:
      return handleServerError(apiError)
    default:
      return handleGenericError(apiError)
  }
}

function handleValidationError(error: ApiError): UserFriendlyError {
  const message = error.message || 'Please check your input'
  
  // Extract field-specific validation errors
  if (message.includes('email')) {
    return {
      title: 'Email Issue',
      message: 'Please check your email address',
      description: 'Make sure your email is valid and not already registered.',
      actionable: 'Try a different email or log in if you already have an account.',
      severity: 'warning',
      category: 'validation'
    }
  }
  
  if (message.includes('password')) {
    return {
      title: 'Password Requirements',
      message: 'Your password needs to be stronger',
      description: 'Passwords must be at least 8 characters with a mix of letters, numbers, and symbols.',
      actionable: 'Create a secure password that meets our requirements.',
      severity: 'warning',
      category: 'validation'
    }
  }
  
  if (message.includes('username')) {
    return {
      title: 'Username Unavailable',
      message: 'This username is already taken',
      description: 'Choose a unique username that represents you.',
      actionable: 'Try a different username or add numbers/symbols.',
      severity: 'warning',
      category: 'validation'
    }
  }

  // Challenge creation specific errors
  if (message.includes('title') || message.includes('name')) {
    return {
      title: 'Title Required',
      message: 'Your challenge needs a meaningful title',
      description: 'Give your challenge a name that motivates you and others.',
      actionable: 'Add a descriptive title for your wellness challenge.',
      severity: 'warning',
      category: 'validation'
    }
  }

  if (message.includes('description')) {
    return {
      title: 'Description Required',
      message: 'Please describe your challenge',
      description: 'Help others understand what this challenge is about.',
      actionable: 'Add a detailed description of your wellness challenge.',
      severity: 'warning',
      category: 'validation'
    }
  }

  return {
    title: 'Input Validation',
    message: 'Please review your information',
    description: message,
    actionable: 'Check the highlighted fields and try again.',
    severity: 'warning',
    category: 'validation'
  }
}

function handleAuthenticationError(error: ApiError): UserFriendlyError {
  if (error.message?.includes('verify') || error.message?.includes('verification')) {
    return {
      title: 'Email Verification Required',
      message: 'Please verify your email first',
      description: 'Check your inbox for our verification email.',
      actionable: 'Click the verification link in your email, or request a new one.',
      severity: 'warning',
      category: 'authentication'
    }
  }

  return {
    title: 'Authentication Required',
    message: 'Please log in to continue',
    description: 'Your session may have expired or you need to sign in.',
    actionable: 'Sign in to access your wellness journey.',
    severity: 'warning',
    category: 'authentication'
  }
}

function handleAuthorizationError(error: ApiError): UserFriendlyError {
  return {
    title: 'Access Restricted',
    message: 'You don\'t have permission for this action',
    description: 'This feature might require a different membership level or verification.',
    actionable: 'Check your account status or contact support if needed.',
    severity: 'warning',
    category: 'authorization'
  }
}

function handleNotFoundError(error: ApiError): UserFriendlyError {
  return {
    title: 'Content Not Found',
    message: 'This content is no longer available',
    description: 'The item you\'re looking for might have been moved or deleted.',
    actionable: 'Try refreshing the page or browsing other content.',
    severity: 'info',
    category: 'unknown'
  }
}

function handleConflictError(error: ApiError): UserFriendlyError {
  if (error.message?.includes('email') || error.message?.includes('already exists')) {
    return {
      title: 'Account Already Exists',
      message: 'You already have an account with us',
      description: 'Try logging in instead of creating a new account.',
      actionable: 'Use the sign-in option or reset your password if forgotten.',
      severity: 'info',
      category: 'validation'
    }
  }

  return {
    title: 'Duplicate Action',
    message: 'This action has already been completed',
    description: 'You might have already performed this action.',
    actionable: 'Refresh the page to see the current state.',
    severity: 'info',
    category: 'validation'
  }
}

function handleRateLimitError(error: ApiError): UserFriendlyError {
  return {
    title: 'Please Slow Down',
    message: 'Too many attempts detected',
    description: 'We\'ve temporarily limited your requests to protect our servers.',
    actionable: 'Wait a few minutes before trying again.',
    severity: 'warning',
    category: 'server'
  }
}

function handleServerError(error: ApiError): UserFriendlyError {
  return {
    title: 'Temporary Service Issue',
    message: 'Our servers are experiencing a brief hiccup',
    description: 'This is usually temporary and resolves quickly.',
    actionable: 'Please try again in a moment. Your data is safe.',
    severity: 'error',
    category: 'server'
  }
}

function handleBadRequestError(error: ApiError): UserFriendlyError {
  return {
    title: 'Invalid Request',
    message: 'Something went wrong with your request',
    description: error.message || 'Please check your input and try again.',
    actionable: 'Review your information and submit again.',
    severity: 'warning',
    category: 'validation'
  }
}

function handleGenericError(error: ApiError): UserFriendlyError {
  // Network/connectivity errors
  if (error.message?.includes('fetch') || error.message?.includes('network') || error.status === 0) {
    return {
      title: 'Connection Issue',
      message: 'Unable to connect to MantraPath services',
      description: 'This might be a temporary network issue.',
      actionable: 'Check your internet connection and try again.',
      severity: 'error',
      category: 'network'
    }
  }

  return {
    title: 'Unexpected Error',
    message: 'Something unexpected happened',
    description: error.message || 'An unknown error occurred.',
    actionable: 'Please try again or contact support if this persists.',
    severity: 'error',
    category: 'unknown'
  }
}

/**
 * Creates MantraPath-specific success messages
 */
export function createSuccessMessage(action: string, context?: string): { title: string; message: string; description?: string } {
  const successMessages = {
    login: {
      title: 'Welcome back!',
      message: 'You\'re ready to continue your wellness journey',
      description: 'All your data and progress are waiting for you.'
    },
    register: {
      title: 'Welcome to MantraPath!',
      message: 'Your wellness journey begins now',
      description: 'Check your email to verify your account and unlock all features.'
    },
    'mood-entry': {
      title: 'Mood logged!',
      message: 'Thank you for checking in with yourself',
      description: 'Your emotional awareness is growing stronger each day.'
    },
    'journal-entry': {
      title: 'Journal saved!',
      message: 'Your thoughts have been safely recorded',
      description: 'Reflection is a powerful tool for personal growth.'
    },
    'challenge-join': {
      title: 'Challenge accepted!',
      message: 'You\'re now part of this wellness challenge',
      description: 'Stay committed and watch yourself grow.'
    },
    'challenge-create': {
      title: 'Challenge created!',
      message: 'Your wellness challenge is now live',
      description: 'Others can now join you on this journey.'
    },
    'forum-join': {
      title: 'Welcome to the community!',
      message: 'You\'ve joined a supportive wellness community',
      description: 'Share experiences and support others on their journey.'
    }
  }

  return successMessages[action] || {
    title: 'Success!',
    message: 'Action completed successfully',
    description: context
  }
}

/**
 * GDPR and Privacy Compliance Helpers
 */
export function createPrivacyNotice(dataType: 'profile' | 'mood' | 'journal' | 'community'): string {
  const notices = {
    profile: 'Your profile information is stored securely and only shared according to your privacy settings.',
    mood: 'Your mood data is private by default and used only to provide personalized insights.',
    journal: 'Journal entries are completely private unless you choose to share specific insights.',
    community: 'Community interactions are visible to other members. You can adjust your visibility settings anytime.'
  }
  
  return notices[dataType] + ' You have full control over your data and can delete it anytime.'
}

/**
 * Subscription and Feature Access Messages
 */
export function getFeatureAccessMessage(feature: string, userTier: 'free' | 'premium' | 'pro'): UserFriendlyError | null {
  const featureRequirements = {
    'advanced-analytics': 'premium',
    'export-data': 'premium',
    'unlimited-journal': 'premium',
    'priority-support': 'pro',
    'custom-insights': 'pro',
    'team-challenges': 'pro'
  }

  const requiredTier = featureRequirements[feature]
  if (!requiredTier || userTier === requiredTier || 
      (requiredTier === 'premium' && userTier === 'pro')) {
    return null
  }

  return {
    title: 'Upgrade Required',
    message: `This feature requires ${requiredTier} membership`,
    description: 'Unlock advanced wellness tools and insights with an upgrade.',
    actionable: 'View upgrade options to access this feature.',
    severity: 'info',
    category: 'authorization'
  }
}
