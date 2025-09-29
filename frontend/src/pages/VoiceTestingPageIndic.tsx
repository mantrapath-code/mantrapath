/**
 * Enhanced Voice Testing Page with Indic Language Support
 * Comprehensive testing interface for voice features including IndicWav2Vec and Indic-TTS
 */

import React, { useState, useEffect } from 'react'
import { Card, CardHeader, CardContent, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { 
  Settings, 
  Headphones, 
  Activity, 
  CheckCircle, 
  XCircle, 
  RefreshCw,
  ExternalLink,
  Volume2,
  Languages,
  Mic,
  PlayCircle,
  TestTube
} from 'lucide-react'

import VoiceInterface from '@/components/VoiceInterface'
import VoiceServiceDebug from '@/components/VoiceServiceDebug'
import { voiceServiceClient, IndicLanguageInfo, VoiceTestResponse, LanguageDetectionResponse } from '@/services/voiceService'
import { voiceEventProcessorClient } from '@/services/voiceEventProcessor'

const VoiceTestingPage: React.FC = () => {
  const [serviceStatus, setServiceStatus] = useState({
    voiceService: { status: 'unknown', version: '', loading: true },
    eventProcessor: { status: 'unknown', connections: 0, loading: true }
  })
  
  const [testResults, setTestResults] = useState<any[]>([])
  const [isRunningTests, setIsRunningTests] = useState(false)
  const [customText, setCustomText] = useState('नमस्ते! यह आवाज़ प्रणाली का परीक्षण है। Hello! This is a test of the voice system.')
  const [voiceEvents, setVoiceEvents] = useState<any[]>([])
  const [transcriptions, setTranscriptions] = useState<string[]>([])
  
  // Indic Language Testing
  const [selectedLanguage, setSelectedLanguage] = useState('hi')
  const [supportedLanguages, setSupportedLanguages] = useState<IndicLanguageInfo[]>([])
  const [languageDetection, setLanguageDetection] = useState<LanguageDetectionResponse | null>(null)
  const [voiceTestResult, setVoiceTestResult] = useState<VoiceTestResponse | null>(null)
  const [isTestingPipeline, setIsTestingPipeline] = useState(false)
  const [isDetectingLanguage, setIsDetectingLanguage] = useState(false)

  // Sample texts for different languages
  const sampleTexts: Record<string, string> = {
    'hi': 'नमस्ते! आप कैसे हैं? यह हिंदी भाषा का परीक्षण है।',
    'bn': 'নমস্কার! আপনি কেমন আছেন? এটি বাংলা ভাষার পরীক্ষা।',
    'gu': 'નમસ્તે! તમે કેમ છો? આ ગુજરાતી ભાષાની પરીક્ષા છે।',
    'kn': 'ನಮಸ್ತೆ! ನೀವು ಹೇಗಿದ್ದೀರಿ? ಇದು ಕನ್ನಡ ಭಾಷೆಯ ಪರೀಕ್ಷೆ.',
    'ml': 'നമസ്തെ! നിങ്ങൾ എങ്ങനെയുണ്ട്? ഇത് മലയാളം ഭാഷയുടെ പരിശോധനയാണ്.',
    'mr': 'नमस्कार! तुम्ही कसे आहात? ही मराठी भाषेची चाचणी आहे.',
    'or': 'ନମସ୍କାର! ଆପଣ କେମିତି ଅଛନ୍ତି? ଏହା ଓଡ଼ିଆ ଭାଷାର ପରୀକ୍ଷା।',
    'pa': 'ਸਤ ਸ੍ਰੀ ਅਕਾਲ! ਤੁਸੀਂ ਕਿਵੇਂ ਹੋ? ਇਹ ਪੰਜਾਬੀ ਭਾਸ਼ਾ ਦਾ ਟੈਸਟ ਹੈ।',
    'ta': 'வணக்கம்! நீங்கள் எப்படி இருக்கிறீர்கள்? இது தமிழ் மொழியின் சோதனை.',
    'te': 'నమస్తే! మీరు ఎలా ఉన్నారు? ఇది తెలుగు భాష పరీక్ష.',
    'ur': 'السلام علیکم! آپ کیسے ہیں؟ یہ اردو زبان کا امتحان ہے۔',
    'as': 'নমস্কাৰ! আপুনি কেনে আছে? এইটো অসমীয়া ভাষাৰ পৰীক্ষা।',
    'en': 'Hello! How are you? This is an English language test.'
  }

  useEffect(() => {
    checkServiceStatus()
    loadSupportedLanguages()
    const interval = setInterval(checkServiceStatus, 30000)
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    // Update custom text when language changes
    if (sampleTexts[selectedLanguage]) {
      setCustomText(sampleTexts[selectedLanguage])
    }
  }, [selectedLanguage])

  const checkServiceStatus = async () => {
    try {
      const voiceHealth = await voiceServiceClient.healthCheck()
      setServiceStatus(prev => ({
        ...prev,
        voiceService: {
          status: voiceHealth.status,
          version: voiceHealth.version || '2.0.0',
          loading: false
        }
      }))

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

  const loadSupportedLanguages = async () => {
    try {
      const languages = await voiceServiceClient.getSupportedIndicLanguages()
      setSupportedLanguages(languages)
    } catch (error) {
      console.error('Failed to load supported languages:', error)
    }
  }

  const detectLanguage = async () => {
    if (!customText.trim()) return
    
    setIsDetectingLanguage(true)
    try {
      const result = await voiceServiceClient.detectLanguage({ text: customText })
      setLanguageDetection(result)
    } catch (error) {
      console.error('Language detection failed:', error)
    } finally {
      setIsDetectingLanguage(false)
    }
  }

  const testVoicePipeline = async () => {
    if (!customText.trim()) return
    
    setIsTestingPipeline(true)
    setVoiceTestResult(null)
    
    try {
      const result = await voiceServiceClient.testVoicePipeline({
        text: customText,
        language: selectedLanguage === 'auto' ? 'auto' : selectedLanguage
      })
      setVoiceTestResult(result)
    } catch (error) {
      console.error('Voice pipeline test failed:', error)
      setVoiceTestResult({
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
        original_text: customText,
        transcribed_text: '',
        detected_language: selectedLanguage,
        similarity_score: 0,
        tts_model: 'unknown',
        stt_model: 'unknown',
        audio_duration: 0,
        pipeline_quality: 'poor'
      })
    } finally {
      setIsTestingPipeline(false)
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
        name: 'Language Detection Test',
        test: async () => {
          const testText = 'नमस्ते! यह हिंदी का परीक्षण है।'
          const result = await voiceServiceClient.detectLanguage({ text: testText })
          return { 
            success: result.detected_language === 'hi', 
            data: { ...result, test_text: testText }
          }
        }
      },
      {
        name: 'Indic Language Support Test',
        test: async () => {
          const languages = await voiceServiceClient.getSupportedIndicLanguages()
          return { 
            success: languages.length > 0, 
            data: { supported_count: languages.length, languages }
          }
        }
      },
      {
        name: 'Voice Pipeline Test (Hindi)',
        test: async () => {
          const result = await voiceServiceClient.testVoicePipeline({
            text: 'नमस्ते! यह परीक्षण है।',
            language: 'hi'
          })
          return { 
            success: result.success && result.similarity_score > 0.5, 
            data: result
          }
        }
      },
      {
        name: 'Voice Pipeline Test (English)',
        test: async () => {
          const result = await voiceServiceClient.testVoicePipeline({
            text: 'Hello! This is a test.',
            language: 'en'
          })
          return { 
            success: result.success && result.similarity_score > 0.5, 
            data: result
          }
        }
      }
    ]

    for (const test of tests) {
      try {
        const result = await test.test()
        setTestResults(prev => [...prev, { name: test.name, ...result }])
      } catch (error) {
        setTestResults(prev => [...prev, { 
          name: test.name, 
          success: false, 
          error: error instanceof Error ? error.message : 'Unknown error' 
        }])
      }
    }
    
    setIsRunningTests(false)
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'text-green-600'
      case 'error': return 'text-red-600'
      case 'degraded': return 'text-yellow-600'
      default: return 'text-gray-600'
    }
  }

  const getQualityColor = (quality: string) => {
    switch (quality) {
      case 'excellent': return 'bg-green-100 text-green-800 border-green-200'
      case 'good': return 'bg-blue-100 text-blue-800 border-blue-200'
      case 'fair': return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      case 'poor': return 'bg-red-100 text-red-800 border-red-200'
      default: return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold flex items-center gap-2">
          <TestTube className="w-8 h-8" />
          Enhanced Voice Testing Console
        </h1>
        <Button 
          onClick={runComprehensiveTests} 
          disabled={isRunningTests}
          className="flex items-center gap-2"
        >
          {isRunningTests ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Activity className="w-4 h-4" />}
          Run All Tests
        </Button>
      </div>

      {/* Service Status */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Voice Service</CardTitle>
            <Headphones className="w-4 h-4" />
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className={`text-2xl font-bold ${getStatusColor(serviceStatus.voiceService.status)}`}>
                {serviceStatus.voiceService.loading ? 'Checking...' : serviceStatus.voiceService.status}
              </div>
              <p className="text-xs text-muted-foreground">
                Version: {serviceStatus.voiceService.version || 'Unknown'}
              </p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Event Processor</CardTitle>
            <Activity className="w-4 h-4" />
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className={`text-2xl font-bold ${getStatusColor(serviceStatus.eventProcessor.status)}`}>
                {serviceStatus.eventProcessor.loading ? 'Checking...' : serviceStatus.eventProcessor.status}
              </div>
              <p className="text-xs text-muted-foreground">
                Active Connections: {serviceStatus.eventProcessor.connections}
              </p>
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="indic-testing" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="indic-testing">Indic Languages</TabsTrigger>
          <TabsTrigger value="voice-interface">Voice Interface</TabsTrigger>
          <TabsTrigger value="test-results">Test Results</TabsTrigger>
          <TabsTrigger value="debug">Debug</TabsTrigger>
        </TabsList>

        {/* Enhanced Indic Language Testing */}
        <TabsContent value="indic-testing" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Languages className="w-5 h-5" />
                Indic Language Testing
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Language Selection */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Select Language</label>
                  <Select value={selectedLanguage} onValueChange={setSelectedLanguage}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select a language" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="auto">Auto-detect</SelectItem>
                      {supportedLanguages.map((lang) => (
                        <SelectItem key={lang.code} value={lang.code}>
                          {lang.name} ({lang.native_name})
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium mb-2">Supported Features</label>
                  <div className="flex gap-2">
                    {supportedLanguages.find(l => l.code === selectedLanguage) && (
                      <>
                        {supportedLanguages.find(l => l.code === selectedLanguage)?.supported_stt && (
                          <Badge variant="secondary" className="text-xs">STT</Badge>
                        )}
                        {supportedLanguages.find(l => l.code === selectedLanguage)?.supported_tts && (
                          <Badge variant="secondary" className="text-xs">TTS</Badge>
                        )}
                      </>
                    )}
                  </div>
                </div>
              </div>

              {/* Text Input */}
              <div>
                <label className="block text-sm font-medium mb-2">Test Text</label>
                <Textarea
                  value={customText}
                  onChange={(e) => setCustomText(e.target.value)}
                  placeholder="Enter text to test..."
                  className="min-h-[100px]"
                />
              </div>

              {/* Action Buttons */}
              <div className="flex gap-4">
                <Button 
                  onClick={detectLanguage} 
                  disabled={isDetectingLanguage || !customText.trim()}
                  variant="outline"
                  className="flex items-center gap-2"
                >
                  {isDetectingLanguage ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Languages className="w-4 h-4" />}
                  Detect Language
                </Button>
                
                <Button 
                  onClick={testVoicePipeline} 
                  disabled={isTestingPipeline || !customText.trim()}
                  className="flex items-center gap-2"
                >
                  {isTestingPipeline ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Volume2 className="w-4 h-4" />}
                  Test Voice Pipeline
                </Button>
              </div>

              {/* Language Detection Results */}
              {languageDetection && (
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Language Detection Result</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div>
                        <p className="text-sm text-muted-foreground">Detected Language</p>
                        <p className="font-semibold">{languageDetection.detected_language.toUpperCase()}</p>
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground">Confidence</p>
                        <p className="font-semibold">{(languageDetection.confidence * 100).toFixed(1)}%</p>
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground">Supported Languages</p>
                        <p className="font-semibold">{languageDetection.supported_languages.length} languages</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Voice Pipeline Test Results */}
              {voiceTestResult && (
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg flex items-center gap-2">
                      Voice Pipeline Test Result
                      {voiceTestResult.success ? (
                        <CheckCircle className="w-5 h-5 text-green-600" />
                      ) : (
                        <XCircle className="w-5 h-5 text-red-600" />
                      )}
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {voiceTestResult.success ? (
                      <>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div>
                            <p className="text-sm text-muted-foreground">Original Text</p>
                            <p className="font-mono text-sm bg-gray-50 p-2 rounded">{voiceTestResult.original_text}</p>
                          </div>
                          <div>
                            <p className="text-sm text-muted-foreground">Transcribed Text</p>
                            <p className="font-mono text-sm bg-gray-50 p-2 rounded">{voiceTestResult.transcribed_text}</p>
                          </div>
                        </div>
                        
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                          <div>
                            <p className="text-sm text-muted-foreground">Language</p>
                            <p className="font-semibold">{voiceTestResult.detected_language.toUpperCase()}</p>
                          </div>
                          <div>
                            <p className="text-sm text-muted-foreground">Similarity Score</p>
                            <p className="font-semibold">{(voiceTestResult.similarity_score * 100).toFixed(1)}%</p>
                          </div>
                          <div>
                            <p className="text-sm text-muted-foreground">Audio Duration</p>
                            <p className="font-semibold">{voiceTestResult.audio_duration?.toFixed(2)}s</p>
                          </div>
                          <div>
                            <p className="text-sm text-muted-foreground">Quality</p>
                            <Badge className={getQualityColor(voiceTestResult.pipeline_quality)}>
                              {voiceTestResult.pipeline_quality}
                            </Badge>
                          </div>
                        </div>
                        
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs text-muted-foreground">
                          <div>
                            <p>TTS Model: {voiceTestResult.tts_model}</p>
                          </div>
                          <div>
                            <p>STT Model: {voiceTestResult.stt_model}</p>
                          </div>
                        </div>
                      </>
                    ) : (
                      <Alert>
                        <XCircle className="h-4 w-4" />
                        <AlertDescription>
                          Test failed at {voiceTestResult.stage}: {voiceTestResult.error}
                        </AlertDescription>
                      </Alert>
                    )}
                  </CardContent>
                </Card>
              )}

              {/* Supported Languages Grid */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Supported Indic Languages</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                    {supportedLanguages.map((lang) => (
                      <div key={lang.code} className="p-3 border rounded-lg hover:bg-gray-50">
                        <div className="flex items-center justify-between mb-1">
                          <span className="font-semibold text-sm">{lang.name}</span>
                          <span className="text-xs text-muted-foreground">{lang.code}</span>
                        </div>
                        <p className="text-lg mb-2">{lang.native_name}</p>
                        <p className="text-xs text-muted-foreground mb-2">Script: {lang.script}</p>
                        <div className="flex gap-1">
                          {lang.supported_stt && (
                            <Badge variant="secondary" className="text-xs">STT</Badge>
                          )}
                          {lang.supported_tts && (
                            <Badge variant="secondary" className="text-xs">TTS</Badge>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Voice Interface Tab */}
        <TabsContent value="voice-interface">
          <Card>
            <CardHeader>
              <CardTitle>Voice Interface Test</CardTitle>
            </CardHeader>
            <CardContent>
              <VoiceInterface />
            </CardContent>
          </Card>
        </TabsContent>

        {/* Test Results Tab */}
        <TabsContent value="test-results">
          <Card>
            <CardHeader>
              <CardTitle>Comprehensive Test Results</CardTitle>
            </CardHeader>
            <CardContent>
              {testResults.length === 0 && !isRunningTests && (
                <p className="text-muted-foreground">No test results yet. Click "Run All Tests" to start.</p>
              )}
              
              {testResults.map((result, index) => (
                <div key={index} className="border rounded-lg p-4 mb-4">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-semibold">{result.name}</h3>
                    {result.success ? (
                      <CheckCircle className="w-5 h-5 text-green-600" />
                    ) : (
                      <XCircle className="w-5 h-5 text-red-600" />
                    )}
                  </div>
                  
                  {result.error && (
                    <Alert className="mb-2">
                      <XCircle className="h-4 w-4" />
                      <AlertDescription>{result.error}</AlertDescription>
                    </Alert>
                  )}
                  
                  {result.data && (
                    <pre className="bg-gray-50 p-2 rounded text-xs overflow-auto">
                      {JSON.stringify(result.data, null, 2)}
                    </pre>
                  )}
                </div>
              ))}
              
              {isRunningTests && (
                <div className="text-center py-8">
                  <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-4" />
                  <p>Running tests...</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Debug Tab */}
        <TabsContent value="debug">
          <VoiceServiceDebug />
        </TabsContent>
      </Tabs>
    </div>
  )
}

export default VoiceTestingPage