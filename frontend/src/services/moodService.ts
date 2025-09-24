/**
 * Mood Service API Client
 * Integrates with the modular MantraPath Mood Service
 */

import { getServiceUrls } from '../config/api-config'
import { getAuthToken } from '../utils/auth'
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
}

export interface EmotionAnalysis {
  dominant_emotion: string;
  dominant_sentiment: string;
  emotions: Record<string, number>;
  sentiment_scores: Record<string, number>;
  confidence: number;
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
    // Use API Gateway URL for all mood service requests
    this.baseUrl = `${serviceUrls.API_BASE_URL}`;
    this.refreshToken();
  }

  refreshToken() {
    this.token = getAuthToken();
  }

  private async makeRequest<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    try {
      const url = `${this.baseUrl}${endpoint}`;
      
      const defaultOptions: RequestInit = {
        headers: {
          'Content-Type': 'application/json',
          ...(this.token && { Authorization: `Bearer ${this.token}` }),
        },
      };

      const response = await fetch(url, { ...defaultOptions, ...options });

      if (!response.ok) {
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
  async analyzeEmotion(text: string): Promise<EmotionAnalysis> {
    return this.makeRequest<EmotionAnalysis>('/api/v1/mood/analyze', {
      method: 'POST',
      body: JSON.stringify({ text }),
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