// Re-export all types from the types/index.ts for consistency
export * from './types/index'

// Legacy exports for backward compatibility
export interface MoodEntry {
  id: string
  mood: 'excellent' | 'good' | 'neutral' | 'low' | 'very-low'
  timestamp: number
  note?: string
  triggers?: string[]
  dayOfWeek?: number
  timeOfDay?: 'morning' | 'afternoon' | 'evening' | 'night'
  energy?: 'high' | 'medium' | 'low'
  context?: string[]
}

export interface JournalEntry {
  id: string
  title: string
  content: string
  sentiment: 'positive' | 'neutral' | 'negative'
  timestamp: number
  keywords: string[]
  mood?: MoodEntry['mood']
}

export interface ChatMessage {
  id: string
  content: string
  sender: 'user' | 'mitra'
  timestamp: number
  context?: {
    type?: 'mood_support' | 'general' | 'crisis' | 'celebration'
    suggestedMood?: MoodEntry['mood']
    relatedData?: any
  }
}

export interface CommunityPost {
  id: string
  title: string
  content: string
  author: string
  timestamp: number
  likes: number
  replies: number
  tags: string[]
}

export interface UserStats {
  moodStreak: number
  journalStreak: number
  communityContributions: number
  unlockedThemes: string[]
  badges: string[]
  totalPoints?: number
  currentTheme?: string
}

export interface MoodPattern {
  type: 'daily' | 'weekly' | 'trigger-based' | 'context-based'
  pattern: string
  confidence: number
  frequency: number
  suggestion: string
  impact: 'positive' | 'negative' | 'neutral'
}

export interface PersonalizedInsight {
  id: string
  type: 'pattern' | 'achievement' | 'recommendation' | 'warning'
  title: string
  description: string
  actionItems: string[]
  priority: 'high' | 'medium' | 'low'
  timestamp: number
  category: 'mood' | 'activity' | 'social' | 'wellness'
}

export interface WeeklyAnalysis {
  week: {
    start: number
    end: number
  }
  averageMood: number
  moodVariability: number
  dominantMood: MoodEntry['mood']
  patterns: MoodPattern[]
  insights: PersonalizedInsight[]
  recommendations: RecommendationCard[]
  streaks: {
    current: number
    longest: number
  }
}

export interface RecommendationCard {
  id: string
  title: string
  description: string
  type: 'exercise' | 'mindfulness' | 'social' | 'routine' | 'professional'
  urgency: 'low' | 'medium' | 'high'
  estimatedTime: string
  benefits: string[]
  basedOn: string[]
}