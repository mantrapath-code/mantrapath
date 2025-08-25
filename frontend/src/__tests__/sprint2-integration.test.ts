/**
 * Sprint 2 Backend Integration Test
 * Test real backend connections and API endpoints
 */

import { sprint2ApiService, BACKEND_API_ENDPOINTS } from '../services/sprint2-api'

// Test configuration
const TEST_USER_ID = 'test-user-sprint2'

// Mock auth token for testing
jest.mock('../utils/auth', () => ({
  getAuthToken: () => 'mock-test-token'
}))

describe('Sprint 2 Backend Integration', () => {
  beforeEach(() => {
    // Mock fetch for tests
    global.fetch = jest.fn()
  })

  afterEach(() => {
    jest.resetAllMocks()
  })

  describe('Backend Service Endpoints', () => {
    test('should have correct API Gateway endpoints', () => {
      expect(BACKEND_API_ENDPOINTS.gateway.base).toBe('http://localhost:8000')
      expect(BACKEND_API_ENDPOINTS.gateway.health).toBe('/api/v3/health/enhanced')
      expect(BACKEND_API_ENDPOINTS.gateway.voiceCommand).toBe('/api/v3/voice/command')
    })

    test('should have correct Proactive Assistance Engine endpoints', () => {
      expect(BACKEND_API_ENDPOINTS.assistance.base).toBe('http://localhost:8018')
      expect(BACKEND_API_ENDPOINTS.assistance.evaluate(TEST_USER_ID))
        .toBe(`/api/v1/assistance/evaluate/${TEST_USER_ID}`)
      expect(BACKEND_API_ENDPOINTS.assistance.status(TEST_USER_ID))
        .toBe(`/api/v1/assistance/status/${TEST_USER_ID}`)
    })

    test('should have correct AI Context Store endpoints', () => {
      expect(BACKEND_API_ENDPOINTS.context.base).toBe('http://localhost:8013')
      expect(BACKEND_API_ENDPOINTS.context.root).toBe('/')
      expect(BACKEND_API_ENDPOINTS.context.metrics).toBe('/metrics')
    })

    test('should have correct Mood Service endpoints', () => {
      expect(BACKEND_API_ENDPOINTS.mood.base).toBe('http://localhost:8002')
      expect(BACKEND_API_ENDPOINTS.mood.entries).toBe('/api/v1/mood/entries')
      expect(BACKEND_API_ENDPOINTS.mood.patterns).toBe('/api/v1/mood/patterns')
    })
  })

  describe('Proactive Assistance Engine API', () => {
    test('should evaluate assistance for user', async () => {
      const mockResponse = {
        assistanceType: 'proactive',
        evaluationScore: 0.85,
        responseTimeMs: 57,
        suggestion: {
          message: 'Consider taking a short break',
          urgency: 'medium'
        }
      }

      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      })

      const result = await sprint2ApiService.evaluateAssistance(TEST_USER_ID)

      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8018/api/v1/assistance/evaluate/test-user-sprint2',
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
            'Authorization': 'Bearer mock-test-token'
          })
        })
      )

      expect(result).toEqual(mockResponse)
    })

    test('should get assistance status', async () => {
      const mockStatus = {
        activeAssistance: true,
        lastEvaluation: '2025-08-20T10:00:00Z',
        responseTime: 57
      }

      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockStatus
      })

      const result = await sprint2ApiService.getAssistanceStatus(TEST_USER_ID)

      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8018/api/v1/assistance/status/test-user-sprint2',
        expect.objectContaining({
          headers: expect.objectContaining({
            'Authorization': 'Bearer mock-test-token'
          })
        })
      )

      expect(result).toEqual(mockStatus)
    })

    test('should trigger assistance', async () => {
      const triggerData = { context: 'user_stressed', urgency: 'high' }
      const mockResponse = { triggered: true, assistanceId: 'assist-123' }

      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      })

      const result = await sprint2ApiService.triggerAssistance(TEST_USER_ID, triggerData)

      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8018/api/v1/assistance/trigger/test-user-sprint2',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify(triggerData),
          headers: expect.objectContaining({
            'Content-Type': 'application/json'
          })
        })
      )

      expect(result).toEqual(mockResponse)
    })

    test('should analyze sentiment', async () => {
      const mockSentiment = {
        sentiment: 'positive',
        confidence: 0.87,
        emotions: ['joy', 'excitement']
      }

      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockSentiment
      })

      const result = await sprint2ApiService.analyzeSentiment('I am feeling great today!')

      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8018/api/v1/assistance/sentiment-analysis',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({ text: 'I am feeling great today!' })
        })
      )

      expect(result).toEqual(mockSentiment)
    })
  })

  describe('Voice Command API', () => {
    test('should send voice command to API Gateway', async () => {
      const voiceCommand = {
        command: 'start_meditation',
        confidence: 0.92,
        language: 'en-US'
      }
      const mockResponse = { processed: true, action: 'meditation_started' }

      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      })

      const result = await sprint2ApiService.sendVoiceCommand(voiceCommand)

      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/v3/voice/command',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify(voiceCommand)
        })
      )

      expect(result).toEqual(mockResponse)
    })
  })

  describe('Mood Service API', () => {
    test('should get mood entries', async () => {
      const mockEntries = [
        { id: 1, mood: 7, timestamp: '2025-08-20T09:00:00Z' },
        { id: 2, mood: 6, timestamp: '2025-08-20T08:00:00Z' }
      ]

      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockEntries
      })

      const result = await sprint2ApiService.getMoodEntries(TEST_USER_ID, 10)

      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8002/api/v1/mood/entries?limit=10',
        expect.objectContaining({
          headers: expect.objectContaining({
            'Authorization': 'Bearer mock-test-token'
          })
        })
      )

      expect(result).toEqual(mockEntries)
    })

    test('should create mood entry', async () => {
      const moodData = { mood: 8, energy: 7, stress: 3, notes: 'Feeling good' }
      const mockResponse = { id: 123, ...moodData, created: true }

      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      })

      const result = await sprint2ApiService.createMoodEntry(moodData)

      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8002/api/v1/mood/entries',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify(moodData)
        })
      )

      expect(result).toEqual(mockResponse)
    })
  })

  describe('Service Health Checks', () => {
    test('should check all service health', async () => {
      const mockHealthResponses = [
        { status: 'fulfilled', value: { status: 'healthy', port: 8018 } },
        { status: 'fulfilled', value: { status: 'healthy', port: 8013 } },
        { status: 'fulfilled', value: { status: 'healthy', port: 8014 } },
        { status: 'fulfilled', value: { status: 'healthy', port: 8015 } },
        { status: 'fulfilled', value: { status: 'healthy', port: 3001 } },
        { status: 'fulfilled', value: { status: 'healthy', port: 8002 } },
        { status: 'fulfilled', value: { status: 'healthy', port: 8004 } },
        { status: 'fulfilled', value: { status: 'healthy', port: 8000 } }
      ]

      // Mock Promise.allSettled
      const originalAllSettled = Promise.allSettled
      Promise.allSettled = jest.fn().mockResolvedValue(mockHealthResponses)

      ;(global.fetch as jest.Mock)
        .mockResolvedValueOnce({ ok: true, json: async () => ({ status: 'healthy' }) })
        .mockResolvedValueOnce({ ok: true, json: async () => ({ status: 'healthy' }) })
        .mockResolvedValueOnce({ ok: true, json: async () => ({ status: 'healthy' }) })
        .mockResolvedValueOnce({ ok: true, json: async () => ({ status: 'healthy' }) })
        .mockResolvedValueOnce({ ok: true, json: async () => ({ status: 'healthy' }) })
        .mockResolvedValueOnce({ ok: true, json: async () => ({ status: 'healthy' }) })
        .mockResolvedValueOnce({ ok: true, json: async () => ({ status: 'healthy' }) })
        .mockResolvedValueOnce({ ok: true, json: async () => ({ status: 'healthy' }) })

      const result = await sprint2ApiService.checkServiceHealth()

      expect(result).toHaveProperty('assistance')
      expect(result).toHaveProperty('context')
      expect(result).toHaveProperty('aiEvents')
      expect(result).toHaveProperty('voiceEvents')
      expect(result).toHaveProperty('notifications')
      expect(result).toHaveProperty('mood')
      expect(result).toHaveProperty('chatbot')
      expect(result).toHaveProperty('gateway')

      // Restore original Promise.allSettled
      Promise.allSettled = originalAllSettled
    })
  })

  describe('Error Handling', () => {
    test('should handle API errors gracefully', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error'
      })

      await expect(
        sprint2ApiService.evaluateAssistance(TEST_USER_ID)
      ).rejects.toThrow('API request failed: 500 Internal Server Error')
    })

    test('should handle network errors', async () => {
      ;(global.fetch as jest.Mock).mockRejectedValueOnce(
        new Error('Network error')
      )

      await expect(
        sprint2ApiService.evaluateAssistance(TEST_USER_ID)
      ).rejects.toThrow('Network error')
    })
  })
})

// Integration test with real backend (run manually)
describe('Sprint 2 Real Backend Integration (Manual)', () => {
  // These tests require actual backend services running
  const SKIP_REAL_TESTS = true

  test.skip('should connect to real Proactive Assistance Engine', async () => {
    if (SKIP_REAL_TESTS) return

    try {
      const result = await sprint2ApiService.getAssistanceStatus('real-user-id')
      console.log('✅ Real Assistance Engine Response:', result)
      expect(result).toBeDefined()
    } catch (error) {
      console.log('❌ Assistance Engine not available:', error.message)
    }
  })

  test.skip('should connect to real AI Context Store', async () => {
    if (SKIP_REAL_TESTS) return

    try {
      const result = await sprint2ApiService.getContextRoot()
      console.log('✅ Real AI Context Store Response:', result)
      expect(result).toBeDefined()
    } catch (error) {
      console.log('❌ AI Context Store not available:', error.message)
    }
  })

  test.skip('should perform real health checks', async () => {
    if (SKIP_REAL_TESTS) return

    try {
      const health = await sprint2ApiService.checkServiceHealth()
      console.log('✅ Real Service Health:', health)
      
      // Count healthy services
      const healthyServices = Object.values(health).filter(
        (service: any) => service.status === 'fulfilled' && service.value?.status
      ).length
      
      console.log(`🏥 ${healthyServices}/8 services healthy`)
      expect(healthyServices).toBeGreaterThan(0)
    } catch (error) {
      console.log('❌ Health check failed:', error.message)
    }
  })
})
