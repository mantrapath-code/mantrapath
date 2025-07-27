import { useState, useEffect, useCallback } from 'react'
import { useKV } from '@github/spark/hooks'
import { toast } from 'sonner'
import { journalApi, moodApi, insightsApi } from '../services/api'
import type { 
  JournalEntry, 
  MoodEntry, 
  ApiResponse, 
  PaginatedResponse,
  JournalAnalytics,
  BackendInsight
} from '../types'

// Enhanced journal hook with backend integration
export function useJournal() {
  const [entries, setEntries] = useState<JournalEntry[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [analytics, setAnalytics] = useState<JournalAnalytics | null>(null)
  const [hasMore, setHasMore] = useState(true)
  const [currentPage, setCurrentPage] = useState(1)
  
  // Offline fallback using local storage
  const [offlineEntries, setOfflineEntries] = useKV<JournalEntry[]>('journal-entries-offline', [])
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

  // Load entries from backend or fallback to offline
  const loadEntries = useCallback(async (page = 1, append = false) => {
    if (!isOnline) {
      setEntries(offlineEntries)
      return
    }

    try {
      setLoading(true)
      setError(null)

      const response: ApiResponse<PaginatedResponse<JournalEntry>> = await journalApi.getEntries({
        limit: 10,
        offset: (page - 1) * 10,
        sort: 'desc'
      })

      const newEntries = response.data.items.map(entry => ({
        ...entry,
        timestamp: entry.created_at ? new Date(entry.created_at).getTime() : entry.timestamp,
        keywords: entry.tags || entry.keywords || []
      }))

      if (append) {
        setEntries(prev => [...prev, ...newEntries])
      } else {
        setEntries(newEntries)
        // Update offline cache
        setOfflineEntries(newEntries)
      }

      setHasMore(response.data.has_next)
      setCurrentPage(page)

    } catch (error) {
      console.error('Failed to load journal entries:', error)
      setError('Failed to load journal entries')
      // Fallback to offline data
      setEntries(offlineEntries)
      toast.error('Using offline data - some entries may be outdated')
    } finally {
      setLoading(false)
    }
  }, [isOnline, offlineEntries, setOfflineEntries])

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

      const entryData = {
        title: title.trim(),
        content: content.trim(),
        mood_id: options?.mood_id,
        tags: options?.tags || [],
        is_private: options?.is_private || false
      }

      if (isOnline) {
        const response: ApiResponse<JournalEntry> = await journalApi.createEntry(entryData)
        const newEntry = {
          ...response.data,
          timestamp: response.data.created_at ? new Date(response.data.created_at).getTime() : Date.now(),
          keywords: response.data.tags || []
        }

        setEntries(prev => [newEntry, ...prev])
        setOfflineEntries(prev => [newEntry, ...prev])
        
        toast.success('Journal entry saved!')
        
        // Try to generate insights after adding entry
        try {
          await insightsApi.generateInsights()
        } catch (error) {
          console.log('Insight generation failed, but entry was saved')
        }

        return newEntry
      } else {
        // Offline mode - save locally
        const offlineEntry: JournalEntry = {
          id: `offline-${Date.now()}`,
          title: entryData.title,
          content: entryData.content,
          sentiment: analyzeSentiment(entryData.content),
          timestamp: Date.now(),
          keywords: extractKeywords(entryData.content),
          tags: entryData.tags,
          is_private: entryData.is_private
        }

        setEntries(prev => [offlineEntry, ...prev])
        setOfflineEntries(prev => [offlineEntry, ...prev])
        
        toast.warning('Saved offline - will sync when connection is restored')
        return offlineEntry
      }

    } catch (error) {
      console.error('Failed to save journal entry:', error)
      toast.error('Failed to save journal entry')
      return null
    } finally {
      setLoading(false)
    }
  }, [isOnline, setOfflineEntries])

  // Update existing entry
  const updateEntry = useCallback(async (entryId: string, updates: {
    title?: string
    content?: string
    tags?: string[]
    is_private?: boolean
  }) => {
    try {
      setLoading(true)

      if (isOnline && !entryId.startsWith('offline-')) {
        const response: ApiResponse<JournalEntry> = await journalApi.updateEntry(entryId, updates)
        const updatedEntry = {
          ...response.data,
          timestamp: response.data.updated_at ? new Date(response.data.updated_at).getTime() : response.data.timestamp,
          keywords: response.data.tags || response.data.keywords || []
        }

        setEntries(prev => prev.map(entry => 
          entry.id === entryId ? updatedEntry : entry
        ))
        setOfflineEntries(prev => prev.map(entry => 
          entry.id === entryId ? updatedEntry : entry
        ))

        toast.success('Entry updated!')
        return updatedEntry
      } else {
        // Update offline entry
        const updatedEntry = { ...updates, id: entryId }
        setEntries(prev => prev.map(entry => 
          entry.id === entryId ? { ...entry, ...updatedEntry } : entry
        ))
        setOfflineEntries(prev => prev.map(entry => 
          entry.id === entryId ? { ...entry, ...updatedEntry } : entry
        ))

        if (!isOnline) {
          toast.warning('Updated offline - will sync when connection is restored')
        }
        return updatedEntry
      }

    } catch (error) {
      console.error('Failed to update entry:', error)
      toast.error('Failed to update entry')
      return null
    } finally {
      setLoading(false)
    }
  }, [isOnline, setOfflineEntries])

  // Delete entry
  const deleteEntry = useCallback(async (entryId: string) => {
    try {
      setLoading(true)

      if (isOnline && !entryId.startsWith('offline-')) {
        await journalApi.deleteEntry(entryId)
      }

      setEntries(prev => prev.filter(entry => entry.id !== entryId))
      setOfflineEntries(prev => prev.filter(entry => entry.id !== entryId))

      toast.success('Entry deleted')

    } catch (error) {
      console.error('Failed to delete entry:', error)
      toast.error('Failed to delete entry')
    } finally {
      setLoading(false)
    }
  }, [isOnline, setOfflineEntries])

  // Search entries
  const searchEntries = useCallback(async (query: string) => {
    if (!query.trim()) {
      loadEntries()
      return
    }

    try {
      setLoading(true)

      if (isOnline) {
        const response: ApiResponse<JournalEntry[]> = await journalApi.searchEntries(query)
        const searchResults = response.data.map(entry => ({
          ...entry,
          timestamp: entry.created_at ? new Date(entry.created_at).getTime() : entry.timestamp,
          keywords: entry.tags || entry.keywords || []
        }))
        setEntries(searchResults)
      } else {
        // Search offline entries
        const filtered = offlineEntries.filter(entry =>
          entry.title.toLowerCase().includes(query.toLowerCase()) ||
          entry.content.toLowerCase().includes(query.toLowerCase()) ||
          entry.keywords.some(keyword => keyword.toLowerCase().includes(query.toLowerCase()))
        )
        setEntries(filtered)
      }

    } catch (error) {
      console.error('Search failed:', error)
      toast.error('Search failed')
    } finally {
      setLoading(false)
    }
  }, [isOnline, offlineEntries, loadEntries])

  // Load analytics
  const loadAnalytics = useCallback(async () => {
    if (!isOnline) return

    try {
      const [sentimentResponse, themeResponse] = await Promise.all([
        journalApi.getSentimentAnalysis(),
        journalApi.getThemeAnalysis()
      ])

      setAnalytics({
        total_entries: entries.length,
        average_word_count: entries.reduce((sum, entry) => sum + entry.content.length, 0) / entries.length,
        sentiment_distribution: sentimentResponse.data,
        common_themes: themeResponse.data,
        writing_streak: calculateWritingStreak(entries),
        entries_by_month: groupEntriesByMonth(entries)
      })

    } catch (error) {
      console.error('Failed to load analytics:', error)
    }
  }, [isOnline, entries])

  // Initial load
  useEffect(() => {
    loadEntries()
  }, [loadEntries])

  // Load analytics when entries change
  useEffect(() => {
    if (entries.length > 0) {
      loadAnalytics()
    }
  }, [entries, loadAnalytics])

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