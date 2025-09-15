/**
 * Enhanced Error Handler for API Requests
 * Implements circuit breaker pattern and graceful degradation
 */

export interface ApiError {
  message: string
  status: number
  details?: any
  isRetryable?: boolean
  timestamp?: string
}

export class CircuitBreaker {
  private failureCount = 0
  private nextAttemptTime = 0
  private readonly failureThreshold: number
  private readonly resetTimeoutMs: number
  private readonly halfOpenMaxAttempts: number
  private state: 'CLOSED' | 'OPEN' | 'HALF_OPEN' = 'CLOSED'

  constructor(
    failureThreshold = 5,
    resetTimeoutMs = 60000, // 1 minute
    halfOpenMaxAttempts = 3
  ) {
    this.failureThreshold = failureThreshold
    this.resetTimeoutMs = resetTimeoutMs
    this.halfOpenMaxAttempts = halfOpenMaxAttempts
  }

  async execute<T>(operation: () => Promise<T>): Promise<T> {
    if (this.state === 'OPEN') {
      if (Date.now() < this.nextAttemptTime) {
        throw new Error('Circuit breaker is OPEN. Service temporarily unavailable.')
      }
      // Try to recover
      this.state = 'HALF_OPEN'
    }

    try {
      const result = await operation()
      this.onSuccess()
      return result
    } catch (error) {
      this.onFailure()
      throw error
    }
  }

  private onSuccess(): void {
    this.failureCount = 0
    this.state = 'CLOSED'
  }

  private onFailure(): void {
    this.failureCount++
    if (this.failureCount >= this.failureThreshold) {
      this.state = 'OPEN'
      this.nextAttemptTime = Date.now() + this.resetTimeoutMs
    }
  }

  getState(): string {
    return this.state
  }

  isAvailable(): boolean {
    return this.state === 'CLOSED' || (this.state === 'HALF_OPEN' && Date.now() >= this.nextAttemptTime)
  }
}

export class ApiErrorHandler {
  private static circuitBreakers = new Map<string, CircuitBreaker>()
  private static retryDelays = [1000, 2000, 4000] // Exponential backoff

  static getCircuitBreaker(endpoint: string): CircuitBreaker {
    if (!this.circuitBreakers.has(endpoint)) {
      this.circuitBreakers.set(endpoint, new CircuitBreaker())
    }
    return this.circuitBreakers.get(endpoint)!
  }

  static createError(message: string, status: number, details?: any): ApiError {
    return {
      message,
      status,
      details,
      isRetryable: status >= 500 || status === 0, // Server errors and network errors are retryable
      timestamp: new Date().toISOString()
    }
  }

  static async withRetry<T>(
    operation: () => Promise<T>,
    endpoint: string,
    maxRetries = 3
  ): Promise<T> {
    const circuitBreaker = this.getCircuitBreaker(endpoint)

    if (!circuitBreaker.isAvailable()) {
      throw this.createError(
        'Service temporarily unavailable due to circuit breaker',
        503,
        { circuitBreakerState: circuitBreaker.getState() }
      )
    }

    return circuitBreaker.execute(async () => {
      let lastError: any = null

      for (let attempt = 0; attempt <= maxRetries; attempt++) {
        try {
          return await operation()
        } catch (error: any) {
          lastError = error
          
          // Don't retry on client errors (4xx) except 429 (rate limit)
          if (error.status >= 400 && error.status < 500 && error.status !== 429) {
            throw error
          }

          // Don't retry on the last attempt
          if (attempt === maxRetries) {
            break
          }

          // Wait before retry with exponential backoff
          const delay = this.retryDelays[attempt] || this.retryDelays[this.retryDelays.length - 1]
          await new Promise(resolve => setTimeout(resolve, delay))
        }
      }

      throw lastError
    })
  }

  static handleFetchError(error: any, endpoint: string): ApiError {
    if (error instanceof TypeError && error.message.includes('Failed to fetch')) {
      return this.createError(
        'Network error: Unable to connect to backend services',
        0,
        {
          endpoint,
          cause: 'Network connectivity issue or CORS error',
          suggestion: 'Check if backend services are running and accessible'
        }
      )
    }

    if (error.name === 'AbortError') {
      return this.createError(
        'Request timeout: Backend services are not responding',
        408,
        {
          endpoint,
          cause: 'Request took too long to complete',
          suggestion: 'Try again later or check backend service health'
        }
      )
    }

    // If it's already an ApiError, return it
    if (error.status !== undefined) {
      return error
    }

    // Generic error
    return this.createError(
      error.message || 'An unexpected error occurred',
      500,
      { originalError: error, endpoint }
    )
  }

  static shouldUseOfflineMode(error: ApiError): boolean {
    // Use offline mode for network errors, timeouts, and consistent 5xx errors
    return error.status === 0 || error.status === 408 || error.status >= 500
  }

  static logError(error: ApiError, context: string): void {
    const isDevelopment = import.meta.env.DEV
    
    if (isDevelopment) {
      console.group(`🔥 API Error - ${context}`)
      console.error('Message:', error.message)
      console.error('Status:', error.status)
      console.error('Details:', error.details)
      console.error('Timestamp:', error.timestamp)
      console.groupEnd()
    } else {
      // In production, log less verbosely
      console.error(`API Error [${error.status}]: ${error.message}`)
    }
  }
}

// Export utility for consistent error processing
export const processApiError = (error: any, endpoint: string): ApiError => {
  return ApiErrorHandler.handleFetchError(error, endpoint)
}

export const withRetry = ApiErrorHandler.withRetry.bind(ApiErrorHandler)
export const shouldUseOfflineMode = ApiErrorHandler.shouldUseOfflineMode.bind(ApiErrorHandler)
export const logApiError = ApiErrorHandler.logError.bind(ApiErrorHandler)