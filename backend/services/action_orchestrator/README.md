# Action Orchestrator Service

## Overview
The Action Orchestrator Service is the central coordination hub for MantraPath's voice-driven cross-service workflows. It processes voice intents, adapts to cultural contexts, and orchestrates complex multi-service actions.

## Features
- Voice intent classification and processing
- Cultural context adaptation
- Cross-service workflow coordination
- Automatic rollback on failures
- Circuit breaker pattern for resilience
- Event-driven architecture with NATS

## Architecture

### Core Components
- **ActionOrchestrator**: Main orchestration engine
- **IntentClassifier**: Voice intent analysis
- **CulturalProcessor**: Cultural context adaptation
- **WorkflowBuilder**: Multi-service workflow construction
- **ActionDispatcher**: Service action execution with resilience
- **RollbackManager**: Failure recovery and cleanup

### Data Models
- **VoiceIntent**: Voice input representation
- **ActionWorkflow**: Complete workflow definition
- **WorkflowStep**: Individual workflow steps
- **ServiceAction**: Service-specific actions
- **ActionResult**: Execution results
- **CulturalContext**: Cultural adaptation data

## API Endpoints

### POST /orchestrate
Orchestrate a voice-driven action workflow.

**Request Body:**
```json
{
  "voice_input": "I want to journal about my meditation today",
  "user_id": "user123",
  "language": "en",
  "cultural_context": {
    "country": "US",
    "timezone": "America/New_York"
  }
}
```

**Response:**
```json
{
  "workflow_id": "wf_123456",
  "status": "completed",
  "results": [...],
  "execution_time": 2.5
}
```

### GET /workflow/{workflow_id}
Get workflow execution status and results.

### POST /workflow/{workflow_id}/rollback
Rollback a completed workflow.

### GET /intents
Get supported voice intents.

### GET /health
Health check endpoint.

## Configuration

### Environment Variables
See `.env.example` for all configuration options.

### Key Settings
- `PORT`: Service port (default: 8012)
- `MAX_WORKFLOW_STEPS`: Maximum workflow complexity
- `CIRCUIT_BREAKER_THRESHOLD`: Failure threshold for circuit breaker
- `SUPPORTED_LANGUAGES`: Comma-separated language codes

## Development

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your configuration

# Run the service
python main.py
```

### Testing
```bash
# Run tests with coverage
python -m pytest tests/ -v --cov=src --cov-report=term-missing

# Run specific test categories
python -m pytest tests/unit/ -v
python -m pytest tests/integration/ -v
```

## Service Integration

### Mood Service
- Create mood entries from voice input
- Update mood tracking data

### Journal Service  
- Create journal entries
- Tag and categorize content

### Chatbot Service
- Process conversational intents
- Generate contextual responses

### Profile Service
- Update user preferences
- Manage cultural settings

### Community Service
- Share content with community
- Manage social interactions

### Analytics Service
- Track user engagement
- Generate insights

## Error Handling

### Circuit Breaker
Automatically opens circuit when service failure rate exceeds threshold.

### Rollback Management
Automatically reverses completed actions when workflow fails.

### Retry Logic
Configurable retry attempts with exponential backoff.

## Monitoring

### Health Checks
- `/health` endpoint for service status
- Individual component health validation

### Logging
Structured logging with request correlation IDs.

### Metrics
Integration with monitoring systems for performance tracking.

## Security

### Authentication
JWT-based authentication for all endpoints.

### Input Validation
Comprehensive input validation using Pydantic models.

### Rate Limiting
Configurable rate limiting to prevent abuse.

## Cultural Adaptation

### Language Support
Multi-language support for voice intent processing.

### Context Processing
Cultural context adaptation for workflows and responses.

### Localization
Region-specific behavior adaptation.
