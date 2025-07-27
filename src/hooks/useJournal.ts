import { useState, useEffect, useCallback } from 'react'
import { toast } from 'sonner'
import type { 
  JournalEntry, 
  JournalAnalytics
} from '@/types'

// Enhanced journal hook with backend integration
export function useJournal() {
  const [entries, setEntries] = useState<JournalEntry[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [analytics, setAnalytics] = useState<JournalAnalytics | null>(null)
  const [hasMore, setHasMore] = useState(true)
  const [currentPage, setCurrentPage] = useState(1)
  
  // Offline fallback using local storage
  const [offlineEntries, setOfflineEntries] = useState<JournalEntry[]>([])
  const [isOnline, setIsOnline] = useState(navigator.onLine)

  // Monitor online status
  useEffect(() => {
    const handleOnline = () => setIsOnline(true)
    const handleOffline = () => setIsOnline(false)

    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)

    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [])

  // Load entries (simplified mock version for now)
  const loadEntries = useCallback(async (page = 1, append = false) => {
    try {
      setLoading(true)
      setError(null)

      // Mock delay
      await new Promise(resolve => setTimeout(resolve, 500))

      // Mock data with more entries
      const mockEntries: JournalEntry[] = [
        {
          id: '1',
          title: 'Grateful for Today',
          content: 'Had a wonderful day with friends. Feeling grateful for the support system around me. Sometimes it\'s easy to forget how blessed we are with the people in our lives.',
          sentiment: 'positive',
          timestamp: Date.now() - 1000 * 60 * 60 * 24,
          keywords: ['grateful', 'friends', 'support'],
          tags: ['gratitude', 'social'],
          word_count: 28
        },
        {
          id: '2',
          title: 'Processing Work Stress',
          content: 'Work has been overwhelming lately. Need to find better ways to manage my stress levels. Maybe it\'s time to try meditation or take short breaks throughout the day.',
          sentiment: 'negative',
          timestamp: Date.now() - 1000 * 60 * 60 * 48,
          keywords: ['work', 'stress', 'overwhelming', 'meditation'],
          tags: ['work', 'stress', 'mindfulness'],
          word_count: 29
        },
        {
          id: '3',
          title: 'Peaceful Morning',
          content: 'Woke up feeling refreshed today. The sunrise was beautiful and I took some time to just appreciate the moment. These quiet times are becoming more important to me.',
          sentiment: 'positive',
          timestamp: Date.now() - 1000 * 60 * 60 * 72,
          keywords: ['peaceful', 'sunrise', 'refreshed'],
          tags: ['peace', 'nature', 'mindfulness'],
          word_count: 30
        }
      ]

      if (page > 1) {
        setHasMore(false)
        return
      }

      if (append) {
        setEntries(prev => [...prev, ...mockEntries])
      } else {
        setEntries(mockEntries)
        setOfflineEntries(mockEntries)
      }

      setHasMore(mockEntries.length >= 3)
      setCurrentPage(page)

    } catch (error) {
      console.error('Failed to load journal entries:', error)
      setError('Failed to load journal entries')
      setEntries(offlineEntries)
    } finally {
      setLoading(false)
    }
  }, [offlineEntries])

  // Load more entries (pagination)
  const loadMore = useCallback(() => {
    if (!loading && hasMore && isOnline) {
      loadEntries(currentPage + 1, true)
    }
  }, [loading, hasMore, isOnline, currentPage, loadEntries])

  // Create new journal entry
  const addEntry = useCallback(async (title: string, content: string, options?: {
    mood_id?: string
    tags?: string[]
    is_private?: boolean
  }) => {
    if (!title.trim() || !content.trim()) {
      toast.error('Title and content are required')
      return null
    }

    try {
      setLoading(true)

      const newEntry: JournalEntry = {
        id: Date.now().toString(),
        title: title.trim(),
        content: content.trim(),
        sentiment: analyzeSentiment(content.trim()),
        timestamp: Date.now(),
        keywords: extractKeywords(content.trim()),
        tags: options?.tags || [],
        is_private: options?.is_private || false,
        word_count: content.trim().split(/\s+/).length
      }

      setEntries(prev => [newEntry, ...prev])
      setOfflineEntries(prev => [newEntry, ...prev])
      
      toast.success('Journal entry saved!')
      return newEntry

    } catch (error) {
      console.error('Failed to save journal entry:', error)
      toast.error('Failed to save journal entry')
      return null
    } finally {
      setLoading(false)
    }
  }, [])

  // Update existing entry
  const updateEntry = useCallback(async (entryId: string, updates: {
    title?: string
    content?: string
    tags?: string[]
    is_private?: boolean
  }) => {
    try {
      setLoading(true)

      const updatedEntry = { ...updates, id: entryId }
      setEntries(prev => prev.map(entry => 
        entry.id === entryId ? { ...entry, ...updatedEntry } : entry
      ))
      setOfflineEntries(prev => prev.map(entry => 
        entry.id === entryId ? { ...entry, ...updatedEntry } : entry
      ))

      toast.success('Entry updated!')
      return updatedEntry

    } catch (error) {
      console.error('Failed to update entry:', error)
      toast.error('Failed to update entry')
      return null
    } finally {
      setLoading(false)
    }
  }, [])

  // Delete entry
  const deleteEntry = useCallback(async (entryId: string) => {
    try {
      setLoading(true)

      setEntries(prev => prev.filter(entry => entry.id !== entryId))
      setOfflineEntries(prev => prev.filter(entry => entry.id !== entryId))

      toast.success('Entry deleted')

    } catch (error) {
      console.error('Failed to delete entry:', error)
      toast.error('Failed to delete entry')
    } finally {
      setLoading(false)
    }
  }, [])

  // Search entries
  const searchEntries = useCallback(async (query: string) => {
    if (!query.trim()) {
      loadEntries()
      return
    }

    try {
      setLoading(true)

      // Search offline entries for now
      const filtered = offlineEntries.filter(entry =>
        entry.title.toLowerCase().includes(query.toLowerCase()) ||
        entry.content.toLowerCase().includes(query.toLowerCase()) ||
        entry.keywords.some(keyword => keyword.toLowerCase().includes(query.toLowerCase()))
      )
      setEntries(filtered)

    } catch (error) {
      console.error('Search failed:', error)
      toast.error('Search failed')
    } finally {
      setLoading(false)
    }
  }, [offlineEntries, loadEntries])

  // Initial load
  useEffect(() => {
    loadEntries()
  }, [loadEntries])

  // Load analytics when entries change
  useEffect(() => {
    if (entries.length > 0) {
      setAnalytics({
        total_entries: entries.length,
        average_word_count: entries.reduce((sum, entry) => sum + (entry.word_count || 0), 0) / entries.length,
        sentiment_distribution: {
          positive: entries.filter(e => e.sentiment === 'positive').length,
          neutral: entries.filter(e => e.sentiment === 'neutral').length,
          negative: entries.filter(e => e.sentiment === 'negative').length
        },
        writing_streak: calculateWritingStreak(entries),
        entries_by_month: groupEntriesByMonth(entries)
      })
    }
  }, [entries])

  return {
    entries,
    loading,
    error,
    analytics,
    hasMore,
    isOnline,
    addEntry,
    updateEntry,
    deleteEntry,
    searchEntries,
    loadMore,
    refresh: () => loadEntries()
  }
}

// Helper functions
function analyzeSentiment(text: string): 'positive' | 'neutral' | 'negative' {
  const positiveWords = ['happy', 'joy', 'great', 'wonderful', 'amazing', 'good', 'better', 'grateful', 'peaceful', 'love', 'excited', 'proud']
  const negativeWords = ['sad', 'angry', 'stressed', 'anxious', 'worried', 'difficult', 'hard', 'struggling', 'overwhelming', 'upset', 'frustrated', 'depressed']
  
  const words = text.toLowerCase().split(/\s+/)
  const positiveCount = words.filter(word => positiveWords.some(pos => word.includes(pos))).length
  const negativeCount = words.filter(word => negativeWords.some(neg => word.includes(neg))).length
  
  if (positiveCount > negativeCount + 1) return 'positive'
  if (negativeCount > positiveCount + 1) return 'negative'
  return 'neutral'
}

function extractKeywords(text: string): string[] {
  const keywords = ['work', 'stress', 'anxiety', 'sleep', 'exercise', 'family', 'friends', 'goals', 'gratitude', 'mindfulness', 'meditation', 'therapy', 'relationship', 'health', 'career']
  const words = text.toLowerCase().split(/\s+/)
  return keywords.filter(keyword => words.some(word => word.includes(keyword)))
}

function calculateWritingStreak(entries: JournalEntry[]): number {
  if (entries.length === 0) return 0
  
  const sortedEntries = entries.sort((a, b) => b.timestamp - a.timestamp)
  let streak = 1
  let lastDate = new Date(sortedEntries[0].timestamp).toDateString()
  
  for (let i = 1; i < sortedEntries.length; i++) {
    const currentDate = new Date(sortedEntries[i].timestamp).toDateString()
    const dayDiff = Math.floor((new Date(lastDate).getTime() - new Date(currentDate).getTime()) / (1000 * 60 * 60 * 24))
    
    if (dayDiff === 1) {
      streak++
      lastDate = currentDate
    } else {
      break
    }
  }
  
  return streak
}

function groupEntriesByMonth(entries: JournalEntry[]): Record<string, number> {
  return entries.reduce((acc, entry) => {
    const month = new Date(entry.timestamp).toISOString().substring(0, 7) // YYYY-MM
    acc[month] = (acc[month] || 0) + 1
    return acc
  }, {} as Record<string, number>)
}

// Helper functions
function analyzeSentiment(text: string): 'positive' | 'neutral' | 'negative' {
  const positiveWords = ['happy', 'joy', 'great', 'wonderful', 'amazing', 'good', 'better', 'grateful', 'peaceful', 'love', 'excited', 'proud']
  const negativeWords = ['sad', 'angry', 'stressed', 'anxious', 'worried', 'difficult', 'hard', 'struggling', 'overwhelming', 'upset', 'frustrated', 'depressed']
  
  const words = text.toLowerCase().split(/\s+/)
  const positiveCount = words.filter(word => positiveWords.some(pos => word.includes(pos))).length
  const negativeCount = words.filter(word => negativeWords.some(neg => word.includes(neg))).length
  
  if (positiveCount > negativeCount + 1) return 'positive'
  if (negativeCount > positiveCount + 1) return 'negative'
  return 'neutral'
}

function extractKeywords(text: string): string[] {
  const keywords = ['work', 'stress', 'anxiety', 'sleep', 'exercise', 'family', 'friends', 'goals', 'gratitude', 'mindfulness', 'meditation', 'therapy', 'relationship', 'health', 'career']
  const words = text.toLowerCase().split(/\s+/)
  return keywords.filter(keyword => words.some(word => word.includes(keyword)))
}

function calculateWritingStreak(entries: JournalEntry[]): number {
  if (entries.length === 0) return 0
  
  const sortedEntries = entries.sort((a, b) => b.timestamp - a.timestamp)
  let streak = 1
  let lastDate = new Date(sortedEntries[0].timestamp).toDateString()
  
  for (let i = 1; i < sortedEntries.length; i++) {
    const currentDate = new Date(sortedEntries[i].timestamp).toDateString()
    const dayDiff = Math.floor((new Date(lastDate).getTime() - new Date(currentDate).getTime()) / (1000 * 60 * 60 * 24))
    
    if (dayDiff === 1) {
      streak++
      lastDate = currentDate
    } else {
      break
    }
  }
  
  return streak
}

function groupEntriesByMonth(entries: JournalEntry[]): Record<string, number> {
  return entries.reduce((acc, entry) => {
    const month = new Date(entry.timestamp).toISOString().substring(0, 7) // YYYY-MM
    acc[month] = (acc[month] || 0) + 1
    return acc
  }, {} as Record<string, number>)
}