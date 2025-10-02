# MantraPath Enhanced Journal Flow - Multi-Modal Entry System

## Overview

Enhanced journal system supporting **Voice + Video + Text** entries with AI-powered insights through integrated backend services.

## Entry Types & Data Flow

### 📝 **Text Journal**
- **Input**: Text content only
- **Processing**: Content analysis, sentiment, themes
- **Services**: Content Service → AI Event Processor → Memory Service

### 🎤 **Voice Journal** 
- **Input**: Voice recording + transcribed text
- **Processing**: Voice emotion analysis + text analysis
- **Services**: Voice Service → Voice Event Processor → AI Event Processor → Memory Service

### 📹 **Video Journal**
- **Input**: Video recording + facial expressions + voice + transcribed text
- **Processing**: Facial emotion + voice emotion + text analysis (triple insights)
- **Services**: Media Service → Voice Service → Voice Event Processor → AI Event Processor → Memory Service

## Multi-Modal Journal Entry Flow

### 1. **Frontend Entry Creation**
```
User selects entry type → Records/Types content → Frontend processes → API call
```

### 2. **Backend Service Processing**

#### **Text Entry Flow**
```
API Gateway → Content Service → AI Event Processor → Memory Service → Response
```
- Content Service: Text analysis, sentiment, themes
- AI Event Processor: Behavioral patterns, wellness insights
- Memory Service: Store with context and history

#### **Voice Entry Flow**
```
API Gateway → Voice Service → Voice Event Processor → AI Event Processor → Memory Service
```
- Voice Service: Speech-to-text transcription (95% accuracy)
- Voice Event Processor: Emotion detection, stress analysis
- AI Event Processor: Combined voice + text insights
- Memory Service: Store with voice patterns and text context

#### **Video Entry Flow**
```
API Gateway → Media Service → Voice Service + Facial Analysis → Voice Event Processor → AI Event Processor → Memory Service
```
- Media Service: Video processing, facial emotion detection
- Voice Service: Audio extraction and transcription
- Voice Event Processor: Voice emotion analysis
- AI Event Processor: Triple analysis (facial + voice + text)
- Memory Service: Rich multi-modal context storage

## Service Integration & Insights

### **Memory Service Role**
- **Context Storage**: Links entries with user history and patterns
- **Progress Tracking**: Emotional journey over time
- **Pattern Recognition**: Identifies recurring themes and triggers

### **AI Context Store Integration**
- **User Understanding**: Maintains comprehensive user profile
- **Cultural Context**: Adapts insights to cultural background
- **Therapeutic Goals**: Aligns insights with wellness objectives

### **Proactive Assistance Engine**
- **Smart Recommendations**: Suggests coping strategies based on analysis
- **Intervention Timing**: Identifies when professional help might be needed
- **Wellness Optimization**: Recommends activities based on mood patterns

### **Action Orchestrator Role**
- **Service Coordination**: Manages flow between services
- **Event Sequencing**: Ensures proper processing order
- **Error Handling**: Manages fallback scenarios and retries
    user = relationship("User", back_populates="journal_entries")
```

---

## 3. Chatbot Integration & Journal Reference System

### 3.1 How Chatbot Should Access Journal Data

#### **AI Context Store Integration**
```python
# Location: backend/services/ai_context_store/data_collectors/journal_data_collector.py
class JournalDataCollector:
    """Collects journal data for context building"""
    
    async def collect_user_journal_data(self, user_id: str, jwt_token: str, days_back: int = 30):
        """
        Collect journal data for a user for AI context
        """
        try:
            headers = {"Authorization": f"Bearer {jwt_token}"}
            
            # Get journal entries from content service
            journal_response = await client.get(
                f"{self.content_service_url}/api/v1/journal/entries",
                headers=headers
            )
            
            if journal_response.status_code == 200:
                journal_entries = journal_response.json()
                return self._process_journal_data(journal_entries)
                
        except Exception as e:
            logger.warning(f"Error collecting journal data: {e}")
            return {}
    
    def _process_journal_data(self, journal_entries: List[Dict]) -> Dict[str, Any]:
        """Process raw journal data into context format"""
        return {
            "total_entries": len(journal_entries),
            "recent_entries_count": len(recent_entries),
            "latest_entry": sorted_entries[0] if sorted_entries else None,
            "common_themes": self._extract_themes(all_text),
            "sentiment_patterns": self._analyze_sentiment_patterns(journal_entries),
            "writing_patterns": {
                "avg_length": avg_length,
                "entries_this_week": len(recent_entries),
                "most_active_day": self._get_most_active_day(dates)
            }
        }
```

#### **Chatbot Context Integration**
```python
# Location: backend/services/chatbot_service/src/intelligent_engine/mood_aware_responder.py
base_prompt = f"""You are Mantra-Mitra, the AI wellness companion for MantraPath - a comprehensive mental health platform. You have access to the user's mood tracking data, journal entries, and wellness journey.

Platform Context:
- MantraPath tracks mood scores (1-10 scale), energy levels, stress levels, and sleep quality
- Users can journal, join community forums, and participate in wellness challenges
- The platform provides emotional weather forecasts and personalized insights
- Current user mood score: {mood_context.current_mood_score}/10

Response Guidelines:
- Reference their actual mood data when relevant
- Be aware of their wellness journey on MantraPath
- Suggest platform features when appropriate (mood tracking, journaling, community)
- Keep responses warm, personal, and actionable (2-3 sentences)
"""
```

### 3.2 Event-Driven Journal Integration

#### **Journal Entry Creation Event**
```python
# Location: backend/shared/events/enhanced_bus.py
class V3EventChannels:
    JOURNAL_ENTRY_CREATED = "journal.entry.created"

# When journal entry is created, publish event
async def publish_journal_entry_event(entry_data: Dict[str, Any], user_id: str):
    bus = get_enhanced_event_bus()
    await bus.publish(
        V3EventChannels.JOURNAL_ENTRY_CREATED,
        {
            "entry_id": entry_data["id"],
            "user_id": user_id,
            "content_summary": entry_data["content"][:200],
            "sentiment": entry_data.get("sentiment_label"),
            "themes": entry_data.get("themes", []),
            "created_at": entry_data["created_at"]
        },
        user_id
    )
```

#### **Chatbot Event Subscription**
```python
# Chatbot service subscribes to journal events
async def handle_journal_entry_created(event: Event):
    """Handle new journal entry for context update"""
    user_id = event.user_id
    entry_data = event.data
    
    # Update user context in AI context store
    await update_user_context(user_id, {
        "recent_journal_activity": entry_data,
        "last_journal_entry": entry_data["created_at"],
        "journal_sentiment_trend": entry_data["sentiment"]
    })
    
    # Trigger proactive suggestions if needed
    if entry_data["sentiment"] == "negative":
        await trigger_wellness_check(user_id)
```

---

## 4. Complete Data Flow Diagram

## Enhanced Insights & Analytics

### **Multi-Modal Data Correlation**
- **Text**: Sentiment, themes, writing patterns
- **Voice**: Emotion, stress levels, energy patterns  
- **Video**: Facial expressions, body language, visual cues
- **Combined**: Comprehensive emotional and mental state analysis

### **Real-Time Processing Pipeline**
```
Entry Created → Service Processing → AI Analysis → Context Update → Insights Generated → User Feedback
```

### **Intelligent Recommendations**
- **Mood-Based**: Activity suggestions based on detected emotional state
- **Pattern-Based**: Interventions based on historical patterns
- **Context-Aware**: Recommendations considering user situation and goals
- **Professional Alerts**: Notifications to healthcare providers when needed

## Implementation Flow

### **Frontend Components**
```
JournalEntry
├── TextEditor (existing)
├── VoiceRecorder (new)
├── VideoRecorder (new)
└── EntryTypeSelector (new)
```

### **API Endpoints**
```
POST /api/v1/journal/text     → Content Service
POST /api/v1/journal/voice    → Voice Service  
POST /api/v1/journal/video    → Media Service
GET  /api/v1/journal/insights → AI Context Store
```

### **Service Orchestration**
Action Orchestrator manages the service flow:
1. **Routes** entry to appropriate service
2. **Coordinates** multi-service processing
3. **Aggregates** insights from all services
4. **Triggers** follow-up actions based on analysis
5. **Updates** Memory Service with complete context

## Key Benefits

- **Rich Context**: Multi-modal entries provide comprehensive emotional picture
- **Better Insights**: Triple analysis (facial + voice + text) for video entries
- **Personalized Care**: AI-powered recommendations based on complete user understanding
- **Professional Integration**: Healthcare providers get richer patient insights
- **Pattern Recognition**: Long-term trends across all entry types

---

## 5. Implementation Gaps & Requirements

### 5.1 Critical Missing Backend Implementation

#### **Priority 1: Core Journal CRUD Operations**
```python
# Required Implementation in mood_service/src/api/journal_routes.py

@router.post("/")
async def create_journal_entry(
    journal_data: JournalCreateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new journal entry with full processing"""
    try:
        # 1. Create journal entry in database
        entry = JournalEntry(
            user_id=current_user["user_id"],
            title=journal_data.title,
            content=journal_data.content,
            mood_before=journal_data.mood_before,
            mood_after=journal_data.mood_after,
            is_private=journal_data.is_private
        )
        
        # 2. Process content (sentiment, themes, word count)
        entry.sentiment_score, entry.sentiment_label = analyze_sentiment(entry.content)
        entry.themes = extract_themes(entry.content)
        entry.word_count = len(entry.content.split())
        entry.reading_time = calculate_reading_time(entry.content)
        
        db.add(entry)
        db.commit()
        db.refresh(entry)
        
        # 3. Publish event for other services
        background_tasks.add_task(
            publish_journal_entry_event,
            entry.to_dict(),
            current_user["user_id"]
        )
        
        return entry.to_dict()
        
    except Exception as e:
        logger.error(f"Failed to create journal entry: {e}")
        raise HTTPException(status_code=500, detail="Failed to create journal entry")

@router.get("/")
async def get_journal_entries(
    limit: int = 20,
    offset: int = 0,
    include_private: bool = True,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get user's journal entries with pagination"""
    query = db.query(JournalEntry).filter(
        JournalEntry.user_id == current_user["user_id"]
    )
    
    if not include_private:
        query = query.filter(JournalEntry.is_private == False)
    
    entries = query.order_by(
        JournalEntry.created_at.desc()
    ).offset(offset).limit(limit).all()
    
    return [entry.to_dict() for entry in entries]
```

#### **Priority 2: AI Integration Services**
```python
# Required: Sentiment Analysis Service
async def analyze_sentiment(content: str) -> Tuple[float, str]:
    """Analyze sentiment of journal content"""
    # Integration with ML service for sentiment analysis
    
# Required: Theme Extraction Service  
async def extract_themes(content: str) -> List[str]:
    """Extract themes from journal content"""
    # Integration with ML service for theme extraction
    
# Required: Reading Time Calculation
def calculate_reading_time(content: str) -> int:
    """Calculate estimated reading time in seconds"""
    words = len(content.split())
    # Average reading speed: 200-250 words per minute
    return (words / 225) * 60
```

#### **Priority 3: Event-Driven Integration**
```python
# Required: Event Publishing
async def publish_journal_entry_event(entry_data: Dict, user_id: str):
    """Publish journal entry creation event"""
    bus = get_enhanced_event_bus()
    await bus.publish(
        V3EventChannels.JOURNAL_ENTRY_CREATED,
        {
            "entry_id": entry_data["id"],
            "user_id": user_id,
            "content_preview": entry_data["content"][:200],
            "sentiment": entry_data["sentiment_label"],
            "themes": entry_data["themes"],
            "word_count": entry_data["word_count"],
            "is_private": entry_data["is_private"],
            "created_at": entry_data["created_at"]
        },
        user_id
    )
```

### 5.2 Chatbot Integration Requirements

#### **Context-Aware Journal References**
```python
# Required in chatbot service
class JournalContextManager:
    """Manage journal context for chatbot responses"""
    
    async def get_recent_journal_context(self, user_id: str, days: int = 7) -> Dict:
        """Get recent journal context for chatbot"""
        context_data = await journal_data_collector.collect_user_journal_data(
            user_id, days_back=days
        )
        
        return {
            "recent_themes": context_data.get("common_themes", [])[:5],
            "sentiment_trend": context_data.get("sentiment_patterns", {}).get("sentiment_trend"),
            "writing_frequency": context_data.get("writing_patterns", {}).get("entries_this_week", 0),
            "last_entry_date": context_data.get("latest_entry", {}).get("created_at")
        }
    
    def generate_journal_aware_response(self, user_message: str, journal_context: Dict) -> str:
        """Generate response that references journal data"""
        if journal_context.get("recent_themes"):
            themes_str = ", ".join(journal_context["recent_themes"][:3])
            return f"I notice you've been writing about {themes_str} recently. {base_response}"
        
        if journal_context.get("sentiment_trend") == "negative":
            return f"I see you've been processing some challenging thoughts in your journal. {supportive_response}"
            
        return base_response
```

---

## 6. Service Integration Architecture

### 6.1 Current Service Routing
```
Frontend Request: POST /api/v1/journal/
    ↓
API Gateway: Routes to mood-service
    ↓  
Mood Service: journal_routes.py (PLACEHOLDER)
    ↓
Returns: 501 Not Implemented
```

### 6.2 Recommended Service Architecture
```
Frontend Request: POST /api/v1/journal/
    ↓
API Gateway: Routes to content-service OR dedicated journal-service
    ↓  
Content/Journal Service: Full CRUD implementation
    ↓
Database: journal_entries table
    ↓
Event Bus: Publishes journal.entry.created
    ↓
Subscribers:
    - AI Context Store (context building)
    - Chatbot Service (conversation context)
    - ML Service (sentiment/theme analysis)
    - Notification Service (wellness checks)
```

---

## 7. Implementation Roadmap

### Phase 1: Core Backend Implementation (1-2 weeks)
1. **Implement journal CRUD endpoints** in mood service or content service
2. **Database operations** for journal entries
3. **Basic content processing** (word count, reading time)
4. **API Gateway routing** verification

### Phase 2: AI Integration (1 week)
1. **Sentiment analysis** integration with ML service
2. **Theme extraction** capabilities
3. **Event publishing** for journal entry creation
4. **AI context store** journal data collection

### Phase 3: Chatbot Integration (1 week)
1. **Journal context** integration in chatbot responses
2. **Event subscription** for real-time context updates
3. **Proactive wellness** suggestions based on journal sentiment
4. **Reference patterns** in conversation responses

### Phase 4: Advanced Features (Ongoing)
1. **Analytics backend** for writing insights
2. **Search capabilities** with full-text search
3. **Export/import** functionality
4. **Sharing and collaboration** features

---

## 8. Technical Specifications

### 8.1 API Endpoints (Required Implementation)
```
POST   /api/v1/journal/           # Create journal entry
GET    /api/v1/journal/           # List entries (paginated)
GET    /api/v1/journal/{id}       # Get specific entry  
PUT    /api/v1/journal/{id}       # Update entry
DELETE /api/v1/journal/{id}       # Delete entry
GET    /api/v1/journal/search     # Search entries
GET    /api/v1/journal/analytics  # Writing analytics
```

### 8.2 Database Schema
```sql
CREATE TABLE journal_entries (
    id VARCHAR PRIMARY KEY,
    user_id VARCHAR NOT NULL,
    title VARCHAR,
    content TEXT NOT NULL,
    mood_before INTEGER,
    mood_after INTEGER,
    sentiment_score FLOAT,
    sentiment_label VARCHAR,
    themes JSON,
    is_private BOOLEAN DEFAULT TRUE,
    word_count INTEGER DEFAULT 0,
    reading_time INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### 8.3 Event Schema
```json
{
  "channel": "journal.entry.created",
  "data": {
    "entry_id": "uuid",
    "user_id": "uuid", 
    "content_preview": "First 200 characters...",
    "sentiment": "positive|negative|neutral",
    "themes": ["theme1", "theme2"],
    "word_count": 150,
    "is_private": true,
    "created_at": "2024-01-01T12:00:00Z"
  },
  "user_id": "uuid",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

---

## 9. Security & Privacy Considerations

### 9.1 Data Privacy
- **Private by default**: All journal entries default to private
- **User control**: Users explicitly choose to make entries public
- **Access control**: Strict user-based access restrictions
- **Data encryption**: Consider encrypting journal content at rest

### 9.2 API Security
- **Authentication required**: All endpoints require valid JWT
- **User isolation**: Users can only access their own entries
- **Rate limiting**: Prevent journal spam/abuse
- **Input validation**: Sanitize all journal content

---

## 10. Monitoring & Analytics

### 10.1 Business Metrics
- **Journal entries created** per day/week/month
- **User engagement** with journaling feature
- **Average entry length** and writing patterns
- **Sentiment distribution** across entries

### 10.2 Technical Metrics
- **API response times** for journal operations
- **Database performance** for journal queries
- **Event processing** latency for journal events
- **Error rates** for journal operations

---

## Conclusion

The MantraPath journal system has a **complete frontend implementation** ready for production use, but requires **backend implementation** to enable full functionality. The architecture is well-designed with proper separation of concerns, event-driven integration, and comprehensive chatbot context integration planned.

**Immediate Priority**: Implement the backend journal CRUD operations to enable the complete journal workflow and unlock the sophisticated frontend capabilities that are already built and ready to use.

The chatbot integration architecture is designed to provide **context-aware responses** based on journal content, sentiment patterns, and writing frequency, making it a truly personalized wellness companion that understands the user's journaling journey.