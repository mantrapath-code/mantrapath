// API Gateway Response Parser Utility
// Handles the wrapped response format from the API Gateway

export interface GatewayResponse<T = any> {
  status_code: number
  headers: Record<string, string>
  body: string
  response_time: number
  service_name: string
  request_id: string
}

export function parseGatewayResponse<T>(response: any): T {
  // Check if this is a wrapped API Gateway response
  if (response && typeof response === 'object' && response.body && typeof response.body === 'string') {
    // Parse the body JSON string
    try {
      return JSON.parse(response.body) as T
    } catch (error) {
      console.error('Failed to parse Gateway response body:', error)
      throw new Error('Invalid response format from API Gateway')
    }
  }
  
  // Return as-is if not wrapped (direct service response)
  return response as T
}

export function isGatewayResponse(response: any): response is GatewayResponse {
  return (
    response &&
    typeof response === 'object' &&
    typeof response.status_code === 'number' &&
    typeof response.body === 'string' &&
    typeof response.service_name === 'string'
  )
}
