# Frontend Video Journal Implementation Plan

## Current State Analysis

### Existing Infrastructure ✅
- **Framework**: React 19 + TypeScript + Vite
- **UI Library**: Radix UI + shadcn/ui components
- **Styling**: TailwindCSS
- **State Management**: React Hooks
- **Journal Component**: `JournalSection.tsx` (text-only)
- **API Service**: `api.ts` with `createJournalEntry()` method
- **Journal Hook**: `useJournal` hook exists

### What We Need to Build
1. Install `face-api.js` library
2. Create utility functions for emotion analysis
3. Create 3 new components:
   - `VideoJournalEntry.tsx` - Main recording component
   - `EmotionTimeline.tsx` - Timeline visualization
   - `FaceOverlay.tsx` - Canvas overlay
4. Update `JournalSection.tsx` - Add video tab
5. Update API service - Add video journal methods

---

## Implementation Phases

### Phase 1: Setup Dependencies (15 minutes)

#### Step 1.1: Install face-api.js
```bash
cd frontend
npm install face-api.js
```

**Verify**: Check `package.json` includes `"face-api.js": "^0.22.2"`

---

### Phase 2: Utility Functions (30 minutes)

#### Step 2.1: Create `frontend/src/utils/emotionAnalysis.ts`

**Purpose**: Emotion analysis utilities (matching plan)

**Functions to implement**:
1. `getDominantEmotion(expressions)` - Find highest scoring emotion
2. `calculateFacialSummary(snapshots)` - Aggregate statistics  
3. `getEmotionColor(emotion)` - Color mapping

**Reference**: See VIDEO_INTEGRATION_README.md section "Component 4: Utility Functions"

---

### Phase 3: Build Components (4 hours)

#### Step 3.1: Create `FaceOverlay.tsx` (1 hour)
**File**: `frontend/src/components/journal/FaceOverlay.tsx`

**Purpose**: Draw bounding boxes and landmarks on canvas

**Key Features**:
- Match canvas to video dimensions
- Draw bounding box around face
- Draw 68 facial landmarks (optional)
- Draw emotion label with confidence

**Props Interface**:
```typescript
interface FaceOverlayProps {
  videoRef: RefObject<HTMLVideoElement>
  canvasRef: RefObject<HTMLCanvasElement>
  detection: any | null  // face-api.js detection result
  currentEmotion: EmotionSnapshot | null
}
```

---

#### Step 3.2: Create `EmotionTimeline.tsx` (1 hour)
**File**: `frontend/src/components/journal/EmotionTimeline.tsx`

**Purpose**: Visualize emotion changes over time

**Key Features**:
- Horizontal color-coded segments
- Each segment = one emotion snapshot
- Hover tooltip with timestamp + emotion + confidence
- Smooth color transitions

**Props Interface**:
```typescript
interface EmotionTimelineProps {
  snapshots: EmotionSnapshot[]
  height?: number
  showLabels?: boolean
  interactive?: boolean
}
```

**Colors to Use**:
- neutral: #9CA3AF (Gray)
- happy: #10B981 (Green)
- sad: #3B82F6 (Blue)
- angry: #EF4444 (Red)
- fearful: #8B5CF6 (Purple)
- disgusted: #92400E (Brown)
- surprised: #F59E0B (Orange)

---

#### Step 3.3: Create `VideoJournalEntry.tsx` (2 hours)
**File**: `frontend/src/components/journal/VideoJournalEntry.tsx`

**Purpose**: Main video recording component

**Implementation Order**:
1. **State Management** (20 lines)
   - Recording state, emotion snapshots, video blob, models loaded
   
2. **Model Loading** (30 lines)
   - Load face-api.js models on mount
   - Use CDN: `https://cdn.jsdelivr.net/npm/@vladmandic/face-api/model`
   - Or load from `public/models/` directory
   
3. **Camera & Recording** (40 lines)
   - Request camera/mic permissions
   - Initialize MediaRecorder (WebM format)
   - Start/stop recording functions
   
4. **Emotion Detection Loop** (50 lines)
   - setInterval every 500ms
   - Call `faceapi.detectSingleFace().withFaceExpressions().withFaceLandmarks()`
   - Extract expressions, calculate dominant emotion
   - Update live display and snapshots array
   
5. **Real-Time Display** (60 lines)
   - Live emotion text ("happy (85.2%)")
   - Canvas overlay with FaceOverlay component
   - Timeline bar with EmotionTimeline component
   - Recording timer
   
6. **Backend Processing** (50 lines)
   - Stop recording → create video blob
   - Send to Voice Service → get transcript
   - Send transcript to AI Event Processor → get text emotion
   - Calculate facial summary
   - Create journal entry with all data
   
7. **Error Handling** (20 lines)
   - Camera permission denied
   - No face detected
   - Model load failed
   - Network errors

**Estimated Total**: ~270 lines

---

### Phase 4: Integration (30 minutes)

#### Step 4.1: Update `JournalSection.tsx`

**Changes Required**:
1. Add Tabs component (already available from Radix UI)
2. Add "🎥 Video" tab
3. Import VideoJournalEntry component
4. Handle success callback

**File**: `frontend/src/components/journal/JournalSection.tsx`

**Code Changes** (~20 lines):
```tsx
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { VideoJournalEntry } from "./VideoJournalEntry"

// Inside component, replace writing section with:
<Tabs defaultValue="text">
  <TabsList>
    <TabsTrigger value="text">📝 Write</TabsTrigger>
    <TabsTrigger value="video">🎥 Video</TabsTrigger>
  </TabsList>
  
  <TabsContent value="text">
    {/* Existing text journal form */}
  </TabsContent>
  
  <TabsContent value="video">
    <VideoJournalEntry onSuccess={() => {
      refresh() // Refresh journal list
      toast.success('Video journal entry saved!')
    }} />
  </TabsContent>
</Tabs>
```

---

#### Step 4.2: Update API Service

**File**: `frontend/src/services/api.ts`

**Add New Method** (20 lines):
```typescript
async createVideoJournalEntry(journalData: {
  title?: string
  content: string
  entry_type: 'video'
  is_private?: boolean
  video_analysis: {
    facial_emotions: Array<{
      timestamp: number
      expressions: Record<string, number>
      dominant: string
      confidence: number
    }>
    facial_summary: {
      duration_seconds: number
      snapshots_count: number
      dominant_emotion_overall: string
      emotion_distribution: Record<string, string>
    }
    text_emotion: any  // From AI Event Processor
    stt_confidence: number
    language: string
    video_duration: number
    has_face_detected: boolean
  }
}) {
  return this.request('/api/v1/journal/entries', {
    method: 'POST',
    body: JSON.stringify(journalData),
  })
}
```

**Add Voice STT Method** (15 lines):
```typescript
async transcribeVideo(videoBlob: Blob) {
  const formData = new FormData()
  formData.append('audio_file', videoBlob, 'video.webm')
  
  return this.request('/api/v1/voice/stt', {
    method: 'POST',
    body: formData,
  }, false) // Don't stringify, send FormData
}
```

---

### Phase 5: Type Definitions (10 minutes)

#### Step 5.1: Create `frontend/src/types/journal.ts`

**File**: `frontend/src/types/journal.ts`

**Interfaces**:
```typescript
export interface EmotionSnapshot {
  timestamp: number
  expressions: {
    neutral: number
    happy: number
    sad: number
    angry: number
    fearful: number
    disgusted: number
    surprised: number
  }
  dominant: string
  confidence: number
}

export interface FacialSummary {
  duration_seconds: number
  snapshots_count: number
  dominant_emotion_overall: string
  emotion_distribution: Record<string, string>
}

export interface TextEmotion {
  emotion: string
  confidence: number
  all_emotions: Record<string, number>
  language: string
  processing_time_ms?: number
}
```

---

## Implementation Timeline

| Phase | Task | Time | File(s) |
|-------|------|------|---------|
| 1 | Install face-api.js | 5 min | - |
| 2 | Create emotionAnalysis.ts | 30 min | utils/emotionAnalysis.ts |
| 3.1 | Create FaceOverlay.tsx | 60 min | components/journal/FaceOverlay.tsx |
| 3.2 | Create EmotionTimeline.tsx | 60 min | components/journal/EmotionTimeline.tsx |
| 3.3 | Create VideoJournalEntry.tsx | 120 min | components/journal/VideoJournalEntry.tsx |
| 4.1 | Update JournalSection.tsx | 15 min | components/journal/JournalSection.tsx |
| 4.2 | Update API service | 15 min | services/api.ts |
| 5 | Create types | 10 min | types/journal.ts |
| **Total** | | **~4.5 hours** | |

---

## Testing Checklist

### Functional Tests
- [ ] Camera permission requested correctly
- [ ] Video preview displays
- [ ] face-api.js models load successfully
- [ ] Face detected with bounding box
- [ ] Live emotion updates every 500ms
- [ ] Timeline bar updates in real-time
- [ ] Recording stops properly
- [ ] Video blob created successfully
- [ ] STT returns transcript
- [ ] Text emotion analysis works
- [ ] Journal entry saves with video_analysis
- [ ] Success message displays

### Edge Cases
- [ ] Camera denied → error message
- [ ] No face detected → warning displayed
- [ ] Model load fails → error handling
- [ ] STT fails → fallback or error
- [ ] Network error → retry option

### UI/UX
- [ ] Tab switching works smoothly
- [ ] Loading states display properly
- [ ] Error messages are clear
- [ ] Timeline colors are accurate
- [ ] Canvas overlay scales correctly
- [ ] Responsive on mobile

---

## File Structure After Implementation

```
frontend/src/
├── components/
│   └── journal/
│       ├── JournalSection.tsx          (MODIFIED - add tabs)
│       ├── VideoJournalEntry.tsx       (NEW - 270 lines)
│       ├── EmotionTimeline.tsx         (NEW - 100 lines)
│       ├── FaceOverlay.tsx             (NEW - 80 lines)
│       └── index.ts                    (UPDATE - export new components)
├── utils/
│   └── emotionAnalysis.ts              (NEW - 50 lines)
├── services/
│   └── api.ts                          (MODIFIED - add 2 methods)
└── types/
    └── journal.ts                      (NEW - type definitions)
```

---

## Dependencies

### New Dependencies Required
- `face-api.js` ^0.22.2

### Existing Dependencies Used
- `react` (already in package.json)
- `framer-motion` (already in package.json)
- `sonner` (toast notifications - already in package.json)
- `@radix-ui/react-tabs` (already in package.json)

---

## Next Steps

1. ✅ Review this plan
2. ⬜ Install face-api.js
3. ⬜ Create utility functions
4. ⬜ Build components one by one
5. ⬜ Integrate into JournalSection
6. ⬜ Test end-to-end
7. ⬜ Document any issues

---

## Notes

- **face-api.js Models**: Should be loaded from CDN initially for speed
- **Browser Support**: Chrome 90+, Firefox 88+, Safari 14+
- **Performance**: Target <50ms per face detection
- **File Size**: Video files ~5-10MB for 30-second recording
- **Backend Ready**: Backend already updated to accept video_analysis

---

**Status**: Ready to proceed with implementation
