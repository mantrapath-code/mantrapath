# MantraPath Voice Service Documentation

## Overview

The MantraPath Voice Service is an enterprise-grade, multilingual voice processing microservice that provides Speech-to-Text (STT), Text-to-Speech (TTS), voice cloning, emotion analysis, and voice command processing capabilities. Built with FastAPI and designed for scalability, security, and real-time performance.

## 📁 Documentation Structure

- [`01-ARCHITECTURE.md`](01-ARCHITECTURE.md) - Service architecture and design patterns
- [`02-API_REFERENCE.md`](02-API_REFERENCE.md) - Complete API endpoint documentation  
- [`03-LANGUAGE_SUPPORT.md`](03-LANGUAGE_SUPPORT.md) - Multilingual capabilities and configuration
- [`04-VOICE_CONTROL.md`](04-VOICE_CONTROL.md) - Voice control features and user interaction
- [`05-INTEGRATION.md`](05-INTEGRATION.md) - Service integration and communication
- [`06-DEPLOYMENT.md`](06-DEPLOYMENT.md) - Deployment and configuration guide
- [`07-TESTING.md`](07-TESTING.md) - Testing strategies and procedures
- [`08-SECURITY.md`](08-SECURITY.md) - Security implementation and best practices
- [`09-PERFORMANCE.md`](09-PERFORMANCE.md) - Performance optimization and monitoring
- [`10-TROUBLESHOOTING.md`](10-TROUBLESHOOTING.md) - Common issues and solutions

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- API keys for voice engines (ElevenLabs, Google, Azure)
- MantraPath API Gateway running

### Local Development
```bash
# Navigate to voice service
cd backend/services/voice_service

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your configuration

# Run service
python main.py
```

### Docker Deployment
```bash
# From backend directory
docker-compose up voice_service
```

## 🎯 Core Capabilities

| Feature | Description | Status |
|---------|-------------|--------|
| **Speech-to-Text** | Multi-engine STT with Whisper, Google, Azure | ✅ Production |
| **Text-to-Speech** | High-quality TTS with ElevenLabs, Azure, Google | ✅ Production |
| **Voice Cloning** | Custom voice profile creation and training | ✅ Production |
| **Emotion Analysis** | Real-time emotion detection from voice | ✅ Production |
| **Voice Commands** | Natural language command processing | ✅ Production |
| **Multilingual** | 16 languages with tiered support | ✅ Production |
| **Real-time Processing** | WebSocket-based streaming | ✅ Production |
| **Voice Profiles** | User-specific voice customization | ✅ Production |

## 🌐 Language Support

### Tier 1 (Premium Support)
- **English, Hindi, Spanish, French** - Full neural models with cultural adaptation
- **Arabic, Chinese, Japanese** - Advanced emotion detection
- **Sanskrit, Thai, Myanmar** - Meditation-optimized processing

### Tier 2 (Standard Support)  
- **German, Italian, Portuguese** - High-quality voice synthesis
- **Russian, Korean, Dutch** - Standard emotion detection

## 🔗 Quick Links

- [API Gateway Integration](05-INTEGRATION.md#api-gateway)
- [Voice Control Commands](04-VOICE_CONTROL.md#commands)
- [Testing Voice Features](07-TESTING.md#voice-testing)
- [Security Configuration](08-SECURITY.md#authentication)

## 📞 Support

For technical support or questions:
- Check [Troubleshooting Guide](10-TROUBLESHOOTING.md)
- Review [Performance Monitoring](09-PERFORMANCE.md)
- Contact: MantraPath Development Team

---

**Version:** 1.0.0  
**Last Updated:** December 2024  
**Maintainer:** MantraPath Voice Team
