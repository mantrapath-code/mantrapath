# MantraPath Mood Service Documentation

This directory contains comprehensive documentation for the MantraPath mood service - a FastAPI-based microservice that handles mood tracking, journaling, analytics, and ML-powered insights.

## 🏗️ Current Architecture

### System Overview
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │  Mood Service   │    │   ML Service    │
│  (React/TS)     │◄──►│   (FastAPI)     │◄──►│   (FastAPI)     │
│  Port: 3000     │    │  Port: 8003     │    │  Port: 8004     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 ▼
                    ┌─────────────────┐
                    │   Database      │
                    │   (SQLite)      │
                    │   Shared Models │
                    └─────────────────┘
```

### 🔧 Backend Service (`/backend/services/mood_service/`)

**Technology Stack:**
- **Framework**: FastAPI 
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: JWT-based auth via shared auth module
- **NLP**: TextBlob for sentiment analysis
- **Port**: 8003

**Core Features:**
- Mood entry tracking (1-5 scale)
- Journal entry management with sentiment analysis  
- Analytics and pattern recognition
- User data export/deletion (GDPR compliance)
- Integration with ML service for intelligent insights

### 🎨 Frontend Components (`/frontend/src/components/`)

**Key Components:**
- `MoodTracker.tsx` - Main mood logging interface
- `MoodInsights.tsx` - Analytics and pattern visualization
- `WellnessDashboard.tsx` - Overall wellness overview
- `EnhancedMoodChart.tsx` - Data visualization
- `WeeklyMoodReport.tsx` - Weekly analysis reports
- `MoodPatternNotifications.tsx` - Smart notifications

## 📊 Current Data Models

### MoodEntry Schema
```python
class MoodEntry(Base):
    id: String (UUID)
    user_id: String (Foreign Key)
    mood_score: Integer (1-5 scale)  # 1=very-low, 5=excellent
    energy_level: Integer (1-5 scale)
    stress_level: Integer (1-5 scale) 
    sleep_quality: Integer (1-5 scale)
    notes: Text (optional)
    context_tags: JSON (array of strings)
    created_at: DateTime
    updated_at: DateTime
```

### JournalEntry Schema
```python
class JournalEntry(Base):
    id: String (UUID)
    user_id: String (Foreign Key)
    title: String (optional)
    content: Text (required)
    mood_before: Integer (1-5 scale)
    mood_after: Integer (1-5 scale)
    sentiment_score: Float (-1 to 1)
    sentiment_label: String (positive/negative/neutral)
    themes: JSON (extracted themes array)
    is_private: Boolean (default: True)
    word_count: Integer
    reading_time: Integer (seconds)
    created_at: DateTime
    updated_at: DateTime
```

## 🔌 API Endpoints

### Mood Tracking
- `GET /api/v1/mood/` - Retrieve user's mood entries
- `POST /api/v1/mood/` - Create new mood entry

### Journal Management  
- `GET /api/v1/journal/` - Get journal entries
- `POST /api/v1/journal/` - Create journal entry with sentiment analysis

### Analytics & Insights
- `GET /api/v1/analytics/overview` - Comprehensive analytics overview
- `GET /api/v1/analytics/patterns/weekly` - Weekly pattern analysis
- `GET /api/v1/analytics/personalized-insights` - AI-generated insights
- `GET /api/v1/analytics/optimal-notification-times` - ML-powered timing

### User Data Management
- `DELETE /api/v1/user/{user_id}/delete` - GDPR data deletion
- `GET /api/v1/user/{user_id}/export` - Data export

### Health Check
- `GET /health` - Service health status

## 🤖 ML Integration

### Current ML Capabilities
The mood service integrates with the ML service (`/backend/services/ml_service/`) for:

**Pattern Analysis:**
- `MoodPatternAnalyzer` - Identifies temporal and behavioral patterns
- `OptimalTimingPredictor` - Predicts best notification times
- `EffectivenessTracker` - Measures intervention success

**Crisis Prevention:**
- `CrisisPredictionSystem` - Early warning for mental health risks
- `EarlyWarningSystem` - Real-time monitoring and alerts
- Crisis Dashboard API for monitoring metrics

**Content Intelligence:**
- `NotificationContentEngine` - Personalized notification content
- Sentiment analysis via TextBlob (plans to upgrade to Transformers)

## 🎯 Frontend Features

### Mood Tracking Interface
```typescript
// Mood options with emoji-like interface
const moodOptions = [
  { value: 'excellent', icon: Heart, label: 'Excellent', color: 'text-green-500' },
  { value: 'good', icon: Smiley, label: 'Good', color: 'text-blue-500' },
  { value: 'neutral', icon: SmileyMeh, label: 'Neutral', color: 'text-yellow-500' },
  { value: 'low', icon: SmileySad, label: 'Low', color: 'text-orange-500' },
  { value: 'very-low', icon: X, label: 'Very Low', color: 'text-red-500' }
]
```

### Analytics Features
- **Weekly Pattern Recognition** - Identifies day-of-week trends
- **Mood Correlations** - Links mood with activities, sleep, etc.
- **Streak Tracking** - Monitors consecutive logging days
- **Trend Analysis** - Improving/declining/stable mood trends
- **Personalized Insights** - AI-generated recommendations

### Smart Notifications
- **Optimal Timing** - ML-predicted best notification times
- **Content Personalization** - Tailored message content
- **Pattern-Based Triggers** - Notifications based on detected patterns
- **Crisis Intervention** - Immediate support when risk detected

## 📈 Current Analytics Capabilities

### Overview Analytics
```python
class AnalyticsResponse(BaseModel):
    average_mood: float
    mood_trend: str  # "improving", "declining", "stable"
    total_entries: int
    streak: int  # consecutive days logged
    weekly_pattern: dict  # mood by day of week
    monthly_summary: dict
```

### Pattern Recognition
- **Circadian Patterns** - Time-of-day mood variations
- **Weekly Patterns** - Weekday vs weekend differences  
- **Activity Correlations** - Mood impact of different activities
- **Sequential Patterns** - Mood transition patterns
- **Anomaly Detection** - Unusual mood patterns

### Insights Generation
- **Trend Analysis** - Compare current week vs previous weeks
- **Optimal Times** - Best times for interventions
- **Risk Assessment** - Mental health risk indicators
- **Recommendations** - Personalized action suggestions

## 🔍 Document Breakdown

### 📊 [01. Current State Analysis](./01-current-state-analysis.md)
**Purpose**: Deep dive into the existing implementation
**Analysis Covers**:
- Code review of mood service backend (`main.py`, 809 lines)
- Frontend component analysis (`MoodTracker.tsx`, `MoodInsights.tsx`)
- Database schema limitations and technical debt
- Integration gaps and performance issues

**Key Findings**:
- Basic 1-5 scale mood tracking is functional but limited
- TextBlob sentiment analysis is outdated
- Good foundation for ML integration but needs enhancement
- GDPR compliance implemented but could be improved

### 🚀 [02. Improvement Plan](./02-improvement-plan.md)  
**Purpose**: Roadmap for enhancing the mood service
**Proposed Enhancements**:
- Multi-dimensional emotion model (Russell's Circumplex + PANAS)
- Advanced NLP with transformer models
- Real-time pattern recognition
- Cross-service intelligence coordination
- Enhanced UI with scientific emotion capture

**Timeline**: 16-week phased implementation
**Expected Impact**: 40%+ user engagement increase

### 🤖 [03. ML Integration Strategy](./03-ml-integration-strategy.md)
**Purpose**: Advanced ML capabilities integration plan
**Current Integration**: 
- Basic pattern analysis via ML service
- Notification timing optimization
- Crisis prediction framework (Phase 2A)

**Proposed Enhancements**:
- Unified data pipeline across all services
- Real-time emotional intelligence processing
- Multi-modal emotion recognition (text, voice, behavior)
- Predictive mood forecasting

### 🔄 [04. Migration Plan](./04-migration-plan.md)
**Purpose**: Safe transition strategy for enhancements
**Migration Strategy**:
- Zero-downtime migration approach
- Data preservation and enhancement
- Gradual feature rollout with A/B testing
- Comprehensive rollback procedures

**Risk Mitigation**: Multiple backup layers, user communication plan

### 🛠️ [05. Technical Specifications](./05-technical-specifications.md)
**Purpose**: Detailed implementation specifications
**Technical Details**:
- Enhanced database schema designs
- New API endpoint specifications
- ML model architectures (Multi-modal emotion classifier)
- Performance optimization strategies

## 🎯 Quick Start Guide

### For Developers
1. **Backend Setup**: 
   ```bash
   cd backend/services/mood_service
   pip install -r requirements.txt
   uvicorn main:app --port 8003 --reload
   ```

2. **Frontend Development**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. **Key Files to Understand**:
   - `backend/services/mood_service/main.py` - Main service implementation
   - `frontend/src/hooks/useMoods.ts` - Frontend data management
   - `frontend/src/components/MoodTracker.tsx` - UI component

### For Product Managers
1. Review current features in [Current State Analysis](./01-current-state-analysis.md)
2. Understand enhancement roadmap in [Improvement Plan](./02-improvement-plan.md)
3. Check user impact metrics and business value propositions

### For Data Scientists
1. Examine ML integration in [ML Integration Strategy](./03-ml-integration-strategy.md)
2. Review current analytics in `backend/services/mood_service/main.py` (lines 245-703)
3. Understand model architectures in [Technical Specifications](./05-technical-specifications.md)

### For QA/Testing
1. API endpoints testing guide in main service file
2. Frontend component testing in React components
3. Integration testing with ML service endpoints

## 🔧 Development Status

### Current State (July 2025)
- ✅ **Basic mood tracking** - Functional 1-5 scale system
- ✅ **Journal integration** - With sentiment analysis
- ✅ **Analytics dashboard** - Weekly patterns and insights  
- ✅ **ML service integration** - Pattern analysis and notifications
- ✅ **GDPR compliance** - Data export and deletion
- ⚠️ **Limited emotion model** - Simple numeric scale
- ⚠️ **Basic NLP** - TextBlob needs upgrade
- ❌ **Advanced personalization** - Limited user-specific insights

### Planned Enhancements
- 🎯 **Multi-dimensional emotion capture** - Scientific models
- 🤖 **Advanced ML models** - Transformer-based NLP
- 📱 **Real-time processing** - Stream processing architecture
- 🔗 **Cross-service intelligence** - Unified platform insights
- 📊 **Predictive analytics** - Mood forecasting capabilities

## 📱 User Experience Flow

### Current Mood Logging Flow
1. **Entry Point**: User clicks mood tracking in dashboard
2. **Mood Selection**: Choose from 5 emoji-based options (excellent → very-low)
3. **Context Capture**: Optional notes, triggers, energy/stress levels
4. **Instant Feedback**: Immediate confirmation and basic insights
5. **Historical View**: View past entries and patterns in analytics

### Analytics & Insights Flow
1. **Dashboard Overview**: Average mood, streak, trend indicator
2. **Pattern Recognition**: Weekly patterns, time-of-day trends
3. **Personalized Insights**: AI-generated recommendations
4. **Weekly Reports**: Comprehensive analysis with improvement suggestions
5. **Crisis Support**: Automatic detection and resource provision

## 🔬 Technical Deep Dive

### Backend Architecture (`main.py` - 809 lines)
```python
# Key Classes & Endpoints:
class MoodEntryCreate(BaseModel):          # Lines 45-52
class JournalEntryCreate(BaseModel):       # Lines 64-69
@app.get("/api/v1/mood/")                  # Lines 93-118
@app.post("/api/v1/mood/")                 # Lines 119-152
@app.get("/api/v1/analytics/overview")     # Lines 245-326
@app.get("/api/v1/analytics/personalized-insights")  # Lines 379-564
```

### Frontend Hook System (`useMoods.ts`)
```typescript
// Core mood management hook
export function useMoods() {
  // Handles state management, API calls, data transformation
  // Converts between frontend mood strings and backend numbers
  // Provides optimistic updates and error handling
}
```

### ML Service Integration
```python
# Current ML Models:
- MoodPatternAnalyzer: Temporal pattern recognition
- OptimalTimingPredictor: Notification timing
- CrisisPredictionSystem: Mental health risk assessment
- NotificationContentEngine: Personalized messaging
```

## 🚨 Known Limitations & Technical Debt

### Current Issues
1. **Simple Emotion Model**: 1-5 scale lacks emotional nuance
2. **TextBlob Dependency**: Outdated NLP library
3. **Limited Context**: Basic tags don't capture rich context
4. **Sync Processing**: No real-time stream processing
5. **Basic Personalization**: Generic insights vs. truly personalized

### Performance Considerations
- Database queries not optimized for large datasets
- No caching layer for analytics
- Real-time analytics calculated on each request
- Missing background processing for complex analysis

### Security & Privacy
- Basic JWT authentication
- GDPR compliance implemented but minimal
- No data anonymization for research
- Missing audit logs for sensitive operations

## 📞 Support & Contributing

### Getting Help
- **Technical Issues**: Check [Technical Specifications](./05-technical-specifications.md)
- **API Questions**: Review endpoint documentation above
- **Frontend Questions**: Examine React component implementations
- **ML Integration**: See [ML Integration Strategy](./03-ml-integration-strategy.md)

### Development Workflow
1. **Local Setup**: Follow quick start guide above
2. **Testing**: Run `pytest` for backend, `npm test` for frontend
3. **API Testing**: Use `/health` endpoint to verify service status
4. **Integration Testing**: Ensure mood ↔ ML service communication

### Contributing Guidelines
1. Fork the repository
2. Review current implementation thoroughly
3. Follow enhancement plans in improvement documentation
4. Submit PRs with comprehensive testing and documentation
5. Ensure backward compatibility with existing data

---

**Last Updated**: July 31, 2025  
**Service Version**: 1.0.0  
**Mood Service Port**: 8003  
**ML Service Port**: 8004  
**Database**: SQLite with shared models  
**Documentation Status**: Reflects current implementation + enhancement roadmap
