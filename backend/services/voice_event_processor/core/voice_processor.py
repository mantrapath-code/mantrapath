"""
Voice Event Processor
Handles real-time voice event processing with WebSocket streaming
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import numpy as np

import nats
from nats.js import JetStreamContext
import redis.asyncio as redis
from fastapi import WebSocket
import torch
import torchaudio
import librosa
import soundfile as sf
from transformers import pipeline

from models.voice_events import VoiceEvent, VoiceAnalysisResult
from utils.redis_manager import RedisManager
from utils.nats_client import NATSClient

logger = logging.getLogger(__name__)

class VoiceActivityDetector:
    """Voice Activity Detection using energy-based approach"""
    
    def __init__(self, threshold: float = 0.01, frame_duration: float = 0.02):
        self.threshold = threshold
        self.frame_duration = frame_duration
        self.sample_rate = 16000
        
    def detect_voice_activity(self, audio_data: np.ndarray) -> bool:
        """Detect if there's voice activity in the audio"""
        try:
            # Calculate energy
            energy = np.sum(audio_data ** 2) / len(audio_data)
            return energy > self.threshold
        except Exception as e:
            logger.error(f"Voice activity detection error: {e}")
            return False

class VoiceStreamManager:
    """Manages voice streaming and real-time processing"""
    
    def __init__(self, websocket: WebSocket):
        self.websocket = websocket
        self.is_streaming = False
        self.buffer = []
        self.buffer_size = 1024 * 4  # 4KB buffer
        
    async def start_streaming(self):
        """Start voice streaming"""
        self.is_streaming = True
        logger.info("Voice streaming started")
        
    async def stop_streaming(self):
        """Stop voice streaming"""
        self.is_streaming = False
        self.buffer.clear()
        logger.info("Voice streaming stopped")
        
    async def process_audio_chunk(self, chunk: bytes) -> Optional[np.ndarray]:
        """Process incoming audio chunk"""
        try:
            # Add to buffer
            self.buffer.extend(chunk)
            
            # Process when buffer is full
            if len(self.buffer) >= self.buffer_size:
                audio_data = np.frombuffer(bytes(self.buffer), dtype=np.int16)
                # Convert to float and normalize
                audio_data = audio_data.astype(np.float32) / 32768.0
                
                # Clear buffer
                self.buffer = self.buffer[self.buffer_size:]
                
                return audio_data
                
        except Exception as e:
            logger.error(f"Audio chunk processing error: {e}")
            
        return None

class VoiceEventProcessor:
    """Main Voice Event Processor class"""
    
    def __init__(self):
        self.redis_manager = None
        self.nats_client = None
        self.js = None
        
        # Voice processing components
        self.vad = VoiceActivityDetector()
        self.active_streams: Dict[str, VoiceStreamManager] = {}
        
        # AI Models (will be loaded on startup)
        self.emotion_classifier = None
        self.speech_recognizer = None
        
        # Processing stats
        self.processed_events = 0
        self.active_connections = 0
        
    async def initialize(self):
        """Initialize all connections and models"""
        try:
            # Initialize Redis
            self.redis_manager = RedisManager(host="redis", db=2)  # Voice processing DB
            await self.redis_manager.connect()
            
            # Initialize NATS
            self.nats_client = NATSClient(servers=["nats://mantrapath-nats:4222"])
            await self.nats_client.connect()
            self.js = self.nats_client.jetstream()
            
            # Load AI models
            await self._load_models()
            
            # Setup streams
            await self._setup_streams()
            
            logger.info("Voice Event Processor initialized successfully")
            
        except Exception as e:
            logger.error(f"Initialization error: {e}")
            raise
    
    async def _load_models(self):
        """Load AI models for voice processing"""
        try:
            # Load emotion classification model
            self.emotion_classifier = pipeline(
                "audio-classification",
                model="ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition",
                device="cpu"  # Use GPU if available
            )
            
            # Load speech recognition model
            self.speech_recognizer = pipeline(
                "automatic-speech-recognition",
                model="openai/whisper-base",
                device="cpu"
            )
            
            logger.info("Voice AI models loaded successfully")
            
        except Exception as e:
            logger.error(f"Model loading error: {e}")
            # Continue without models if they fail to load
    
    async def _setup_streams(self):
        """Setup NATS JetStream streams"""
        try:
            # Voice events stream
            await self.js.add_stream(
                name="voice-events",
                subjects=["voice.>"],
                retention="limits",
                max_age=3600  # 1 hour retention
            )
            
            logger.info("NATS streams setup completed")
            
        except Exception as e:
            logger.error(f"Stream setup error: {e}")
    
    async def start_voice_stream(self, session_id: str, websocket: WebSocket) -> VoiceStreamManager:
        """Start a new voice stream for a session"""
        try:
            stream_manager = VoiceStreamManager(websocket)
            self.active_streams[session_id] = stream_manager
            await stream_manager.start_streaming()
            
            self.active_connections += 1
            
            logger.info(f"Voice stream started for session: {session_id}")
            return stream_manager
            
        except Exception as e:
            logger.error(f"Error starting voice stream: {e}")
            raise
    
    async def stop_voice_stream(self, session_id: str):
        """Stop voice stream for a session"""
        try:
            if session_id in self.active_streams:
                await self.active_streams[session_id].stop_streaming()
                del self.active_streams[session_id]
                self.active_connections -= 1
                
                logger.info(f"Voice stream stopped for session: {session_id}")
                
        except Exception as e:
            logger.error(f"Error stopping voice stream: {e}")
    
    async def process_voice_event(self, voice_event: VoiceEvent) -> VoiceAnalysisResult:
        """Process a voice event and return analysis"""
        try:
            start_time = datetime.now(timezone.utc)
            
            # Voice Activity Detection
            has_voice = False
            if voice_event.audio_data:
                audio_array = np.frombuffer(voice_event.audio_data, dtype=np.float32)
                has_voice = self.vad.detect_voice_activity(audio_array)
            
            # Emotion Analysis (if models are loaded and voice detected)
            emotion_scores = {}
            if has_voice and self.emotion_classifier and voice_event.audio_data:
                try:
                    # Convert audio data for emotion analysis
                    emotion_result = self.emotion_classifier(voice_event.audio_data)
                    if emotion_result:
                        emotion_scores = {
                            result['label']: result['score'] 
                            for result in emotion_result
                        }
                except Exception as e:
                    logger.warning(f"Emotion analysis failed: {e}")
            
            # Speech Recognition (if models are loaded and voice detected)
            transcript = ""
            if has_voice and self.speech_recognizer and voice_event.audio_data:
                try:
                    transcript_result = self.speech_recognizer(voice_event.audio_data)
                    transcript = transcript_result.get('text', '') if transcript_result else ""
                except Exception as e:
                    logger.warning(f"Speech recognition failed: {e}")
            
            # Create analysis result
            analysis_result = VoiceAnalysisResult(
                event_id=voice_event.event_id,
                session_id=voice_event.session_id,
                user_id=voice_event.user_id,
                timestamp=voice_event.timestamp,
                voice_detected=has_voice,
                emotion_scores=emotion_scores,
                transcript=transcript,
                audio_quality=voice_event.audio_quality or "unknown",
                processing_time=(datetime.now(timezone.utc) - start_time).total_seconds(),
                metadata=voice_event.metadata or {}
            )
            
            # Store in Redis
            await self._store_analysis_result(analysis_result)
            
            # Publish to NATS
            await self._publish_voice_analysis(analysis_result)
            
            self.processed_events += 1
            
            logger.info(f"Voice event processed: {voice_event.event_id}")
            return analysis_result
            
        except Exception as e:
            logger.error(f"Voice event processing error: {e}")
            raise
    
    async def _store_analysis_result(self, result: VoiceAnalysisResult):
        """Store analysis result in Redis"""
        try:
            key = f"voice_analysis:{result.session_id}:{result.event_id}"
            await self.redis_manager.setex(
                key, 
                3600,  # 1 hour TTL
                result.model_dump_json()
            )
            
            # Also store in session-based list for easy retrieval
            session_key = f"voice_session:{result.session_id}"
            await self.redis_manager.lpush(session_key, result.event_id)
            await self.redis_manager.expire(session_key, 3600)
            
        except Exception as e:
            logger.error(f"Error storing analysis result: {e}")
    
    async def _publish_voice_analysis(self, result: VoiceAnalysisResult):
        """Publish voice analysis to NATS"""
        try:
            subject = f"voice.analysis.{result.session_id}"
            await self.js.publish(
                subject,
                result.model_dump_json().encode(),
                headers={"event_type": "voice_analysis"}
            )
            
        except Exception as e:
            logger.error(f"Error publishing voice analysis: {e}")
    
    async def process_audio_stream(self, session_id: str, audio_chunk: bytes):
        """Process real-time audio stream"""
        try:
            if session_id not in self.active_streams:
                logger.warning(f"No active stream for session: {session_id}")
                return
            
            stream_manager = self.active_streams[session_id]
            audio_data = await stream_manager.process_audio_chunk(audio_chunk)
            
            if audio_data is not None:
                # Create voice event from audio data
                voice_event = VoiceEvent(
                    session_id=session_id,
                    user_id=f"stream_user_{session_id}",
                    audio_data=audio_data.tobytes(),
                    audio_format="pcm_16",
                    sample_rate=16000,
                    timestamp=datetime.now(timezone.utc)
                )
                
                # Process the voice event
                analysis_result = await self.process_voice_event(voice_event)
                
                # Send result back through WebSocket
                await stream_manager.websocket.send_text(
                    analysis_result.model_dump_json()
                )
                
        except Exception as e:
            logger.error(f"Audio stream processing error: {e}")
    
    async def get_session_analysis(self, session_id: str) -> List[VoiceAnalysisResult]:
        """Get all voice analysis results for a session"""
        try:
            session_key = f"voice_session:{session_id}"
            event_ids = await self.redis_manager.lrange(session_key, 0, -1)
            
            results = []
            for event_id in event_ids:
                key = f"voice_analysis:{session_id}:{event_id.decode()}"
                data = await self.redis_manager.get(key)
                if data:
                    result = VoiceAnalysisResult.model_validate_json(data)
                    results.append(result)
            
            return sorted(results, key=lambda x: x.timestamp)
            
        except Exception as e:
            logger.error(f"Error getting session analysis: {e}")
            return []
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get health status of the voice processor"""
        try:
            redis_connected = await self.redis_manager.ping() if self.redis_manager else False
            nats_connected = self.nats_client.is_connected if self.nats_client else False
            
            return {
                "status": "healthy" if redis_connected and nats_connected else "unhealthy",
                "redis_connected": redis_connected,
                "nats_connected": nats_connected,
                "processed_events": self.processed_events,
                "active_connections": self.active_connections,
                "models_loaded": {
                    "emotion_classifier": self.emotion_classifier is not None,
                    "speech_recognizer": self.speech_recognizer is not None
                },
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Health check error: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            # Stop all active streams
            for session_id in list(self.active_streams.keys()):
                await self.stop_voice_stream(session_id)
            
            # Close connections
            if self.redis_manager:
                await self.redis_manager.close()
            
            if self.nats_client:
                await self.nats_client.close()
            
            logger.info("Voice Event Processor cleanup completed")
            
        except Exception as e:
            logger.error(f"Cleanup error: {e}")
