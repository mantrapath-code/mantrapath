/**
 * Voice Service Configuration Update Guide
 * This file documents the changes made to fix voice service integration
 */

// CHANGES MADE TO FRONTEND:

// 1. Updated voiceService.ts to use API Gateway endpoints:
//    - Changed base URL to use API Gateway (port 8000) instead of direct voice service (port 8011)
//    - Fixed endpoint paths:
//      * /api/v1/voice/speech-to-text -> /api/v1/voice/stt
//      * /api/v1/voice/text-to-speech (kept for compatibility)
//      * /api/v1/session/start (updated response handling)
//      * /api/v1/voice/status (for health checks)

// 2. Fixed session handling:
//    - Updated session response parsing to handle backend format
//    - Removed unsupported session end endpoint

// 3. Updated health checks:
//    - Use /api/v1/voice/status for comprehensive status
//    - Fallback to basic /health endpoint

// BACKEND CHANGES ALREADY APPLIED:
// 1. Added routing rules in API Gateway for:
//    - /api/v1/voice/* -> voice service
//    - /api/v1/session/* -> voice service
// 2. Added alias endpoints in voice service:
//    - /api/v1/session/start
//    - /api/v1/voice/text-to-speech
// 3. Fixed response handling in API Gateway proxy
// 4. Added streaming support for audio files

// AUTHENTICATION:
// - Voice endpoints are now public (no auth required)
// - Chatbot endpoints still require JWT tokens
// - Use window.setMoodToken() in dev console to set test token

export const VOICE_SERVICE_ENDPOINTS = {
  // Through API Gateway (recommended)
  HEALTH: '/api/v1/voice/status',
  TTS: '/api/v1/voice/tts',
  TTS_LEGACY: '/api/v1/voice/text-to-speech', // For compatibility
  STT: '/api/v1/voice/stt',
  SESSION_START: '/api/v1/session/start',
  SUPPORTED_LANGUAGES_TTS: '/api/v1/voice/languages/tts',
  SUPPORTED_LANGUAGES_STT: '/api/v1/voice/languages/stt',
  
  // Chatbot (requires auth)
  CHATBOT_SESSION: '/api/chatbot/chat/session',
  CHATBOT_CHAT: '/api/chatbot/chat',
}

export const TESTING_GUIDE = `
# Voice Service Testing Guide

## 1. Basic Health Check
curl http://localhost:8000/api/v1/voice/status

## 2. Session Creation
curl -X POST http://localhost:8000/api/v1/session/start \\
  -H "Content-Type: application/json" \\
  -d '{"user_id": "test", "language": "en"}'

## 3. Text-to-Speech
curl -X POST http://localhost:8000/api/v1/voice/tts \\
  -H "Content-Type: application/json" \\
  -d '{"text": "Hello world", "language": "en"}' \\
  --output test.wav

## 4. Legacy TTS Endpoint
curl -X POST http://localhost:8000/api/v1/voice/text-to-speech \\
  -H "Content-Type: application/json" \\
  -d '{"text": "Hello world", "language": "en"}' \\
  --output test.wav

## 5. Chatbot (requires auth token)
# First set token in browser console: window.setMoodToken()
# Then test in frontend or with curl:
curl -X POST http://localhost:8000/api/chatbot/chat/session \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer YOUR_TOKEN" \\
  -d '{}'
`