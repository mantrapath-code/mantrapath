/**
 * Type definitions for video journal emotion analysis
 */

export interface EmotionSnapshot {
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

export interface FacialSummary {
  duration_seconds: number                    // Total recording duration
  snapshots_count: number                     // Number of snapshots captured
  dominant_emotion_overall: string            // Most frequent emotion
  emotion_distribution: Record<string, string> // Percentages as strings
}

export interface TextEmotion {
  emotion: string                              // Primary emotion
  confidence: number                           // Confidence score
  all_emotions: Record<string, number>        // All emotions with scores
  cultural_context?: string                    // Optional cultural notes
  processing_time_ms?: number
  language?: string
}

export interface VideoAnalysis {
  facial_emotions: EmotionSnapshot[]          // Array of all snapshots
  facial_summary: FacialSummary               // Aggregated facial data
  text_emotion: TextEmotion                   // Text-based emotion
  stt_confidence: number                      // Transcription quality
  language: string                            // Detected language
  video_duration: number                      // Seconds
  has_face_detected: boolean                  // Was face found?
}

export interface VideoJournalData {
  title?: string
  content: string  // Transcript
  entry_type: 'video'
  is_private?: boolean
  video_analysis: VideoAnalysis
}
