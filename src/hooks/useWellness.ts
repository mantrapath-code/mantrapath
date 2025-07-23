import { useKV } from '@github/spark/hooks'
import { MoodEntry, JournalEntry, ChatMessage, CommunityPost, UserStats } from '@/types'

export function useMoods() {
  const [moods, setMoods] = useKV<MoodEntry[]>('user-moods', [])
  
  const addMood = (mood: MoodEntry['mood'], note?: string, triggers?: string[]) => {
    const newMood: MoodEntry = {
      id: Date.now().toString(),
      mood,
      timestamp: Date.now(),
      note,
      triggers
    }
    setMoods(current => [newMood, ...current])
    return newMood
  }

  const getMoodTrend = () => {
    const recent = moods.slice(0, 7)
    if (recent.length === 0) return 'neutral'
    
    const moodValues = {
      'very-low': 1,
      'low': 2,
      'neutral': 3,
      'good': 4,
      'excellent': 5
    }
    
    const average = recent.reduce((sum, entry) => sum + moodValues[entry.mood], 0) / recent.length
    
    if (average >= 4) return 'positive'
    if (average <= 2) return 'concerning'
    return 'neutral'
  }

  return { moods, addMood, getMoodTrend }
}

export function useJournal() {
  const [entries, setEntries] = useKV<JournalEntry[]>('journal-entries', [])
  
  const addEntry = (title: string, content: string) => {
    const sentiment = analyzeSentiment(content)
    const keywords = extractKeywords(content)
    
    const newEntry: JournalEntry = {
      id: Date.now().toString(),
      title,
      content,
      sentiment,
      timestamp: Date.now(),
      keywords
    }
    
    setEntries(current => [newEntry, ...current])
    return newEntry
  }
  
  return { entries, addEntry }
}

export function useChat() {
  const [messages, setMessages] = useKV<ChatMessage[]>('chat-messages', [])
  
  const addMessage = (content: string, sender: 'user' | 'mitra', context?: ChatMessage['context']) => {
    const newMessage: ChatMessage = {
      id: Date.now().toString(),
      content,
      sender,
      timestamp: Date.now(),
      context
    }
    
    setMessages(current => [...current, newMessage])
    return newMessage
  }
  
  const getMitraResponse = async (userMessage: string): Promise<string> => {
    const prompt = spark.llmPrompt`You are Mantra-Mitra, a compassionate AI wellness companion. Respond to this user message with empathy and practical support. Keep responses warm, supportive, and actionable. User message: ${userMessage}`
    
    try {
      const response = await spark.llm(prompt, 'gpt-4o-mini')
      return response
    } catch (error) {
      return "I'm here to support you. Sometimes I need a moment to think - please try again."
    }
  }
  
  return { messages, addMessage, getMitraResponse }
}

export function useUserStats() {
  const [stats, setStats] = useKV<UserStats>('user-stats', {
    moodStreak: 0,
    journalStreak: 0,
    communityContributions: 0,
    unlockedThemes: ['default'],
    badges: []
  })
  
  const updateStats = (updates: Partial<UserStats>) => {
    setStats(current => ({ ...current, ...updates }))
  }
  
  return { stats, updateStats }
}

function analyzeSentiment(text: string): 'positive' | 'neutral' | 'negative' {
  const positiveWords = ['happy', 'joy', 'great', 'wonderful', 'amazing', 'good', 'better', 'grateful', 'peaceful']
  const negativeWords = ['sad', 'angry', 'stressed', 'anxious', 'worried', 'difficult', 'hard', 'struggling', 'overwhelming']
  
  const words = text.toLowerCase().split(/\s+/)
  const positiveCount = words.filter(word => positiveWords.some(pos => word.includes(pos))).length
  const negativeCount = words.filter(word => negativeWords.some(neg => word.includes(neg))).length
  
  if (positiveCount > negativeCount) return 'positive'
  if (negativeCount > positiveCount) return 'negative'
  return 'neutral'
}

function extractKeywords(text: string): string[] {
  const words = text.toLowerCase().split(/\s+/)
  const keywords = ['work', 'stress', 'anxiety', 'sleep', 'exercise', 'family', 'friends', 'goals', 'gratitude', 'mindfulness']
  return keywords.filter(keyword => words.some(word => word.includes(keyword)))
}