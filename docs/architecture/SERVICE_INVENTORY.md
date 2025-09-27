# MantraPath Service Inventory

## Infrastructure Services
- **PostgreSQL**: Port 5432 (Database)
- **Redis**: Port 6379 (Cache/Session Store)
- **Agent Redis**: Port 6380 (Agent-specific cache)
- **NATS**: Ports 4222 (Client), 8222 (HTTP Monitor), 6222 (Cluster)

## Application Services

### Core Services
1. **API Gateway**: Port 8000 (Main entry point)
   - WebSocket: Port 8080
   - Metrics: Port 9090
   - Docker service: `api-gateway`

2. **Auth Service**: Port 8001
   - Docker service: `auth-service`
   - Environment var: `AUTH_SERVICE_PORT`

### User & Content Services
3. **Profile Service**: Port 8002
   - Docker service: `profile-service`
   - Environment var: `PROFILE_SERVICE_PORT`

4. **Mood Service**: Port 8003
   - Docker service: `mood-service`
   - Environment var: `MOOD_SERVICE_PORT`

5. **Chatbot Service**: Port 8004
   - Docker service: `chatbot-service`
   - Environment var: `CHATBOT_SERVICE_PORT`

6. **Content Service**: Port 8005 (Translation Service)
   - Docker service: `content-service`
   - Environment var: `CONTENT_SERVICE_PORT`

7. **Community Service**: Port 8006
   - Docker service: `community-service`
   - Environment var: `COMMUNITY_SERVICE_PORT`

8. **Notification Service**: Port 8007
   - Docker service: `notification-service`
   - Environment var: `NOTIFICATION_SERVICE_PORT`

### AI & ML Services
9. **ML Service**: Port 8008
   - Docker service: `ml-service`
   - Environment var: `ML_SERVICE_PORT`

10. **Media Service**: Port 8009
    - Docker service: `media-service`
   - Environment var: `MEDIA_SERVICE_PORT` (default 8021)

11. **Translation Service**: Port 8010
    - Docker service: `translation-service`
    - Environment var: `TRANSLATION_SERVICE_PORT`

12. **Voice Service**: Port 8011
    - Docker service: `voice-service`
    - Environment var: `VOICE_SERVICE_PORT`

13. **Action Orchestrator**: Port 8012
    - Docker service: `action-orchestrator`
    - Environment var: `ORCHESTRATOR_PORT`

14. **AI Context Store**: Port 8013
    - Docker service: `ai-context-store`
    - Environment var: `AI_CONTEXT_STORE_PORT`

15. **AI Event Processor**: Port 8014
    - Docker service: `ai-event-processor`
    - Environment var: `AI_EVENT_PROCESSOR_PORT`

16. **Voice Event Processor**: Port 8015
    - Docker service: `voice-event-processor`
    - Environment var: `VOICE_EVENT_PROCESSOR_PORT`

### Additional Services Found in Services Directory
17. **Models Service**: Port 8080 (default from code)
    - Environment var: `MODELS_SERVICE_PORT`
    - Note: Not in main docker-compose.yml

18. **Recommendation Engine**: Found in services directory
19. **Gamification Service**: Found in services directory
20. **Analytics Service**: Found in services directory
21. **Achievement Service**: Found in services directory

## Service Categories

### Essential Core (Required for basic operation)
- postgres, redis, nats, api-gateway, auth-service

### User Experience
- profile-service, mood-service, chatbot-service, content-service, community-service, notification-service

### AI/ML Pipeline
- ml-service, ai-context-store, ai-event-processor, action-orchestrator

### Voice & Translation
- voice-service, voice-event-processor, translation-service

### Media & Analytics
- media-service, models-service, recommendation-engine, analytics-service

### Gamification & Engagement
- gamification-service, achievement-service
