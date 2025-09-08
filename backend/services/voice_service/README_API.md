# Voice Service - API Documentation

## 🎯 Overview

The Voice Service is a FastAPI-based service that provides speech processing capabilities by integrating with the Models Service. It supports Speech-to-Text (STT), Text-to-Speech (TTS), and conversation flows with sentiment analysis.

## ✅ Successfully Implemented Features

### 1. **Models Service Integration**
- ✅ Real-time communication with Models Service
- ✅ Health monitoring and status checks
- ✅ Dynamic language support discovery

### 2. **Speech-to-Text (STT)**  
- ✅ Multiple model support (Whisper, Vosk, Wav2Vec2)
- ✅ 17+ language support including Indian languages
- ✅ Auto language detection
- ✅ Model preference selection

### 3. **Text-to-Speech (TTS)**
- ✅ Multiple TTS engines (Coqui, Festival, eSpeak)
- ✅ 20+ language support
- ✅ Voice selection capabilities
- ✅ Audio streaming response

### 4. **Conversation Flow**
- ✅ Context-aware conversation processing
- ✅ Sentiment analysis integration
- ✅ Multi-turn conversation support
- ✅ User context management

### 5. **Indian Language Support**
- ✅ Hindi (hi) - Full STT/TTS support
- ✅ Bengali (bn) - STT/TTS support
- ✅ Telugu (te), Tamil (ta), Marathi (mr)
- ✅ Gujarati (gu), Kannada (kn), Malayalam (ml)
- ✅ Punjabi (pa), Odia (or), Assamese (as)

## 🚀 API Endpoints

### Health & Status
- `GET /health` - Service health check
- `GET /api/v1/models/status` - Models Service integration status
- `GET /api/v1/voice/status` - Comprehensive service status

### Voice Processing
- `POST /api/v1/voice/stt` - Speech to Text conversion
- `POST /api/v1/voice/tts` - Text to Speech synthesis
- `POST /api/v1/voice/conversation` - Full conversation flow

### Language Support
- `GET /api/v1/voice/languages/stt` - Available STT languages
- `GET /api/v1/voice/languages/tts` - Available TTS languages

## 📋 Coming Soon (Phase 2)

- WebSocket support for real-time streaming
- Voice cloning capabilities
- Rasa dialogue management integration
- Advanced voice enhancement
- Performance optimization

## 🏗️ Architecture

```
Voice Service (Port 8011) 
    ↓ HTTP/JSON
Models Service (Port 8085)
    ↓ AI Processing
STT/TTS/NLP Models
```

## ✅ Integration Success

The Voice Service successfully integrates with the existing Models Service, providing a clean abstraction layer for voice-related operations while leveraging the powerful AI capabilities already available in the MantraPath ecosystem.

## 🎯 Success Metrics

- ✅ **Models Service Integration**: Active connection verified
- ✅ **Multi-language Support**: 17 STT + 20 TTS languages
- ✅ **API Endpoints**: All primary endpoints functional
- ✅ **Sentiment Analysis**: Real-time emotion detection
- ✅ **Docker Integration**: Container ready for deployment
- ✅ **Error Handling**: Graceful failure management
