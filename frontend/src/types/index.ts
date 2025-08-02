// Backend API compatible types
export interface MoodEntry {
  id: string
  mood: 'very-low' | 'low' | 'neutral' | 'good' | 'excellent'
  mood_level: number // 1-5 scale for backend compatibility
  timestamp: number
  note?: string
  notes?: string // Backend field name
  triggers?: string[]
  dayOfWeek?: number
  timeOfDay?: 'morning' | 'afternoon' | 'evening' | 'night'
  energy?: 'high' | 'medium' | 'low'
  energy_level?: number // 1-5 scale for backend
  stress_level?: number // 1-5 scale for enhanced mood tracking
  sleep_quality?: number // 1-5 scale for enhanced mood tracking
  context?: string[]
  context_tags?: string[] // Backend field name
  created_at?: string
  updated_at?: string
  user_id?: string
}

export interface JournalEntry {
  id: string
  title: string
  content: string
  sentiment: 'positive' | 'neutral' | 'negative'
  sentiment_score?: number
  timestamp: number
  keywords: string[]
  tags?: string[] // Backend field name
  mood_id?: string // Link to mood entry
  is_private?: boolean
  created_at?: string
  updated_at?: string
  user_id?: string
  word_count?: number
  reading_time?: number
}

// API Response types
export interface ApiResponse<T> {
  success: boolean
  data: T
  message?: string
  timestamp?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  limit: number
  has_next: boolean
  has_prev: boolean
}

// Analytics types matching backend
export interface MoodAnalytics {
  average_mood: number
  mood_variance: number
  total_entries: number
  streak_current: number
  streak_longest: number
  weekly_trend: number
  monthly_trend: number
  common_triggers: string[]
  mood_by_time_of_day: Record<string, number>
  mood_by_day_of_week: Record<string, number>
}

export interface JournalAnalytics {
  total_entries: number
  average_word_count: number
  sentiment_distribution: Record<string, number>
  common_themes: string[]
  writing_streak: number
  entries_by_month: Record<string, number>
}

// Insight types from backend
export interface BackendInsight {
  id: string
  type: 'pattern' | 'trigger' | 'achievement' | 'recommendation' | 'warning'
  title: string
  description: string
  confidence: number
  category: string
  priority: 'low' | 'medium' | 'high'
  created_at: string
  is_read: boolean
  data?: any
  action_items?: string[]
}

export interface ChatMessage {
  id: string
  content: string
  sender: 'user' | 'assistant'
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