// API configuration and utilities for MantraPath backend integration

// Environment-aware API base URL configuration
const API_BASE_URL = typeof window !== 'undefined' 
  ? (process.env.NODE_ENV === 'production' 
    ? window.location.origin // Use same origin in production
    : 'http://localhost:8000' // API Gateway URL for development
  )
  : 'http://localhost:8000' // Fallback for SSR

// Helper to get auth token (this would be managed by your auth system)
const getAuthToken = () => {
  // This should be replaced with your actual auth token management
  if (typeof window !== 'undefined') {
    return localStorage.getItem('auth_token') || ''
  }
  return ''
}

// Generic API request function
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`
  const token = getAuthToken()
  
  const config: RequestInit = {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options.headers,
    },
  }

  try {
    const response = await fetch(url, config)
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    return await response.json()
  } catch (error) {
    console.error('API request failed:', error)
    throw error
  }
}

// Community API functions
export const communityApi = {
  // Forums
  getForums: () => apiRequest<any[]>('/forums'),
  createForum: (data: any) => apiRequest('/forums', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  getForum: (forumId: string) => apiRequest(`/forums/${forumId}`),
  updateForum: (forumId: string, data: any) => apiRequest(`/forums/${forumId}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  }),
  deleteForum: (forumId: string) => apiRequest(`/forums/${forumId}`, {
    method: 'DELETE',
  }),
  
  // Forum membership
  joinForum: (forumId: string) => apiRequest(`/forums/${forumId}/join`, {
    method: 'POST',
  }),
  leaveForum: (forumId: string) => apiRequest(`/forums/${forumId}/leave`, {
    method: 'DELETE',
  }),
  getForumMembers: (forumId: string) => apiRequest(`/forums/${forumId}/members`),
  
  // Threads
  getForumThreads: (forumId: string) => apiRequest(`/forums/${forumId}/threads`),
  createThread: (data: any) => apiRequest('/forums/thread', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  getThread: (threadId: string) => apiRequest(`/forums/thread/${threadId}`),
  updateThread: (threadId: string, data: any) => apiRequest(`/forums/thread/${threadId}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  }),
  deleteThread: (threadId: string) => apiRequest(`/forums/thread/${threadId}`, {
    method: 'DELETE',
  }),
  replyToThread: (threadId: string, data: any) => apiRequest(`/forums/thread/${threadId}/reply`, {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  trackThreadView: (threadId: string) => apiRequest(`/forums/thread/${threadId}/view`, {
    method: 'POST',
  }),
  
  // Likes and interactions
  likeContent: (data: { content_type: string; content_id: string }) => 
    apiRequest('/forums/like', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  getLikeStatus: (contentType: string, contentId: string) => 
    apiRequest(`/forums/like/${contentType}/${contentId}`),
  removeLike: (contentType: string, contentId: string) => 
    apiRequest(`/forums/like/${contentType}/${contentId}`, {
      method: 'DELETE',
    }),
  
  // Comments
  addComment: (data: any) => apiRequest('/forums/comment', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  
  // Search
  searchCommunity: (query: string) => apiRequest(`/forums/search?q=${encodeURIComponent(query)}`),
  
  // Events and challenges
  getEvents: () => apiRequest('/forums/events'),
  createEvent: (data: any) => apiRequest('/forums/events', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  getChallenges: () => apiRequest('/forums/challenges'),
  createChallenge: (data: any) => apiRequest('/forums/challenges', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  
  // Tags
  getTags: () => apiRequest('/forums/tags'),
  createTag: (data: any) => apiRequest('/forums/tags', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  
  // User activity
  getUserForums: () => apiRequest('/users/forums'),
  getUserActivity: (userId: string) => apiRequest(`/users/${userId}/activity`),
  getUserReputation: (userId: string) => apiRequest(`/forums/users/${userId}/reputation`),
  
  // Moderation and reporting
  reportContent: (data: any) => apiRequest('/forums/report', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  getReports: () => apiRequest('/forums/reports'),
  takeModerationAction: (data: any) => apiRequest('/forums/moderation/action', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  
  // Guidelines and support
  getGuidelines: () => apiRequest('/forums/guidelines'),
  getSupport: () => apiRequest('/forums/support'),
  
  // Media upload for community posts
  uploadMedia: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    
    return apiRequest('/api/v1/media/upload', {
      method: 'POST',
      body: formData,
      headers: {
        // Don't set Content-Type for FormData
      },
    })
  },
}

// Auth API functions
export const authApi = {
  register: (data: any) => apiRequest('/register', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  login: (data: any) => apiRequest('/login', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  logout: () => apiRequest('/logout', { method: 'POST' }),
  refreshToken: () => apiRequest('/refresh-token', { method: 'POST' }),
  getMe: () => apiRequest('/me'),
}

// Profile API functions
export const profileApi = {
  getProfile: () => apiRequest('/api/profiles/me'),
  updateProfile: (data: any) => apiRequest('/api/profiles/', {
    method: 'PATCH',
    body: JSON.stringify(data),
  }),
  getPreferences: () => apiRequest('/api/preferences/'),
  updatePreferences: (data: any) => apiRequest('/api/preferences/', {
    method: 'PATCH',
    body: JSON.stringify(data),
  }),
}

// Mood API functions
export const moodApi = {
  getMoodEntries: () => apiRequest('/api/v1/mood/'),
  createMoodEntry: (data: any) => apiRequest('/api/v1/mood/', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  getMoodAnalytics: () => apiRequest('/api/v1/mood/analytics/summary'),
  getInsights: () => apiRequest('/api/v1/insights/'),
  generateInsights: () => apiRequest('/api/v1/insights/generate', {
    method: 'POST',
  }),
  getAnalyticsOverview: () => apiRequest('/api/v1/analytics/overview'),
  getTrends: () => apiRequest('/api/v1/analytics/trends'),
  getHealthScore: () => apiRequest('/api/v1/analytics/health-score'),
  getWeeklyPatterns: () => apiRequest('/api/v1/analytics/patterns/weekly'),
}

// Chatbot API functions  
export const chatbotApi = {
  sendMessage: (data: any) => apiRequest('/api/chatbot/chat', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  enhancedChat: (data: any) => apiRequest('/api/chatbot/enhanced/chat', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  getSession: () => apiRequest('/api/chatbot/chat/session'),
  createSession: () => apiRequest('/api/chatbot/chat/session', {
    method: 'POST',
  }),
  getChatHistory: () => apiRequest('/api/chatbot/chat/history'),
  getSuggestions: () => apiRequest('/api/chatbot/chat/suggestions'),
}

// Content API functions
export const contentApi = {
  getContent: (id: string) => apiRequest(`/content/${id}`),
  getContentFeed: () => apiRequest('/content/feed'),
  searchContent: (query: string) => apiRequest(`/content/search?q=${encodeURIComponent(query)}`),
  getAffirmations: () => apiRequest('/affirmations'),
  getRandomAffirmation: () => apiRequest('/affirmations/random'),
  bookmarkContent: (contentId: string) => apiRequest(`/bookmark/${contentId}`, {
    method: 'POST',
  }),
  getBookmarks: () => apiRequest('/bookmarks'),
}

// Notification API functions
export const notificationApi = {
  sendNotification: (data: any) => apiRequest('/notify/send', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  getRecentNotifications: () => apiRequest('/notify/recent'),
  getPreferences: () => apiRequest('/notify/preferences'),
  updatePreferences: (data: any) => apiRequest('/notify/preferences', {
    method: 'PUT',
    body: JSON.stringify(data),
  }),
}

// Health check function
export const healthCheck = {
  gateway: () => apiRequest('/health'),
  auth: () => apiRequest('/auth/health'),
  community: () => apiRequest('/forums/health'),
  mood: () => apiRequest('/api/v1/mood/health'),
  chatbot: () => apiRequest('/api/chatbot/health'),
}