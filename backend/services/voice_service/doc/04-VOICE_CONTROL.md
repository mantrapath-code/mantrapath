# Voice Control Features

## Overview

The Voice Control system enables users to interact with MantraPath services through natural voice commands. Supporting 16 languages with intelligent intent recognition, the system provides hands-free navigation, content management, and wellness features.

## 🎯 Core Voice Control Features

### 1. Natural Language Commands
Users can speak naturally in any supported language:
- **"Start a meditation session"** → Launches meditation service
- **"Show my mood history"** → Opens mood analytics  
- **"Create a new journal entry"** → Opens journal interface
- **"Find articles about mindfulness"** → Searches content library

### 2. Context-Aware Processing
- **Session Context**: Commands adapt based on current user activity
- **User Preferences**: Personalized command interpretation
- **Location Awareness**: Context-sensitive responses
- **Time-Based**: Different responses for morning vs evening commands

### 3. Multilingual Voice Commands
Each language tier supports culturally appropriate commands:

#### Tier 1 Languages (Premium Support)
- **English**: Full command vocabulary with cultural variations
- **Hindi**: Sanskrit mantra integration, traditional greeting commands  
- **Spanish**: Regional dialect support, cultural meditation terms
- **Sanskrit**: Mantra-specific commands, pronunciation guidance
- **Others**: Culturally adapted command sets

#### Tier 2 Languages (Standard Support)
- Comprehensive command vocabulary
- Standard voice processing
- Basic cultural adaptation

## 🗣️ Voice Command Categories

### Navigation Commands
```yaml
Categories:
  - page_navigation: "Go to dashboard", "Open settings", "Show profile"
  - feature_access: "Start meditation", "Open journal", "Check mood"
  - service_control: "Pause music", "Stop recording", "Save entry"
  
Examples:
  English:
    - "Navigate to my dashboard"
    - "Open the meditation library"
    - "Show me today's activities"
  
  Hindi:
    - "डैशबोर्ड खोलें" (Open dashboard)
    - "ध्यान शुरू करें" (Start meditation)
    - "आज के कार्य दिखाएं" (Show today's activities)
  
  Spanish:
    - "Navega al tablero"
    - "Abre la biblioteca de meditación"
    - "Muestra mis actividades de hoy"
```

### Content Management Commands
```yaml
Categories:
  - content_creation: "Create new entry", "Record voice note", "Save bookmark"
  - content_search: "Find articles about...", "Search my journals", "Show recent"
  - content_organization: "Tag this entry", "Archive old notes", "Export data"

Examples:
  English:
    - "Create a new journal entry about today"
    - "Find all my meditation sessions from last week"
    - "Bookmark this article for later reading"
  
  Hindi:
    - "आज के बारे में नई डायरी लिखें"
    - "पिछले हफ्ते के सभी ध्यान सत्र खोजें"
    - "इस लेख को बाद में पढ़ने के लिए सेव करें"
```

### Wellness Commands
```yaml
Categories:
  - mood_tracking: "Log my mood as happy", "Rate today's energy", "Record feelings"
  - habit_management: "Mark habit complete", "Check habit streak", "Add new habit"  
  - meditation_control: "Start 10-minute meditation", "Play calm music", "Set timer"

Examples:
  English:
    - "Log my mood as calm and focused"
    - "Mark my morning meditation as complete"
    - "Start a 15-minute breathing exercise"
  
  Sanskrit:
    - "शांति का ध्यान शुरू करें" (Start peace meditation)
    - "ओम मंत्र का जाप करें" (Chant Om mantra)
    - "प्राणायाम अभ्यास शुरू करें" (Start pranayama practice)
```

### Social & Community Commands  
```yaml
Categories:
  - community_interaction: "Check community posts", "Reply to message", "Join discussion"
  - sharing: "Share my progress", "Post in community", "Send to friend"
  - notifications: "Read notifications", "Mark as read", "Clear all alerts"

Examples:
  English:
    - "Check what's happening in the mindfulness community"
    - "Share my 30-day meditation streak achievement"
    - "Read my unread notifications"
```

## 🔧 Technical Implementation

### Command Processing Pipeline
```python
# Voice Command Processing Flow
async def process_voice_command(audio_data: bytes, user_context: dict) -> VoiceCommandResponse:
    # 1. Speech-to-Text
    transcription = await stt_engine.transcribe(audio_data, user_language)
    
    # 2. Intent Recognition
    intent = await intent_classifier.classify(transcription, user_context)
    
    # 3. Context Enhancement
    enhanced_intent = await context_processor.enhance(intent, user_context)
    
    # 4. Command Execution
    result = await command_executor.execute(enhanced_intent)
    
    # 5. Response Generation
    response = await response_generator.generate(result, user_preferences)
    
    return response
```

### Intent Classification System
```python
class IntentClassifier:
    """Advanced intent recognition with multilingual support"""
    
    INTENT_CATEGORIES = {
        "navigation": ["go", "open", "show", "display", "navigate"],
        "content": ["create", "write", "save", "find", "search"],
        "wellness": ["meditate", "mood", "habit", "track", "log"],
        "social": ["share", "post", "message", "community", "friend"]
    }
    
    async def classify_intent(self, text: str, context: dict) -> Intent:
        # Multi-stage classification
        primary_intent = await self.classify_primary(text)
        secondary_intent = await self.classify_secondary(text, primary_intent)
        confidence_score = await self.calculate_confidence(text, context)
        
        return Intent(
            primary=primary_intent,
            secondary=secondary_intent,
            confidence=confidence_score,
            parameters=self.extract_parameters(text)
        )
```

### Context-Aware Processing
```python
class ContextProcessor:
    """Enhances commands with user and session context"""
    
    async def enhance_intent(self, intent: Intent, context: UserContext) -> EnhancedIntent:
        # User preference integration
        preferences = await self.get_user_preferences(context.user_id)
        
        # Session context
        current_session = await self.get_current_session(context.session_id)
        
        # Time-based context
        time_context = self.get_time_context()
        
        # Location awareness (if enabled)
        location_context = await self.get_location_context(context)
        
        return EnhancedIntent(
            original_intent=intent,
            user_preferences=preferences,
            session_context=current_session,
            temporal_context=time_context,
            spatial_context=location_context
        )
```

## 🌟 Advanced Voice Control Features

### 1. Conversation Memory
```python
class ConversationMemory:
    """Maintains conversation context across multiple commands"""
    
    def __init__(self):
        self.conversation_history = []
        self.context_window = 10  # Remember last 10 interactions
    
    async def add_interaction(self, command: str, response: str, context: dict):
        interaction = {
            "timestamp": datetime.now(),
            "command": command,
            "response": response,
            "context": context
        }
        self.conversation_history.append(interaction)
        
        # Maintain context window
        if len(self.conversation_history) > self.context_window:
            self.conversation_history.pop(0)
    
    async def get_relevant_context(self, current_command: str) -> dict:
        # Find contextually relevant previous interactions
        relevant_interactions = self.find_relevant_interactions(current_command)
        return self.build_context_summary(relevant_interactions)
```

### 2. Proactive Voice Assistance
```python
class ProactiveAssistant:
    """Provides contextual suggestions and reminders"""
    
    PROACTIVE_TRIGGERS = {
        "time_based": {
            "morning": ["meditation_reminder", "habit_check", "daily_planning"],
            "evening": ["mood_check", "day_reflection", "gratitude_practice"]
        },
        "activity_based": {
            "meditation_completion": ["mood_log_suggestion", "progress_sharing"],
            "stress_detection": ["breathing_exercise", "calming_music"]
        }
    }
    
    async def generate_proactive_suggestions(self, context: UserContext) -> List[ProactiveSuggestion]:
        suggestions = []
        
        # Time-based suggestions
        time_suggestions = await self.get_time_based_suggestions(context)
        suggestions.extend(time_suggestions)
        
        # Activity-based suggestions
        activity_suggestions = await self.get_activity_based_suggestions(context)
        suggestions.extend(activity_suggestions)
        
        # Personalized suggestions
        personal_suggestions = await self.get_personalized_suggestions(context)
        suggestions.extend(personal_suggestions)
        
        return self.rank_and_filter_suggestions(suggestions)
```

### 3. Voice Command Customization
```python
class CommandCustomization:
    """Allows users to create custom voice commands"""
    
    async def create_custom_command(self, user_id: str, command_phrase: str, action_sequence: List[Action]) -> CustomCommand:
        custom_command = CustomCommand(
            user_id=user_id,
            trigger_phrase=command_phrase,
            actions=action_sequence,
            language=user_language,
            created_at=datetime.now()
        )
        
        # Train personalized recognition
        await self.train_personal_recognition(user_id, command_phrase)
        
        # Store custom command
        await self.store_custom_command(custom_command)
        
        return custom_command
    
    async def execute_custom_command(self, command: CustomCommand, context: UserContext) -> CommandResult:
        results = []
        for action in command.actions:
            result = await self.execute_action(action, context)
            results.append(result)
        
        return CommandResult(
            success=all(r.success for r in results),
            results=results,
            custom_command_id=command.id
        )
```

## 🎤 Voice UI Components

### 1. Voice Input Handler
```typescript
class VoiceInputHandler {
    private mediaRecorder: MediaRecorder | null = null;
    private isRecording = false;
    
    async startVoiceInput(): Promise<void> {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            this.mediaRecorder = new MediaRecorder(stream);
            
            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    this.processAudioData(event.data);
                }
            };
            
            this.mediaRecorder.start();
            this.isRecording = true;
            
            // Visual feedback
            this.showRecordingIndicator();
            
        } catch (error) {
            console.error('Voice input failed:', error);
            this.showErrorMessage('Microphone access denied');
        }
    }
    
    async stopVoiceInput(): Promise<void> {
        if (this.mediaRecorder && this.isRecording) {
            this.mediaRecorder.stop();
            this.isRecording = false;
            this.hideRecordingIndicator();
        }
    }
    
    private async processAudioData(audioData: Blob): Promise<void> {
        const formData = new FormData();
        formData.append('file', audioData, 'voice_command.wav');
        formData.append('language', this.getUserLanguage());
        
        try {
            const response = await fetch('/voice/voice-command', {
                method: 'POST',
                body: formData,
                headers: {
                    'Authorization': `Bearer ${this.getAuthToken()}`
                }
            });
            
            const result = await response.json();
            await this.handleCommandResult(result);
            
        } catch (error) {
            console.error('Command processing failed:', error);
            this.showErrorMessage('Voice command processing failed');
        }
    }
}
```

### 2. Voice Response System  
```typescript
class VoiceResponseSystem {
    private speechSynthesis: SpeechSynthesis;
    private currentUtterance: SpeechSynthesisUtterance | null = null;
    
    async speakResponse(text: string, options: VoiceOptions = {}): Promise<void> {
        // Stop any current speech
        this.stopSpeaking();
        
        // Create utterance with user preferences
        this.currentUtterance = new SpeechSynthesisUtterance(text);
        this.currentUtterance.lang = options.language || this.getUserLanguage();
        this.currentUtterance.voice = this.selectVoice(options);
        this.currentUtterance.rate = options.rate || this.getUserSpeechRate();
        this.currentUtterance.pitch = options.pitch || this.getUserSpeechPitch();
        
        // Add event listeners
        this.currentUtterance.onstart = () => this.showSpeakingIndicator();
        this.currentUtterance.onend = () => this.hideSpeakingIndicator();
        this.currentUtterance.onerror = (error) => console.error('Speech synthesis error:', error);
        
        // Speak response
        this.speechSynthesis.speak(this.currentUtterance);
    }
    
    stopSpeaking(): void {
        if (this.currentUtterance) {
            this.speechSynthesis.cancel();
            this.currentUtterance = null;
            this.hideSpeakingIndicator();
        }
    }
    
    private selectVoice(options: VoiceOptions): SpeechSynthesisVoice | null {
        const voices = this.speechSynthesis.getVoices();
        const userLanguage = options.language || this.getUserLanguage();
        
        // Find best matching voice
        return voices.find(voice => 
            voice.lang.startsWith(userLanguage) && 
            (options.gender ? voice.name.toLowerCase().includes(options.gender) : true)
        ) || null;
    }
}
```

## 🧠 Machine Learning Integration

### Intent Recognition Model
```python
class VoiceIntentModel:
    """ML model for voice command intent recognition"""
    
    def __init__(self):
        self.model = self.load_trained_model()
        self.tokenizer = self.load_tokenizer()
        self.label_encoder = self.load_label_encoder()
    
    async def predict_intent(self, text: str, context: dict) -> IntentPrediction:
        # Preprocess text
        processed_text = await self.preprocess_text(text)
        
        # Tokenize
        tokens = self.tokenizer.encode(processed_text)
        
        # Add context features
        context_features = self.extract_context_features(context)
        
        # Predict
        prediction = self.model.predict(tokens, context_features)
        
        # Decode prediction
        intent_label = self.label_encoder.inverse_transform([prediction.argmax()])[0]
        confidence = float(prediction.max())
        
        return IntentPrediction(
            intent=intent_label,
            confidence=confidence,
            alternatives=self.get_alternative_intents(prediction)
        )
```

## 📱 Cross-Platform Voice Control

### Mobile Implementation
```typescript
// React Native voice control integration
class MobileVoiceController {
    async initializeVoiceRecognition(): Promise<void> {
        const hasPermission = await this.requestMicrophonePermission();
        if (!hasPermission) {
            throw new Error('Microphone permission required');
        }
        
        // Configure voice recognition
        Voice.onSpeechStart = this.onSpeechStart.bind(this);
        Voice.onSpeechEnd = this.onSpeechEnd.bind(this);
        Voice.onSpeechResults = this.onSpeechResults.bind(this);
        Voice.onSpeechError = this.onSpeechError.bind(this);
    }
    
    async startListening(): Promise<void> {
        try {
            await Voice.start(this.getUserLanguage());
            this.setState({ isListening: true });
        } catch (error) {
            console.error('Voice recognition start failed:', error);
        }
    }
    
    private onSpeechResults(event: { value: string[] }): void {
        const bestResult = event.value[0];
        this.processVoiceCommand(bestResult);
    }
}
```

### Web Implementation
```typescript
// Web-based voice control with Web Speech API
class WebVoiceController {
    private recognition: SpeechRecognition | null = null;
    
    initializeWebSpeech(): void {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        
        if (!SpeechRecognition) {
            throw new Error('Speech recognition not supported');
        }
        
        this.recognition = new SpeechRecognition();
        this.recognition.continuous = true;
        this.recognition.interimResults = true;
        this.recognition.lang = this.getUserLanguage();
        
        // Event handlers
        this.recognition.onstart = () => this.onRecognitionStart();
        this.recognition.onresult = (event) => this.onRecognitionResult(event);
        this.recognition.onerror = (error) => this.onRecognitionError(error);
        this.recognition.onend = () => this.onRecognitionEnd();
    }
    
    startContinuousListening(): void {
        if (this.recognition) {
            this.recognition.start();
        }
    }
    
    private onRecognitionResult(event: SpeechRecognitionEvent): void {
        let finalTranscript = '';
        let interimTranscript = '';
        
        for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            
            if (event.results[i].isFinal) {
                finalTranscript += transcript;
            } else {
                interimTranscript += transcript;
            }
        }
        
        if (finalTranscript) {
            this.processVoiceCommand(finalTranscript);
        }
        
        // Show interim results for better UX
        this.showInterimResults(interimTranscript);
    }
}
```

## 🔒 Privacy & Security

### Voice Data Protection
- **No Permanent Storage**: Voice data processed in memory only
- **Encryption**: All audio transmissions encrypted in transit
- **User Consent**: Explicit permission for microphone access
- **Data Retention**: Configurable voice data retention policies

### Privacy Controls
```python
class VoicePrivacyManager:
    """Manages voice data privacy and user consent"""
    
    async def check_voice_consent(self, user_id: str) -> bool:
        consent = await self.get_user_consent(user_id)
        return consent.voice_processing_enabled
    
    async def process_with_privacy(self, audio_data: bytes, user_id: str) -> ProcessingResult:
        # Check consent
        if not await self.check_voice_consent(user_id):
            raise VoicePrivacyError("Voice processing not consented")
        
        # Process with privacy controls
        result = await self.process_voice_data(audio_data)
        
        # Clean sensitive data
        await self.clean_temporary_data(audio_data, result)
        
        return result
```

## 🌍 Accessibility Features

### Voice Control for Accessibility
- **Screen Reader Integration**: Works with NVDA, JAWS, VoiceOver
- **Motor Impairment Support**: Hands-free navigation
- **Cognitive Assistance**: Simple command structure
- **Visual Impairment**: Audio-first interaction design

### Inclusive Design Principles
- **Multi-modal Input**: Voice + touch + keyboard support
- **Clear Feedback**: Audio and visual confirmation
- **Error Recovery**: Graceful handling of misrecognition
- **Customization**: Adjustable sensitivity and commands

---

The Voice Control system transforms MantraPath into a truly accessible, hands-free wellness platform that responds naturally to user intent across multiple languages and contexts.
