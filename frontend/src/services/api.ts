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
  private isBackendAvailable: boolean = true
  private backendCheckPromise: Promise<boolean> | null = null

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl
    this.token = localStorage.getItem('mantrapath_token')
    this.checkBackendAvailability()
  }

  private async checkBackendAvailability(): Promise<boolean> {
    if (this.backendCheckPromise) {
      return this.backendCheckPromise
    }

    this.backendCheckPromise = new Promise(async (resolve) => {
      try {
        console.log('🔍 Checking backend availability at:', this.baseUrl)
        const response = await fetch(`${this.baseUrl}/health`, {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' },
          signal: AbortSignal.timeout(5000) // 5 second timeout
        })
        
        this.isBackendAvailable = response.ok
        
        if (this.isBackendAvailable) {
          console.log('✅ Backend is available and healthy at', this.baseUrl)
          const healthData = await response.json()
          console.log('Backend health data:', healthData)
        } else {
          console.warn('⚠️ Backend responded but not healthy:', response.status)
        }
        
        resolve(this.isBackendAvailable)
      } catch (error) {
        console.warn('🔧 Backend not available at', this.baseUrl)
        console.warn('To start the backend services:')
        console.warn('   cd backend')
        console.warn('   python3 simple_start.py')
        console.warn('   # OR')
        console.warn('   ./start_backend.sh')
        console.warn('')
        console.warn('Using mock data mode until backend is available...')
        this.isBackendAvailable = false
        resolve(false)
      }
    })

    return this.backendCheckPromise
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
    const backendAvailable = await this.checkBackendAvailability()
    
    if (!backendAvailable) {
      return this.handleMockRequest<T>(endpoint, options)
    }

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
      // Only fall back to mock data for network/connection errors
      // Don't use mock data for authentication or other API errors
      console.error('API request failed:', error)
      
      if (error instanceof TypeError && error.message.includes('Failed to fetch')) {
        // Network error - backend might be down
        console.warn('Network error detected, backend may be unavailable')
        this.isBackendAvailable = false
        return this.handleMockRequest<T>(endpoint, options)
      }
      
      // For other errors (auth, validation, etc.), throw the error
      throw error
    }
  }

  private handleMockRequest<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    console.log('🔧 Using mock data for:', endpoint)
    
    // Mock authentication responses
    if (endpoint === '/login' && options.method === 'POST') {
      return Promise.resolve({
        access_token: 'mock_access_token_' + Date.now(),
        refresh_token: 'mock_refresh_token_' + Date.now(),
        token_type: 'bearer'
      } as T)
    }

    if (endpoint === '/register' && options.method === 'POST') {
      return Promise.resolve({
        access_token: 'mock_access_token_' + Date.now(),
        refresh_token: 'mock_refresh_token_' + Date.now(),
        token_type: 'bearer'
      } as T)
    }

    if (endpoint === '/me') {
      return Promise.resolve({
        id: 'mock_user_' + Date.now(),
        email: 'user@example.com',
        username: 'demo_user',
        is_active: true,
        role: 'user'
      } as T)
    }

    // Mock mood data
    if (endpoint.startsWith('/api/v1/mood/') && options.method !== 'POST') {
      const mockMoods = Array.from({ length: 30 }, (_, i) => ({
        id: `mood_${i}`,
        mood_score: Math.floor(Math.random() * 10) + 1,
        energy_level: Math.floor(Math.random() * 10) + 1,
        stress_level: Math.floor(Math.random() * 10) + 1,
        sleep_quality: Math.floor(Math.random() * 10) + 1,
        notes: `Mock mood entry ${i}`,
        context_tags: ['work', 'exercise', 'sleep'][Math.floor(Math.random() * 3)] ? ['work'] : [],
        created_at: new Date(Date.now() - i * 24 * 60 * 60 * 1000).toISOString()
      }))
      return Promise.resolve(mockMoods as T)
    }

    if (endpoint.startsWith('/api/v1/mood/') && options.method === 'POST') {
      return Promise.resolve({
        id: 'mood_' + Date.now(),
        message: 'Mood entry created successfully'
      } as T)
    }

    // Mock journal data
    if (endpoint.startsWith('/api/v1/journal/') && options.method !== 'POST') {
      const mockJournals = Array.from({ length: 10 }, (_, i) => ({
        id: `journal_${i}`,
        title: `Journal Entry ${i + 1}`,
        content: `This is a mock journal entry content for entry ${i + 1}. It contains reflective thoughts and daily experiences.`,
        mood_before: Math.floor(Math.random() * 10) + 1,
        mood_after: Math.floor(Math.random() * 10) + 1,
        sentiment_score: Math.random() * 2 - 1,
        sentiment_label: ['positive', 'neutral', 'negative'][Math.floor(Math.random() * 3)],
        themes: ['gratitude', 'work', 'family', 'health'][Math.floor(Math.random() * 4)] ? ['gratitude'] : [],
        is_private: false,
        created_at: new Date(Date.now() - i * 24 * 60 * 60 * 1000).toISOString()
      }))
      return Promise.resolve(mockJournals as T)
    }

    if (endpoint.startsWith('/api/v1/journal/') && options.method === 'POST') {
      return Promise.resolve({
        id: 'journal_' + Date.now(),
        message: 'Journal entry created successfully'
      } as T)
    }

    // Mock analytics data
    if (endpoint.startsWith('/api/v1/analytics/')) {
      if (endpoint.includes('overview')) {
        return Promise.resolve({
          average_mood: 7.2,
          mood_trend: 'improving',
          total_entries: 45,
          streak: 7,
          weekly_pattern: {
            'monday': 6.5,
            'tuesday': 7.0,
            'wednesday': 7.5,
            'thursday': 7.2,
            'friday': 8.0,
            'saturday': 8.5,
            'sunday': 7.8
          },
          monthly_summary: {
            average_mood: 7.2,
            best_day: 'Friday',
            worst_day: 'Monday'
          }
        } as T)
      }

      if (endpoint.includes('patterns/weekly')) {
        return Promise.resolve({
          weekly_averages: {
            'monday': 6.5,
            'tuesday': 7.0,
            'wednesday': 7.5,
            'thursday': 7.2,
            'friday': 8.0,
            'saturday': 8.5,
            'sunday': 7.8
          },
          patterns: [
            {
              type: 'improvement',
              severity: 'mild',
              message: 'Your mood tends to improve throughout the week',
              recommendation: 'Keep up your weekend self-care routine'
            }
          ],
          total_weeks: 6
        } as T)
      }
    }

    // Mock community data - More comprehensive
    if (endpoint.startsWith('/forums') && options.method !== 'POST') {
      if (endpoint.includes('/replies')) {
        // Mock replies for thread
        const mockReplies = [
          {
            id: 'reply_1',
            thread_id: 'thread_1',
            content: 'That\'s amazing! Small steps really do add up. Keep going! 💪',
            author: {
              id: 'user_2',
              name: 'Emma Johnson',
              avatar_url: null,
              badges: []
            },
            created_at: new Date(Date.now() - 1800000).toISOString(),
            like_count: 5,
            is_liked: false,
            parent_id: null
          },
          {
            id: 'reply_2',
            thread_id: 'thread_1',
            content: 'I totally understand this feeling. Even a 5-minute walk is better than staying inside all day. Proud of you!',
            author: {
              id: 'user_3',
              name: 'Mike Chen',
              avatar_url: null,
              badges: []
            },
            created_at: new Date(Date.now() - 3000000).toISOString(),
            like_count: 3,
            is_liked: true,
            parent_id: null
          },
          {
            id: 'reply_3',
            thread_id: 'thread_1',
            content: '@Emma Johnson Thank you so much for the encouragement! It really means a lot 🙏',
            author: {
              id: 'user_4',
              name: 'Sarah Williams',
              avatar_url: null,
              badges: []
            },
            created_at: new Date(Date.now() - 1200000).toISOString(),
            like_count: 2,
            is_liked: false,
            parent_id: 'reply_1'
          },
          {
            id: 'reply_4',
            thread_id: 'thread_1',
            content: '@Mike Chen Exactly! Every step counts. Thank you for understanding ❤️',
            author: {
              id: 'user_5',
              name: 'Alex Thompson',
              avatar_url: null,
              badges: []
            },
            created_at: new Date(Date.now() - 900000).toISOString(),
            like_count: 1,
            is_liked: false,
            parent_id: 'reply_2'
          }
        ]
        return Promise.resolve(mockReplies as T)
      }
      if (endpoint.includes('/threads')) {
        // Mock threads for specific forum
        const mockThreads = [
          {
            id: 'thread_1',
            forum_id: 'forum_1',
            title: 'Small wins today! 🌟',
            content: 'I managed to go for a 10-minute walk even though I was feeling anxious. Sometimes the smallest steps matter most.',
            author: 'Sarah',
            reply_count: 8,
            view_count: 156,
            like_count: 23,
            is_liked: false,
            created_at: new Date(Date.now() - 3600000).toISOString(),
            is_pinned: false
          },
          {
            id: 'thread_2',
            forum_id: 'forum_1',
            title: 'Tips for managing morning anxiety?',
            content: 'Does anyone have good strategies for dealing with anxiety first thing in the morning? I\'ve been struggling with this lately.',
            author: 'Alex',
            reply_count: 12,
            view_count: 234,
            like_count: 18,
            is_liked: false,
            created_at: new Date(Date.now() - 7200000).toISOString(),
            is_pinned: false
          },
          {
            id: 'thread_3',
            forum_id: 'forum_2',
            title: 'Breathing techniques that work',
            content: 'Sharing some breathing exercises that have been really helpful for my anxiety. The 4-7-8 technique has been a game changer.',
            author: 'Jordan',
            reply_count: 5,
            view_count: 89,
            like_count: 31,
            is_liked: true,
            created_at: new Date(Date.now() - 10800000).toISOString(),
            is_pinned: true
          }
        ]
        return Promise.resolve(mockThreads as T)
      }
      
      const mockForums = [
        {
          id: 'forum_1',
          name: 'General Support',
          description: 'Share experiences and support each other through daily challenges',
          category: 'support',
          member_count: 1247,
          is_joined: false  // Changed from true to false for new users
        },
        {
          id: 'forum_2',
          name: 'Anxiety & Stress',
          description: 'Discussing anxiety management and stress relief techniques',
          category: 'anxiety',
          member_count: 823,
          is_joined: false
        },
        {
          id: 'forum_3',
          name: 'Achievements & Milestones',
          description: 'Celebrate your progress and inspire others with your journey',
          category: 'achievements',
          member_count: 567,
          is_joined: false
        }
      ]
      return Promise.resolve(mockForums as T)
    }

    // Enhanced community mock data for reputation and stats
    if (endpoint === '/user/stats') {
      const mockStats = {
        reputation: 127,
        forums_joined: 3,
        threads_liked: 24,
        threads_created: 8,
        replies_posted: 15,
        likes_received: 31,
        help_score: 7.2
      }
      return Promise.resolve(mockStats as T)
    }

    if (endpoint.startsWith('/user/activity')) {
      const mockActivity = {
        activity: [
          {
            type: 'thread_created',
            id: 'thread_1',
            title: 'Finding balance through mindfulness',
            content: 'I wanted to share my journey with mindfulness meditation and how it has helped me find better balance in daily life...',
            forum_name: 'Mindfulness & Meditation',
            created_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
            like_count: 12
          },
          {
            type: 'reply_posted',
            id: 'reply_1', 
            content: 'Thank you for sharing this! I have been struggling with similar challenges and your insights are very helpful.',
            thread_title: 'Managing work stress during busy periods',
            created_at: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
            like_count: 8
          }
        ]
      }
      return Promise.resolve(mockActivity as T)
    }

    // Mock community actions
    if (endpoint.startsWith('/forums') && options.method === 'POST') {
      if (endpoint.includes('/join')) {
        return Promise.resolve({ message: 'Successfully joined forum' } as T)
      }
      if (endpoint.includes('/reply')) {
        return Promise.resolve({
          id: 'reply_' + Date.now(),
          message: 'Reply posted successfully'
        } as T)
      }
      if (endpoint.includes('/like')) {
        return Promise.resolve({
          message: 'Content liked successfully',
          liked: Math.random() > 0.5, // Random like/unlike for testing
          like_count: Math.floor(Math.random() * 50) + 1
        } as T)
      }
      return Promise.resolve({
        id: 'thread_' + Date.now(),
        message: 'Thread created successfully'
      } as T)
    }

    if (endpoint.startsWith('/forums') && options.method === 'DELETE') {
      if (endpoint.includes('/leave')) {
        return Promise.resolve({ message: 'Successfully left forum' } as T)
      }
      if (endpoint.includes('/like')) {
        return Promise.resolve({
          message: 'Like removed successfully',
          liked: false,
          like_count: Math.floor(Math.random() * 50)
        } as T)
      }
    }

    // Mock chatbot data
    if (endpoint.startsWith('/api/chatbot/chat') && options.method === 'POST') {
      const mockResponses = [
        "Thank you for sharing that with me. How are you feeling right now?",
        "I understand this might be challenging. Would you like to try a breathing exercise?",
        "It sounds like you're going through a lot. Remember, it's okay to take things one step at a time.",
        "Your feelings are valid. Have you tried any mindfulness practices before?"
      ]
      
      return Promise.resolve({
        response: mockResponses[Math.floor(Math.random() * mockResponses.length)],
        session_id: 'mock_session_' + Date.now(),
        message_type: 'text'
      } as T)
    }

    // Default mock response
    return Promise.resolve({
      message: 'Mock response for ' + endpoint,
      success: true
    } as T)
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
    
    // Also get and store user data for WebSocket and other services
    try {
      const userData = await this.getCurrentUser()
      localStorage.setItem('user_data', JSON.stringify(userData))
    } catch (error) {
      console.warn('Failed to get user data after login:', error)
    }
    
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
    
    // Also get and store user data for WebSocket and other services
    try {
      const currentUser = await this.getCurrentUser()
      localStorage.setItem('user_data', JSON.stringify(currentUser))
    } catch (error) {
      console.warn('Failed to get user data after registration:', error)
    }
    
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
    localStorage.removeItem('user_data') // Also clear user data
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

  async getThreadReplies(threadId: string) {
    return this.request(`/forums/thread/${threadId}/replies`)
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
    // Use the same toggle endpoint - backend will handle unlike if already liked
    return this.request('/forums/like', {
      method: 'POST',
      body: JSON.stringify({
        content_type: contentType,
        content_id: contentId,
      }),
    })
  }

  // User Stats and Reputation
  async getUserStats() {
    return this.request<{
      reputation: number
      forums_joined: number
      threads_liked: number
      threads_created: number
      replies_posted: number
      likes_received: number
      help_score: number
    }>('/user/stats')
  }

  async getUserActivity(limit: number = 10) {
    return this.request<{
      activity: Array<{
        type: 'thread_created' | 'reply_posted'
        id: string
        title?: string
        content: string
        forum_name?: string
        thread_title?: string
        created_at: string
        like_count: number
      }>
    }>(`/user/activity?limit=${limit}`)
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

  // Notification Service methods
  async getNotifications(limit: number = 20) {
    return this.request(`/notify/recent?limit=${limit}`)
  }

  async getNotificationPreferences() {
    return this.request('/notify/preferences')
  }

  async updateNotificationPreferences(preferences: any) {
    return this.request('/notify/preferences', {
      method: 'PUT',
      body: JSON.stringify(preferences)
    })
  }

  async scheduleNotification(userId: string, notificationData: any, sendAt: string) {
    return this.request('/notify/schedule', {
      method: 'POST',
      body: JSON.stringify({
        user_id: userId,
        ...notificationData,
        send_at: sendAt
      })
    })
  }

  async sendNotification(userId: string, notificationData: any) {
    return this.request(`/notify/send/${userId}`, {
      method: 'POST',
      body: JSON.stringify(notificationData)
    })
  }

  async markNotificationRead(notificationId: string) {
    return this.request(`/notify/${notificationId}/read`, {
      method: 'POST'
    })
  }

  async markAllNotificationsRead() {
    return this.request('/notify/mark-all-read', {
      method: 'POST'
    })
  }

  async getNotificationAnalytics(days: number = 30) {
    return this.request(`/notify/analytics?days=${days}`)
  }

  async triggerMoodPatternNotification(userId: string, patternType: string, patternData: any) {
    return this.request('/notify/mood-pattern', {
      method: 'POST',
      body: JSON.stringify({
        user_id: userId,
        pattern_type: patternType,
        pattern_data: patternData
      })
    })
  }
}

export const apiService = new ApiService()

// Export specific API modules for convenience
export const moodApi = {
  getEntries: apiService.getMoodEntries.bind(apiService),
  createEntry: apiService.createMoodEntry.bind(apiService),
  getAnalytics: apiService.getAnalyticsOverview.bind(apiService),
  getWeeklyPatterns: apiService.getWeeklyPatterns.bind(apiService),
}

export const communityApi = {
  getForums: apiService.getForums.bind(apiService),
  joinForum: apiService.joinForum.bind(apiService),
  leaveForum: apiService.leaveForum.bind(apiService),
  getForumThreads: apiService.getForumThreads.bind(apiService),
  createThread: apiService.createThread.bind(apiService),
  replyToThread: apiService.replyToThread.bind(apiService),
  getThreadReplies: apiService.getThreadReplies.bind(apiService),
  likeContent: apiService.likeContent.bind(apiService),
  removeLike: apiService.unlikeContent.bind(apiService),
  getUserStats: apiService.getUserStats.bind(apiService),
  getUserActivity: apiService.getUserActivity.bind(apiService),
  // Add missing functions for events and challenges
  getEvents: () => Promise.resolve([]),
  getChallenges: () => Promise.resolve([]),
  joinEvent: (eventId: string) => Promise.resolve({ message: 'Joined event' }),
  leaveEvent: (eventId: string) => Promise.resolve({ message: 'Left event' }),
  createEvent: (eventData: any) => Promise.resolve({ id: Date.now().toString(), ...eventData }),
  joinChallenge: (challengeId: string) => Promise.resolve({ message: 'Joined challenge' }),
  leaveChallenge: (challengeId: string) => Promise.resolve({ message: 'Left challenge' }),
  createChallenge: (challengeData: any) => Promise.resolve({ id: Date.now().toString(), ...challengeData }),
}

export const notificationApi = {
  getNotifications: apiService.getNotifications.bind(apiService),
  getPreferences: apiService.getNotificationPreferences.bind(apiService),
  updatePreferences: apiService.updateNotificationPreferences.bind(apiService),
  scheduleNotification: apiService.scheduleNotification.bind(apiService),
  sendNotification: apiService.sendNotification.bind(apiService),
  markAsRead: apiService.markNotificationRead.bind(apiService),
  markAllAsRead: apiService.markAllNotificationsRead.bind(apiService),
  getAnalytics: apiService.getNotificationAnalytics.bind(apiService),
  triggerMoodPattern: apiService.triggerMoodPatternNotification.bind(apiService),
}

export default apiService