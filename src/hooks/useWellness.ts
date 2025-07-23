import { useKV } from '@github/spark/hooks'
import { MoodEntry, JournalEntry, ChatMessage, CommunityPost, UserStats } from '@/types'

export function useMoods() {
  const [moods, setMoods] = useKV<MoodEntry[]>('user-moods', [])
  
  const addMood = (mood: MoodEntry['mood'], note?: string, triggers?: string[], energy?: 'high' | 'medium' | 'low', context?: string[]) => {
    const getTimeOfDay = (): 'morning' | 'afternoon' | 'evening' | 'night' => {
      const hour = new Date().getHours()
      if (hour >= 5 && hour < 12) return 'morning'
      if (hour >= 12 && hour < 17) return 'afternoon'
      if (hour >= 17 && hour < 21) return 'evening'
      return 'night'
    }

    const newMood: MoodEntry = {
      id: Date.now().toString(),
      mood,
      timestamp: Date.now(),
      note,
      triggers,
      dayOfWeek: new Date().getDay(),
      timeOfDay: getTimeOfDay(),
      energy: energy || 'medium',
      context
    }
    setMoods(current => [newMood, ...current])
    
    // Update mood streak
    updateMoodStreak(mood)
    
    return newMood
  }

  const updateMoodStreak = (mood: MoodEntry['mood']) => {
    const moodValue = { 'very-low': 1, 'low': 2, 'neutral': 3, 'good': 4, 'excellent': 5 }[mood]
    // If mood is neutral or above, continue/start streak
    if (moodValue >= 3) {
      // This would typically update the user stats, but we'll keep it simple for now
    }
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

export function useMoodAnalytics() {
  const { moods } = useMoods()
  const { entries } = useJournal()

  const getWeeklyInsights = () => {
    const oneWeekAgo = Date.now() - (7 * 24 * 60 * 60 * 1000)
    const weekMoods = moods.filter(mood => mood.timestamp >= oneWeekAgo)
    
    if (weekMoods.length === 0) return []

    const insights = []
    
    // Analyze day of week patterns
    const dayPattern = analyzeDayOfWeekTrends(weekMoods)
    if (dayPattern) insights.push(dayPattern)
    
    // Analyze time of day patterns
    const timePattern = analyzeTimeOfDayTrends(weekMoods)
    if (timePattern) insights.push(timePattern)
    
    // Analyze trigger patterns
    const triggerPattern = analyzeTriggerTrends(weekMoods)
    if (triggerPattern) insights.push(triggerPattern)

    return insights
  }

  const getMoodPredictions = () => {
    // Simple prediction based on historical patterns
    const now = new Date()
    const currentDay = now.getDay()
    const currentHour = now.getHours()
    
    const similarMoods = moods.filter(mood => {
      const moodDate = new Date(mood.timestamp)
      return moodDate.getDay() === currentDay && 
             Math.abs(moodDate.getHours() - currentHour) <= 2
    })

    if (similarMoods.length < 3) return null

    const moodValues = { 'very-low': 1, 'low': 2, 'neutral': 3, 'good': 4, 'excellent': 5 }
    const avgMood = similarMoods.reduce((sum, mood) => sum + moodValues[mood.mood], 0) / similarMoods.length
    
    return {
      predictedMood: avgMood,
      confidence: Math.min(0.9, similarMoods.length / 10),
      basedOnEntries: similarMoods.length
    }
  }

  return {
    getWeeklyInsights,
    getMoodPredictions
  }
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

function analyzeDayOfWeekTrends(moods: MoodEntry[]) {
  const dayMoods = moods.reduce((acc, mood) => {
    const day = mood.dayOfWeek || new Date(mood.timestamp).getDay()
    if (!acc[day]) acc[day] = []
    acc[day].push(mood.mood)
    return acc
  }, {} as Record<number, string[]>)

  const dayNames = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
  const moodValues = { 'very-low': 1, 'low': 2, 'neutral': 3, 'good': 4, 'excellent': 5 }
  
  let bestDay = -1
  let worstDay = -1
  let bestAvg = 0
  let worstAvg = 6
  
  Object.entries(dayMoods).forEach(([day, dayMoodList]) => {
    if (dayMoodList.length < 2) return
    const avg = dayMoodList.reduce((sum, mood) => sum + moodValues[mood], 0) / dayMoodList.length
    if (avg > bestAvg) {
      bestAvg = avg
      bestDay = parseInt(day)
    }
    if (avg < worstAvg) {
      worstAvg = avg
      worstDay = parseInt(day)
    }
  })

  if (bestDay === -1 || Math.abs(bestAvg - worstAvg) < 0.8) return null

  return {
    type: 'day-pattern',
    insight: `Your mood tends to be ${bestAvg > worstAvg ? 'higher' : 'lower'} on ${dayNames[bestDay]}s`,
    recommendation: bestDay < worstDay 
      ? `Plan self-care for ${dayNames[worstDay]}s`
      : `Use ${dayNames[bestDay]} energy for challenging tasks`,
    confidence: Math.min(0.9, Math.abs(bestAvg - worstAvg) / 2)
  }
}

function analyzeTimeOfDayTrends(moods: MoodEntry[]) {
  const timeMoods = moods.reduce((acc, mood) => {
    const time = mood.timeOfDay || getTimeOfDayFromTimestamp(mood.timestamp)
    if (!acc[time]) acc[time] = []
    acc[time].push(mood.mood)
    return acc
  }, {} as Record<string, string[]>)

  const moodValues = { 'very-low': 1, 'low': 2, 'neutral': 3, 'good': 4, 'excellent': 5 }
  const timeAverages = Object.entries(timeMoods).map(([time, moodList]) => ({
    time,
    average: moodList.reduce((sum, mood) => sum + moodValues[mood], 0) / moodList.length,
    count: moodList.length
  })).filter(item => item.count >= 2)

  if (timeAverages.length < 2) return null

  const bestTime = timeAverages.reduce((a, b) => a.average > b.average ? a : b)
  const worstTime = timeAverages.reduce((a, b) => a.average < b.average ? a : b)

  if (Math.abs(bestTime.average - worstTime.average) < 0.8) return null

  return {
    type: 'time-pattern',
    insight: `You tend to feel best during ${bestTime.time} and lowest during ${worstTime.time}`,
    recommendation: `Schedule important activities during ${bestTime.time}, and plan self-care for ${worstTime.time}`,
    confidence: Math.min(0.8, Math.abs(bestTime.average - worstTime.average) / 2)
  }
}

function analyzeTriggerTrends(moods: MoodEntry[]) {
  const triggeredMoods = moods.filter(m => m.triggers && m.triggers.length > 0)
  if (triggeredMoods.length < 3) return null

  const triggerImpact = triggeredMoods.reduce((acc, mood) => {
    mood.triggers!.forEach(trigger => {
      if (!acc[trigger]) acc[trigger] = { total: 0, count: 0 }
      acc[trigger].total += { 'very-low': 1, 'low': 2, 'neutral': 3, 'good': 4, 'excellent': 5 }[mood.mood]
      acc[trigger].count++
    })
    return acc
  }, {} as Record<string, { total: number, count: number }>)

  const triggerAverages = Object.entries(triggerImpact)
    .map(([trigger, data]) => ({
      trigger,
      average: data.total / data.count,
      count: data.count
    }))
    .filter(item => item.count >= 2)
    .sort((a, b) => b.count - a.count)

  if (triggerAverages.length === 0) return null

  const mostCommon = triggerAverages[0]
  const impact = mostCommon.average > 3 ? 'positive' : 'negative'

  return {
    type: 'trigger-pattern',
    insight: `"${mostCommon.trigger}" appears frequently and has a ${impact} impact on your mood`,
    recommendation: impact === 'positive' 
      ? `Try to incorporate "${mostCommon.trigger}" more often`
      : `Consider strategies to manage "${mostCommon.trigger}" triggers`,
    confidence: Math.min(0.9, mostCommon.count / triggeredMoods.length)
  }
}

function getTimeOfDayFromTimestamp(timestamp: number): 'morning' | 'afternoon' | 'evening' | 'night' {
  const hour = new Date(timestamp).getHours()
  if (hour >= 5 && hour < 12) return 'morning'
  if (hour >= 12 && hour < 17) return 'afternoon'
  if (hour >= 17 && hour < 21) return 'evening'
  return 'night'
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