import { useState, useEffect, useCallback } from 'react'
import { toast } from 'sonner'
import { apiService } from '@/services/api'

export interface JournalEntry {
  id: string
  title?: string
  content: string
  timestamp: string
  moodBefore?: number
  moodAfter?: number
  tags: string[]
  isPrivate: boolean
  sentiment?: {
    score: number
    label: 'positive' | 'negative' | 'neutral'
  }
  themes?: string[]
}

export interface JournalAnalytics {
  totalEntries: number
  averageSentiment: number
  mostCommonThemes: string[]
  writingStreak: number
  monthlyProgress: Record<string, number>
  sentimentTrend: Array<{
    date: string
    sentiment: number
  }>
}

export function useJournal() {
  const [entries, setEntries] = useState<JournalEntry[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [analytics, setAnalytics] = useState<JournalAnalytics | null>(null)

  // Load journal entries from backend
  const loadEntries = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)

      const backendEntries = await apiService.getJournalEntries(50)
      
      // Convert backend format to frontend format
      const formattedEntries: JournalEntry[] = backendEntries.map(entry => ({
        id: entry.id,
        title: entry.title || '',
        content: entry.content,
        timestamp: entry.created_at,
        moodBefore: entry.mood_before,
        moodAfter: entry.mood_after,
        tags: entry.themes || [],
        isPrivate: entry.is_private,
        sentiment: entry.sentiment_score !== undefined ? {
          score: entry.sentiment_score,
          label: entry.sentiment_label as 'positive' | 'negative' | 'neutral'
        } : undefined,
        themes: entry.themes
      }))

      setEntries(formattedEntries)
      generateAnalytics(formattedEntries)
      
    } catch (err) {
      console.error('Failed to load journal entries:', err)
      setError('Failed to load journal entries')
      toast.error('Failed to load journal entries')
    } finally {
      setLoading(false)
    }
  }, [])

  // Load entries on mount
  useEffect(() => {
    loadEntries()
  }, [loadEntries])

  // Add new journal entry
  const addEntry = useCallback(async (
    title: string, 
    content: string, 
    options: {
      tags?: string[]
      is_private?: boolean
      moodBefore?: number
      moodAfter?: number
      sentiment?: 'positive' | 'neutral' | 'negative'
    } = {}
  ) => {
    try {
      setLoading(true)
      setError(null)

      const backendEntry = await apiService.createJournalEntry({
        title: title,
        content: content,
        mood_before: options.moodBefore,
        mood_after: options.moodAfter,
        is_private: options.is_private ?? true
      }) as {
        id: string
        title?: string
        content: string
        mood_before?: number
        mood_after?: number
        sentiment_score?: number
        sentiment_label?: string
        themes: string[]
        is_private: boolean
        created_at: string
      }

      // Convert and add to local state
      const newEntry: JournalEntry = {
        id: backendEntry.id,
        title: backendEntry.title || '',
        content: backendEntry.content,
        timestamp: backendEntry.created_at,
        moodBefore: backendEntry.mood_before,
        moodAfter: backendEntry.mood_after,
        tags: backendEntry.themes || [],
        isPrivate: backendEntry.is_private,
        sentiment: options.sentiment ? {
          score: options.sentiment === 'positive' ? 0.8 : options.sentiment === 'negative' ? -0.8 : 0,
          label: options.sentiment
        } : (backendEntry.sentiment_score !== undefined ? {
          score: backendEntry.sentiment_score,
          label: backendEntry.sentiment_label as 'positive' | 'negative' | 'neutral'
        } : {
          score: 0,
          label: 'neutral' as 'positive' | 'negative' | 'neutral'
        }),
        themes: backendEntry.themes
      }

      setEntries(prev => [newEntry, ...prev])
      toast.success('Journal entry saved!')
      
      // Regenerate analytics
      const updatedEntries = [newEntry, ...entries]
      generateAnalytics(updatedEntries)

      return newEntry
      
    } catch (err) {
      console.error('Failed to save journal entry:', err)
      setError('Failed to save journal entry')
      toast.error('Failed to save journal entry')
      throw err
    } finally {
      setLoading(false)
    }
  }, [entries])

  // Generate analytics from entries
  const generateAnalytics = useCallback((entriesData: JournalEntry[]) => {
    if (entriesData.length === 0) {
      setAnalytics(null)
      return
    }

    const totalEntries = entriesData.length
    
    // Calculate average sentiment
    const sentimentScores = entriesData
      .filter(entry => entry.sentiment?.score !== undefined)
      .map(entry => entry.sentiment!.score)
    
    const averageSentiment = sentimentScores.length > 0 
      ? sentimentScores.reduce((sum, score) => sum + score, 0) / sentimentScores.length
      : 0

    // Find most common themes
    const themeCount: Record<string, number> = {}
    entriesData.forEach(entry => {
      entry.themes?.forEach(theme => {
        themeCount[theme] = (themeCount[theme] || 0) + 1
      })
    })
    
    const mostCommonThemes = Object.entries(themeCount)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 5)
      .map(([theme]) => theme)

    // Calculate writing streak
    const writingStreak = calculateWritingStreak(entriesData)

    // Generate monthly progress
    const monthlyProgress = groupEntriesByMonth(entriesData)

    // Generate sentiment trend
    const sentimentTrend = entriesData
      .filter(entry => entry.sentiment?.score !== undefined)
      .slice(0, 30) // Last 30 entries
      .reverse()
      .map(entry => ({
        date: entry.timestamp.split('T')[0],
        sentiment: entry.sentiment!.score
      }))

    setAnalytics({
      totalEntries,
      averageSentiment,
      mostCommonThemes,
      writingStreak,
      monthlyProgress,
      sentimentTrend
    })
  }, [])

  // Delete entry
  const deleteEntry = useCallback(async (id: string) => {
    // Note: Backend delete endpoint would need to be implemented
    setEntries(prev => prev.filter(entry => entry.id !== id))
    toast.success('Journal entry deleted')
  }, [])

  // Search entries
  const searchEntries = useCallback((query: string) => {
    if (!query.trim()) return entries
    
    const searchTerms = query.toLowerCase().split(' ')
    
    return entries.filter(entry => {
      const searchText = `${entry.title} ${entry.content}`.toLowerCase()
      return searchTerms.some(term => searchText.includes(term))
    })
  }, [entries])

  // Filter entries by mood range
  const filterByMood = useCallback((minMood: number, maxMood: number) => {
    return entries.filter(entry => {
      const mood = entry.moodBefore || entry.moodAfter
      return mood !== undefined && mood >= minMood && mood <= maxMood
    })
  }, [entries])

  // Get entries by theme
  const getEntriesByTheme = useCallback((theme: string) => {
    return entries.filter(entry => 
      entry.themes?.includes(theme) || entry.tags.includes(theme)
    )
  }, [entries])

  return {
    entries,
    loading,
    error,
    analytics,
    hasMore: false, // You can implement pagination logic here
    isOnline: true, // You can implement online/offline detection here
    addEntry,
    updateEntry: addEntry, // Using addEntry for now, you can implement a separate updateEntry function
    deleteEntry,
    searchEntries,
    loadMore: loadEntries, // Using loadEntries for now, you can implement proper pagination
    refresh: loadEntries,
    filterByMood,
    getEntriesByTheme,
    refreshAnalytics: () => generateAnalytics(entries)
  }
}

// Helper functions
function calculateWritingStreak(entries: JournalEntry[]): number {
  if (entries.length === 0) return 0
  
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  
  let streak = 0
  let currentDate = new Date(today)
  
  // Sort entries by date (newest first)
  const sortedEntries = entries.sort((a, b) => 
    new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
  )
  
  // Check each day going backwards
  for (let i = 0; i < 365; i++) { // Maximum of 1 year
    const hasEntryOnDate = sortedEntries.some(entry => {
      const entryDate = new Date(entry.timestamp)
      entryDate.setHours(0, 0, 0, 0)
      return entryDate.getTime() === currentDate.getTime()
    })
    
    if (hasEntryOnDate) {
      streak++
    } else {
      break
    }
    
    // Move to previous day
    currentDate.setDate(currentDate.getDate() - 1)
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