/**
 * Voice Service Debug Component
 * Use this component to test voice service integration
 */

import React, { useState, useEffect } from 'react'
import { Card, CardHeader, CardContent, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { voiceServiceClient } from '@/services/voiceService'
import { setAuthToken, getAuthToken, setDevToken } from '@/utils/auth'

const VoiceServiceDebug: React.FC = () => {
  const [status, setStatus] = useState<any>({})
  const [testResults, setTestResults] = useState<any[]>([])
  const [testText, setTestText] = useState('Hello from MantraPath voice service!')
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    runBasicTests()
  }, [])

  const runBasicTests = async () => {
    setIsLoading(true)
    const results: any[] = []

    // Test 1: Health Check
    try {
      const health = await voiceServiceClient.healthCheck()
      results.push({
        name: 'Health Check',
        success: true,
        data: health
      })
      setStatus(health)
    } catch (error) {
      results.push({
        name: 'Health Check',
        success: false,
        error: error instanceof Error ? error.message : String(error)
      })
    }

    // Test 2: Service Info
    try {
      const info = await voiceServiceClient.getServiceInfo()
      results.push({
        name: 'Service Info',
        success: true,
        data: info
      })
    } catch (error) {
      results.push({
        name: 'Service Info',
        success: false,
        error: error instanceof Error ? error.message : String(error)
      })
    }

    // Test 3: Session Creation
    try {
      const session = await voiceServiceClient.startSession({
        userId: 'debug_user',
        metadata: { test: true }
      })
      results.push({
        name: 'Session Creation',
        success: true,
        data: session
      })
    } catch (error) {
      results.push({
        name: 'Session Creation',
        success: false,
        error: error instanceof Error ? error.message : String(error)
      })
    }

    setTestResults(results)
    setIsLoading(false)
  }

  const testTTS = async () => {
    try {
      setIsLoading(true)
      const result = await voiceServiceClient.textToSpeech({
        text: testText,
        language: 'en'
      })
      
      if (result.success && result.audioUrl) {
        // Play the audio
        const audio = new Audio(result.audioUrl)
        await audio.play()
        
        // Add success result
        setTestResults(prev => [...prev, {
          name: 'Text-to-Speech',
          success: true,
          data: { audioGenerated: true, textLength: testText.length }
        }])
      } else {
        setTestResults(prev => [...prev, {
          name: 'Text-to-Speech',
          success: false,
          error: result.error
        }])
      }
    } catch (error) {
      setTestResults(prev => [...prev, {
        name: 'Text-to-Speech',
        success: false,
        error: error instanceof Error ? error.message : String(error)
      }])
    } finally {
      setIsLoading(false)
    }
  }

  const setupAuthToken = () => {
    setDevToken()
    alert('Development token set! You can now test authenticated endpoints.')
  }

  const getStatusBadge = (success: boolean) => {
    return success ? 
      <Badge className="bg-green-100 text-green-800">✅ Pass</Badge> : 
      <Badge className="bg-red-100 text-red-800">❌ Fail</Badge>
  }

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Voice Service Debug Panel</CardTitle>
          <div className="flex gap-2">
            <Button onClick={runBasicTests} disabled={isLoading}>
              Run Tests
            </Button>
            <Button onClick={setupAuthToken} variant="outline">
              Set Dev Token
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {/* Current Status */}
          <div className="mb-6">
            <h3 className="font-semibold mb-2">Current Status</h3>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-gray-600">Status:</span>
                <Badge className="ml-2">
                  {status.status || 'Unknown'}
                </Badge>
              </div>
              <div>
                <span className="text-gray-600">Version:</span>
                <span className="ml-2">{status.version || 'Unknown'}</span>
              </div>
            </div>
          </div>

          {/* Test Results */}
          <div className="mb-6">
            <h3 className="font-semibold mb-2">Test Results</h3>
            <div className="space-y-2">
              {testResults.map((result, index) => (
                <div key={index} className="flex items-center justify-between p-2 border rounded">
                  <span>{result.name}</span>
                  <div className="flex items-center gap-2">
                    {getStatusBadge(result.success)}
                    {!result.success && (
                      <span className="text-xs text-red-600">{result.error}</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* TTS Test */}
          <div className="mb-6">
            <h3 className="font-semibold mb-2">Text-to-Speech Test</h3>
            <div className="flex gap-2">
              <Input
                value={testText}
                onChange={(e) => setTestText(e.target.value)}
                placeholder="Enter text to synthesize..."
                className="flex-1"
              />
              <Button onClick={testTTS} disabled={isLoading || !testText}>
                Test TTS
              </Button>
            </div>
          </div>

          {/* Configuration Info */}
          <div>
            <h3 className="font-semibold mb-2">Configuration</h3>
            <Alert>
              <AlertDescription>
                <div className="text-sm space-y-1">
                  <div><strong>API Gateway:</strong> {import.meta.env.VITE_API_GATEWAY_URL}</div>
                  <div><strong>Auth Token:</strong> {getAuthToken() ? '✅ Present' : '❌ Missing'}</div>
                  <div><strong>Environment:</strong> {import.meta.env.MODE}</div>
                </div>
              </AlertDescription>
            </Alert>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default VoiceServiceDebug