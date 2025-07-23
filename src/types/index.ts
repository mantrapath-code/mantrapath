export interface MoodEntry {
  id: string
  mood: 'very-low' | 'low' | 'neutral' | 'good' | 'excellent'
  timestamp: number
  note?: string
  triggers?: string[]
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
}