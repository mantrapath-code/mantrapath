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
  
  // Prioritize environment variable first, then fall back to origin-based URL
  // This ensures proper configuration for server deployment
  return import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_GATEWAY_URL || `${window.location.origin}/api`;
};

// Function to get service URLs based on environment
export const getServiceUrls = () => {
  const baseUrl = getApiBaseUrl();
  const origin = window.location.origin; // Root origin without /api
  
  if (isAccessedThroughNgrok()) {
    // When accessed through ngrok, all services still go through the API Gateway.
    // Use origin-level base for custom calls so endpoints can include "/api/..." paths once.
    return {
      API_BASE_URL: baseUrl,
      // Custom bases for service-specific calls (endpoints will include /api/.. or /api/ml/..)
      ML_SERVICE_URL: origin,
      COMMUNITY_SERVICE_URL: origin,
      PROFILE_SERVICE_URL: origin,
      AI_CONTEXT_SERVICE_URL: origin,
      AI_EVENT_PROCESSOR_URL: origin,
      ASSISTANCE_ENGINE_URL: origin,
      MOOD_SERVICE_URL: origin,
      // IMPORTANT: Keep chatbot pointing to origin; helper methods supply full path.
      CHATBOT_SERVICE_URL: origin,
    };
  }
  
  // Local development - use API Gateway for consistency
  return {
    API_BASE_URL: baseUrl,
    // For custom calls, use origin-level base; endpoints will include /api/... paths
    ML_SERVICE_URL: origin,
    COMMUNITY_SERVICE_URL: origin,
    PROFILE_SERVICE_URL: origin,
    AI_CONTEXT_SERVICE_URL: origin,
    AI_EVENT_PROCESSOR_URL: origin,
    ASSISTANCE_ENGINE_URL: origin,
    MOOD_SERVICE_URL: origin,
    // Keep chatbot pointing to origin; helper methods supply full path.
    CHATBOT_SERVICE_URL: origin,
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
