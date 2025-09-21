# MantraPath Container Images

All images are stored in the Vultr Container Registry: **blr.vultrcr.com/mantrapath**

## Core Services

| Service | Image Name | Registry URL |
|---------|------------|--------------|
| API Gateway | mantrapath-api-gateway | blr.vultrcr.com/mantrapath/mantrapath-api-gateway |
| Frontend | mantrapath-frontend | blr.vultrcr.com/mantrapath/mantrapath-frontend |
| Translation Service | mantrapath-translation-service | blr.vultrcr.com/mantrapath/mantrapath-translation-service |
| Models Service | mantrapath-models-service | blr.vultrcr.com/mantrapath/mantrapath-models-service |
| Auth Service | mantrapath-auth-service | blr.vultrcr.com/mantrapath/mantrapath-auth-service |

## Additional Services

| Service | Image Name | Registry URL |
|---------|------------|--------------|
| Chatbot Service | mantrapath-chatbot-service | blr.vultrcr.com/mantrapath/mantrapath-chatbot-service |
| Voice Service | mantrapath-voice-service | blr.vultrcr.com/mantrapath/mantrapath-voice-service |
| ML Service | mantrapath-ml-service | blr.vultrcr.com/mantrapath/mantrapath-ml-service |
| Mood Service | mantrapath-mood-service | blr.vultrcr.com/mantrapath/mantrapath-mood-service |
| Profile Service | mantrapath-profile-service | blr.vultrcr.com/mantrapath/mantrapath-profile-service |
| Content Service | mantrapath-content-service | blr.vultrcr.com/mantrapath/mantrapath-content-service |
| Community Service | mantrapath-community-service | blr.vultrcr.com/mantrapath/mantrapath-community-service |
| Notification Service | mantrapath-notification-service | blr.vultrcr.com/mantrapath/mantrapath-notification-service |
| Memory Service | mantrapath-memory-service | blr.vultrcr.com/mantrapath/mantrapath-memory-service |
| Media Service | mantrapath-media-service | blr.vultrcr.com/mantrapath/mantrapath-media-service |
| AI Context Store | mantrapath-ai-context-store | blr.vultrcr.com/mantrapath/mantrapath-ai-context-store |
| AI Event Processor | mantrapath-ai-event-processor | blr.vultrcr.com/mantrapath/mantrapath-ai-event-processor |
| Action Orchestrator | mantrapath-action-orchestrator | blr.vultrcr.com/mantrapath/mantrapath-action-orchestrator |
| Voice Event Processor | mantrapath-voice-event-processor | blr.vultrcr.com/mantrapath/mantrapath-voice-event-processor |
| Proactive Assistance | mantrapath-proactive-assistance | blr.vultrcr.com/mantrapath/mantrapath-proactive-assistance |

## Image Tags

Each image is tagged with:
- `latest` - Latest version from main branch
- `prod` - Production release (from main branch)
- `dev` - Development version (from develop branch)
- `<commit-sha>` - Specific commit version

## Registry Access

- **Registry URL:** https://blr.vultrcr.com/mantrapath
- **Username:** e9b950f6-81b8-4433-bb62-844d3f44b6bb
- **Authentication:** Required for pull/push operations

## Kubernetes Configuration

Both prod and dev environments are configured to pull from this registry:

```yaml
global:
  registry: "blr.vultrcr.com/mantrapath"
  imagePullSecrets: ["vultr-cr-credentials"]
```

## CI/CD Integration

All images are automatically built and pushed by GitHub Actions:
- Push to `main` → Build and tag as `latest`, `prod`
- Push to `develop` → Build and tag as `latest`, `dev`
- All commits → Tag with commit SHA
