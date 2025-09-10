/**
 * API Configuration utility
 * Detects if app is accessed through ngrok and configures API endpoints accordingly
 */

// Function to detect if we're accessing through ngrok
const isAccessedThroughNgrok = (): boolean => {
  return window.location.hostname.includes('ngrok-free.app') || 
         window.location.hostname.includes('ngrok.io');
};

// Function to get the correct API base URL
export const getApiBaseUrl = (): string => {
  // If accessed through ngrok, use the ngrok backend URL
  if (isAccessedThroughNgrok()) {
    // This should be the ngrok URL for the backend
    return import.meta.env.VITE_NGROK_BACKEND_URL || 'https://f5b4589b2fdf.ngrok-free.app';
  }
  
  // Default to local development
  return import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
};

// Function to get service URLs based on environment
export const getServiceUrls = () => {
  const baseUrl = getApiBaseUrl();
  
  if (isAccessedThroughNgrok()) {
    // When accessed through ngrok, all services should go through the API Gateway
    return {
      API_BASE_URL: baseUrl,
      ML_SERVICE_URL: `${baseUrl}/ml`,
      COMMUNITY_SERVICE_URL: `${baseUrl}/community`,
      PROFILE_SERVICE_URL: `${baseUrl}/profile`,
      AI_CONTEXT_SERVICE_URL: `${baseUrl}/ai-context`,
      AI_EVENT_PROCESSOR_URL: `${baseUrl}/ai-events`,
      ASSISTANCE_ENGINE_URL: `${baseUrl}/assistance`,
      MOOD_SERVICE_URL: `${baseUrl}/mood`,
  // IMPORTANT: Do NOT append /chatbot here. Frontend request helpers already
  // include paths like /chat/intelligent or /api/chatbot/chat/session.
  // Previously this produced URLs like /chatbot/api/chatbot/chat/session (404).
  // Using the gateway base fixes routing via existing rules (^/chat/ and ^/api/chatbot/).
  CHATBOT_SERVICE_URL: `${baseUrl}`,
    };
  }
  
  // Local development - use API Gateway for consistency
  return {
    API_BASE_URL: baseUrl,
    ML_SERVICE_URL: `${baseUrl}/ml`,
    COMMUNITY_SERVICE_URL: `${baseUrl}/community`,
    PROFILE_SERVICE_URL: `${baseUrl}/profile`,
    AI_CONTEXT_SERVICE_URL: `${baseUrl}/ai-context`,
    AI_EVENT_PROCESSOR_URL: `${baseUrl}/ai-events`,
    ASSISTANCE_ENGINE_URL: `${baseUrl}/assistance`,
    MOOD_SERVICE_URL: `${baseUrl}/mood`,
  // Keep chatbot pointing to gateway root; helper methods supply full path.
  CHATBOT_SERVICE_URL: `${baseUrl}`,
  };
};

// Environment info for debugging
export const getEnvironmentInfo = () => {
  return {
    hostname: window.location.hostname,
    isNgrok: isAccessedThroughNgrok(),
    baseUrl: getApiBaseUrl(),
    serviceUrls: getServiceUrls(),
  };
};

// Log environment info in development
if (import.meta.env.DEV) {
  console.log('🔧 API Configuration:', getEnvironmentInfo());
}
