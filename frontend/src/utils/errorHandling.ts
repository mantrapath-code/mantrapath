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
  const lowerMessage = message.toLowerCase()
  
  // Extract field-specific validation errors
  if (lowerMessage.includes('email')) {
    if (lowerMessage.includes('invalid') || lowerMessage.includes('format')) {
      return {
        title: 'Invalid Email Format',
        message: 'Please enter a valid email address',
        description: 'Make sure your email follows the standard format (e.g., user@example.com).',
        actionable: 'Check for typos and ensure you\'re using a valid email address.',
        severity: 'warning',
        category: 'validation'
      }
    } else if (lowerMessage.includes('required') || lowerMessage.includes('missing')) {
      return {
        title: 'Email Required',
        message: 'Please provide your email address',
        description: 'We need your email to create your account and send important updates.',
        actionable: 'Enter a valid email address in the email field.',
        severity: 'warning',
        category: 'validation'
      }
    } else if (lowerMessage.includes('already registered') || lowerMessage.includes('already exists')) {
      return {
        title: 'Email Already Registered',
        message: 'This email is already in use',
        description: 'You already have an account with us using this email address.',
        actionable: 'Try logging in instead, or use a different email address.',
        severity: 'info',
        category: 'validation'
      }
    }
  }
  
  if (lowerMessage.includes('password')) {
    if (lowerMessage.includes('weak') || lowerMessage.includes('too short') || lowerMessage.includes('minimum')) {
      return {
        title: 'Password Too Weak',
        message: 'Your password needs to be stronger',
        description: 'Passwords must be at least 8 characters with a mix of letters, numbers, and symbols.',
        actionable: 'Create a secure password that meets our requirements.',
        severity: 'warning',
        category: 'validation'
      }
    } else if (lowerMessage.includes('required') || lowerMessage.includes('missing')) {
      return {
        title: 'Password Required',
        message: 'Please create a password',
        description: 'A strong password helps protect your account and personal information.',
        actionable: 'Enter a secure password that meets our requirements.',
        severity: 'warning',
        category: 'validation'
      }
    } else if (lowerMessage.includes('mismatch') || lowerMessage.includes('confirm')) {
      return {
        title: 'Password Mismatch',
        message: 'Passwords do not match',
        description: 'The password and confirmation password must be identical.',
        actionable: 'Make sure both password fields contain the same value.',
        severity: 'warning',
        category: 'validation'
      }
    }
  }
  
  if (lowerMessage.includes('username')) {
    if (lowerMessage.includes('taken') || lowerMessage.includes('already exists')) {
      return {
        title: 'Username Unavailable',
        message: 'This username is already taken',
        description: 'Choose a unique username that represents you.',
        actionable: 'Try a different username or add numbers/symbols.',
        severity: 'warning',
        category: 'validation'
      }
    } else if (lowerMessage.includes('invalid') || lowerMessage.includes('format')) {
      return {
        title: 'Invalid Username Format',
        message: 'Username contains invalid characters',
        description: 'Usernames can only contain letters, numbers, underscores, and hyphens.',
        actionable: 'Use only alphanumeric characters, underscores, and hyphens.',
        severity: 'warning',
        category: 'validation'
      }
    } else if (lowerMessage.includes('too short') || lowerMessage.includes('minimum')) {
      return {
        title: 'Username Too Short',
        message: 'Username must be at least 3 characters',
        description: 'Choose a username that\'s easy to remember and type.',
        actionable: 'Make your username at least 3 characters long.',
        severity: 'warning',
        category: 'validation'
      }
    } else if (lowerMessage.includes('required') || lowerMessage.includes('missing')) {
      return {
        title: 'Username Required',
        message: 'Please choose a username',
        description: 'A username helps identify you in the community.',
        actionable: 'Enter a unique username for your account.',
        severity: 'warning',
        category: 'validation'
      }
    }
  }
  
  if (lowerMessage.includes('first_name') || lowerMessage.includes('first name')) {
    if (lowerMessage.includes('required') || lowerMessage.includes('missing')) {
      return {
        title: 'First Name Required',
        message: 'Please provide your first name',
        description: 'We use your name to personalize your experience.',
        actionable: 'Enter your first name in the appropriate field.',
        severity: 'warning',
        category: 'validation'
      }
    } else if (lowerMessage.includes('invalid') || lowerMessage.includes('format')) {
      return {
        title: 'Invalid First Name',
        message: 'First name contains invalid characters',
        description: 'Names should only contain letters, spaces, hyphens, and apostrophes.',
        actionable: 'Use only valid characters for your name.',
        severity: 'warning',
        category: 'validation'
      }
    }
  }
  
  if (lowerMessage.includes('last_name') || lowerMessage.includes('last name')) {
    if (lowerMessage.includes('required') || lowerMessage.includes('missing')) {
      return {
        title: 'Last Name Required',
        message: 'Please provide your last name',
        description: 'We use your name to personalize your experience.',
        actionable: 'Enter your last name in the appropriate field.',
        severity: 'warning',
        category: 'validation'
      }
    } else if (lowerMessage.includes('invalid') || lowerMessage.includes('format')) {
      return {
        title: 'Invalid Last Name',
        message: 'Last name contains invalid characters',
        description: 'Names should only contain letters, spaces, hyphens, and apostrophes.',
        actionable: 'Use only valid characters for your name.',
        severity: 'warning',
        category: 'validation'
      }
    }
  }

  // Challenge creation specific errors
  if (lowerMessage.includes('title') || lowerMessage.includes('name')) {
    return {
      title: 'Title Required',
      message: 'Your challenge needs a meaningful title',
      description: 'Give your challenge a name that motivates you and others.',
      actionable: 'Add a descriptive title for your wellness challenge.',
      severity: 'warning',
      category: 'validation'
    }
  }

  // Generic validation error
  return {
    title: 'Validation Error',
    message: 'Please check your input',
    description: message,
    actionable: 'Review the highlighted fields and correct any errors.',
    severity: 'warning',
    category: 'validation'
  }
}

function handleAuthenticationError(error: ApiError): UserFriendlyError {
  const message = error.message || ''
  const lowerMessage = message.toLowerCase()
  
  // Handle email verification errors
  if (lowerMessage.includes('verify') || lowerMessage.includes('verification')) {
    return {
      title: 'Email Verification Required',
      message: 'Please verify your email first',
      description: 'Check your inbox for our verification email.',
      actionable: 'Click the verification link in your email, or request a new one.',
      severity: 'warning',
      category: 'authentication'
    }
  }
  
  // Handle invalid credentials
  if (lowerMessage.includes('invalid credentials') || 
      lowerMessage.includes('incorrect password') ||
      lowerMessage.includes('wrong password') ||
      lowerMessage.includes('bad credentials')) {
    return {
      title: 'Invalid Credentials',
      message: 'The email/username or password you entered is incorrect',
      description: 'Please double-check your login information and try again.',
      actionable: 'Verify your email/username and password, or use the "Forgot Password" option.',
      severity: 'warning',
      category: 'authentication'
    }
  }
  
  // Handle user not found
  if (lowerMessage.includes('user not found') || 
      lowerMessage.includes('does not exist') ||
      lowerMessage.includes('no account') ||
      lowerMessage.includes('account not found')) {
    return {
      title: 'Account Not Found',
      message: 'No account found with these credentials',
      description: 'The email or username you entered doesn\'t match any existing account.',
      actionable: 'Check your spelling, create a new account, or contact support if you believe this is an error.',
      severity: 'info',
      category: 'authentication'
    }
  }
  
  // Handle account locked/suspended
  if (lowerMessage.includes('locked') || 
      lowerMessage.includes('suspended') ||
      lowerMessage.includes('disabled') ||
      lowerMessage.includes('inactive')) {
    return {
      title: 'Account Temporarily Unavailable',
      message: 'Your account has been temporarily restricted',
      description: 'This may be due to security concerns or policy violations.',
      actionable: 'Please contact our support team to resolve this issue.',
      severity: 'error',
      category: 'authentication'
    }
  }
  
  // Handle too many attempts
  if (lowerMessage.includes('too many attempts') || 
      lowerMessage.includes('rate limit') ||
      lowerMessage.includes('multiple failed')) {
    return {
      title: 'Too Many Login Attempts',
      message: 'Your account has been temporarily locked',
      description: 'For security reasons, we\'ve temporarily blocked login attempts.',
      actionable: 'Wait 15 minutes before trying again, or use the "Forgot Password" option.',
      severity: 'warning',
      category: 'authentication'
    }
  }
  
  // Handle expired tokens
  if (lowerMessage.includes('expired') || 
      lowerMessage.includes('token expired') ||
      lowerMessage.includes('session expired')) {
    return {
      title: 'Session Expired',
      message: 'Your login session has expired',
      description: 'Please sign in again to continue using MantraPath.',
      actionable: 'Enter your credentials to start a new session.',
      severity: 'info',
      category: 'authentication'
    }
  }

  // Default authentication error
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
  const message = error.message || ''
  const lowerMessage = message.toLowerCase()
  
  // Handle email already exists
  if (lowerMessage.includes('email') && 
      (lowerMessage.includes('already exists') || 
       lowerMessage.includes('already registered') ||
       lowerMessage.includes('duplicate'))) {
    return {
      title: 'Email Already Registered',
      message: 'This email address is already in use',
      description: 'You already have an account with us using this email address.',
      actionable: 'Try logging in instead, or use a different email address for registration.',
      severity: 'info',
      category: 'validation'
    }
  }
  
  // Handle username already taken
  if (lowerMessage.includes('username') && 
      (lowerMessage.includes('already exists') || 
       lowerMessage.includes('already taken') ||
       lowerMessage.includes('duplicate') ||
       lowerMessage.includes('taken'))) {
    return {
      title: 'Username Unavailable',
      message: 'This username is already taken',
      description: 'Choose a unique username that represents you.',
      actionable: 'Try adding numbers, symbols, or using a different username.',
      severity: 'warning',
      category: 'validation'
    }
  }
  
  // Handle phone number conflicts
  if (lowerMessage.includes('phone') && 
      (lowerMessage.includes('already exists') || 
       lowerMessage.includes('already registered'))) {
    return {
      title: 'Phone Number Already Registered',
      message: 'This phone number is already in use',
      description: 'You already have an account with us using this phone number.',
      actionable: 'Try logging in instead, or use a different phone number.',
      severity: 'info',
      category: 'validation'
    }
  }
  
  // Handle general account conflicts
  if (lowerMessage.includes('already exists') || 
      lowerMessage.includes('already registered') ||
      lowerMessage.includes('duplicate')) {
    return {
      title: 'Account Already Exists',
      message: 'You already have an account with us',
      description: 'Try logging in instead of creating a new account.',
      actionable: 'Use the sign-in option or reset your password if forgotten.',
      severity: 'info',
      category: 'validation'
    }
  }

  // Default conflict error
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
