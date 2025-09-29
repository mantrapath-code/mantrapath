// Canonical service endpoint resolver for frontend.
// Mirrors backend docs/SERVICE_ENDPOINTS.md authoritative mapping.
// Prefer using environment variables beginning with VITE_* to override.

interface ServiceEntry {
  key: string;
  host: string;
  port: number;
  envVar?: string; // Vite env var for override
  pathPrefix?: string; // optional base path
}

export const SERVICE_ENDPOINTS: ServiceEntry[] = [
  { key: 'api_gateway', host: 'api-gateway', port: 8000, envVar: 'VITE_API_GATEWAY_URL' },
  { key: 'auth', host: 'auth-service', port: 8001, envVar: 'VITE_AUTH_SERVICE_URL' },
  { key: 'profile', host: 'profile-service', port: 8002, envVar: 'VITE_PROFILE_SERVICE_URL' },
  { key: 'mood', host: 'mood-service', port: 8003, envVar: 'VITE_MOOD_SERVICE_URL' },
  { key: 'chatbot', host: 'chatbot-service', port: 8004, envVar: 'VITE_CHATBOT_SERVICE_URL' },
  { key: 'content', host: 'content-service', port: 8005, envVar: 'VITE_CONTENT_SERVICE_URL' },
  { key: 'community', host: 'community-service', port: 8006, envVar: 'VITE_COMMUNITY_SERVICE_URL' },
  { key: 'notification', host: 'notification-service', port: 8007, envVar: 'VITE_NOTIFICATION_SERVICE_URL' },
  { key: 'ml', host: 'ml-service', port: 8008, envVar: 'VITE_ML_SERVICE_URL' },
  { key: 'translation', host: 'translation-service', port: 8010, envVar: 'VITE_TRANSLATION_SERVICE_URL' },
  { key: 'voice', host: 'voice-service', port: 8011, envVar: 'VITE_VOICE_SERVICE_URL' },
  { key: 'action', host: 'action-orchestrator', port: 8012, envVar: 'VITE_ACTION_ORCHESTRATOR_URL' },
  { key: 'ai_context', host: 'ai-context-store', port: 8013, envVar: 'VITE_AI_CONTEXT_URL' },
  { key: 'ai_events', host: 'ai-event-processor', port: 8014, envVar: 'VITE_AI_EVENT_PROCESSOR_URL' },
  { key: 'voice_events', host: 'voice-event-processor', port: 8015, envVar: 'VITE_VOICE_EVENT_PROCESSOR_URL' },
  { key: 'memory', host: 'memory-service', port: 8017, envVar: 'VITE_MEMORY_SERVICE_URL' },
  { key: 'assistance', host: 'proactive-assistance-engine', port: 8018, envVar: 'VITE_ASSISTANCE_ENGINE_URL' },
  { key: 'media', host: 'media-service', port: 8021, envVar: 'VITE_MEDIA_SERVICE_URL' },
];

export function serviceBaseUrl(key: string): string {
  const entry = SERVICE_ENDPOINTS.find(e => e.key === key);
  if (!entry) throw new Error(`Unknown service key '${key}'`);
  const envOverride = (import.meta as any).env[entry.envVar || ''];
  return (envOverride || `http://${entry.host}:${entry.port}`);
}

export function serviceHealthUrl(key: string): string {
  return serviceBaseUrl(key).replace(/\/$/, '') + '/health';
}

export function allServiceBaseUrls(): Record<string, string> {
  const map: Record<string, string> = {};
  SERVICE_ENDPOINTS.forEach(e => { map[e.key] = serviceBaseUrl(e.key); });
  return map;
}
