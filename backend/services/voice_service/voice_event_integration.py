"""
Voice Service Integration with Enhanced Event Bus
Demonstrates how to integrate voice processing with the V3 event system.
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

# Enhanced event system imports
try:
    from shared.events.enhanced_bus import (
        get_enhanced_event_bus,
        publish_voice_activity_event,
        V3EventChannels
    )
    from shared.events.voice_events import (
        VoiceEventType,
        VoiceIntentType,
        DeviceInfo,
        create_voice_activity_event,
        create_voice_intent_event
    )
    ENHANCED_EVENTS_AVAILABLE = True
except ImportError as e:
    ENHANCED_EVENTS_AVAILABLE = False
    logging.warning(f"Enhanced events not available: {e}")

logger = logging.getLogger(__name__)


class VoiceEventProcessor:
    """Voice event processor with enhanced event bus integration"""
    
    def __init__(self):
        self.bus = None
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.processing_stats = {
            "events_processed": 0,
            "voice_activities": 0,
            "intents_classified": 0,
            "errors": 0
        }
        
    async def initialize(self) -> bool:
        """Initialize the voice event processor"""
        if not ENHANCED_EVENTS_AVAILABLE:
            logger.error("Enhanced events not available - voice processing disabled")
            return False
        
        try:
            # Get enhanced event bus
            self.bus = get_enhanced_event_bus()
            await self.bus.initialize()
            
            # Subscribe to voice events
            await self._setup_subscriptions()
            
            logger.info("✅ Voice event processor initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize voice processor: {e}")
            return False
    
    async def _setup_subscriptions(self):
        """Set up event subscriptions"""
        # Subscribe to voice activity events
        await self.bus.subscribe(
            channel="voice.activity_detected",
            handler=self._handle_voice_activity
        )
        
        # Subscribe to speech events
        await self.bus.subscribe(
            channel="voice.speech_start",
            handler=self._handle_speech_start
        )
        
        await self.bus.subscribe(
            channel="voice.speech_end", 
            handler=self._handle_speech_end
        )
        
        # Subscribe to intent events
        await self.bus.subscribe(
            channel="voice.intent_classified",
            handler=self._handle_intent_classified
        )
        
        logger.info("🔔 Voice event subscriptions set up")
    
    async def process_audio_input(
        self,
        audio_data: bytes,
        user_id: str,
        device_id: str,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process audio input and generate voice events"""
        try:
            if session_id is None:
                session_id = str(uuid.uuid4())
            
            # Create device info
            device_info = DeviceInfo(
                device_id=device_id,
                device_type="microphone",
                app_version="1.0.0"
            )
            
            # Simulate voice activity detection
            voice_activity = await self._detect_voice_activity(audio_data)
            
            # Publish voice activity event
            if voice_activity["activity_detected"]:
                await self._publish_voice_activity_event(
                    user_id=user_id,
                    session_id=session_id,
                    device_info=device_info,
                    activity_data=voice_activity
                )
            
            # If speech detected, process intent
            if voice_activity.get("speech_detected"):
                intent_result = await self._process_speech_intent(
                    audio_data=audio_data,
                    user_id=user_id,
                    session_id=session_id,
                    device_info=device_info
                )
                return intent_result
            
            return {"status": "processed", "activity": voice_activity}
            
        except Exception as e:
            logger.error(f"❌ Error processing audio input: {e}")
            self.processing_stats["errors"] += 1
            return {"status": "error", "message": str(e)}
    
    async def _detect_voice_activity(self, audio_data: bytes) -> Dict[str, Any]:
        """Simulate voice activity detection"""
        # In real implementation, this would use actual VAD algorithms
        import random
        
        activity_detected = len(audio_data) > 1000  # Simple threshold
        volume_level = random.uniform(0.3, 0.9)
        pitch_frequency = random.uniform(80, 300)
        
        return {
            "activity_detected": activity_detected,
            "speech_detected": activity_detected and volume_level > 0.5,
            "volume_level": volume_level,
            "pitch_frequency": pitch_frequency,
            "duration_ms": len(audio_data) // 16,  # Assuming 16kHz sample rate
            "quality_score": random.uniform(0.7, 0.95)
        }
    
    async def _publish_voice_activity_event(
        self,
        user_id: str,
        session_id: str,
        device_info: DeviceInfo,
        activity_data: Dict[str, Any]
    ):
        """Publish voice activity event"""
        try:
            # Create voice activity event
            event = create_voice_activity_event(
                event_type=VoiceEventType.ACTIVITY_DETECTED,
                audio_duration_ms=activity_data["duration_ms"],
                volume_level=activity_data["volume_level"],
                pitch_frequency=activity_data["pitch_frequency"],
                device_info=device_info,
                user_id=user_id,
                session_id=session_id
            )
            
            # Publish through enhanced bus
            success = await publish_voice_activity_event(
                activity_type="activity_detected",
                audio_data={
                    "duration_ms": activity_data["duration_ms"],
                    "volume_level": activity_data["volume_level"],
                    "pitch_frequency": activity_data["pitch_frequency"],
                    "quality_score": activity_data["quality_score"]
                },
                user_id=user_id
            )
            
            if success:
                self.processing_stats["voice_activities"] += 1
                logger.debug(f"📤 Published voice activity event for user {user_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to publish voice activity event: {e}")
    
    async def _process_speech_intent(
        self,
        audio_data: bytes,
        user_id: str,
        session_id: str,
        device_info: DeviceInfo
    ) -> Dict[str, Any]:
        """Process speech for intent classification"""
        try:
            # Simulate speech-to-text
            transcription = await self._speech_to_text(audio_data)
            
            # Simulate intent classification
            intent_result = await self._classify_intent(transcription, user_id)
            
            # Create and publish intent event
            intent_event = create_voice_intent_event(
                event_type=VoiceIntentType.INTENT_CLASSIFIED,
                primary_intent=intent_result["intent"],
                confidence_score=intent_result["confidence"],
                language_detected=intent_result["language"],
                classification_model="intent-classifier-v1",
                processing_time_ms=intent_result["processing_time_ms"],
                device_info=device_info,
                user_id=user_id,
                session_id=session_id
            )
            
            # Publish intent event
            await self.bus.publish(
                channel=V3EventChannels.VOICE_INTENT_CLASSIFIED,
                data=intent_event.dict(),
                user_id=user_id
            )
            
            self.processing_stats["intents_classified"] += 1
            
            return {
                "status": "intent_classified",
                "transcription": transcription,
                "intent": intent_result["intent"],
                "confidence": intent_result["confidence"],
                "language": intent_result["language"]
            }
            
        except Exception as e:
            logger.error(f"❌ Error processing speech intent: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _speech_to_text(self, audio_data: bytes) -> str:
        """Simulate speech-to-text conversion"""
        # In real implementation, this would use Whisper or similar
        sample_transcriptions = [
            "I want to start a meditation session",
            "Help me with breathing exercises", 
            "Show me my mood tracking progress",
            "I'm feeling anxious today",
            "Start a 10 minute relaxation session",
            "Play calming music",
            "Record my daily journal entry"
        ]
        import random
        return random.choice(sample_transcriptions)
    
    async def _classify_intent(self, transcription: str, user_id: str) -> Dict[str, Any]:
        """Simulate intent classification"""
        import random
        import time
        
        start_time = time.time()
        
        # Simple keyword-based intent classification
        intents = {
            "meditation": ["meditat", "calm", "relax", "peace"],
            "mood_tracking": ["mood", "feeling", "emotion", "track"],
            "breathing": ["breath", "breathing", "inhale", "exhale"],
            "journal": ["journal", "diary", "write", "record"],
            "music": ["music", "sound", "audio", "play"],
            "anxiety": ["anxious", "worry", "stress", "nervous"]
        }
        
        detected_intent = "general_request"
        confidence = 0.5
        
        text_lower = transcription.lower()
        for intent, keywords in intents.items():
            if any(keyword in text_lower for keyword in keywords):
                detected_intent = intent
                confidence = random.uniform(0.75, 0.95)
                break
        
        processing_time = int((time.time() - start_time) * 1000)
        
        return {
            "intent": detected_intent,
            "confidence": confidence,
            "language": "en",  # Could add language detection
            "processing_time_ms": processing_time,
            "parameters": self._extract_parameters(transcription, detected_intent)
        }
    
    def _extract_parameters(self, transcription: str, intent: str) -> Dict[str, Any]:
        """Extract parameters from transcription based on intent"""
        parameters = {}
        
        if intent == "meditation":
            # Extract duration if mentioned
            import re
            duration_match = re.search(r'(\d+)\s*(minute|min)', transcription.lower())
            if duration_match:
                parameters["duration"] = f"{duration_match.group(1)} minutes"
        
        elif intent == "mood_tracking":
            # Extract mood keywords
            mood_words = ["happy", "sad", "anxious", "calm", "excited", "tired"]
            for mood in mood_words:
                if mood in transcription.lower():
                    parameters["mood_detected"] = mood
                    break
        
        return parameters
    
    # Event Handlers
    async def _handle_voice_activity(self, event):
        """Handle voice activity events"""
        logger.debug(f"🎤 Voice activity detected: {event.channel}")
        self.processing_stats["events_processed"] += 1
        
        # Update session tracking
        if event.user_id and "session_id" in event.data:
            session_id = event.data["session_id"]
            if session_id not in self.active_sessions:
                self.active_sessions[session_id] = {
                    "user_id": event.user_id,
                    "start_time": datetime.now(),
                    "activity_count": 0
                }
            self.active_sessions[session_id]["activity_count"] += 1
    
    async def _handle_speech_start(self, event):
        """Handle speech start events"""
        logger.debug(f"🗣️ Speech started for user: {event.user_id}")
        # Could trigger UI updates, prepare for transcription, etc.
    
    async def _handle_speech_end(self, event):
        """Handle speech end events"""
        logger.debug(f"🔇 Speech ended for user: {event.user_id}")
        # Could finalize transcription, clean up resources, etc.
    
    async def _handle_intent_classified(self, event):
        """Handle intent classification events"""
        intent_data = event.data.get("intent_data", {})
        logger.info(f"🎯 Intent classified: {intent_data.get('primary_intent')} "
                   f"(confidence: {intent_data.get('confidence_score', 0):.2f})")
        
        # Forward to appropriate service based on intent
        await self._route_intent(event)
    
    async def _route_intent(self, event):
        """Route intent to appropriate service"""
        intent_data = event.data.get("intent_data", {})
        intent = intent_data.get("primary_intent")
        
        if intent == "meditation":
            # Route to meditation service
            await self.bus.publish(
                channel="service.meditation.intent_received",
                data=event.data,
                user_id=event.user_id
            )
        elif intent == "mood_tracking":
            # Route to mood service
            await self.bus.publish(
                channel="service.mood.intent_received", 
                data=event.data,
                user_id=event.user_id
            )
        elif intent == "journal":
            # Route to journal service
            await self.bus.publish(
                channel="service.journal.intent_received",
                data=event.data,
                user_id=event.user_id
            )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        return {
            **self.processing_stats,
            "active_sessions": len(self.active_sessions),
            "bus_connected": self.bus is not None and getattr(self.bus, 'connected', False)
        }
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.bus:
            await self.bus.close()
        self.active_sessions.clear()
        logger.info("🧹 Voice event processor cleaned up")


# Example usage and testing
async def main():
    """Example usage of the voice event processor"""
    processor = VoiceEventProcessor()
    
    # Initialize
    if not await processor.initialize():
        print("Failed to initialize voice processor")
        return
    
    # Simulate processing some audio inputs
    test_audio_data = b"fake_audio_data" * 100  # Simulate audio data
    
    for i in range(3):
        result = await processor.process_audio_input(
            audio_data=test_audio_data,
            user_id=f"test_user_{i}",
            device_id=f"device_{i}"
        )
        print(f"Processing result {i}: {result}")
        
        # Wait a bit between processing
        await asyncio.sleep(0.1)
    
    # Print stats
    stats = processor.get_stats()
    print(f"Processing stats: {stats}")
    
    # Get bus performance stats
    if processor.bus:
        bus_stats = processor.bus.get_performance_stats()
        print(f"Bus stats: {bus_stats}")
    
    # Cleanup
    await processor.cleanup()


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run example
    asyncio.run(main())
