// API Service Layer for MantraPath Backend Integration
const API_BASE_URL = 'http://localhost:8000' // API Gateway URL

// Common API configuration
const getAuthHeaders = () => {
  const token = localStorage.getItem('auth_token')
  return {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` })
  }
}

const handleApiResponse = async (response: Response) => {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: 'Network error' }))
    throw new Error(error.message || 'API request failed')
  }
  return response.json()
}

// Journal API
export const journalApi = {
  // Get journal entries with pagination and filtering
  getEntries: async (params?: {
    limit?: number
    offset?: number
    sort?: 'desc' | 'asc'
    search?: string
  }) => {
    const queryParams = new URLSearchParams()
    if (params?.limit) queryParams.set('limit', params.limit.toString())
    if (params?.offset) queryParams.set('offset', params.offset.toString())
    if (params?.sort) queryParams.set('sort', params.sort)
    if (params?.search) queryParams.set('search', params.search)
    
    const response = await fetch(`${API_BASE_URL}/api/v1/journal/?${queryParams}`, {
      headers: getAuthHeaders()
    })
    return handleApiResponse(response)
  },

  // Create new journal entry
  createEntry: async (entry: {
    title: string
    content: string
    mood_id?: string
    tags?: string[]
    is_private?: boolean
  }) => {
    const response = await fetch(`${API_BASE_URL}/api/v1/journal/`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(entry)
    })
    return handleApiResponse(response)
  },

  // Get specific journal entry
  getEntry: async (entryId: string) => {
    const response = await fetch(`${API_BASE_URL}/api/v1/journal/${entryId}`, {
      headers: getAuthHeaders()
    })
    return handleApiResponse(response)
  },

  // Update journal entry
  updateEntry: async (entryId: string, updates: {
    title?: string
    content?: string
    tags?: string[]
    is_private?: boolean
  }) => {
    const response = await fetch(`${API_BASE_URL}/api/v1/journal/${entryId}`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify(updates)
    })
    return handleApiResponse(response)
  },

  // Delete journal entry
  deleteEntry: async (entryId: string) => {
    const response = await fetch(`${API_BASE_URL}/api/v1/journal/${entryId}`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    })
    return handleApiResponse(response)
  },

  // Search journal entries
  searchEntries: async (query: string) => {
    const response = await fetch(`${API_BASE_URL}/api/v1/journal/search/?q=${encodeURIComponent(query)}`, {
      headers: getAuthHeaders()
    })
    return handleApiResponse(response)
  },

  // Get sentiment analysis for journal entries
  getSentimentAnalysis: async () => {
    const response = await fetch(`${API_BASE_URL}/api/v1/journal/analytics/sentiment`, {
      headers: getAuthHeaders()
    })
    return handleApiResponse(response)
  },

  // Get theme analysis from journal entries
  getThemeAnalysis: async () => {
    const response = await fetch(`${API_BASE_URL}/api/v1/journal/analytics/themes`, {
      headers: getAuthHeaders()
    })
    return handleApiResponse(response)
  },

  // Reanalyze journal entry sentiment/themes
  reanalyzeEntry: async (entryId: string) => {
    const response = await fetch(`${API_BASE_URL}/api/v1/journal/${entryId}/reanalyze`, {
      method: 'POST',
      headers: getAuthHeaders()
    })
    return handleApiResponse(response)
  }
}

// Mood API
export const moodApi = {
  // Get mood entries
  getMoods: async (params?: {
    limit?: number
    offset?: number
    date_from?: string
    date_to?: string
  }) => {
    const queryParams = new URLSearchParams()
    if (params?.limit) queryParams.set('limit', params.limit.toString())
    if (params?.offset) queryParams.set('offset', params.offset.toString())
    if (params?.date_from) queryParams.set('date_from', params.date_from)
    if (params?.date_to) queryParams.set('date_to', params.date_to)
    
    const response = await fetch(`${API_BASE_URL}/api/v1/mood/?${queryParams}`, {
      headers: getAuthHeaders()
    })
    return handleApiResponse(response)
  },

  // Create mood entry
  createMood: async (mood: {
    mood_level: number
    energy_level?: number
    notes?: string
    context_tags?: string[]
    triggers?: string[]
  }) => {
    const response = await fetch(`${API_BASE_URL}/api/v1/mood/`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(mood)
    })
    return handleApiResponse(response)
  },

  // Update mood entry
  updateMood: async (moodId: string, updates: {
    mood_level?: number
    energy_level?: number
    notes?: string
    context_tags?: string[]
    triggers?: string[]
  }) => {
    const response = await fetch(`${API_BASE_URL}/api/v1/mood/${moodId}`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify(updates)
    })
    return handleApiResponse(response)
  },

  // Delete mood entry
  deleteMood: async (moodId: string) => {
    const response = await fetch(`${API_BASE_URL}/api/v1/mood/${moodId}`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    })
    return handleApiResponse(response)
  },

  // Get mood analytics summary
  getAnalyticsSummary: async () => {
    const response = await fetch(`${API_BASE_URL}/api/v1/mood/analytics/summary`, {
      headers: getAuthHeaders()
    })
    return handleApiResponse(response)
  },

  // Get mood predictions
  getPredictions: async () => {
    const response = await fetch(`${API_BASE_URL}/api/v1/mood/prediction/next`, {
      headers: getAuthHeaders()
    })
    return handleApiResponse(response)
  },

  // Get popular context tags
  getPopularContextTags: async () => {
    const response = await fetch(`${API_BASE_URL}/api/v1/mood/context-tags/popular`, {
      headers: getAuthHeaders()
    })
    return handleApiResponse(response)
  }
}

// Analytics API
export const analyticsApi = {
  // Get overview analytics
  getOverview: async () => {
    const response = await fetch(`${API_BASE_URL}/api/v1/analytics/overview`, {
      headers: getAuthHeaders()
    })
    return handleApiResponse(response)
  },

  // Get trend analysis
  getTrends: async () => {
    const response = await fetch(`${API_BASE_URL}/api/v1/analytics/trends`, {
      headers: getAuthHeaders()
    })
    return handleApiResponse(response)
  },

  // Get correlations
  getCorrelations: async () => {
    const response = await fetch(`${API_BASE_URL}/api/v1/analytics/correlations`, {
      headers: getAuthHeaders()
    })
    return handleApiResponse(response)
  },

  // Get health score
  getHealthScore: async () => {
    const response = await fetch(`${API_BASE_URL}/api/v1/analytics/health-score`, {
      headers: getAuthHeaders()
    })
    return handleApiResponse(response)
  },

  // Get weekly patterns
  getWeeklyPatterns: async () => {
    const response = await fetch(`${API_BASE_URL}/api/v1/analytics/patterns/weekly`, {
      headers: getAuthHeaders()
    })
    return handleApiResponse(response)
  },

  // Get seasonal patterns
  getSeasonalPatterns: async () => {
    const response = await fetch(`${API_BASE_URL}/api/v1/analytics/patterns/seasonal`, {
      headers: getAuthHeaders()
    })
    return handleApiResponse(response)
  },

  // Get mood triggers
  getMoodTriggers: async () => {
    const response = await fetch(`${API_BASE_URL}/api/v1/analytics/insights/triggers`, {
      headers: getAuthHeaders()
    })
    return handleApiResponse(response)
  },

  // Get mood boosters
  getMoodBoosters: async () => {
    const response = await fetch(`${API_BASE_URL}/api/v1/analytics/insights/boosters`, {
      headers: getAuthHeaders()
    })
    return handleApiResponse(response)
  }
}

// Insights API
export const insightsApi = {
  // Get insights
  getInsights: async () => {
    const response = await fetch(`${API_BASE_URL}/api/v1/insights/`, {
      headers: getAuthHeaders()
    })
    return handleApiResponse(response)
  },

  // Generate new insights
  generateInsights: async () => {
    const response = await fetch(`${API_BASE_URL}/api/v1/insights/generate`, {
      method: 'POST',
      headers: getAuthHeaders()
    })
    return handleApiResponse(response)
  },

  // Get unread insights
  getUnreadInsights: async () => {
    const response = await fetch(`${API_BASE_URL}/api/v1/insights/recent/unread`, {
      headers: getAuthHeaders()
    })
    return handleApiResponse(response)
  },

  // Mark insight as read
  markInsightRead: async (insightId: string) => {
    const response = await fetch(`${API_BASE_URL}/api/v1/insights/${insightId}/mark-read`, {
      method: 'POST',
      headers: getAuthHeaders()
    })
    return handleApiResponse(response)
  },

  // Mark all insights as read
  markAllInsightsRead: async () => {
    const response = await fetch(`${API_BASE_URL}/api/v1/insights/mark-all-read`, {
      method: 'POST',
      headers: getAuthHeaders()
    })
    return handleApiResponse(response)
  },

  // Provide insight feedback
  provideFeedback: async (insightId: string, feedback: {
    helpful: boolean
    comment?: string
  }) => {
    const response = await fetch(`${API_BASE_URL}/api/v1/insights/${insightId}/feedback`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(feedback)
    })
    return handleApiResponse(response)
  }
}

// Chatbot API
export const chatbotApi = {
  // Send chat message
  sendMessage: async (message: {
    message: string
    context?: any
    session_id?: string
  }) => {
    const response = await fetch(`${API_BASE_URL}/api/chatbot/chat`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(message)
    })
    return handleApiResponse(response)
  },

  // Get chat history
  getChatHistory: async () => {
    const response = await fetch(`${API_BASE_URL}/api/chatbot/chat/history`, {
      headers: getAuthHeaders()
    })
    return handleApiResponse(response)
  },

  // Get chat sessions
  getChatSessions: async () => {
    const response = await fetch(`${API_BASE_URL}/api/chatbot/chat/sessions`, {
      headers: getAuthHeaders()
    })
    return handleApiResponse(response)
  },

  // Create new chat session
  createSession: async () => {
    const response = await fetch(`${API_BASE_URL}/api/chatbot/chat/session`, {
      method: 'POST',
      headers: getAuthHeaders()
    })
    return handleApiResponse(response)
  }
}

// Community API
export const communityApi = {
  // Forums
  getForums: async () => {
    const response = await fetch(`${API_BASE_URL}/forums`, {
      headers: getAuthHeaders()
    })
    return handleApiResponse(response)
  },

  createForum: async (forum: {
    name: string
    description: string
    category: string
    tags?: string[]
  }) => {
    const response = await fetch(`${API_BASE_URL}/forums`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(forum)
    })
    return handleApiResponse(response)
  },

  getForum: async (forumId: string) => {
    const response = await fetch(`${API_BASE_URL}/forums/${forumId}`, {
      headers: getAuthHeaders()
    })
    return handleApiResponse(response)
  },

  joinForum: async (forumId: string) => {
    const response = await fetch(`${API_BASE_URL}/forums/${forumId}/join`, {
      method: 'POST',
      headers: getAuthHeaders()
    })
    return handleApiResponse(response)
  },

  leaveForum: async (forumId: string) => {
    const response = await fetch(`${API_BASE_URL}/forums/${forumId}/leave`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    })
    return handleApiResponse(response)
  },

  // Threads
  getThreads: async (forumId: string, params?: {
    limit?: number
    offset?: number
    sort?: string
  }) => {
    const queryParams = new URLSearchParams()
    if (params?.limit) queryParams.set('limit', params.limit.toString())
    if (params?.offset) queryParams.set('offset', params.offset.toString())
    if (params?.sort) queryParams.set('sort', params.sort)
    
    const response = await fetch(`${API_BASE_URL}/forums/${forumId}/threads?${queryParams}`, {
      headers: getAuthHeaders()
    })
    return handleApiResponse(response)
  },

  createThread: async (thread: {
    title: string
    content: string
    forum_id: string
    tags?: string[]
  }) => {
    const response = await fetch(`${API_BASE_URL}/forums/thread`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(thread)
    })
    return handleApiResponse(response)
  },

  getThread: async (threadId: string) => {
    const response = await fetch(`${API_BASE_URL}/forums/thread/${threadId}`, {
      headers: getAuthHeaders()
    })
    return handleApiResponse(response)
  },

  replyToThread: async (threadId: string, content: string) => {
    const response = await fetch(`${API_BASE_URL}/forums/thread/${threadId}/reply`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ content })
    })
    return handleApiResponse(response)
  },

  // Likes and interactions
  likeContent: async (contentType: 'thread' | 'reply', contentId: string) => {
    const response = await fetch(`${API_BASE_URL}/forums/like`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({
        content_type: contentType,
        content_id: contentId
      })
    })
    return handleApiResponse(response)
  },

  unlikeContent: async (contentType: 'thread' | 'reply', contentId: string) => {
    const response = await fetch(`${API_BASE_URL}/forums/like/${contentType}/${contentId}`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    })
    return handleApiResponse(response)
  },

  getLikeStatus: async (contentType: 'thread' | 'reply', contentId: string) => {
    const response = await fetch(`${API_BASE_URL}/forums/like/${contentType}/${contentId}`, {
      headers: getAuthHeaders()
    })
    return handleApiResponse(response)
  },

  // Comments
  addComment: async (comment: {
    content: string
    content_type: 'thread' | 'reply'
    content_id: string
  }) => {
    const response = await fetch(`${API_BASE_URL}/forums/comment`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(comment)
    })
    return handleApiResponse(response)
  },

  // Search
  searchCommunity: async (query: string, filters?: {
    type?: 'forum' | 'thread' | 'reply'
    category?: string
  }) => {
    const queryParams = new URLSearchParams()
    queryParams.set('q', query)
    if (filters?.type) queryParams.set('type', filters.type)
    if (filters?.category) queryParams.set('category', filters.category)
    
    const response = await fetch(`${API_BASE_URL}/forums/search?${queryParams}`, {
      headers: getAuthHeaders()
    })
    return handleApiResponse(response)
  },

  // Events and challenges
  getEvents: async () => {
    const response = await fetch(`${API_BASE_URL}/forums/events`, {
      headers: getAuthHeaders()
    })
    return handleApiResponse(response)
  },

  createEvent: async (event: {
    title: string
    description: string
    start_time: string
    end_time?: string
    forum_id?: string
    type: 'meditation' | 'discussion' | 'challenge' | 'workshop'
  }) => {
    const response = await fetch(`${API_BASE_URL}/forums/events`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(event)
    })
    return handleApiResponse(response)
  },

  getChallenges: async () => {
    const response = await fetch(`${API_BASE_URL}/forums/challenges`, {
      headers: getAuthHeaders()
    })
    return handleApiResponse(response)
  },

  createChallenge: async (challenge: {
    title: string
    description: string
    duration_days: number
    start_date: string
    forum_id?: string
    type: 'mood' | 'journal' | 'meditation' | 'activity'
  }) => {
    const response = await fetch(`${API_BASE_URL}/forums/challenges`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(challenge)
    })
    return handleApiResponse(response)
  },

  // Moderation
  reportContent: async (report: {
    content_type: 'thread' | 'reply' | 'user'
    content_id: string
    reason: string
    description?: string
  }) => {
    const response = await fetch(`${API_BASE_URL}/forums/report`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(report)
    })
    return handleApiResponse(response)
  },

  // User activity
  getUserForums: async () => {
    const response = await fetch(`${API_BASE_URL}/users/forums`, {
      headers: getAuthHeaders()
    })
    return handleApiResponse(response)
  },

  getUserActivity: async (userId: string) => {
    const response = await fetch(`${API_BASE_URL}/users/${userId}/activity`, {
      headers: getAuthHeaders()
    })
    return handleApiResponse(response)
  },

  getUserReputation: async (userId: string) => {
    const response = await fetch(`${API_BASE_URL}/forums/users/${userId}/reputation`, {
      headers: getAuthHeaders()
    })
    return handleApiResponse(response)
  }
}

// Content API (continued from previous)
export const contentApi = {
  // Get content by ID
  getContent: async (id: string) => {
    const response = await fetch(`${API_BASE_URL}/content/${id}`, {
      headers: getAuthHeaders()
    })
    return handleApiResponse(response)
  },

  // Get content by category
  getContentByCategory: async (category: string) => {
    const response = await fetch(`${API_BASE_URL}/content/category/${category}`, {
      headers: getAuthHeaders()
    })
    return handleApiResponse(response)
  },

  // Get personalized content feed
  getContentFeed: async () => {
    const response = await fetch(`${API_BASE_URL}/content/feed`, {
      headers: getAuthHeaders()
    })
    return handleApiResponse(response)
  },

  // Search content
  searchContent: async (query: string) => {
    const response = await fetch(`${API_BASE_URL}/content/search?q=${encodeURIComponent(query)}`, {
      headers: getAuthHeaders()
    })
    return handleApiResponse(response)
  },

  // Affirmations
  getAffirmations: async () => {
    const response = await fetch(`${API_BASE_URL}/affirmations`, {
      headers: getAuthHeaders()
    })
    return handleApiResponse(response)
  },

  getRandomAffirmation: async () => {
    const response = await fetch(`${API_BASE_URL}/affirmations/random`, {
      headers: getAuthHeaders()
    })
    return handleApiResponse(response)
  },

  // Bookmarks
  getBookmarks: async () => {
    const response = await fetch(`${API_BASE_URL}/bookmarks`, {
      headers: getAuthHeaders()
    })
    return handleApiResponse(response)
  },

  bookmarkContent: async (contentId: string) => {
    const response = await fetch(`${API_BASE_URL}/bookmark/${contentId}`, {
      method: 'POST',
      headers: getAuthHeaders()
    })
    return handleApiResponse(response)
  },

  removeBookmark: async (contentId: string) => {
    const response = await fetch(`${API_BASE_URL}/bookmark/${contentId}`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    })
    return handleApiResponse(response)
  }
}

// Notification API
export const notificationApi = {
  // Send notification
  sendNotification: async (notification: {
    message: string
    type?: 'info' | 'success' | 'warning' | 'error'
    recipient_id?: string
  }) => {
    const response = await fetch(`${API_BASE_URL}/notify/send`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(notification)
    })
    return handleApiResponse(response)
  },

  // Get recent notifications
  getRecentNotifications: async () => {
    const response = await fetch(`${API_BASE_URL}/notify/recent`, {
      headers: getAuthHeaders()
    })
    return handleApiResponse(response)
  },

  // Schedule notification
  scheduleNotification: async (notification: {
    message: string
    scheduled_time: string
    type?: 'info' | 'success' | 'warning' | 'error'
  }) => {
    const response = await fetch(`${API_BASE_URL}/notify/schedule`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(notification)
    })
    return handleApiResponse(response)
  },

  // Get notification preferences
  getPreferences: async () => {
    const response = await fetch(`${API_BASE_URL}/notify/preferences`, {
      headers: getAuthHeaders()
    })
    return handleApiResponse(response)
  },

  // Update notification preferences
  updatePreferences: async (preferences: {
    email_notifications?: boolean
    push_notifications?: boolean
    mood_reminders?: boolean
    journal_reminders?: boolean
    community_updates?: boolean
  }) => {
    const response = await fetch(`${API_BASE_URL}/notify/preferences`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify(preferences)
    })
    return handleApiResponse(response)
  }
}

// Error handling utility
export class ApiError extends Error {
  constructor(
    message: string,
    public status?: number,
    public code?: string
  ) {
    super(message)
    this.name = 'ApiError'
  }
}