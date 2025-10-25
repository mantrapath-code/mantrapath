# Mood Service Migration Guide

## 🚨 Breaking Changes

This guide documents the migration from the old slider-based mood tracking system to the new AI-powered emotion detection system.

## 📋 Overview of Changes

### ❌ Removed Features
- **Manual sliders** for mood_score, stress_level, energy_level
- **Manual score input** - users can no longer manually set scores
- **Journal routes** - journal functionality moved to separate service
- **Legacy mood entry endpoints** - old API endpoints removed

### ✅ New Features
- **AI-powered emotion detection** from text and voice input
- **Automatic score inference** using AI algorithms
- **Voice input support** with Speech-to-Text integration
- **Real-time event publishing** to other services
- **Enhanced emotion analysis** with confidence scores and reasoning

## 🔄 API Changes

### Old API (Deprecated)

```json
POST /api/v1/mood/entries
{
  "mood_score": 8,
  "stress_level": 3,
  "energy_level": 7,
  "description": "Feeling great!",
  "tags": ["work", "weekend"]
}
```

### New API (Current)

```json
POST /api/v1/mood/entries
{
  "input_text": "I am feeling absolutely fantastic and ready to take on the world!",
  "input_type": "text",
  "context_tags": ["work", "weekend"],
  "location": "office",
  "activity": "planning"
}
```

**Note:** Fields are sent directly (no `mood_data` wrapper). The `mood_score`, `stress_level`, and `energy_level` are automatically inferred by AI from the `input_text` and optional `audio_emotion_data`.

## 🗄️ Database Schema Changes

### New Columns Added

```sql
-- AI-powered input fields
ALTER TABLE mood_entries ADD COLUMN input_text TEXT NOT NULL;
ALTER TABLE mood_entries ADD COLUMN input_type VARCHAR(10) DEFAULT 'text';
ALTER TABLE mood_entries ADD COLUMN language VARCHAR(10) DEFAULT 'en';

-- AI analysis results
ALTER TABLE mood_entries ADD COLUMN text_emotion_analysis JSONB;
ALTER TABLE mood_entries ADD COLUMN voice_emotion_analysis JSONB;
ALTER TABLE mood_entries ADD COLUMN combined_emotion_confidence FLOAT;
ALTER TABLE mood_entries ADD COLUMN ai_inferred_scores JSONB;
```

### Column Changes

- `mood_score`, `stress_level`, `energy_level` are now **AI-inferred** (not manual)
- `description` field is now populated from `input_text`
- `tags` field renamed to `context_tags` and changed to array format

## 🔧 Frontend Migration

### Component Changes

#### Old MoodEntryComponent
```typescript
// OLD: Manual sliders
<Slider value={[moodData.mood_score]} onValueChange={...} />
<Slider value={[moodData.stress_level]} onValueChange={...} />
<Slider value={[moodData.energy_level]} onValueChange={...} />
```

#### New MoodEntryComponent
```typescript
// NEW: AI-powered text/voice input
<Textarea 
  value={moodData.input_text}
  onChange={(e) => setMoodData(prev => ({ ...prev, input_text: e.target.value }))}
  placeholder="Describe your current mood, thoughts, and feelings..."
/>

// Voice recording
<Button onClick={isRecording ? stopRecording : startRecording}>
  {isRecording ? <MicOff /> : <Mic />}
</Button>
```

### API Client Changes

#### Old moodService
```typescript
// OLD: Manual scores
async createMoodEntry(moodData: {
  mood_score: number;
  stress_level: number;
  energy_level: number;
  description?: string;
  tags?: string[];
}): Promise<MoodEntry>
```

#### New moodService
```typescript
// NEW: AI-powered input
async createMoodEntry(moodData: {
  input_text: string;
  input_type: 'text' | 'voice';
  audio_emotion_data?: any;
  context_tags?: string[];
  location?: string;
  activity?: string;
}): Promise<MoodEntry>

// NEW: Voice input
async createMoodEntryFromVoice(
  audioFile: File,
  language?: string,
  contextTags?: string[]
): Promise<MoodEntry>
```

## 📊 Data Migration

### Existing Mood Entries

If you have existing mood entries with manual scores, you can:

1. **Keep existing data** - old entries remain unchanged
2. **Migrate to new format** - run migration script to convert old entries
3. **Hybrid approach** - support both old and new formats temporarily

### Migration Script Example

```python
# migrate_old_entries.py
def migrate_old_mood_entries():
    """Migrate old mood entries to new AI-powered format"""
    
    old_entries = db.query(OldMoodEntry).all()
    
    for entry in old_entries:
        # Convert old format to new format
        new_entry = MoodEntry(
            user_id=entry.user_id,
            input_text=entry.description or f"Mood score: {entry.mood_score}",
            input_type="text",
            mood_score=entry.mood_score,  # Keep original scores
            stress_level=entry.stress_level,
            energy_level=entry.energy_level,
            # Mark as migrated
            ai_inferred_scores={
                "migrated": True,
                "original_scores": True,
                "reasoning": "Migrated from old slider-based system"
            }
        )
        db.add(new_entry)
    
    db.commit()
```

## 🔄 Service Integration Changes

### Event Publishing

#### Old System
- No automatic event publishing
- Manual context sharing required

#### New System
- Automatic NATS event publishing
- Real-time context sharing with ai-context-store
- Memory service integration

### Emotion Analysis

#### Old System
- Basic sentiment analysis only
- No emotion detection

#### New System
- Advanced emotion detection via AI Event Processor
- Voice tone emotion analysis
- Combined text + voice analysis
- Cultural intelligence support

## 🚀 Migration Steps

### 1. Backend Migration

```bash
# 1. Update database schema
docker-compose exec postgres psql -U mantrapath -d mantrapath -c "
ALTER TABLE mood_entries 
ADD COLUMN IF NOT EXISTS input_text TEXT,
ADD COLUMN IF NOT EXISTS input_type VARCHAR(10) DEFAULT 'text',
ADD COLUMN IF NOT EXISTS text_emotion_analysis JSONB,
ADD COLUMN IF NOT EXISTS voice_emotion_analysis JSONB,
ADD COLUMN IF NOT EXISTS combined_emotion_confidence FLOAT,
ADD COLUMN IF NOT EXISTS ai_inferred_scores JSONB;
"

# 2. Deploy new mood service
docker-compose build mood-service
docker-compose up -d mood-service

# 3. Verify service health
curl http://localhost:8003/api/v1/health
```

### 2. Frontend Migration

```bash
# 1. Update mood service API client
# Replace old createMoodEntry with new AI-powered version

# 2. Update MoodEntryComponent
# Remove sliders, add text/voice input

# 3. Test new UI
npm run dev
# Test both text and voice input
```

### 3. Data Migration (Optional)

```bash
# Run migration script if needed
python migrate_old_entries.py
```

## ⚠️ Breaking Changes Summary

| Component | Old | New | Impact |
|-----------|-----|-----|--------|
| **API Request** | Manual scores in request | AI-inferred scores in response | High |
| **Frontend UI** | Sliders for scores | Text/voice input | High |
| **Database** | Manual score columns | AI analysis columns | Medium |
| **Event Publishing** | None | Automatic NATS events | Medium |
| **Emotion Analysis** | Basic sentiment | Advanced AI emotions | High |

## 🔍 Testing Migration

### 1. Test New API

```bash
# Test text input
curl -X POST http://localhost:8003/api/v1/mood/entries \
  -H "Content-Type: application/json" \
  -d '{
    "mood_data": {
      "input_text": "I am feeling great today!",
      "input_type": "text",
      "context_tags": ["test"]
    }
  }'

# Test voice input
curl -X POST http://localhost:8003/api/v1/mood/entries/voice \
  -F "audio=@test.wav" \
  -F "language=en"
```

### 2. Test Frontend

```bash
# Start frontend
npm run dev

# Test text input
# 1. Enter mood description
# 2. Submit form
# 3. Verify AI scores are displayed

# Test voice input
# 1. Click voice recording button
# 2. Record audio
# 3. Submit
# 4. Verify voice analysis results
```

### 3. Test Event Publishing

```bash
# Check if events are published
docker-compose logs mood-service | grep "Published mood event"

# Check ai-context-store receives events
docker-compose logs ai-context-store | grep "mood"
```

## 🆘 Rollback Plan

If migration issues occur:

### 1. Rollback Backend

```bash
# Revert to old mood service version
git checkout previous-version
docker-compose build mood-service
docker-compose up -d mood-service
```

### 2. Rollback Frontend

```bash
# Revert to old frontend version
git checkout previous-version
npm install
npm run dev
```

### 3. Database Rollback

```bash
# Remove new columns if needed
docker-compose exec postgres psql -U mantrapath -d mantrapath -c "
ALTER TABLE mood_entries 
DROP COLUMN IF EXISTS input_text,
DROP COLUMN IF EXISTS input_type,
DROP COLUMN IF EXISTS text_emotion_analysis,
DROP COLUMN IF EXISTS voice_emotion_analysis,
DROP COLUMN IF EXISTS combined_emotion_confidence,
DROP COLUMN IF EXISTS ai_inferred_scores;
"
```

## 📞 Support

For migration support:

1. **Check logs**: `docker-compose logs mood-service`
2. **Verify health**: `curl http://localhost:8003/api/v1/health`
3. **Test API**: Use provided curl examples
4. **Check events**: Verify NATS event publishing
5. **Contact team**: Create GitHub issue with migration details

## 📚 Additional Resources

- [API Documentation](./README.md#api-endpoints)
- [Architecture Overview](./README.md#architecture)
- [Configuration Guide](./README.md#configuration)
- [Troubleshooting Guide](./README.md#troubleshooting)

---

**Migration completed successfully!** 🎉

The mood service now uses AI-powered emotion detection instead of manual sliders, providing more accurate and intelligent mood tracking.

