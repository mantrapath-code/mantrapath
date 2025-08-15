# Translation Service Documentation

## Overview

The MantraPath Translation Service provides real-time, culturally-aware translation capabilities specifically designed for meditation and mindfulness content. It uses local translation models for independence from external APIs while providing cultural adaptation for spiritual content.

## Features

- **Local Translation Models**: Self-hosted translation without external API dependencies
- **Cultural Adaptation**: Context-aware translation for meditation terminology
- **Offline Support**: Critical translations cached locally
- **Multi-language Support**: 50+ languages across 3 tiers
- **Quality Assurance**: Translation confidence scoring and validation
- **Meditation Glossaries**: Specialized terminology for spiritual content

## Quick Start

### Using Docker (Recommended)

```bash
# Build and run the service
cd /path/to/translation_service
docker build -t mantrapath-translation .
docker run -p 8010:8010 mantrapath-translation
```

### Using Docker Compose

```bash
# Start all services (translation + dependencies)
docker-compose up -d

# Check service health
curl http://localhost:8010/health
```

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the service
uvicorn main:app --host 0.0.0.0 --port 8010 --reload
```

## API Endpoints

### Health Check
```http
GET /health
```
Returns service health status and available features.

### Single Translation
```http
POST /translate
Content-Type: application/json

{
  "text": "inner peace and mindfulness",
  "target_language": "es",
  "source_language": "en",
  "domain": "meditation"
}
```

### Batch Translation
```http
POST /translate/batch
Content-Type: application/json

{
  "texts": ["peace", "love", "wisdom"],
  "target_language": "hi",
  "source_language": "en",
  "domain": "meditation"
}
```

### Language Detection
```http
POST /detect-language
Content-Type: application/json

{
  "text": "This text is in English"
}
```

### Supported Languages
```http
GET /languages
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SERVICE_PORT` | 8010 | Port for the service |
| `ENVIRONMENT` | development | Service environment |
| `LOCAL_MODEL_ENABLED` | true | Enable local translation models |
| `CULTURAL_ADAPTATION_ENABLED` | true | Enable cultural adaptation |
| `OFFLINE_MODE_ENABLED` | true | Enable offline support |
| `LOG_LEVEL` | INFO | Logging level |

### Language Tiers

**Tier 1 (Premium)**: English, Spanish, French, German, Hindi, Chinese
- Highest accuracy with cultural adaptation
- Specialized meditation terminology
- Advanced confidence scoring

**Tier 2 (Standard)**: Italian, Portuguese, Russian, Japanese, Korean, Arabic
- Good accuracy with basic cultural adaptation
- Standard meditation terms
- Reliable quality scoring

**Tier 3 (Basic)**: 40+ additional languages
- Acceptable accuracy
- Basic terminology support
- Standard confidence scoring

## Testing

### Run All Tests
```bash
# Run core functionality tests
python3 -m pytest tests/test_core_functionality.py -v

# Run with coverage
python3 -m pytest tests/ --cov=. --cov-report=html
```

### Language-Specific Tests

The test suite includes comprehensive testing for:
- English ↔ Spanish translation
- English ↔ Hindi (meditation terms)
- English ↔ Chinese (spiritual content)
- French, German, Arabic translations
- Cultural adaptation validation
- Batch processing
- Language detection accuracy

### Performance Tests
```bash
# Run performance benchmarks
python3 -m pytest tests/test_performance.py -v
```

## Docker Usage

### Build Image
```bash
docker build -t mantrapath-translation:latest .
```

### Run Container
```bash
docker run -d \
  --name translation-service \
  -p 8010:8010 \
  -e ENVIRONMENT=production \
  -e LOG_LEVEL=INFO \
  mantrapath-translation:latest
```

### Check Logs
```bash
docker logs translation-service
```

### Health Check
```bash
curl http://localhost:8010/health
```

## Cultural Adaptation

The service provides culturally-sensitive translations for meditation content:

### Supported Cultural Contexts

- **Western Secular**: Modern mindfulness and secular meditation
- **Buddhist Traditional**: Traditional Buddhist terminology
- **Hindu Vedantic**: Vedantic spiritual terminology  
- **Christian Contemplative**: Christian meditation practices
- **Islamic Sufi**: Islamic contemplative traditions
- **Secular Scientific**: Scientific mindfulness terminology

### Example Adaptations

| Original | Language | Context | Adapted Translation |
|----------|----------|---------|-------------------|
| meditation | Arabic | Islamic | مراقبة (muraqaba) |
| meditation | Arabic | Secular | تأمل (ta'amul) |
| mindfulness | Chinese | Buddhist | 正念 (zhèng niàn) |
| mindfulness | Chinese | Scientific | 专注 (zhuān zhù) |

## Troubleshooting

### Common Issues

**Service Won't Start**
- Check port 8010 is available
- Verify environment variables
- Check Docker daemon is running

**Translation Errors**
- Verify source/target language codes
- Check text length limits (max 5000 chars)
- Ensure proper UTF-8 encoding

**Poor Translation Quality**
- Use domain="meditation" for spiritual content
- Enable cultural adaptation
- Check language tier support

### Debugging

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Check service status
curl http://localhost:8010/health

# View detailed logs
docker logs translation-service --follow
```

## Performance

### Benchmarks

- **Single Translation**: < 100ms average
- **Batch Processing**: 10 translations < 500ms
- **Language Detection**: < 50ms
- **Cultural Adaptation**: < 200ms additional
- **Memory Usage**: < 512MB baseline

### Optimization

- Use batch endpoints for multiple translations
- Enable caching for repeated content
- Use appropriate language tiers
- Configure cultural adaptation only when needed

## Security

- No external API keys required for basic functionality
- Local processing ensures data privacy
- Configurable rate limiting
- Input validation and sanitization
- No persistent storage of translation data

## Integration

### MantraPath Platform

The service integrates with the MantraPath platform through:
- Shared authentication system
- Event-driven architecture
- Service discovery
- Centralized logging and monitoring

### API Clients

Example client usage:
```python
import httpx

async def translate_text(text, target_lang):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8010/translate",
            json={
                "text": text,
                "target_language": target_lang,
                "domain": "meditation"
            }
        )
        return response.json()
```

## Support

For issues and questions:
- Check the troubleshooting section
- Review test cases for usage examples
- Check service logs for detailed error messages
- Verify Docker container health status
