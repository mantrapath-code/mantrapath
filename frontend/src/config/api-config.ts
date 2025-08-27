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
      CHATBOT_SERVICE_URL: `${baseUrl}/chatbot`,
    };
  }
  
  // Local development - direct service URLs
  return {
    API_BASE_URL: baseUrl,
    ML_SERVICE_URL: import.meta.env.VITE_ML_SERVICE_URL || 'http://localhost:8008',
    COMMUNITY_SERVICE_URL: 'http://localhost:8006',
    PROFILE_SERVICE_URL: 'http://localhost:8002',
    AI_CONTEXT_SERVICE_URL: 'http://localhost:8001',
    AI_EVENT_PROCESSOR_URL: 'http://localhost:8014',
    ASSISTANCE_ENGINE_URL: 'http://localhost:8018',
    MOOD_SERVICE_URL: 'http://localhost:8003',
    CHATBOT_SERVICE_URL: 'http://localhost:8004',
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
