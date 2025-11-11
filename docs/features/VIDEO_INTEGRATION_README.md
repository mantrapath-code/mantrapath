# Video Journal Integration Plan

## Executive Summary

This document outlines the complete plan for integrating video recording capabilities into the MantraPath journal feature. The implementation focuses on **client-side facial emotion detection** using face-api.js and **server-side speech-to-text** processing, while keeping emotion data **separate** (no fusion).

### Key Metrics
- **Development Time**: 7 hours
- **Services Modified**: 2 out of 8 (25%)
- **Services Reused**: 6 out of 8 (75%)
- **New Code Required**: ~800 lines (frontend + backend)
- **Complexity**: Low-Medium

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Face-API.js Response Format](#face-apijs-response-format)
3. [Frontend Changes](#frontend-changes)
4. [Backend Changes](#backend-changes)
5. [Database Schema Changes](#database-schema-changes)
6. [Service Flow Analysis](#service-flow-analysis)
7. [Data Structures](#data-structures)
8. [Implementation Steps](#implementation-steps)
9. [Testing Strategy](#testing-strategy)
10. [Future Enhancements](#future-enhancements)

---

## Architecture Overview

### Design Principles

1. **No Fusion**: Facial and text emotions stored separately
2. **Client-Side ML**: Face detection happens in browser (face-api.js)
3. **Maximum Reuse**: Leverage existing Voice Service and AI Event Processor
4. **Raw Data Preservation**: Store all 7 emotions per snapshot, not just dominant
5. **Minimal Backend Changes**: Only database schema + accept new fields

### High-Level Flow

```
User Records Video (30 seconds)
    ↓
┌─────────────────────────────────┐
│ FRONTEND (Browser)              │
│ - MediaRecorder (video+audio)   │
│ - face-api.js (every 500ms)     │
│   → 60 emotion snapshots        │
│ - Real-time display + timeline  │
└────────────┬────────────────────┘
             │
             ↓
┌─────────────────────────────────┐
│ BACKEND (Parallel Processing)   │
│                                  │
│ Path 1: Video → Voice Service   │
│         → Transcript             │
│                                  │
│ Path 2: Transcript → AI Proc    │
│         → Text Emotion           │
└────────────┬────────────────────┘
             │
             ↓
┌─────────────────────────────────┐
│ STORAGE                          │
│ - Journal Entry (Mood Service)   │
│   - content: transcript          │
│   - video_analysis: {            │
│       facial_emotions: [],       │
│       text_emotion: {}           │
│     }                            │
└──────────────────────────────────┘
```

---

## Face-API.js Response Format

### Complete Detection Object Structure

Face-api.js returns a rich object when detecting faces with expressions:

```javascript
const detection = await faceapi
  .detectSingleFace(videoElement, new faceapi.TinyFaceDetectorOptions())
  .withFaceLandmarks()
  .withFaceExpressions()

// Structure returned:
{
  detection: {
    _box: {
      _x: 145.23,
      _y: 78.45,
      _width: 210.67,
      _height: 245.89
    },
    _score: 0.9534,  // Face detection confidence
    _classScore: 0.9534
  },
  
  landmarks: {
    _positions: [
      {_x: 180.2, _y: 120.5},  // Point 0
      {_x: 182.1, _y: 125.3},  // Point 1
      // ... 68 facial landmark points total
    ],
    _shift: {_x: 0, _y: 0}
  },
  
  expressions: {
    neutral: 0.02145,
    happy: 0.85234,    // ← Highest score (dominant)
    sad: 0.05123,
    angry: 0.01234,
    fearful: 0.03456,
    disgusted: 0.01789,
    surprised: 0.02019
  }
}
```

### What We Capture Every 500ms

```javascript
const emotionSnapshot = {
  timestamp: 1.5,  // Seconds into recording
  expressions: {
    neutral: 0.02145,
    happy: 0.85234,
    sad: 0.05123,
    angry: 0.01234,
    fearful: 0.03456,
    disgusted: 0.01789,
    surprised: 0.02019
  },
  dominant: "happy",        // Calculated: max(expressions)
  confidence: 0.85234       // Score of dominant emotion
}
```

### Complete Recording Session Data

For a 30-second video:
- **Sample Rate**: Every 500ms
- **Total Snapshots**: 60
- **Array Size**: ~15KB (JSON)

```javascript
facial_emotions = [
  {timestamp: 0.0, expressions: {...}, dominant: "happy", confidence: 0.85},
  {timestamp: 0.5, expressions: {...}, dominant: "happy", confidence: 0.87},
  {timestamp: 1.0, expressions: {...}, dominant: "neutral", confidence: 0.62},
  {timestamp: 1.5, expressions: {...}, dominant: "sad", confidence: 0.71},
  // ... 56 more snapshots
]
```

---

## Frontend Changes

### File Structure

```
frontend/src/
├── components/
│   └── journal/
│       ├── VideoJournalEntry.tsx        (NEW - 500 lines)
│       ├── EmotionTimeline.tsx          (NEW - 100 lines)
│       ├── FaceOverlay.tsx              (NEW - 80 lines)
│       └── JournalPage.tsx              (MODIFY - add video tab)
├── utils/
│   └── emotionAnalysis.ts               (NEW - 50 lines)
└── types/
    └── journal.ts                       (MODIFY - add video types)
```

### Component 1: VideoJournalEntry.tsx

**Purpose**: Main video recording component with face detection

**Key Responsibilities**:
1. Camera access and video preview
2. MediaRecorder for video+audio capture
3. face-api.js integration (detect every 500ms)
4. Real-time emotion display
5. Timeline visualization
6. Backend communication (STT + emotion analysis)
7. Journal entry creation

**State Management**:
```typescript
const [isRecording, setIsRecording] = useState(false)
const [emotionSnapshots, setEmotionSnapshots] = useState<EmotionSnapshot[]>([])
const [currentEmotion, setCurrentEmotion] = useState<EmotionSnapshot | null>(null)
const [videoBlob, setVideoBlob] = useState<Blob | null>(null)
const [modelsLoaded, setModelsLoaded] = useState(false)
const [isProcessing, setIsProcessing] = useState(false)
const [recordingDuration, setRecordingDuration] = useState(0)
```

**Key Functions**:

1. **loadFaceApiModels()**
   - Load TinyFaceDetector, FaceExpressionNet, FaceLandmark68Net
   - Source: CDN or local `/public/models/`
   - One-time load, cached in memory

2. **startRecording()**
   - Request camera/mic permissions
   - Initialize MediaRecorder
   - Start emotion detection loop (setInterval 500ms)
   - Start duration timer

3. **detectEmotions()** (runs every 500ms)
   - Call face-api.js on video element
   - Extract expressions object
   - Calculate dominant emotion
   - Update state (live display)
   - Add to snapshots array

4. **stopRecording()**
   - Stop MediaRecorder
   - Stop emotion detection loop
   - Stop camera stream
   - Create video blob
   - Trigger processing

5. **processAndSave()**
   - Send video → Voice Service → get transcript
   - Send transcript → AI Event Processor → get text emotion
   - Calculate facial summary statistics
   - Create journal entry with all data
   - Success/error handling

**Real-Time Display Elements**:

1. **Live Emotion Text**
   ```tsx
   {currentEmotion && (
     <div className="live-emotion-display">
       <span className="emotion-label">
         {currentEmotion.dominant}
       </span>
       <span className="confidence">
         ({(currentEmotion.confidence * 100).toFixed(1)}%)
       </span>
     </div>
   )}
   ```

2. **Canvas Overlay**
   - Bounding box around detected face
   - 68 facial landmarks (optional)
   - Emotion label with confidence

3. **Timeline Bar**
   - Horizontal color-coded segments
   - Each segment = one snapshot
   - Color = dominant emotion
   - Opacity = confidence level

**Dependencies**:
- `face-api.js`: ^0.22.2
- Browser APIs: MediaRecorder, MediaStream, Canvas

**Estimated Lines**: 500

---

### Component 2: EmotionTimeline.tsx

**Purpose**: Visualize emotion changes over recording duration

**Props**:
```typescript
interface EmotionTimelineProps {
  snapshots: EmotionSnapshot[]
  height?: number
  showLabels?: boolean
  interactive?: boolean
}
```

**Rendering Logic**:
```typescript
// Each snapshot gets equal width
const segmentWidth = 100 / snapshots.length

// Color mapping
const emotionColors = {
  neutral: '#9CA3AF',   // Gray
  happy: '#10B981',     // Green
  sad: '#3B82F6',       // Blue
  angry: '#EF4444',     // Red
  fearful: '#8B5CF6',   // Purple
  disgusted: '#92400E', // Brown
  surprised: '#F59E0B'  // Orange
}

// Render segments
snapshots.map((snap, index) => (
  <div
    key={index}
    style={{
      width: `${segmentWidth}%`,
      backgroundColor: emotionColors[snap.dominant],
      opacity: snap.confidence,  // Fades based on confidence
      height: '40px'
    }}
    title={`${snap.dominant} (${(snap.confidence*100).toFixed(1)}%)`}
  />
))
```

**Features**:
- Tooltip on hover (timestamp + emotion + confidence)
- Click to seek video (if video playback implemented)
- Smooth transitions between segments
- Responsive design

**Estimated Lines**: 100

---

### Component 3: FaceOverlay.tsx

**Purpose**: Draw face detection visuals on canvas overlay

**Props**:
```typescript
interface FaceOverlayProps {
  videoRef: RefObject<HTMLVideoElement>
  canvasRef: RefObject<HTMLCanvasElement>
  detection: FaceAPIDetection | null
  currentEmotion: EmotionSnapshot | null
}
```

**Drawing Functions**:

1. **drawBoundingBox()**
   - Rectangle around face
   - Color based on detection confidence
   - Thickness: 2-4px

2. **drawLandmarks()** (optional)
   - 68 facial points
   - Small circles (3px radius)
   - Semi-transparent

3. **drawEmotionLabel()**
   - Text above bounding box
   - Emotion name + confidence %
   - Background rectangle for readability

**Canvas Setup**:
```typescript
// Match canvas size to video dimensions
useEffect(() => {
  if (videoRef.current && canvasRef.current) {
    const video = videoRef.current
    const canvas = canvasRef.current
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight
  }
}, [videoRef, canvasRef])
```

**Estimated Lines**: 80

---

### Component 4: Utility Functions

**File**: `frontend/src/utils/emotionAnalysis.ts`

**Functions**:

1. **getDominantEmotion(expressions)**
   ```typescript
   function getDominantEmotion(expressions: Record<string, number>): {
     emotion: string
     confidence: number
   } {
     let maxScore = 0
     let dominant = 'neutral'
     
     for (const [emotion, score] of Object.entries(expressions)) {
       if (score > maxScore) {
         maxScore = score
         dominant = emotion
       }
     }
     
     return { emotion: dominant, confidence: maxScore }
   }
   ```

2. **calculateFacialSummary(snapshots)**
   ```typescript
   function calculateFacialSummary(snapshots: EmotionSnapshot[]) {
     const counts: Record<string, number> = {}
     
     // Count dominant emotions
     snapshots.forEach(snap => {
       counts[snap.dominant] = (counts[snap.dominant] || 0) + 1
     })
     
     // Calculate percentages
     const total = snapshots.length
     const distribution: Record<string, string> = {}
     
     Object.keys(counts).forEach(emotion => {
       distribution[emotion] = ((counts[emotion] / total) * 100).toFixed(1)
     })
     
     // Find overall dominant
     const overallDominant = Object.keys(counts).reduce((a, b) =>
       counts[a] > counts[b] ? a : b
     )
     
     return {
       duration_seconds: snapshots[snapshots.length - 1]?.timestamp || 0,
       snapshots_count: total,
       dominant_emotion_overall: overallDominant,
       emotion_distribution: distribution
     }
   }
   ```

3. **getEmotionColor(emotion)**
   - Returns color code for emotion
   - Used by timeline and displays

**Estimated Lines**: 50

---

### Integration into Existing Journal Page

**File**: `frontend/src/pages/JournalPage.tsx` or similar

**Changes Required**:

```tsx
import { VideoJournalEntry } from '@/components/journal/VideoJournalEntry'

// Add tab for video
<Tabs defaultValue="text">
  <TabsList>
    <TabsTrigger value="text">📝 Write</TabsTrigger>
    <TabsTrigger value="video">🎥 Video</TabsTrigger>
  </TabsList>
  
  <TabsContent value="text">
    {/* Existing text journal entry form */}
  </TabsContent>
  
  <TabsContent value="video">
    <VideoJournalEntry 
      onSuccess={() => {
        // Refresh journal list
        // Show success message
      }}
    />
  </TabsContent>
</Tabs>
```

**Estimated Changes**: 20 lines

---

## Backend Changes

### Service-by-Service Analysis

#### 1. Voice Service (Port 8011)
**Status**: ✅ **NO CHANGES REQUIRED**

**Why**: Already accepts video files and extracts audio automatically via FFmpeg.

**Existing Endpoint**:
```
POST /api/v1/voice/stt

Input: 
- File upload (video.webm, video.mp4, audio.wav, etc.)
- FormData with 'audio_file' field

Process:
1. Receives file
2. FFmpeg detects format (video or audio)
3. If video: extracts audio track automatically
4. Runs Whisper STT on audio
5. Returns transcript

Output:
{
  "transcript": "Today was really hard...",
  "language": "en",
  "confidence": 0.89,
  "duration": 30.5
}
```

**Verification**: Already used by Chatbot Service for voice inputs. Confirmed working.

---

#### 2. AI Event Processor (Port 8XXX)
**Status**: ✅ **NO CHANGES REQUIRED**

**Why**: Existing emotion analysis endpoint works for any text source.

**Existing Endpoint**:
```
POST /api/v1/analyze/emotion

Input:
{
  "text": "Today was really hard. I lost my job...",
  "language": "en",
  "user_id": "user_123"
}

Process:
1. EmotionAnalyzer.analyze()
2. Language detection (if needed)
3. Models Service (Phi-4) or local DistilRoBERTa
4. Cultural adaptation
5. Return emotion analysis

Output:
{
  "emotion": "sadness",
  "confidence": 0.82,
  "emotions": {
    "sadness": 0.82,
    "fear": 0.65,
    "neutral": 0.25,
    "joy": 0.05
  },
  "cultural_context": null,
  "processing_time_ms": 124,
  "language": "en",
  "has_cultural_adaptation": false
}
```

**Verification**: Used by chatbot, journal, and mood services. Confirmed working.

---

#### 3. Models Service (Port 8080)
**Status**: ✅ **NO CHANGES REQUIRED**

**Why**: Called by AI Event Processor internally. No direct interaction needed.

---

#### 4. API Gateway (Port 8000)
**Status**: ✅ **NO CHANGES REQUIRED**

**Why**: Already routes `/api/v1/voice/*` and `/ai-events/*` requests.

---

#### 5. AI Context Store (Port 8XXX)
**Status**: ✅ **NO CHANGES REQUIRED**

**Why**: Stores journal context as-is. Video metadata is just additional JSON data.

---

#### 6. Mood Service (Port 8XXX)
**Status**: ⚠️ **MINOR CHANGES REQUIRED**

**Current Implementation**:
**File**: `backend/services/mood_service/src/api/journal_routes.py`

**Endpoint**: `POST /api/v1/journal/`

**Current Request Handling**:
```python
@router.post("/")
async def create_journal_entry_root(
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    body = await request.json()
    
    # Current: only these fields accepted
    journal_entry = JournalEntry(
        user_id=current_user['user_id'],
        title=body.get('title'),
        content=body.get('content', ''),
        mood_before=body.get('mood_before'),
        mood_after=body.get('mood_after'),
        is_private=body.get('is_private', True),
        created_at=datetime.utcnow()
    )
    
    db.add(journal_entry)
    db.commit()
    db.refresh(journal_entry)
    
    return journal_entry
```

**Required Changes**:

1. **Accept new fields**:
   ```python
   @router.post("/")
   async def create_journal_entry_root(
       request: Request,
       current_user: dict = Depends(get_current_user),
       db: Session = Depends(get_db)
   ):
       body = await request.json()
       
       journal_entry = JournalEntry(
           user_id=current_user['user_id'],
           title=body.get('title'),
           content=body.get('content', ''),
           mood_before=body.get('mood_before'),
           mood_after=body.get('mood_after'),
           is_private=body.get('is_private', True),
           entry_type=body.get('entry_type', 'text'),     # NEW
           video_analysis=body.get('video_analysis'),     # NEW
           created_at=datetime.utcnow()
       )
       
       db.add(journal_entry)
       db.commit()
       db.refresh(journal_entry)
       
       return journal_entry
   ```

**Lines Changed**: 2 lines added (entry_type, video_analysis)

**Estimated Effort**: 30 minutes (including testing)

---

## Database Schema Changes

### Current Schema

**Table**: `journal_entries`

**Existing Columns**:
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
    themes JSONB,
    is_private BOOLEAN DEFAULT true,
    word_count INTEGER DEFAULT 0,
    reading_time INTEGER DEFAULT 0,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### Required Changes

**Migration File**: `backend/database/migrations/XXX_add_video_journal_support.sql`

```sql
-- Add entry_type column
ALTER TABLE journal_entries 
ADD COLUMN entry_type VARCHAR(20) DEFAULT 'text';

COMMENT ON COLUMN journal_entries.entry_type IS 
'Type of journal entry: "text" or "video"';

-- Add video_analysis column
ALTER TABLE journal_entries 
ADD COLUMN video_analysis JSONB DEFAULT NULL;

COMMENT ON COLUMN journal_entries.video_analysis IS 
'Contains facial emotions array, text emotion, and metadata for video journals';

-- Add index for faster queries on video journals
CREATE INDEX idx_journal_entries_entry_type 
ON journal_entries(entry_type);
```

### Updated Schema

**After Migration**:
```sql
CREATE TABLE journal_entries (
    -- Existing columns
    id VARCHAR PRIMARY KEY,
    user_id VARCHAR NOT NULL,
    title VARCHAR,
    content TEXT NOT NULL,
    mood_before INTEGER,
    mood_after INTEGER,
    sentiment_score FLOAT,
    sentiment_label VARCHAR,
    themes JSONB,
    is_private BOOLEAN DEFAULT true,
    word_count INTEGER DEFAULT 0,
    reading_time INTEGER DEFAULT 0,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    
    -- NEW columns
    entry_type VARCHAR(20) DEFAULT 'text',
    video_analysis JSONB DEFAULT NULL
);
```

### Model Update

**File**: `backend/shared/models.py`

**Current Model**:
```python
class JournalEntry(Base):
    __tablename__ = "journal_entries"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    title = Column(String)
    content = Column(Text, nullable=False)
    mood_before = Column(Integer)
    mood_after = Column(Integer)
    sentiment_score = Column(Float)
    sentiment_label = Column(String)
    themes = Column(JSON, default=list)
    is_private = Column(Boolean, default=True)
    word_count = Column(Integer, default=0)
    reading_time = Column(Integer, default=0)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
    
    user = relationship("User", back_populates="journal_entries")
```

**Required Changes**:
```python
class JournalEntry(Base):
    __tablename__ = "journal_entries"
    
    # ... existing columns ...
    
    # NEW columns
    entry_type = Column(String, default="text")
    video_analysis = Column(JSON, default=None)
    
    user = relationship("User", back_populates="journal_entries")
```

**Lines Added**: 2

**Estimated Effort**: 30 minutes (migration creation + testing)

---

## Service Flow Analysis

### Detailed Flow Diagram

```
┌────────────────────────────────────────────────────────────────┐
│                      USER ACTION                                │
│  User opens journal page → clicks "Video" tab                   │
│  → clicks "Start Recording"                                     │
└──────────────────────────┬─────────────────────────────────────┘
                           │
                           ↓
┌────────────────────────────────────────────────────────────────┐
│                FRONTEND: VideoJournalEntry.tsx                  │
│                                                                 │
│ Step 1: Initialize (on component mount)                        │
│ ──────────────────────────────────────────────────────────────│
│ ✓ Load face-api.js models (TinyFaceDetector, FaceExpression)  │
│ ✓ Request camera/microphone permissions                       │
│ ✓ Display video preview                                       │
│                                                                 │
│ Step 2: Recording Started                                      │
│ ──────────────────────────────────────────────────────────────│
│ ✓ MediaRecorder.start()                                       │
│   - Records video stream (VP9 codec)                          │
│   - Records audio stream (Opus codec)                         │
│   - Container: WebM                                            │
│                                                                 │
│ ✓ Start emotion detection loop (setInterval 500ms)            │
│   - Every 500ms:                                               │
│     1. Call faceapi.detectSingleFace()                        │
│     2. Extract expressions object                              │
│     3. Calculate dominant emotion                              │
│     4. Add to snapshots array                                  │
│     5. Update live display                                     │
│     6. Draw on canvas overlay                                  │
│                                                                 │
│ Step 3: Real-Time Display Updates                             │
│ ──────────────────────────────────────────────────────────────│
│ ✓ Live Emotion Text: "happy (85.2%)"                          │
│ ✓ Canvas Overlay: Bounding box + landmarks                    │
│ ✓ Timeline Bar: Color segments updating                       │
│ ✓ Recording Timer: "00:15 / 02:00"                            │
│                                                                 │
│ Step 4: Recording Stopped (user clicks "Stop")                │
│ ──────────────────────────────────────────────────────────────│
│ ✓ mediaRecorder.stop()                                        │
│ ✓ Stop emotion detection loop                                 │
│ ✓ Stop camera stream                                          │
│ ✓ Create video blob from chunks                               │
│                                                                 │
│ Data Collected:                                                 │
│ • videoBlob: Blob (WebM, ~5-10MB for 30s)                    │
│ • emotionSnapshots: Array[60] (~15KB JSON)                    │
│   [                                                             │
│     {timestamp: 0.0, expressions: {...}, dominant: "sad"},    │
│     {timestamp: 0.5, expressions: {...}, dominant: "sad"},    │
│     ...                                                         │
│   ]                                                             │
└──────────────────────────┬─────────────────────────────────────┘
                           │
                           ↓
┌────────────────────────────────────────────────────────────────┐
│           BACKEND PROCESSING (Parallel Paths)                   │
└────────────────────────────────────────────────────────────────┘
                           │
            ┌──────────────┴───────────────┐
            │                              │
            ↓                              ↓
┌─────────────────────┐        ┌──────────────────────┐
│   PATH 1: STT       │        │ PATH 2: Text Emotion │
│   (Voice Service)   │        │ (AI Event Processor) │
└─────────────────────┘        └──────────────────────┘
            │                              │
            │                              │
┌────────────────────────────────────────────────────────────────┐
│ PATH 1: Speech-to-Text                                         │
│ ──────────────────────────────────────────────────────────────│
│                                                                 │
│ Frontend → API Gateway → Voice Service                         │
│                                                                 │
│ Request:                                                        │
│ ────────                                                        │
│ POST http://api-gateway:8000/api/v1/voice/stt                 │
│ Content-Type: multipart/form-data                             │
│                                                                 │
│ Body (FormData):                                               │
│ ┌───────────────────────────────┐                             │
│ │ audio_file: video.webm        │                             │
│ │ (5-10MB binary data)          │                             │
│ └───────────────────────────────┘                             │
│                                                                 │
│ Voice Service Processing:                                      │
│ ─────────────────────────                                     │
│ 1. Receives video file                                        │
│ 2. FFmpeg detects format: "video/webm"                       │
│ 3. FFmpeg extracts audio track:                               │
│    Command: ffmpeg -i video.webm -vn -acodec pcm_s16le       │
│             -ar 16000 audio.wav                                │
│ 4. Load Whisper model (if not cached)                        │
│ 5. Run STT: whisper.transcribe(audio.wav)                    │
│ 6. Language detection (if auto)                               │
│ 7. Return result                                               │
│                                                                 │
│ Response:                                                       │
│ ─────────                                                       │
│ Status: 200 OK                                                 │
│ {                                                               │
│   "transcript": "Today was really hard. I lost my job and     │
│                  I'm worried about the future. But I'm        │
│                  trying to stay hopeful.",                     │
│   "language": "en",                                            │
│   "confidence": 0.89,                                          │
│   "duration": 30.5,                                            │
│   "segments": [                                                │
│     {                                                           │
│       "start": 0.0,                                            │
│       "end": 5.2,                                              │
│       "text": "Today was really hard."                        │
│     },                                                          │
│     {                                                           │
│       "start": 5.5,                                            │
│       "end": 12.8,                                             │
│       "text": "I lost my job and I'm worried about the        │
│                future."                                        │
│     },                                                          │
│     {                                                           │
│       "start": 13.2,                                           │
│       "end": 16.5,                                             │
│       "text": "But I'm trying to stay hopeful."              │
│     }                                                           │
│   ]                                                             │
│ }                                                               │
│                                                                 │
│ Processing Time: ~2-5 seconds for 30s video                   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ↓
┌────────────────────────────────────────────────────────────────┐
│ PATH 2: Text Emotion Analysis                                  │
│ ──────────────────────────────────────────────────────────────│
│                                                                 │
│ Frontend → API Gateway → AI Event Processor                    │
│                                                                 │
│ Request:                                                        │
│ ────────                                                        │
│ POST http://api-gateway:8000/ai-events/api/v1/analyze/emotion │
│ Content-Type: application/json                                │
│                                                                 │
│ Body:                                                           │
│ {                                                               │
│   "text": "Today was really hard. I lost my job and I'm       │
│            worried about the future. But I'm trying to stay    │
│            hopeful.",                                          │
│   "language": "en",                                            │
│   "user_id": "user_123"                                        │
│ }                                                               │
│                                                                 │
│ AI Event Processor Processing:                                │
│ ───────────────────────────────                               │
│ 1. EmotionAnalyzer.analyze(text, language, user_id)          │
│                                                                 │
│ 2. Language Detection (if needed):                            │
│    - Uses langdetect library                                   │
│    - Validates against supported languages                     │
│    - Falls back to 'en' if unsupported                        │
│                                                                 │
│ 3. Emotion Analysis (tries Models Service first):            │
│    ┌────────────────────────────────────┐                     │
│    │ ModelsServiceClient                │                     │
│    │ POST models-service:8080/          │                     │
│    │      api/v1/nlp/sentiment          │                     │
│    │                                    │                     │
│    │ Models Service uses Phi-4:         │                     │
│    │ - Prompt engineering               │                     │
│    │ - "Analyze emotion: [text]"        │                     │
│    │ - Temperature: 0.3                 │                     │
│    │ - Returns: emotion + confidence    │                     │
│    └────────────────────────────────────┘                     │
│                                                                 │
│    If Models Service fails → Fallback:                        │
│    ┌────────────────────────────────────┐                     │
│    │ Local DistilRoBERTa model          │                     │
│    │ j-hartmann/emotion-english-        │                     │
│    │ distilroberta-base                 │                     │
│    │                                    │                     │
│    │ - Load model (if not cached)       │                     │
│    │ - Tokenize text                    │                     │
│    │ - Run inference                    │                     │
│    │ - Softmax → probabilities          │                     │
│    └────────────────────────────────────┘                     │
│                                                                 │
│ 4. Cultural Adaptation:                                        │
│    - Apply cultural interpretation (if non-English)            │
│    - Adjust confidence scores                                  │
│    - Add cultural context notes                                │
│                                                                 │
│ Response:                                                       │
│ ─────────                                                       │
│ Status: 200 OK                                                 │
│ {                                                               │
│   "emotion": "sadness",                                        │
│   "confidence": 0.82,                                          │
│   "emotions": {                                                │
│     "sadness": 0.82,                                           │
│     "fear": 0.65,                                              │
│     "neutral": 0.25,                                           │
│     "hope": 0.15,                                              │
│     "anger": 0.05,                                             │
│     "joy": 0.03,                                               │
│     "surprise": 0.02                                           │
│   },                                                            │
│   "cultural_context": null,                                    │
│   "processing_time_ms": 124,                                   │
│   "language": "en",                                            │
│   "has_cultural_adaptation": false,                            │
│   "analysis_metadata": {                                       │
│     "model_source": "models_service",                          │
│     "model_name": "phi-4"                                      │
│   }                                                             │
│ }                                                               │
│                                                                 │
│ Processing Time: ~100-200ms                                    │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ↓
┌────────────────────────────────────────────────────────────────┐
│         FRONTEND: Aggregate and Prepare Data                    │
│                                                                 │
│ Function: calculateFacialSummary(emotionSnapshots)            │
│ ────────────────────────────────────────────────────────────  │
│                                                                 │
│ Input: emotionSnapshots array (60 items)                       │
│                                                                 │
│ Processing:                                                     │
│ 1. Count dominant emotions:                                    │
│    counts = {                                                   │
│      sad: 42,      // 70% of snapshots                        │
│      neutral: 12,  // 20%                                      │
│      fearful: 5,   // 8.3%                                     │
│      happy: 1      // 1.7%                                     │
│    }                                                            │
│                                                                 │
│ 2. Calculate percentages:                                      │
│    distribution = {                                             │
│      sad: "70.0",                                              │
│      neutral: "20.0",                                          │
│      fearful: "8.3",                                           │
│      happy: "1.7"                                              │
│    }                                                            │
│                                                                 │
│ 3. Find overall dominant:                                      │
│    overallDominant = "sad" (highest count)                    │
│                                                                 │
│ Output:                                                         │
│ {                                                               │
│   duration_seconds: 30,                                        │
│   snapshots_count: 60,                                         │
│   dominant_emotion_overall: "sad",                            │
│   emotion_distribution: {                                      │
│     sad: "70.0",                                               │
│     neutral: "20.0",                                           │
│     fearful: "8.3",                                            │
│     happy: "1.7"                                               │
│   }                                                             │
│ }                                                               │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ↓
┌────────────────────────────────────────────────────────────────┐
│              SAVE JOURNAL ENTRY                                 │
│                                                                 │
│ Frontend → API Gateway → Mood Service                          │
│                                                                 │
│ Request:                                                        │
│ ────────                                                        │
│ POST http://api-gateway:8000/api/v1/journal/                  │
│ Content-Type: application/json                                │
│ Authorization: Bearer <jwt_token>                              │
│                                                                 │
│ Body:                                                           │
│ {                                                               │
│   "title": "Video Journal - Job Loss",                        │
│   "content": "Today was really hard. I lost my job and I'm    │
│               worried about the future. But I'm trying to      │
│               stay hopeful.",                                  │
│   "entry_type": "video",                                       │
│   "is_private": true,                                          │
│   "video_analysis": {                                          │
│     "facial_emotions": [                                       │
│       {                                                         │
│         "timestamp": 0.0,                                      │
│         "expressions": {                                       │
│           "neutral": 0.15, "happy": 0.05, "sad": 0.68,       │
│           "angry": 0.02, "fearful": 0.06,                    │
│           "disgusted": 0.01, "surprised": 0.03                │
│         },                                                      │
│         "dominant": "sad",                                     │
│         "confidence": 0.68                                     │
│       },                                                        │
│       ... (59 more snapshots)                                  │
│     ],                                                          │
│     "facial_summary": {                                        │
│       "duration_seconds": 30,                                  │
│       "snapshots_count": 60,                                   │
│       "dominant_emotion_overall": "sad",                      │
│       "emotion_distribution": {                                │
│         "sad": "70.0",                                         │
│         "neutral": "20.0",                                     │
│         "fearful": "8.3",                                      │
│         "happy": "1.7"                                         │
│       }                                                         │
│     },                                                          │
│     "text_emotion": {                                          │
│       "emotion": "sadness",                                    │
│       "confidence": 0.82,                                      │
│       "all_emotions": {                                        │
│         "sadness": 0.82, "fear": 0.65,                       │
│         "neutral": 0.25, "hope": 0.15,                       │
│         "anger": 0.05, "joy": 0.03, "surprise": 0.02         │
│       }                                                         │
│     },                                                          │
│     "stt_confidence": 0.89,                                    │
│     "language": "en",                                          │
│     "video_duration": 30,                                      │
│     "has_face_detected": true                                  │
│   }                                                             │
│ }                                                               │
│                                                                 │
│ Mood Service Processing:                                       │
│ ──────────────────────────                                    │
│ 1. Validate authentication                                     │
│ 2. Extract fields from request                                 │
│ 3. Create JournalEntry object:                                │
│    journal_entry = JournalEntry(                               │
│      user_id=current_user['user_id'],                         │
│      title=body.get('title'),                                  │
│      content=body.get('content'),                              │
│      entry_type=body.get('entry_type', 'text'),               │
│      video_analysis=body.get('video_analysis'),               │
│      sentiment_score=-0.65,  # From text emotion              │
│      sentiment_label="negative",                               │
│      themes=["job_loss", "worry", "hope"],  # NLP extracted   │
│      is_private=True,                                          │
│      created_at=datetime.utcnow()                              │
│    )                                                            │
│ 4. Save to database:                                           │
│    db.add(journal_entry)                                       │
│    db.commit()                                                 │
│    db.refresh(journal_entry)                                   │
│ 5. Publish event: 'journal.entry_created'                     │
│ 6. Return created entry                                        │
│                                                                 │
│ Response:                                                       │
│ ─────────                                                       │
│ Status: 201 Created                                            │
│ {                                                               │
│   "id": "journal_789",                                         │
│   "user_id": "user_123",                                       │
│   "title": "Video Journal - Job Loss",                        │
│   "content": "Today was really hard...",                      │
│   "entry_type": "video",                                       │
│   "sentiment_score": -0.65,                                    │
│   "sentiment_label": "negative",                               │
│   "themes": ["job_loss", "worry", "hope"],                    │
│   "video_analysis": { ... },                                   │
│   "created_at": "2024-10-16T14:30:00Z",                       │
│   "is_private": true                                           │
│ }                                                               │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ↓
┌────────────────────────────────────────────────────────────────┐
│              EVENT PUBLISHING & CONTEXT STORAGE                 │
│                                                                 │
│ Event Bus: 'journal.entry_created'                            │
│ ───────────────────────────────────                           │
│ {                                                               │
│   "event_type": "journal.entry_created",                      │
│   "user_id": "user_123",                                       │
│   "data": {                                                     │
│     "journal_id": "journal_789",                               │
│     "entry_type": "video",                                     │
│     "content": "Today was really hard...",                    │
│     "sentiment": "negative"                                    │
│   }                                                             │
│ }                                                               │
│                                                                 │
│ Subscribed: AI Event Processor                                │
│ ────────────────────────────────                              │
│ Handler: _handle_journal_event()                              │
│ 1. Extract journal data                                        │
│ 2. Analyze patterns                                            │
│ 3. Update AI Context Store                                     │
│ 4. Check for intervention needs                                │
│                                                                 │
│ AI Context Store Update:                                       │
│ ────────────────────────                                       │
│ Key: ai_context:user_123                                       │
│ {                                                               │
│   "user_id": "user_123",                                       │
│   "sources": {                                                  │
│     "journal": {                                               │
│       "analysis": {                                            │
│         "sentiment": "negative",                               │
│         "emotion": "sadness",                                  │
│         "confidence": 0.82,                                    │
│         "themes": ["job_loss", "worry", "hope"],              │
│         "modality": "video_journal",                           │
│         "facial_emotion_dominant": "sad",                     │
│         "text_emotion": "sadness",                            │
│         "emotions_agree": true  # Both sad                    │
│       },                                                        │
│       "timestamp": "2024-10-16T14:30:00Z",                    │
│       "last_updated": 1697467800                               │
│     },                                                          │
│     "mood": { ... },                                           │
│     "chat": { ... }                                            │
│   },                                                            │
│   "last_updated": "2024-10-16T14:30:00Z"                      │
│ }                                                               │
│                                                                 │
│ TTL: 1 hour (Redis cache)                                     │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ↓
┌────────────────────────────────────────────────────────────────┐
│                 FRONTEND: Success Response                      │
│                                                                 │
│ 1. Show success toast:                                         │
│    ✅ "Video journal entry saved successfully!"                │
│                                                                 │
│ 2. Reset form:                                                  │
│    - Clear video preview                                       │
│    - Clear emotion snapshots                                   │
│    - Reset timeline                                            │
│    - Stop camera                                               │
│                                                                 │
│ 3. Navigate to journal list                                    │
│                                                                 │
│ 4. Refresh journal entries                                     │
└────────────────────────────────────────────────────────────────┘
```

---

## Data Structures

### 1. EmotionSnapshot (TypeScript)

**Purpose**: Single point-in-time emotion detection result

```typescript
interface EmotionSnapshot {
  timestamp: number              // Seconds into recording (0.0, 0.5, 1.0, ...)
  expressions: {
    neutral: number             // 0.0 to 1.0
    happy: number
    sad: number
    angry: number
    fearful: number
    disgusted: number
    surprised: number
  }
  dominant: string               // Emotion with highest score
  confidence: number             // Score of dominant emotion
}
```

**Example**:
```typescript
{
  timestamp: 2.5,
  expressions: {
    neutral: 0.12,
    happy: 0.05,
    sad: 0.71,
    angry: 0.03,
    fearful: 0.06,
    disgusted: 0.01,
    surprised: 0.02
  },
  dominant: "sad",
  confidence: 0.71
}
```

---

### 2. FacialSummary (TypeScript)

**Purpose**: Aggregated statistics from all snapshots

```typescript
interface FacialSummary {
  duration_seconds: number                    // Total recording duration
  snapshots_count: number                     // Number of snapshots captured
  dominant_emotion_overall: string            // Most frequent emotion
  emotion_distribution: Record<string, string> // Percentages as strings
}
```

**Example**:
```typescript
{
  duration_seconds: 30,
  snapshots_count: 60,
  dominant_emotion_overall: "sad",
  emotion_distribution: {
    "sad": "70.0",
    "neutral": "20.0",
    "fearful": "8.3",
    "happy": "1.7"
  }
}
```

---

### 3. TextEmotion (TypeScript)

**Purpose**: Emotion analysis from transcribed text

```typescript
interface TextEmotion {
  emotion: string                              // Primary emotion
  confidence: number                           // Confidence score
  all_emotions: Record<string, number>        // All emotions with scores
  cultural_context?: string                    // Optional cultural notes
  processing_time_ms?: number
  language?: string
}
```

**Example**:
```typescript
{
  emotion: "sadness",
  confidence: 0.82,
  all_emotions: {
    sadness: 0.82,
    fear: 0.65,
    neutral: 0.25,
    hope: 0.15,
    anger: 0.05,
    joy: 0.03,
    surprise: 0.02
  },
  cultural_context: null,
  processing_time_ms: 124,
  language: "en"
}
```

---

### 4. VideoAnalysis (TypeScript & Database)

**Purpose**: Complete video journal analysis data

```typescript
interface VideoAnalysis {
  facial_emotions: EmotionSnapshot[]          // Array of all snapshots
  facial_summary: FacialSummary               // Aggregated facial data
  text_emotion: TextEmotion                   // Text-based emotion
  stt_confidence: number                      // Transcription quality
  language: string                            // Detected language
  video_duration: number                      // Seconds
  has_face_detected: boolean                  // Was face found?
}
```

**Storage**: JSON/JSONB column in database

**Size**: ~15-20KB for 30-second video

---

### 5. JournalEntry (Database Model)

**Python (SQLAlchemy)**:
```python
class JournalEntry(Base):
    __tablename__ = "journal_entries"
    
    id: str                          # UUID
    user_id: str                     # Foreign key
    title: str                       # Optional
    content: str                     # Transcript (required)
    mood_before: int                 # 1-5 scale
    mood_after: int                  # 1-5 scale
    sentiment_score: float           # -1 to 1 (from text emotion)
    sentiment_label: str             # "positive", "negative", "neutral"
    themes: List[str]                # ["job_loss", "worry"]
    is_private: bool                 # Default: true
    word_count: int                  # Auto-calculated
    reading_time: int                # Auto-calculated
    entry_type: str                  # "text" or "video" (NEW)
    video_analysis: dict             # JSON data (NEW)
    created_at: datetime
    updated_at: datetime
```

**PostgreSQL**:
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
    themes JSONB,
    is_private BOOLEAN DEFAULT true,
    word_count INTEGER DEFAULT 0,
    reading_time INTEGER DEFAULT 0,
    entry_type VARCHAR(20) DEFAULT 'text',
    video_analysis JSONB,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

---

## Implementation Steps

### Phase 1: Backend Setup (1 hour)

#### Step 1.1: Database Migration (30 minutes)

**Create Migration File**:
```bash
cd backend/database/migrations/
touch 005_add_video_journal_support.sql
```

**Migration Content**:
```sql
-- Add entry_type column
ALTER TABLE journal_entries 
ADD COLUMN entry_type VARCHAR(20) DEFAULT 'text';

-- Add video_analysis column
ALTER TABLE journal_entries 
ADD COLUMN video_analysis JSONB DEFAULT NULL;

-- Add index
CREATE INDEX idx_journal_entries_entry_type 
ON journal_entries(entry_type);

-- Add comments
COMMENT ON COLUMN journal_entries.entry_type IS 
'Type of journal entry: "text" or "video"';

COMMENT ON COLUMN journal_entries.video_analysis IS 
'Contains facial emotions array, text emotion, and metadata';
```

**Run Migration**:
```bash
# Development
psql -U postgres -d mantrapath_dev -f 005_add_video_journal_support.sql

# Production
# Use Alembic or manual deployment process
```

**Verify**:
```sql
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'journal_entries';
```

---

#### Step 1.2: Update Models (5 minutes)

**File**: `backend/shared/models.py`

**Add to JournalEntry class**:
```python
# After existing columns
entry_type = Column(String, default="text")
video_analysis = Column(JSON, default=None)
```

**Verification**: Import model in Python shell
```python
from shared.models import JournalEntry
print(JournalEntry.__table__.columns.keys())
# Should include 'entry_type' and 'video_analysis'
```

---

#### Step 1.3: Update Mood Service (25 minutes)

**File**: `backend/services/mood_service/src/api/journal_routes.py`

**Modify POST endpoint**:
```python
@router.post("/")
async def create_journal_entry_root(
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    body = await request.json()
    
    # ADD these two lines:
    entry_type = body.get('entry_type', 'text')
    video_analysis = body.get('video_analysis')
    
    journal_entry = JournalEntry(
        user_id=current_user['user_id'],
        title=body.get('title'),
        content=body.get('content', ''),
        mood_before=body.get('mood_before'),
        mood_after=body.get('mood_after'),
        is_private=body.get('is_private', True),
        entry_type=entry_type,              # ADD
        video_analysis=video_analysis,      # ADD
        created_at=datetime.utcnow()
    )
    
    db.add(journal_entry)
    db.commit()
    db.refresh(journal_entry)
    
    # Return includes new fields automatically
    return journal_entry
```

**Test with cURL**:
```bash
curl -X POST http://localhost:8000/api/v1/journal/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Video Entry",
    "content": "Test content",
    "entry_type": "video",
    "video_analysis": {
      "test": true
    }
  }'
```

---

### Phase 2: Frontend Development (5 hours)

#### Step 2.1: Install Dependencies (5 minutes)

```bash
cd frontend
npm install face-api.js
```

**Verify Installation**:
```bash
npm list face-api.js
# Should show: face-api.js@0.22.2
```

---

#### Step 2.2: Download face-api.js Models (10 minutes)

**Option A: Use CDN (Recommended for quick start)**
```typescript
const MODEL_URL = 'https://cdn.jsdelivr.net/npm/@vladmandic/face-api/model'

await faceapi.nets.tinyFaceDetector.loadFromUri(MODEL_URL)
await faceapi.nets.faceExpressionNet.loadFromUri(MODEL_URL)
await faceapi.nets.faceLandmark68Net.loadFromUri(MODEL_URL)
```

**Option B: Local Files (Production)**
```bash
# Download models
mkdir -p frontend/public/models
cd frontend/public/models

# Download from GitHub
wget https://github.com/justadudewhohacks/face-api.js/raw/master/weights/tiny_face_detector_model-weights_manifest.json
wget https://github.com/justadudewhohacks/face-api.js/raw/master/weights/tiny_face_detector_model-shard1
# ... repeat for face_expression_model and face_landmark_68_model
```

---

#### Step 2.3: Create Utility Functions (30 minutes)

**File**: `frontend/src/utils/emotionAnalysis.ts`

**Functions to implement**:
1. `getDominantEmotion(expressions)` - Find highest score
2. `calculateFacialSummary(snapshots)` - Aggregate statistics
3. `getEmotionColor(emotion)` - Color mapping for UI

**Refer to "Data Structures" section for implementation details**

---

#### Step 2.4: Create EmotionTimeline Component (1 hour)

**File**: `frontend/src/components/journal/EmotionTimeline.tsx`

**Features**:
- Horizontal bar with color segments
- Each segment = one snapshot
- Hover tooltip with details
- Responsive design

**Refer to "Frontend Changes > Component 2" for implementation details**

---

#### Step 2.5: Create FaceOverlay Component (1 hour)

**File**: `frontend/src/components/journal/FaceOverlay.tsx`

**Features**:
- Canvas overlay on video
- Draw bounding box
- Draw landmarks (optional)
- Draw emotion label

**Refer to "Frontend Changes > Component 3" for implementation details**

---

#### Step 2.6: Create VideoJournalEntry Component (2 hours)

**File**: `frontend/src/components/journal/VideoJournalEntry.tsx`

**Implementation Order**:
1. Basic component structure + state
2. Model loading + camera access
3. MediaRecorder setup
4. face-api.js detection loop
5. Real-time display updates
6. Stop recording + video blob creation
7. Backend communication
8. Success/error handling

**Refer to "Frontend Changes > Component 1" for complete details**

---

#### Step 2.7: Integrate into Journal Page (30 minutes)

**File**: `frontend/src/pages/JournalPage.tsx` (or wherever journal UI lives)

**Add video tab**:
```tsx
<Tabs defaultValue="text">
  <TabsList>
    <TabsTrigger value="text">📝 Write</TabsTrigger>
    <TabsTrigger value="video">🎥 Video</TabsTrigger>
  </TabsList>
  
  <TabsContent value="text">
    {/* Existing text journal form */}
  </TabsContent>
  
  <TabsContent value="video">
    <VideoJournalEntry onSuccess={handleSuccess} />
  </TabsContent>
</Tabs>
```

---

### Phase 3: Testing & Validation (1 hour)

#### Test 1: Database Schema (5 minutes)

```sql
-- Verify columns exist
SELECT * FROM journal_entries LIMIT 1;

-- Test insert
INSERT INTO journal_entries (
  user_id, content, entry_type, video_analysis
) VALUES (
  'test_user', 'Test content', 'video', '{"test": true}'::jsonb
);
```

---

#### Test 2: Backend API (10 minutes)

**Test POST endpoint**:
```bash
curl -X POST http://localhost:8000/api/v1/journal/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d @test_video_journal.json
```

**Verify response includes new fields**

---

#### Test 3: Voice Service STT (10 minutes)

**Upload test video**:
```bash
curl -X POST http://localhost:8000/api/v1/voice/stt \
  -F "audio_file=@test_video.webm"
```

**Verify transcript returned**

---

#### Test 4: AI Event Processor (10 minutes)

**Test emotion analysis**:
```bash
curl -X POST http://localhost:8000/ai-events/api/v1/analyze/emotion \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Today was really hard",
    "language": "en",
    "user_id": "test_user"
  }'
```

**Verify emotion response**

---

#### Test 5: Frontend Component (15 minutes)

**Manual Testing Checklist**:
- [ ] Camera permission requested
- [ ] Video preview displays
- [ ] face-api.js models load
- [ ] Face detected and bounding box shows
- [ ] Live emotion updates
- [ ] Timeline bar updates
- [ ] Recording stops properly
- [ ] Video blob created
- [ ] STT returns transcript
- [ ] Text emotion analysis works
- [ ] Journal entry saved
- [ ] Success message shows

---

#### Test 6: End-to-End Flow (10 minutes)

**Complete User Journey**:
1. Open journal page
2. Click "Video" tab
3. Start recording
4. Speak for 10-30 seconds
5. Stop recording
6. Wait for processing
7. Verify journal entry created
8. Check database for video_analysis field
9. View entry in journal list

---

## Testing Strategy

### Unit Tests

#### Backend Tests

**File**: `backend/services/mood_service/tests/test_journal_routes.py`

**Test Cases**:
```python
def test_create_video_journal_entry():
    """Test creating journal entry with video_analysis"""
    # Setup
    # Call POST /api/v1/journal/ with video data
    # Assert: entry_type == "video"
    # Assert: video_analysis is stored
    # Assert: response includes new fields

def test_create_text_journal_entry():
    """Test that text entries still work"""
    # Ensure backward compatibility
    
def test_video_analysis_validation():
    """Test that invalid video_analysis is rejected"""
    # Test null, malformed JSON, etc.
```

---

#### Frontend Tests

**File**: `frontend/src/components/journal/__tests__/VideoJournalEntry.test.tsx`

**Test Cases**:
```typescript
describe('VideoJournalEntry', () => {
  test('loads face-api models on mount', async () => {
    // Mock face-api.js
    // Render component
    // Assert: models loaded
  })
  
  test('requests camera permission', async () => {
    // Mock navigator.mediaDevices
    // Click start button
    // Assert: getUserMedia called
  })
  
  test('detects emotions every 500ms', async () => {
    // Mock face-api.js detection
    // Start recording
    // Wait 1 second
    // Assert: 2 snapshots captured
  })
  
  test('calculates facial summary correctly', () => {
    // Provide mock snapshots
    // Call calculateFacialSummary
    // Assert: correct percentages
  })
  
  test('calls backend APIs in correct order', async () => {
    // Mock fetch
    // Stop recording
    // Assert: STT called first
    // Assert: emotion analysis called second
    // Assert: journal POST called last
  })
})
```

---

### Integration Tests

**File**: `backend/tests/integration/test_video_journal_flow.py`

**Test Complete Flow**:
```python
async def test_complete_video_journal_flow():
    """Test entire flow from video to saved journal entry"""
    
    # 1. Upload video to Voice Service
    stt_response = await client.post(
        "/api/v1/voice/stt",
        files={"audio_file": test_video_file}
    )
    assert stt_response.status_code == 200
    transcript = stt_response.json()["transcript"]
    
    # 2. Analyze text emotion
    emotion_response = await client.post(
        "/ai-events/api/v1/analyze/emotion",
        json={"text": transcript, "language": "en", "user_id": "test"}
    )
    assert emotion_response.status_code == 200
    text_emotion = emotion_response.json()
    
    # 3. Create journal entry
    journal_response = await client.post(
        "/api/v1/journal/",
        json={
            "content": transcript,
            "entry_type": "video",
            "video_analysis": {
                "facial_emotions": mock_facial_snapshots,
                "text_emotion": text_emotion
            }
        }
    )
    assert journal_response.status_code == 201
    
    # 4. Verify database
    entry = db.query(JournalEntry).filter_by(
        id=journal_response.json()["id"]
    ).first()
    assert entry is not None
    assert entry.entry_type == "video"
    assert entry.video_analysis is not None
```

---

### Manual Testing Checklist

#### Camera & Recording
- [ ] Camera permission prompt appears
- [ ] Video preview shows user's face
- [ ] Recording starts on button click
- [ ] Recording timer displays
- [ ] Recording stops on button click
- [ ] Camera light turns off after stop

#### Face Detection
- [ ] Bounding box appears around face
- [ ] Bounding box moves with face
- [ ] No face detected → appropriate message
- [ ] Multiple faces → warning message
- [ ] Low light → detection still works

#### Emotion Detection
- [ ] Live emotion text updates every 500ms
- [ ] Emotion matches user's expression
- [ ] Confidence percentage displays
- [ ] Timeline bar updates in real-time
- [ ] Timeline colors match emotions

#### Processing
- [ ] Loading spinner shows during processing
- [ ] STT completes (transcript shown)
- [ ] Text emotion analysis completes
- [ ] Facial summary calculated
- [ ] Progress indicator updates

#### Saving
- [ ] Journal entry saves successfully
- [ ] Success message displays
- [ ] Entry appears in journal list
- [ ] Entry shows "Video" badge/icon
- [ ] Clicking entry shows full details

#### Error Handling
- [ ] Camera denied → error message + retry
- [ ] No face detected → warning but allow save
- [ ] STT fails → fallback or error
- [ ] Network error → retry option
- [ ] Validation error → clear message

---

## Future Enhancements

### Phase 2 Improvements (After Initial Release)

#### 1. Video Playback in Journal View

**Feature**: Allow users to watch their video journal entries

**Implementation**:
- Store video files in Media Service (S3/MinIO)
- Add `video_url` field to `video_analysis`
- Create VideoPlayer component
- Sync timeline with video playback

**Effort**: 8 hours

---

#### 2. Emotion Fusion Analysis

**Feature**: Detect emotional incongruence (face vs. words)

**Implementation**:
- Create `multimodal_fusion.py`
- Implement incongruence detection algorithm
- Add therapeutic flags
- Display insights in UI

**Effort**: 10 hours

**Benefit**: Detect emotional masking, improve intervention accuracy

---

#### 3. Advanced Timeline Features

**Feature**: Interactive timeline with video scrubbing

**Implementation**:
- Click timeline → seek to timestamp
- Hover → show frame preview
- Zoom in/out on timeline
- Export timeline as image

**Effort**: 6 hours

---

#### 4. Multi-Language Support

**Feature**: Better support for non-English videos

**Implementation**:
- Language selector in UI
- Pass language hint to Whisper
- Cultural emotion interpretation
- Localized UI text

**Effort**: 4 hours

---

#### 5. Audio-Only Mode

**Feature**: Allow audio recording without video

**Implementation**:
- Toggle "Audio Only" option
- Skip face detection
- Only process audio → text → emotion
- Smaller file size

**Effort**: 2 hours

---

#### 6. Emotion Trends Over Time

**Feature**: Show emotion patterns across multiple journal entries

**Implementation**:
- Aggregate video_analysis across entries
- Create charts/graphs
- Identify patterns (e.g., "sad most Mondays")
- Compare facial vs. text emotions

**Effort**: 12 hours

---

#### 7. Therapist Review Dashboard

**Feature**: Special view for therapists to review video journals

**Implementation**:
- Permission system
- Side-by-side video + timeline
- Annotation tools
- Export reports

**Effort**: 20 hours

---

#### 8. Real-Time Feedback

**Feature**: Give user feedback during recording

**Implementation**:
- "Your facial expression seems sad. How are you feeling?"
- Breathing exercise suggestions if stress detected
- Prompt questions based on emotions

**Effort**: 8 hours

---

#### 9. Voice Emotion Analysis

**Feature**: Analyze voice tone/prosody in addition to words

**Implementation**:
- Extract audio features (pitch, energy, rate)
- Detect voice stress
- Add to video_analysis
- Third modality for analysis

**Effort**: 15 hours

---

#### 10. Privacy Enhancements

**Feature**: Enhanced privacy controls

**Implementation**:
- Option to delete video after processing
- Store only emotions, not video
- Face blur option
- Encrypted storage

**Effort**: 6 hours

---

## Appendix

### A. Emotion Color Mapping

```javascript
const EMOTION_COLORS = {
  neutral: {
    primary: '#9CA3AF',   // Gray
    light: '#D1D5DB',
    dark: '#6B7280'
  },
  happy: {
    primary: '#10B981',   // Green
    light: '#6EE7B7',
    dark: '#047857'
  },
  sad: {
    primary: '#3B82F6',   // Blue
    light: '#93C5FD',
    dark: '#1E40AF'
  },
  angry: {
    primary: '#EF4444',   // Red
    light: '#FCA5A5',
    dark: '#B91C1C'
  },
  fearful: {
    primary: '#8B5CF6',   // Purple
    light: '#C4B5FD',
    dark: '#6D28D9'
  },
  disgusted: {
    primary: '#92400E',   // Brown
    light: '#D97706',
    dark: '#78350F'
  },
  surprised: {
    primary: '#F59E0B',   // Orange
    light: '#FCD34D',
    dark: '#D97706'
  }
}
```

---

### B. Sample API Responses

#### Voice Service STT Response
```json
{
  "transcript": "Today was a really difficult day at work. I feel overwhelmed.",
  "language": "en",
  "confidence": 0.92,
  "duration": 8.5,
  "segments": [
    {
      "start": 0.0,
      "end": 3.2,
      "text": "Today was a really difficult day at work."
    },
    {
      "start": 3.5,
      "end": 5.8,
      "text": "I feel overwhelmed."
    }
  ]
}
```

#### AI Event Processor Emotion Response
```json
{
  "emotion": "sadness",
  "confidence": 0.78,
  "emotions": {
    "sadness": 0.78,
    "fear": 0.52,
    "neutral": 0.31,
    "anger": 0.12,
    "joy": 0.05,
    "surprise": 0.03,
    "disgust": 0.02
  },
  "cultural_context": null,
  "processing_time_ms": 145,
  "language": "en",
  "has_cultural_adaptation": false,
  "analysis_metadata": {
    "model_source": "models_service",
    "model_name": "phi-4"
  }
}
```

---

### C. Error Handling Reference

#### Frontend Error Types
```typescript
type VideoJournalError = 
  | 'camera_permission_denied'
  | 'no_face_detected'
  | 'model_load_failed'
  | 'recording_failed'
  | 'stt_failed'
  | 'emotion_analysis_failed'
  | 'save_failed'
  | 'network_error'

const ERROR_MESSAGES: Record<VideoJournalError, string> = {
  camera_permission_denied: 
    'Camera access denied. Please enable camera permissions in your browser settings.',
  no_face_detected: 
    'No face detected. Please ensure your face is visible and well-lit.',
  model_load_failed: 
    'Failed to load emotion detection models. Please refresh the page.',
  recording_failed: 
    'Recording failed. Please try again.',
  stt_failed: 
    'Speech-to-text conversion failed. The video was saved but without transcript.',
  emotion_analysis_failed: 
    'Emotion analysis failed. The entry was saved without emotion data.',
  save_failed: 
    'Failed to save journal entry. Please try again.',
  network_error: 
    'Network error. Please check your connection and try again.'
}
```

---

### D. Performance Benchmarks

**Target Performance**:
- Model loading: < 5 seconds (first time only)
- Face detection: < 50ms per frame
- 500ms interval: Achievable on modern devices
- STT processing: 2-5 seconds for 30s video
- Text emotion: 100-200ms
- Total save time: < 10 seconds for 30s video

**Browser Requirements**:
- Chrome 90+, Firefox 88+, Safari 14+
- Camera API support
- Canvas API support
- WebAssembly support (for face-api.js)

---

### E. Storage Estimates

**Per 30-Second Video Journal Entry**:
- Video file (if stored): 5-10 MB
- facial_emotions array: ~15 KB
- Complete video_analysis JSON: ~20 KB
- Database row: ~25 KB (including indexes)

**Monthly Storage (100 video entries)**:
- Video files: 500-1000 MB (if stored)
- Database: 2.5 MB
- Total: ~1 GB per 100 entries

---

### F. Browser Compatibility

| Feature | Chrome | Firefox | Safari | Edge |
|---------|--------|---------|--------|------|
| MediaRecorder | ✅ 90+ | ✅ 88+ | ✅ 14+ | ✅ 90+ |
| getUserMedia | ✅ 53+ | ✅ 36+ | ✅ 11+ | ✅ 79+ |
| Canvas API | ✅ All | ✅ All | ✅ All | ✅ All |
| WebAssembly | ✅ 57+ | ✅ 52+ | ✅ 11+ | ✅ 79+ |
| face-api.js | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |

**Minimum Requirements**: Chrome 90, Firefox 88, Safari 14, Edge 90

---

## Conclusion

This implementation plan provides a complete roadmap for integrating video journal functionality into MantraPath. The approach maximizes code reuse (75% of services unchanged), maintains data separation (no fusion), and preserves rich emotion detail (all 7 emotions per snapshot).

**Key Takeaways**:
- **7 hours total development time**
- **Minimal backend changes** (2 columns, 2 lines of code)
- **Client-side emotion detection** (no GPU needed)
- **Leverages existing services** (Voice Service, AI Event Processor)
- **Rich data preservation** (all emotions stored, not just dominant)
- **Future-proof design** (can add fusion later if needed)

The plan is **implementation-ready** and can be followed step-by-step to deliver a production-quality video journal feature.

---

**Document Version**: 1.0  
**Last Updated**: 2024-10-16  
**Status**: Ready for Implementation

