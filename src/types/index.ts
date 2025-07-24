export interface MoodEntry {
  id: string
  mood: 'very-low' | 'low' | 'neutral' | 'good' | 'excellent'
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
}

export interface ChatMessage {
  id: string
  content: string
  sender: 'user' | 'mitra'
  timestamp: number
  context?: {
    suggestedMood?: MoodEntry['mood']
    suggestedContent?: string[]
    breathingExercise?: boolean
    exerciseType?: '4-7-8' | '4-4-4-4' | 'box'
  }
}

export interface CommunityPost {
  id: string
  title: string
  content: string
  author: {
    name: string
    avatar?: string
    badges: string[]
  }
  timestamp: number
  replies: number
  likes: number
  category: 'general' | 'anxiety' | 'depression' | 'support' | 'achievements'
}

export interface UserStats {
  moodStreak: number
  journalStreak: number
  communityContributions: number
  unlockedThemes: string[]
  badges: string[]
  currentTheme?: 'default' | 'calm' | 'energetic' | 'supportive' | 'dynamic'
}

// Enhanced types for mood insights and patterns
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
  priority: 'low' | 'medium' | 'high'
  timestamp: number
  category: string
}

export interface WeeklyAnalysis {
  week: { start: number; end: number }
  averageMood: number
  moodVariability: number
  dominantMood: string
  patterns: MoodPattern[]
  insights: PersonalizedInsight[]
  recommendations: RecommendationCard[]
  streaks: { current: number; longest: number }
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