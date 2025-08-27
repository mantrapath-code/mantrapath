# MantraPath Translation Service

A high-performance, scalable translation service with cultural adaptation and meditation-specific terminology support.

## 🚀 Features

### Core Translation Capabilities
- **Real-time Translation**: Instant text translation across 50+ languages
- **Language Detection**: Automatic source language identification with 95%+ accuracy
- **Cultural Adaptation**: Context-aware meditation terminology and cultural nuances
- **Voice Translation**: Audio translation for guided meditations (coming soon)
- **Offline Support**: Critical translations cached locally for offline access
- **Quality Assurance**: Translation confidence scoring and quality metrics
- **Custom Glossaries**: Meditation-specific term libraries with cultural context

### Performance & Scalability
- **Sub-300ms Response Times**: Optimized for real-time applications
- **Intelligent Caching**: Multi-tier caching with Redis for instant responses
- **Batch Processing**: Efficient handling of multiple translation requests
- **Rate Limiting**: Configurable rate limits to prevent abuse
- **Auto-scaling**: Horizontal scaling support with containerization

### Quality & Reliability
- **Multi-Engine Support**: Google Translate, Microsoft Translator, OpenAI GPT
- **Fallback Mechanisms**: Automatic failover between translation engines
- **Quality Scoring**: AI-powered translation quality assessment
- **Error Handling**: Comprehensive error handling and retry logic
- **Monitoring**: Prometheus metrics and health checks

## 🏗️ Architecture

### Service Structure
```
translation_service/
├── main.py                    # FastAPI application
├── config/
│   └── settings.py           # Configuration management
├── models/
│   ├── translation_models.py # Database models
│   └── request_models.py     # API request/response models
├── engines/
│   ├── base_translator.py    # Abstract translator interface
│   ├── google_translator.py  # Google Translate integration
│   ├── microsoft_translator.py # Microsoft Translator
│   └── openai_translator.py  # OpenAI GPT integration
├── services/
│   └── translation_engine.py # Core orchestration logic
├── tests/
│   ├── test_translation_engine.py
│   ├── test_api_integration.py
│   └── test_language_detection.py
└── data/
    ├── glossaries/           # Custom terminology
    ├── models/              # Local translation models
    └── cache/               # Offline cache
```

### Language Support Tiers

#### Tier 1 - Premium Support (Native Models + Cultural Adaptation)
- **English** (en), **Hindi** (hi), **Spanish** (es), **French** (fr)
- **Arabic** (ar), **Chinese** (zh), **Japanese** (ja), **Sanskrit** (sa)
- **Thai** (th), **Myanmar** (my)

#### Tier 2 - Standard Support
- **German** (de), **Italian** (it), **Portuguese** (pt), **Russian** (ru)
- **Korean** (ko), **Bengali** (bn), **Tamil** (ta), **Telugu** (te)
- **Urdu** (ur), **Persian** (fa), **Hebrew** (he), **Turkish** (tr)
- **Vietnamese** (vi), **Indonesian** (id), **Malay** (ms)

#### Tier 3 - Basic Support (50+ languages total)
- European: Polish, Dutch, Swedish, Danish, Norwegian, Finnish, etc.
- Indian: Kannada, Malayalam, Gujarati, Punjabi, Marathi, etc.
- Others: Filipino, Swahili, Amharic, etc.

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.11+
- Redis Server
- PostgreSQL/SQLite (for production/development)

### Local Development

1. **Clone and Setup**
   ```bash
   cd backend/services/translation_service
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

3. **Start Services**
   ```bash
   # Start Redis (if not running)
   redis-server
   
   # Run the translation service
   python main.py
   ```

### Docker Deployment

```bash
# Build the image
docker build -t mantrapath-translation:latest .

# Run with environment variables
docker run -d \
  --name translation-service \
  -p 8005:8005 \
  -e GOOGLE_TRANSLATE_API_KEY=your-key \
  -e REDIS_URL=redis://host.docker.internal:6379/2 \
  mantrapath-translation:latest
```

### Production Deployment

```yaml
# docker-compose.yml
services:
  translation-service:
    image: mantrapath-translation:latest
    ports:
      - "8005:8005"
    environment:
      - GOOGLE_TRANSLATE_API_KEY=${GOOGLE_TRANSLATE_API_KEY}
      - MICROSOFT_TRANSLATOR_KEY=${MICROSOFT_TRANSLATOR_KEY}
      - REDIS_URL=redis://redis:6379/2
      - DATABASE_URL=postgresql://user:pass@postgres:5432/mantrapath
    depends_on:
      - redis
      - postgres
    deploy:
      replicas: 3
      resources:
        limits:
          memory: 1G
          cpus: "0.5"
```

## 📚 API Documentation

### Core Endpoints

#### Translate Text
```http
POST /translate
Content-Type: application/json
Authorization: Bearer <jwt-token>

{
  "text": "Hello world",
  "source_language": "en",
  "target_language": "es",
  "engine": "auto",
  "domain": "meditation",
  "cultural_adaptation": true,
  "use_custom_glossary": true
}
```

**Response:**
```json
{
  "translated_text": "Hola mundo",
  "source_language": "en",
  "target_language": "es",
  "confidence_score": 0.95,
  "quality_score": 0.92,
  "engine_used": "google",
  "processing_time_ms": 150,
  "cache_hit": false,
  "cultural_adaptations_applied": ["formal_tone"],
  "custom_terms_used": [],
  "request_id": "req_123",
  "status": "completed"
}
```

#### Batch Translation
```http
POST /translate/batch
Content-Type: application/json

{
  "texts": ["Hello", "World", "Peace"],
  "source_language": "en",
  "target_language": "hi",
  "domain": "mindfulness"
}
```

#### Language Detection
```http
POST /detect-language
Content-Type: application/json

{
  "text": "Hola, ¿cómo estás?",
  "engines": ["google", "fasttext"],
  "include_alternatives": true
}
```

#### Supported Languages
```http
GET /languages
```

### Advanced Features

#### Custom Glossary
```http
POST /glossary
Content-Type: application/json

{
  "source_term": "mindfulness",
  "source_language": "en",
  "target_term": "सावधानी",
  "target_language": "hi",
  "domain": "meditation",
  "definition": "Present moment awareness",
  "cultural_context": "Buddhist meditation practice"
}
```

#### Translation Feedback
```http
POST /feedback
Content-Type: application/json

{
  "translation_request_id": "req_123",
  "rating": 4,
  "accuracy_rating": 5,
  "cultural_appropriateness": 4,
  "suggested_translation": "Better translation",
  "comments": "Good but could be more natural"
}
```

## 🧪 Testing

### Run Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Run specific test categories
pytest tests/test_translation_engine.py -v
pytest tests/test_api_integration.py -v
pytest tests/test_language_detection.py -v
```

### Test Coverage Goals
- **Core Translation Engine**: 70%+ coverage
- **API Endpoints**: 60%+ coverage  
- **Language Detection**: 50%+ coverage
- **Error Handling**: 80%+ coverage
- **Overall Service**: 60%+ coverage

### Performance Benchmarks
```bash
# Run performance tests
pytest tests/test_benchmarks.py -v

# Expected Performance:
# - Single translation: <300ms (95th percentile)
# - Batch translation: <100ms per item
# - Language detection: <50ms
# - Cache hit response: <10ms
```

## 📊 Monitoring & Metrics

### Health Check
```http
GET /health
```

### Prometheus Metrics
```http
GET /metrics
```

**Key Metrics:**
- `translation_requests_total` - Total translation requests
- `translation_duration_seconds` - Translation processing time
- `translation_cache_hits_total` - Cache hit rate
- `translation_quality_score` - Average quality scores
- `translation_errors_total` - Error rates by type

### Performance Monitoring
- **Response Time**: Sub-300ms target for 95th percentile
- **Throughput**: 1000+ requests/minute per instance
- **Cache Hit Rate**: 70%+ for repeated content
- **Error Rate**: <1% for all requests
- **Availability**: 99.9% uptime SLA

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `TRANSLATION_PORT` | Service port | 8005 |
| `GOOGLE_TRANSLATE_API_KEY` | Google API key | Required |
| `MICROSOFT_TRANSLATOR_KEY` | Microsoft API key | Optional |
| `REDIS_URL` | Redis connection URL | redis://localhost:6379/2 |
| `TRANSLATION_MAX_TEXT_LENGTH` | Max text length | 5000 |
| `TRANSLATION_RATE_LIMIT_PER_MINUTE` | Rate limit | 1000 |

### Quality Thresholds

| Tier | Quality Threshold | Cache Duration | Features |
|------|-------------------|----------------|----------|
| 1 | 95% | 7 days | All features |
| 2 | 90% | 3 days | Standard + Cultural |
| 3 | 85% | 1 day | Basic translation |

## 🚀 Performance Optimization

### Caching Strategy
1. **Memory Cache**: In-process LRU cache for hot translations
2. **Redis Cache**: Distributed cache for translated content
3. **Offline Cache**: Local storage for critical translations
4. **CDN Cache**: Edge caching for static content

### Scaling Considerations
- **Horizontal Scaling**: Stateless service design for easy scaling
- **Load Balancing**: Round-robin with health checks
- **Database Optimization**: Read replicas and connection pooling
- **Cache Optimization**: Partitioned Redis with consistent hashing

## 🔒 Security

### Authentication & Authorization
- JWT-based authentication for all endpoints
- User-level rate limiting and quotas
- API key rotation support
- Request signing for high-security deployments

### Data Protection
- TLS encryption for all communications
- PII data anonymization in logs
- Secure API key storage
- GDPR compliance for user data

## 🐛 Troubleshooting

### Common Issues

**Translation Timeouts**
```bash
# Check engine health
curl http://localhost:8005/health

# Verify API keys
grep GOOGLE_TRANSLATE_API_KEY .env
```

**Cache Issues**
```bash
# Check Redis connectivity
redis-cli ping

# Clear cache if needed
redis-cli FLUSHDB
```

**Quality Issues**
```bash
# Check engine configuration
curl http://localhost:8005/languages

# Review quality metrics
curl http://localhost:8005/metrics | grep quality
```

### Logging & Debugging
- Set `TRANSLATION_DETAILED_LOGGING=true` for verbose logs
- Use `/health` endpoint to check service status
- Monitor `/metrics` for performance insights

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create feature branch: `git checkout -b feature/translation-enhancement`
3. Add tests for new functionality
4. Ensure all tests pass: `pytest tests/ -v`
5. Submit pull request with detailed description

### Code Quality
- Follow PEP 8 style guidelines
- Add type hints for all functions
- Write comprehensive docstrings
- Maintain test coverage above 60%

## 📄 License

This project is part of MantraPath and follows the project's licensing terms.

## 🆘 Support

For issues and questions:
- Create GitHub issues for bugs and feature requests
- Check existing documentation and troubleshooting guides
- Review performance metrics and health checks

---

**Note**: This translation service is optimized for meditation and mindfulness content with special attention to cultural sensitivity and spiritual terminology accuracy.
