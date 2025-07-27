/**
 * API service for connecting to MantraPath backend
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

interface ApiError {
  message: string
  status: number
}

class ApiService {
  private baseUrl: string
  private token: string | null = null

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl
    this.token = localStorage.getItem('mantrapath_token')
  }

  private getHeaders(): HeadersInit {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    }

    if (this.token) {
      headers.Authorization = `Bearer ${this.token}`
    }

    return headers
  }

  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      const error: ApiError = {
        message: response.statusText || 'An error occurred',
        status: response.status
      }
      
      if (response.status === 401) {
        this.logout()
      }
      
      throw error
    }

    const contentType = response.headers.get('content-type')
    if (contentType && contentType.includes('application/json')) {
      return response.json()
    }

    return response.text() as any
  }

  async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`
    
    const config: RequestInit = {
      ...options,
      headers: {
        ...this.getHeaders(),
        ...options.headers,
      },
    }

    try {
      const response = await fetch(url, config)
      return this.handleResponse<T>(response)
    } catch (error) {
      console.error('API request failed:', error)
      throw error
    }
  }

  // Auth methods
  async login(email: string, password: string) {
    const response = await this.request<{access_token: string, refresh_token: string}>('/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    })

    this.token = response.access_token
    localStorage.setItem('mantrapath_token', response.access_token)
    localStorage.setItem('mantrapath_refresh_token', response.refresh_token)
    
    return response
  }

  async register(userData: {
    email: string
    username: string
    password: string
    first_name?: string
    last_name?: string
  }) {
    const response = await this.request<{access_token: string, refresh_token: string}>('/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    })

    this.token = response.access_token
    localStorage.setItem('mantrapath_token', response.access_token)
    localStorage.setItem('mantrapath_refresh_token', response.refresh_token)
    
    return response
  }

  async getCurrentUser() {
    return this.request<{
      id: string
      email: string
      username: string
      is_active: boolean
      role: string
    }>('/me')
  }

  logout() {
    this.token = null
    localStorage.removeItem('mantrapath_token')
    localStorage.removeItem('mantrapath_refresh_token')
  }

  // Mood tracking
  async getMoodEntries(limit: number = 50) {
    return this.request<Array<{
      id: string
      mood_score: number
      energy_level?: number
      stress_level?: number
      sleep_quality?: number
      notes?: string
      context_tags: string[]
      created_at: string
    }>>(`/api/v1/mood/?limit=${limit}`)
  }

  async createMoodEntry(moodData: {
    mood_score: number
    energy_level?: number
    stress_level?: number
    sleep_quality?: number
    notes?: string
    context_tags?: string[]
  }) {
    return this.request('/api/v1/mood/', {
      method: 'POST',
      body: JSON.stringify(moodData),
    })
  }

  // Journal
  async getJournalEntries(limit: number = 20) {
    return this.request<Array<{
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
    }>>(`/api/v1/journal/?limit=${limit}`)
  }

  async createJournalEntry(journalData: {
    title?: string
    content: string
    mood_before?: number
    mood_after?: number
    is_private?: boolean
  }) {
    return this.request('/api/v1/journal/', {
      method: 'POST',
      body: JSON.stringify(journalData),
    })
  }

  // Analytics
  async getAnalyticsOverview() {
    return this.request<{
      average_mood: number
      mood_trend: string
      total_entries: number
      streak: number
      weekly_pattern: Record<string, number>
      monthly_summary: Record<string, any>
    }>('/api/v1/analytics/overview')
  }

  async getWeeklyPatterns() {
    return this.request<{
      weekly_averages: Record<string, number>
      patterns: Array<{
        type: string
        severity: string
        message: string
        recommendation: string
      }>
      total_weeks: number
    }>('/api/v1/analytics/patterns/weekly')
  }

  // Community
  async getForums() {
    return this.request<Array<{
      id: string
      name: string
      description: string
      category: string
      member_count: number
      is_joined: boolean
    }>>('/forums')
  }

  async joinForum(forumId: string) {
    return this.request(`/forums/${forumId}/join`, {
      method: 'POST',
    })
  }

  async leaveForum(forumId: string) {
    return this.request(`/forums/${forumId}/leave`, {
      method: 'DELETE',
    })
  }

  async getForumThreads(forumId: string, limit: number = 20) {
    return this.request<Array<{
      id: string
      forum_id: string
      title: string
      content: string
      author: string
      reply_count: number
      view_count: number
      created_at: string
      is_pinned: boolean
    }>>(`/forums/${forumId}/threads?limit=${limit}`)
  }

  async createThread(threadData: {
    forum_id: string
    title: string
    content: string
  }) {
    return this.request('/forums/thread', {
      method: 'POST',
      body: JSON.stringify(threadData),
    })
  }

  async replyToThread(threadId: string, content: string, parentId?: string) {
    return this.request(`/forums/thread/${threadId}/reply`, {
      method: 'POST',
      body: JSON.stringify({
        thread_id: threadId,
        content,
        parent_id: parentId,
      }),
    })
  }

  async likeContent(contentType: string, contentId: string) {
    return this.request('/forums/like', {
      method: 'POST',
      body: JSON.stringify({
        content_type: contentType,
        content_id: contentId,
      }),
    })
  }

  async unlikeContent(contentType: string, contentId: string) {
    return this.request(`/forums/like/${contentType}/${contentId}`, {
      method: 'DELETE',
    })
  }

  // Chatbot
  async chatWithBot(message: string, sessionId?: string) {
    return this.request<{
      response: string
      session_id: string
      message_type: string
      breathing_exercise?: {
        name: string
        description: string
        steps: Array<{
          action: string
          duration: number
          instruction: string
        }>
        cycles: number
      }
    }>('/api/chatbot/chat', {
      method: 'POST',
      body: JSON.stringify({
        message,
        session_id: sessionId,
      }),
    })
  }

  async getChatSessions() {
    return this.request<Array<{
      id: string
      title: string
      session_type: string
      is_active: boolean
      created_at: string
    }>>('/api/chatbot/chat/sessions')
  }

  async getChatHistory(sessionId: string) {
    return this.request<Array<{
      id: string
      sender: string
      content: string
      message_type: string
      created_at: string
    }>>(`/api/chatbot/chat/history?session_id=${sessionId}`)
  }

  async createChatSession() {
    return this.request('/api/chatbot/chat/session', {
      method: 'POST',
    })
  }

  async getBreathingExercises() {
    return this.request<{
      exercises: Record<string, {
        name: string
        description: string
        steps: Array<{
          action: string
          duration: number
          instruction: string
        }>
        cycles: number
      }>
    }>('/api/chatbot/breathing-exercises')
  }

  // Health check
  async healthCheck() {
    return this.request('/health')
  }
}

export const apiService = new ApiService()
export default apiService