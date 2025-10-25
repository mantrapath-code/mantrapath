/**
 * Mood Service API Client
 * Integrates with the modular MantraPath Mood Service
 */

import { getServiceUrls } from '../config/api-config'
import { getAuthToken, setDevToken, isDevMode } from '../utils/auth'
import { processApiError } from '../utils/errorHandling'

const serviceUrls = getServiceUrls();

export interface MoodEntry {
  id?: string;
  mood_score: number;
  energy_level?: number;
  stress_level?: number;
  description?: string;
  activities?: string[];
  tags?: string[];
  location?: string;
  primary_emotion?: string;
  primary_sentiment?: string;
  emotion_analysis?: Record<string, number>;
  context_tags?: Record<string, any>;
  created_at?: string;
  updated_at?: string;
}

export interface MoodAnalytics {
  average_mood: number;
  mood_trend: string;
  total_entries: number;
  stress_average?: number;
  energy_average?: number;
  mood_distribution: Record<string, number>;
  recent_patterns: any[];
  current_streak?: number;
  longest_streak?: number;
  emotion_distribution?: Record<string, number>;
  improvement_trend?: number;
  last_entry_date?: string;
}

// Align with backend MoodAnalysisResult schema
export interface TopEmotion {
  emotion: string;
  sentiment: string; // positive | negative | ambiguous | neutral
  confidence: number; // percentage (0-100)
  color?: string;
}

export interface EmotionAnalysisResult {
  top_emotions: TopEmotion[];
  primary_emotion: string;
  primary_sentiment: string;
  confidence_score: number; // percentage (0-100)
}

export interface MoodContext {
  user_id: string;
  context_type: 'daily' | 'weekly' | 'situational';
  mood_summary: MoodAnalytics;
  emotional_weather: {
    current_state: string;
    trend: string;
    risk_factors: string[];
    protective_factors: string[];
  };
  recommendations: string[];
}

class MoodServiceClient {
  private baseUrl: string;
  private token: string | null = null;

  constructor() {
  // Use API Gateway URL (resolved via config) and avoid hardcoded localhost fallbacks
  this.baseUrl = `${serviceUrls.API_BASE_URL}`.replace(/\/$/, '')
    
    // Auto-set dev token in development mode if no token exists
    if (isDevMode() && !getAuthToken()) {
      console.log('Development mode: Auto-setting authentication token');
      setDevToken();
    }
    
    this.refreshToken();
  }

  refreshToken() {
    this.token = getAuthToken();
    if (isDevMode() && !this.token) {
      console.warn('[MoodService] No auth token found in localStorage');
    }
  }

  private async makeRequest<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    try {
      // Refresh token before each request to ensure we have the latest
      this.refreshToken();
      
      // Debug: Check if token exists in localStorage
      const rawToken = localStorage.getItem('mantrapath_token');
      if (isDevMode()) {
        console.log('[MoodService] localStorage token check:', !!rawToken);
        console.log('[MoodService] This.token value:', !!this.token);
        if (rawToken && !this.token) {
          console.error('[MoodService] TOKEN EXISTS IN STORAGE BUT NOT IN SERVICE INSTANCE!');
        }
      }
      
      // Normalize endpoint to avoid double /api (common bug we observed)
      let normalizedEndpoint = endpoint
      if (this.baseUrl.endsWith('/api') && endpoint.startsWith('/api/')) {
        normalizedEndpoint = endpoint.replace('/api', '') // remove the first /api
      }
      const url = `${this.baseUrl}${normalizedEndpoint}`
      
      if (isDevMode()) {
        console.log(`[MoodService] Making request to: ${url}`);
        console.log(`[MoodService] Token available: ${!!this.token}`);
        if (this.token) {
          console.log(`[MoodService] Token preview: ${this.token.substring(0, 20)}...`);
        } else {
          console.error('[MoodService] No token available - request will likely fail with 401');
        }
      }
      
      // Build headers, ensuring Authorization is included if token exists
      const headers: HeadersInit = {
        'Content-Type': 'application/json',
      };

      if (this.token) {
        headers.Authorization = `Bearer ${this.token}`;
      }

      // Merge with any headers passed in options
      const mergedHeaders = { ...headers, ...(options.headers || {}) };

      if (isDevMode()) {
        console.log('[MoodService] Request headers:', mergedHeaders);
      }

      const response = await fetch(url, { ...options, headers: mergedHeaders });

      if (!response.ok) {
        if (isDevMode()) {
          console.error(`[MoodService] Request failed with status ${response.status}`);
        }
        const errorData = await response.json().catch(() => ({ message: 'Unknown error' }));
        throw new Error(errorData.detail || errorData.message || `HTTP ${response.status}`);
      }

      const responseData = await response.json();
      
      // Handle API Gateway response format
      if (responseData && typeof responseData === 'object' && 'body' in responseData && 'status_code' in responseData) {
        // Parse the body if it's a string (API Gateway format)
        if (typeof responseData.body === 'string') {
          return JSON.parse(responseData.body);
        }
        return responseData.body;
      }
      
      // Direct service response
      return responseData;
    } catch (error) {
      console.error('Mood Service API Error:', error);
      processApiError(error as Error);
      throw error;
    }
  }

  // Mood Entries
  async getMoodEntries(limit: number = 50, offset: number = 0): Promise<MoodEntry[]> {
    return this.makeRequest<MoodEntry[]>(`/api/v1/mood/entries?limit=${limit}&offset=${offset}`);
  }

  async createMoodEntry(moodData: Omit<MoodEntry, 'id' | 'created_at' | 'updated_at'>): Promise<MoodEntry> {
    return this.makeRequest<MoodEntry>('/api/v1/mood/entries', {
      method: 'POST',
      body: JSON.stringify(moodData),
    });
  }

  async getMoodEntry(entryId: string): Promise<MoodEntry> {
    return this.makeRequest<MoodEntry>(`/api/v1/mood/entries/${entryId}`);
  }

  async updateMoodEntry(entryId: string, moodData: Partial<MoodEntry>): Promise<MoodEntry> {
    return this.makeRequest<MoodEntry>(`/api/v1/mood/entries/${entryId}`, {
      method: 'PUT',
      body: JSON.stringify(moodData),
    });
  }

  async deleteMoodEntry(entryId: string): Promise<{ message: string }> {
    return this.makeRequest<{ message: string }>(`/api/v1/mood/entries/${entryId}`, {
      method: 'DELETE',
    });
  }

  // Analytics
  async getMoodAnalytics(days: number = 30): Promise<MoodAnalytics> {
    return this.makeRequest<MoodAnalytics>(`/api/v1/mood/analytics/overview?days=${days}`);
  }

  async getMoodPatterns(patternType: string = 'weekly'): Promise<any> {
    return this.makeRequest(`/api/v1/mood/analytics/patterns?pattern_type=${patternType}`);
  }

  async getMoodSummary(): Promise<any> {
    return this.makeRequest('/api/v1/mood/analytics/mood-summary');
  }

  // Emotion Analysis
  async analyzeEmotion(text: string, include_mood_entry: boolean = false, mood_score?: number): Promise<EmotionAnalysisResult> {
    const payload: Record<string, any> = { text, include_mood_entry }
    if (include_mood_entry && mood_score) {
      payload.mood_score = mood_score
    }
    return this.makeRequest<EmotionAnalysisResult>('/api/v1/mood/analyze', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  // Context
  async createMoodContext(contextData: { context_type: string; metadata?: any }): Promise<MoodContext> {
    return this.makeRequest<MoodContext>('/api/v1/mood/context', {
      method: 'POST',
      body: JSON.stringify(contextData),
    });
  }

  async getMoodContext(contextId: string): Promise<MoodContext> {
    return this.makeRequest<MoodContext>(`/api/v1/mood/context/${contextId}`);
  }

  // Health
  async getHealthStatus(): Promise<any> {
    return this.makeRequest('/api/v1/health');
  }

  async getServiceInfo(): Promise<any> {
    return this.makeRequest('/api/v1/info');
  }
}

// Create and export singleton instance
export const moodService = new MoodServiceClient();

// Export class for custom instances if needed
export { MoodServiceClient };