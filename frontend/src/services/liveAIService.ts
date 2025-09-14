/**
 * Live AI Dashboard API Service
 * Provides data for insights, crisis monitoring, and live features
 * Updated to use real backend endpoints
 */

import { getServiceUrls } from '../config/api-config'

class LiveAIService {
  private static instance: LiveAIService;
  private baseUrl: string;
  private mlServiceUrl: string;

  public static getInstance(): LiveAIService {
    if (!LiveAIService.instance) {
      LiveAIService.instance = new LiveAIService();
    }
    return LiveAIService.instance;
  }

  private getAuthHeaders() {
    const token = localStorage.getItem('mantrapath_token') || localStorage.getItem('authToken');
    return {
      'Content-Type': 'application/json',
      'Authorization': token ? `Bearer ${token}` : ''
    };
  }

  private getUserId(): string {
    // Helper method to get current user ID from auth state
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      try {
        const user = JSON.parse(storedUser);
        return user.id || user.user_id || '';
      } catch (e) {
        console.warn('Failed to parse stored user data:', e);
      }
    }
    return '';
  }

  async getInsights() {
    try {
      // Use the real unified insights endpoint from ML service
  const response = await fetch(`${this.mlServiceUrl}/api/v1/insights/unified`, {
        headers: this.getAuthHeaders()
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      const data = await response.json();
      
      // Transform to the format expected by the UI
      return {
        insights: data.aggregated_insights?.predictions?.recommendations || [
          'Continue your wellness journey',
          'Practice mindfulness today'
        ],
        moodScore: data.aggregated_insights?.mood?.current_score || 7,
        trend: data.aggregated_insights?.mood?.trend || 'stable',
        recommendations: data.aggregated_insights?.predictions?.recommendations || []
      };
    } catch (error) {
      console.warn('🔮 Insights service not available:', error);
      return {
        insights: ['Wellness insights will appear here when services are available'],
        moodScore: 0,
        trend: 'unknown',
        recommendations: []
      };
    }
  }

  async getCrisisMonitor() {
    try {
      // Use ML service alerts summary endpoint
      const response = await fetch(`${this.mlServiceUrl}/dashboard/alerts/summary`, {
        headers: this.getAuthHeaders()
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.warn('🚨 Crisis Monitor service not available:', error);
      return {
        status: 'all_clear',
        alerts: [],
        risk_level: 'low'
      };
    }
  }

  async getCommunityData() {
    try {
      // Use API service for consistent routing
      const { apiService } = await import('./api');
      const data = await apiService.getUserStats();
      
      // Transform to expected format
      return {
        totalMembers: 100, // This would come from a different endpoint
        activeMembers: 50,
        userStats: data,
        engagement: data.community_engagement_score || 0
      };
    } catch (error) {
      console.warn('👥 Community service not available:', error);
      return {
        totalMembers: 0,
        activeMembers: 0,
        userStats: null,
        engagement: 0
      };
    }
  }

  async getMoodData() {
    try {
      // Use API service for consistent routing
      const { apiService } = await import('./api');
      const data = await apiService.getMoodEntries(100);
      
      // Process mood data to get current mood
      if (data && data.length > 0) {
        const latestMood = data[0];
        return {
          current_mood: latestMood.mood_type || 'neutral',
          mood_score: latestMood.mood_score || 5,
          trend: 'stable' // Could be calculated from recent entries
        };
      }
      
      return {
        current_mood: 'neutral',
        mood_score: 5,
        trend: 'unknown'
      };
    } catch (error) {
      console.warn('😊 Mood service not available:', error);
      return {
        current_mood: 'neutral',
        mood_score: 0,
        trend: 'unknown'
      };
    }
  }

  async getEmotionDetection(text: string) {
    try {
      // Use real AI Event Processor emotion detection
  const urls = getServiceUrls();
  const response = await fetch(`${urls.AI_EVENT_PROCESSOR_URL}/api/v1/analyze/emotion`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify({ text, user_id: this.getUserId() })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.warn('🎭 Emotion detection service not available:', error);
      return {
        emotion: 'neutral',
        confidence: 0.5,
        sentiment: 'positive'
      };
    }
  }

  async getAssistanceSuggestions() {
    try {
  // Placeholder: implement when assistance suggestions endpoint exists behind gateway
  const response = await fetch(`${this.baseUrl}/notify/recent`, {
        headers: this.getAuthHeaders()
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.warn('🤖 Assistance service not available:', error);
      return {
        suggestions: [
          {
            id: '1',
            type: 'wellness',
            title: 'Take a Mindful Break',
            message: 'Consider taking a 5-minute mindfulness break to center yourself.',
            priority: 'medium',
            timestamp: new Date().toISOString()
          }
        ],
        status: 'ready',
        evaluation_score: 0.85
      };
    }
  }
}

export const liveAIService = LiveAIService.getInstance();
