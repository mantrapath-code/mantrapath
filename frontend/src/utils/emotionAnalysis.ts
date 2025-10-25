/**
 * Emotion analysis utility functions
 */

import type { EmotionSnapshot, FacialSummary } from '@/types/journal'

/**
 * Get the dominant emotion from an expressions object
 * @param expressions - Object with emotion scores
 * @returns Object with dominant emotion name and confidence
 */
export function getDominantEmotion(expressions: Record<string, number>): {
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

/**
 * Calculate facial emotion summary statistics from snapshots
 * @param snapshots - Array of emotion snapshots
 * @returns Aggregated summary with duration, counts, and distribution
 */
export function calculateFacialSummary(snapshots: EmotionSnapshot[]): FacialSummary {
  if (snapshots.length === 0) {
    return {
      duration_seconds: 0,
      snapshots_count: 0,
      dominant_emotion_overall: 'neutral',
      emotion_distribution: {}
    }
  }

  // Count dominant emotions
  const counts: Record<string, number> = {}
  
  snapshots.forEach(snap => {
    counts[snap.dominant] = (counts[snap.dominant] || 0) + 1
  })
  
  // Calculate percentages
  const total = snapshots.length
  const distribution: Record<string, string> = {}
  
  Object.keys(counts).forEach(emotion => {
    distribution[emotion] = ((counts[emotion] / total) * 100).toFixed(1)
  })
  
  // Find overall dominant (emotion that appears most frequently)
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

/**
 * Get color code for an emotion
 * @param emotion - Emotion name
 * @returns Color hex code
 */
export function getEmotionColor(emotion: string): string {
  const colors: Record<string, string> = {
    neutral: '#9CA3AF',   // Gray
    happy: '#10B981',     // Green
    sad: '#3B82F6',       // Blue
    angry: '#EF4444',     // Red
    fearful: '#8B5CF6',   // Purple
    disgusted: '#92400E', // Brown
    surprised: '#F59E0B'  // Orange
  }
  
  return colors[emotion.toLowerCase()] || colors.neutral
}

/**
 * Get a more descriptive label for an emotion
 * @param emotion - Emotion name
 * @returns Human-readable label with emoji
 */
export function getEmotionLabel(emotion: string): string {
  const labels: Record<string, string> = {
    neutral: '😐 Neutral',
    happy: '😊 Happy',
    sad: '😢 Sad',
    angry: '😠 Angry',
    fearful: '😰 Fearful',
    disgusted: '🤢 Disgusted',
    surprised: '😲 Surprised'
  }
  
  return labels[emotion.toLowerCase()] || emotion
}
