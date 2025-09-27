/**
 * Voice Testing Page
 * Comprehensive testing interface for voice features
 */

import React, { useState, useEffect } from 'react'
import { Card, CardHeader, CardContent, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { 
  Settings, 
  Headphones, 
  Activity, 
  CheckCircle, 
  XCircle, 
  RefreshCw,
  ExternalLink,
  Volume2
} from 'lucide-react'

import VoiceInterface from '@/components/VoiceInterface'
import { voiceServiceClient } from '@/services/voiceService'
import { voiceEventProcessorClient } from '@/services/voiceEventProcessor'

const VoiceTestingPage: React.FC = () => {
  const [serviceStatus, setServiceStatus] = useState({
    voiceService: { status: 'unknown', version: '', loading: true },
    eventProcessor: { status: 'unknown', connections: 0, loading: true }
  })
  
  const [testResults, setTestResults] = useState<any[]>([])
  const [isRunningTests, setIsRunningTests] = useState(false)
  const [customText, setCustomText] = useState('Hello! This is a test of the voice system.')
  const [voiceEvents, setVoiceEvents] = useState<any[]>([])
  const [transcriptions, setTranscriptions] = useState<string[]>([])

  useEffect(() => {
    checkServiceStatus()
    const interval = setInterval(checkServiceStatus, 30000) // Check every 30 seconds
    return () => clearInterval(interval)
  }, [])

  const checkServiceStatus = async () => {
    try {
      // Check Voice Service
      const voiceHealth = await voiceServiceClient.healthCheck()
      setServiceStatus(prev => ({
        ...prev,
        voiceService: {
          status: voiceHealth.status,
          version: voiceHealth.version || '2.0.0',
          loading: false
        }
      }))

      // Check Event Processor
      const eventHealth = await voiceEventProcessorClient.healthCheck()
      setServiceStatus(prev => ({
        ...prev,
        eventProcessor: {
          status: eventHealth.status,
          connections: eventHealth.activeConnections || 0,
          loading: false
        }
      }))
    } catch (error) {
      console.error('Failed to check service status:', error)
      setServiceStatus(prev => ({
        voiceService: { ...prev.voiceService, status: 'error', loading: false },
        eventProcessor: { ...prev.eventProcessor, status: 'error', loading: false }
      }))
    }
  }

  const runComprehensiveTests = async () => {
    setIsRunningTests(true)
    setTestResults([])
    
    const tests = [
      {
        name: 'Voice Service Health Check',
        test: async () => {
          const result = await voiceServiceClient.healthCheck()
          return { success: result.status === 'healthy', data: result }
        }
      },
      {
        name: 'Voice Service Info',
        test: async () => {
          const result = await voiceServiceClient.getServiceInfo()
          return { success: !!result.service, data: result }
        }
      },
      {
        name: 'Event Processor Health Check',
        test: async () => {
          const result = await voiceEventProcessorClient.healthCheck()
          return { success: result.status === 'healthy', data: result }
        }
      },
      {
        name: 'Event Processor Config',
        test: async () => {
          const result = await voiceEventProcessorClient.getConfig()
          return { success: !!result.voice_streaming_enabled, data: result }
        }
      },
      {
        name: 'Analytics Data',
        test: async () => {
          const result = await voiceEventProcessorClient.getAnalytics()
          return { success: !!result.totalConnections || result.totalConnections === 0, data: result }
        }
      },
      {
        name: 'Voice Session Management',
        test: async () => {
          const session = await voiceServiceClient.startSession({ userId: 'test_user' })
          if (session?.sessionId) {
            await voiceServiceClient.endSession(session.sessionId)
            return { success: true, data: { sessionId: session.sessionId } }
          }
          return { success: false, data: { error: 'No session ID returned' } }
        }
      },
      {
        name: 'Text-to-Speech Test',
        test: async () => {
          const result = await voiceServiceClient.textToSpeech({
            text: 'This is a test of the text to speech system.',
            language: 'en'
          })
          return { success: result.success, data: result }
        }
      }
    ]

    for (const testCase of tests) {
      try {
        const result = await testCase.test()
        setTestResults(prev => [...prev, {
          name: testCase.name,
          success: result.success,
          data: result.data,
          timestamp: new Date().toISOString()
        }])
      } catch (error) {
        setTestResults(prev => [...prev, {
          name: testCase.name,
          success: false,
          error: error instanceof Error ? error.message : 'Unknown error',
          timestamp: new Date().toISOString()
        }])
      }
    }
    
    setIsRunningTests(false)
  }

  const testTextToSpeech = async () => {
    try {
      const result = await voiceServiceClient.textToSpeech({
        text: customText,
        language: 'en',
        voice: 'default'
      })
      
      if (result.success && result.audioUrl) {
        const audio = new Audio(result.audioUrl)
        await audio.play()
      } else {
        alert(`Text-to-Speech failed: ${result.error}`)
      }
    } catch (error) {
      alert(`Text-to-Speech error: ${error}`)
    }
  }

  const handleTranscription = (text: string) => {
    setTranscriptions(prev => [text, ...prev.slice(0, 4)]) // Keep last 5 transcriptions
  }

  const handleVoiceEvent = (event: any) => {
    setVoiceEvents(prev => [event, ...prev.slice(0, 9)]) // Keep last 10 events
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'healthy':
      case 'active':
        return <Badge className="bg-green-100 text-green-800">Healthy</Badge>
      case 'error':
        return <Badge className="bg-red-100 text-red-800">Error</Badge>
      case 'unknown':
        return <Badge className="bg-gray-100 text-gray-800">Unknown</Badge>
      default:
        return <Badge className="bg-yellow-100 text-yellow-800">{status}</Badge>
    }
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Voice Services Testing
          </h1>
          <p className="text-gray-600 dark:text-gray-300 mt-2">
            Comprehensive testing interface for voice features and analytics
          </p>
        </div>
        <Button onClick={checkServiceStatus} variant="outline">
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh Status
        </Button>
      </div>

      {/* Service Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Voice Service</CardTitle>
            <Headphones className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <div>
                {serviceStatus.voiceService.loading ? (
                  <div className="animate-pulse">Loading...</div>
                ) : (
                  <>
                    {getStatusBadge(serviceStatus.voiceService.status)}
                    <p className="text-xs text-muted-foreground mt-1">
                      Version {serviceStatus.voiceService.version}
                    </p>
                  </>
                )}
              </div>
              <Button 
                size="sm" 
                variant="ghost"
                onClick={() => window.open('http://localhost:8011/docs', '_blank')}
              >
                <ExternalLink className="w-3 h-3 mr-1" />
                API Docs
              </Button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Voice Event Processor</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <div>
                {serviceStatus.eventProcessor.loading ? (
                  <div className="animate-pulse">Loading...</div>
                ) : (
                  <>
                    {getStatusBadge(serviceStatus.eventProcessor.status)}
                    <p className="text-xs text-muted-foreground mt-1">
                      {serviceStatus.eventProcessor.connections} active connections
                    </p>
                  </>
                )}
              </div>
              <Button 
                size="sm" 
                variant="ghost"
                onClick={() => window.open('http://localhost:8015/docs', '_blank')}
              >
                <ExternalLink className="w-3 h-3 mr-1" />
                API Docs
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Testing Interface */}
      <Tabs defaultValue="interface" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="interface">Voice Interface</TabsTrigger>
          <TabsTrigger value="tests">Service Tests</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
          <TabsTrigger value="manual">Manual Tests</TabsTrigger>
        </TabsList>

        <TabsContent value="interface" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Integrated Voice Interface</CardTitle>
            </CardHeader>
            <CardContent>
              <VoiceInterface
                onTranscription={handleTranscription}
                onVoiceEvent={handleVoiceEvent}
                showAnalytics={true}
                autoSpeak={false}
                language="en"
              />
            </CardContent>
          </Card>

          {/* Recent Transcriptions */}
          {transcriptions.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Recent Transcriptions</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {transcriptions.map((text, index) => (
                    <div key={index} className="p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                      <p className="text-sm">{text}</p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="tests" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Comprehensive Service Tests</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <Button 
                  onClick={runComprehensiveTests}
                  disabled={isRunningTests}
                  className="w-full"
                >
                  {isRunningTests ? (
                    <>
                      <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                      Running Tests...
                    </>
                  ) : (
                    <>
                      <Settings className="w-4 h-4 mr-2" />
                      Run All Tests
                    </>
                  )}
                </Button>

                {testResults.length > 0 && (
                  <div className="space-y-3">
                    {testResults.map((result, index) => (
                      <div key={index} className="border rounded-lg p-4">
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-medium">{result.name}</h4>
                          {result.success ? (
                            <CheckCircle className="w-5 h-5 text-green-500" />
                          ) : (
                            <XCircle className="w-5 h-5 text-red-500" />
                          )}
                        </div>
                        <pre className="text-xs bg-gray-100 dark:bg-gray-800 p-2 rounded overflow-x-auto">
                          {JSON.stringify(result.data || result.error, null, 2)}
                        </pre>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="analytics" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Voice Events Analytics</CardTitle>
            </CardHeader>
            <CardContent>
              {voiceEvents.length > 0 ? (
                <div className="space-y-3">
                  {voiceEvents.map((event, index) => (
                    <div key={index} className="border-l-4 border-blue-500 pl-4 py-2">
                      <div className="flex justify-between items-start">
                        <div>
                          <p className="font-medium text-blue-600">{event.eventType}</p>
                          <p className="text-sm text-gray-600">
                            {new Date(event.timestamp).toLocaleTimeString()}
                          </p>
                        </div>
                        {event.confidence && (
                          <Badge variant="outline">
                            {(event.confidence * 100).toFixed(0)}%
                          </Badge>
                        )}
                      </div>
                      {event.metadata && (
                        <pre className="text-xs mt-2 bg-gray-50 dark:bg-gray-800 p-2 rounded">
                          {JSON.stringify(event.metadata, null, 2)}
                        </pre>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <Alert>
                  <Activity className="h-4 w-4" />
                  <AlertDescription>
                    No voice events recorded yet. Start using the voice interface to see real-time analytics.
                  </AlertDescription>
                </Alert>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="manual" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Manual Testing Tools</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">
                  Custom Text for Speech Synthesis
                </label>
                <Textarea
                  value={customText}
                  onChange={(e) => setCustomText(e.target.value)}
                  placeholder="Enter text to convert to speech..."
                  className="mb-2"
                />
                <Button onClick={testTextToSpeech} className="w-full">
                  <Volume2 className="w-4 h-4 mr-2" />
                  Test Text-to-Speech
                </Button>
              </div>

              <div className="pt-4 border-t">
                <h4 className="font-medium mb-2">Quick Service URLs</h4>
                <div className="space-y-2 text-sm">
                  <div>
                    <strong>Voice Service:</strong>{' '}
                    <a 
                      href="http://localhost:8011" 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:underline"
                    >
                      http://localhost:8011
                    </a>
                  </div>
                  <div>
                    <strong>Voice Event Processor:</strong>{' '}
                    <a 
                      href="http://localhost:8015" 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:underline"
                    >
                      http://localhost:8015
                    </a>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

export default VoiceTestingPage