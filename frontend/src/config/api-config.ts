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
  
  // Return empty string so endpoints that already include /api/ work correctly
  // The /api/ prefix is handled by nginx proxy
  return '';
};

// Function to get service URLs based on environment
export const getServiceUrls = () => {
  const baseUrl = getApiBaseUrl();
  
  if (isAccessedThroughNgrok()) {
    // When accessed through ngrok, all services still go through the API Gateway.
    return {
      API_BASE_URL: baseUrl,
      ML_SERVICE_URL: baseUrl,
      COMMUNITY_SERVICE_URL: baseUrl,
      PROFILE_SERVICE_URL: baseUrl,
      AI_CONTEXT_SERVICE_URL: baseUrl,
      AI_EVENT_PROCESSOR_URL: baseUrl,
      ASSISTANCE_ENGINE_URL: baseUrl,
      MOOD_SERVICE_URL: baseUrl,
      CHATBOT_SERVICE_URL: baseUrl,
      VOICE_SERVICE_URL: baseUrl,
    };
  }
  
  // For production/deployment - use relative paths
  return {
    API_BASE_URL: baseUrl,
    ML_SERVICE_URL: baseUrl,
    COMMUNITY_SERVICE_URL: baseUrl,
    PROFILE_SERVICE_URL: baseUrl,
    AI_CONTEXT_SERVICE_URL: baseUrl,
    AI_EVENT_PROCESSOR_URL: baseUrl,
    ASSISTANCE_ENGINE_URL: baseUrl,
    MOOD_SERVICE_URL: baseUrl,
    CHATBOT_SERVICE_URL: baseUrl,
    VOICE_SERVICE_URL: baseUrl,
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
