import { useState, useEffect, useMemo, useCallback } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Switch } from '@/components/ui/switch'
import { motion, AnimatePresence } from 'framer-motion'
import { toast } from 'sonner'
import { 
  Heart, 
  Microphone, 
  Globe, 
  CloudRain,
  Gear,
  TrendUp,
  Clock,
  CheckCircle
} from '@phosphor-icons/react'

// Import our new mood components
import { MoodQuickEntry } from './MoodQuickEntry'
import { EmotionalWeatherWidget } from './EmotionalWeatherWidget'
import { VoiceMoodEntry } from './VoiceMoodEntry'
import { CulturalMoodAdapter } from './CulturalMoodAdapter'

// Types
interface MoodEntry {
  mood_score: number
  energy_level: number
  stress_level: number
  notes: string
  timestamp?: string
}

interface CulturalMoodContext {
  region: string
  language: string
  culturalEmotions: string[]
  moodExpressionPatterns: object
  celebrationTriggers: string[]
}

interface EmotionalWeatherData {
  forecast_date: string
  predicted_mood_range: {
    min: number
    max: number
  }
  weather_emoji: string
  weather_description: string
  risk_factors: string[]
  protective_factors: string[]
  recommendations: Array<{
    id: string
    text: string
    priority: string
    type: string
  }>
  confidence_score: number
}

interface EnhancedMoodTrackerProps {
  enableRealtime?: boolean
  showEmotionalWeather?: boolean
  enableVoice?: boolean
  culturalContext?: Partial<CulturalMoodContext>
  onMoodEntryAdded?: (entry: MoodEntry) => void
  onCulturalContextChange?: (context: CulturalMoodContext) => void
  className?: string
}

export function EnhancedMoodTracker({
  enableRealtime = true,
  showEmotionalWeather = true,
  enableVoice = true,
  culturalContext,
  onMoodEntryAdded,
  onCulturalContextChange,
  className
}: EnhancedMoodTrackerProps) {
  const [activeTab, setActiveTab] = useState('quick')
  const [voiceEnabled, setVoiceEnabled] = useState(enableVoice)
  const [weatherEnabled, setWeatherEnabled] = useState(showEmotionalWeather)
  const [realtimeEnabled, setRealtimeEnabled] = useState(enableRealtime)
  const [currentCulturalContext, setCurrentCulturalContext] = useState<CulturalMoodContext | null>(null)
  const [lastMoodEntry, setLastMoodEntry] = useState<MoodEntry | null>(null)
  const [weatherData, setWeatherData] = useState<EmotionalWeatherData | null>(null)

  // Track recent entries for streak and insights
  const [todayEntryCount, setTodayEntryCount] = useState(0)
  const [isFirstEntryToday, setIsFirstEntryToday] = useState(true)

  // Memoize state setters to prevent infinite loops
  const handleVoiceEnabledChange = useCallback((checked: boolean) => {
    setVoiceEnabled(checked)
  }, [])

  const handleWeatherEnabledChange = useCallback((checked: boolean) => {
    setWeatherEnabled(checked)
  }, [])

  const handleRealtimeEnabledChange = useCallback((checked: boolean) => {
    setRealtimeEnabled(checked)
  }, [])

  const handleActiveTabChange = useCallback((value: string) => {
    setActiveTab(value)
  }, [])

  // Memoize the cultural context object to prevent unnecessary re-renders
  const memoizedCulturalContext = useMemo(() => {
    if (!currentCulturalContext) return undefined
    return {
      region: currentCulturalContext.region,
      language: currentCulturalContext.language,
      weatherMetaphors: {}
    }
  }, [currentCulturalContext?.region, currentCulturalContext?.language])

  // Memoize the voice cultural context object to prevent unnecessary re-renders
  const memoizedVoiceCulturalContext = useMemo(() => {
    if (!currentCulturalContext) return undefined
    return {
      region: currentCulturalContext.region,
      language: currentCulturalContext.language,
      voicePrompts: {
        'en-US': 'Tell me how you\'re feeling today...',
        'ja-JP': '今日の気分を教えてください...',
        'es-ES': 'Dime cómo te sientes hoy...',
        'fr-FR': 'Dis-moi comment tu te sens aujourd\'hui...'
      }
    }
  }, [currentCulturalContext?.region, currentCulturalContext?.language])

  // Memoize the last mood entry time to prevent unnecessary recalculations
  const lastMoodEntryTime = useMemo(() => {
    if (!lastMoodEntry?.timestamp) return null
    return new Date(lastMoodEntry.timestamp).toLocaleTimeString()
  }, [lastMoodEntry?.timestamp])

  // Memoize the cultural context object for callbacks to prevent unnecessary re-renders
  const memoizedCallbackCulturalContext = useMemo(() => {
    return {
      region: 'US',
      language: 'en',
      culturalEmotions: [],
      moodExpressionPatterns: {},
      celebrationTriggers: []
    }
  }, [])

  useEffect(() => {
    // Check if user has already logged mood today
    const today = new Date().toDateString()
    const lastEntryDate = localStorage.getItem('lastMoodEntryDate')
    setIsFirstEntryToday(!lastEntryDate || lastEntryDate !== today)
  }, [])

  // Initialize cultural context from props if provided
  useEffect(() => {
    if (culturalContext && !currentCulturalContext) {
      setCurrentCulturalContext(culturalContext as CulturalMoodContext)
    }
  }, [culturalContext, currentCulturalContext])

  // Sync state with props changes
  useEffect(() => {
    setVoiceEnabled(enableVoice)
  }, [enableVoice])

  useEffect(() => {
    setWeatherEnabled(showEmotionalWeather)
  }, [showEmotionalWeather])

  useEffect(() => {
    setRealtimeEnabled(enableRealtime)
  }, [enableRealtime])

  const handleMoodEntryAdded = useCallback((moodData: any) => {
    const entry: MoodEntry = {
      mood_score: moodData.mood_score || moodData.mood || 0,
      energy_level: moodData.energy_level || moodData.energy || 0,
      stress_level: moodData.stress_level || moodData.stress || 0,
      notes: moodData.notes || '',
      timestamp: new Date().toISOString()
    }

    setLastMoodEntry(entry)
    setTodayEntryCount(prev => prev + 1)
    setIsFirstEntryToday(false)
    
    // Store today's entry date
    localStorage.setItem('lastMoodEntryDate', new Date().toDateString())
    
    onMoodEntryAdded?.(entry)
  }, [onMoodEntryAdded])

  const handleVoiceInput = useCallback((transcript: string) => {
    // Auto-fill notes in quick entry with voice transcript
    console.log('Voice input received:', transcript)
  }, [])

  const handleVoiceComplete = useCallback(async (finalTranscript: string, confidence: number) => {
    if (confidence > 0.3 && finalTranscript.trim()) {
      try {
        // Process voice input and extract mood
        console.log('Processing voice input:', finalTranscript)
        
        const moodData = extractMoodFromText(finalTranscript)
        if (moodData) {
          const entry: MoodEntry = {
            mood_score: moodData.mood,
            energy_level: moodData.energy,
            stress_level: moodData.stress,
            notes: `[Voice Input${moodData.language ? ` - ${moodData.language}` : ''}]: ${finalTranscript}`,
            timestamp: new Date().toISOString()
          }
          
          await handleMoodEntryAdded(entry)
          
          toast.success('Mood updated via voice!', {
            description: `Detected: ${getMoodLabel(moodData.mood)} mood${moodData.language ? ` (${moodData.language})` : ''}`,
            duration: 3000,
          })
          
          // Trigger cultural context update if language detected
          if (moodData.language && onCulturalContextChange) {
            const contextUpdate = {
              region: moodData.language === 'hi' ? 'IN' : moodData.language === 'es' ? 'ES' : 'US',
              language: moodData.language,
              culturalEmotions: [],
              moodExpressionPatterns: {},
              celebrationTriggers: []
            }
            onCulturalContextChange(contextUpdate)
          }
        } else {
          // Even if we couldn't extract specific mood, still create an entry
          const defaultEntry: MoodEntry = {
            mood_score: 5, // Neutral
            energy_level: 5,
            stress_level: 5,
            notes: `[Voice Input]: ${finalTranscript}`,
            timestamp: new Date().toISOString()
          }
          
          await handleMoodEntryAdded(defaultEntry)
          
          toast.info('Voice input recorded', {
            description: 'Added as neutral mood entry. You can edit if needed.',
            duration: 3000,
          })
        }
      } catch (error) {
        console.error('Error processing voice input:', error)
        toast.error('Failed to process voice input', {
          description: 'Please try again or use manual entry'
        })
      }
    }
  }, [handleMoodEntryAdded, onCulturalContextChange])

  // Helper function to extract mood from text using multi-language keyword analysis
  const extractMoodFromText = useCallback((text: string): { mood: number; energy: number; stress: number; language?: string } | null => {
    const lowerText = text.toLowerCase()
    
    // Multi-language mood indicators
    const moodKeywords = {
      en: {
        veryPositive: ['amazing', 'excellent', 'fantastic', 'perfect', 'brilliant', 'outstanding', 'wonderful'],
        positive: ['good', 'great', 'happy', 'pleased', 'satisfied', 'content', 'awesome', 'fine'],
        neutral: ['okay', 'fine', 'alright', 'normal', 'average', 'meh', 'so-so'],
        negative: ['bad', 'sad', 'upset', 'disappointed', 'frustrated', 'down', 'low'],
        veryNegative: ['terrible', 'awful', 'depressed', 'horrible', 'devastating', 'miserable'],
        highEnergy: ['energetic', 'pumped', 'excited', 'active', 'motivated', 'vibrant'],
        lowEnergy: ['tired', 'exhausted', 'drained', 'sluggish', 'sleepy', 'lethargic'],
        highStress: ['stressed', 'anxious', 'worried', 'overwhelmed', 'pressure', 'tense'],
        lowStress: ['calm', 'relaxed', 'peaceful', 'zen', 'chill', 'serene']
      },
      es: {
        veryPositive: ['increíble', 'excelente', 'fantástico', 'perfecto', 'brillante', 'maravilloso'],
        positive: ['bien', 'bueno', 'feliz', 'contento', 'satisfecho', 'genial'],
        neutral: ['normal', 'regular', 'así así', 'promedio'],
        negative: ['mal', 'triste', 'molesto', 'decepcionado', 'frustrado'],
        veryNegative: ['terrible', 'horrible', 'deprimido', 'devastador', 'miserable'],
        highEnergy: ['energético', 'emocionado', 'activo', 'motivado'],
        lowEnergy: ['cansado', 'agotado', 'exhausto', 'somnoliento'],
        highStress: ['estresado', 'ansioso', 'preocupado', 'abrumado'],
        lowStress: ['calmado', 'relajado', 'tranquilo', 'zen']
      },
      hi: {
        veryPositive: ['अद्भुत', 'उत्कृष्ट', 'शानदार', 'परफेक्ट', 'बेहतरीन'],
        positive: ['अच्छा', 'खुश', 'संतुष्ट', 'प्रसन्न', 'ठीक'],
        neutral: ['ठीक', 'सामान्य', 'औसत'],
        negative: ['बुरा', 'दुखी', 'परेशान', 'निराश'],
        veryNegative: ['भयानक', 'अवसादग्रस्त', 'दुखदायी'],
        highEnergy: ['ऊर्जावान', 'उत्साहित', 'सक्रिय'],
        lowEnergy: ['थका', 'कमजोर', 'सुस्त'],
        highStress: ['तनावग्रस्त', 'चिंतित', 'परेशान'],
        lowStress: ['शांत', 'आरामदायक', 'स्थिर']
      }
    }
    
    // Detect language based on keywords found
    let detectedLanguage = 'en'
    let maxMatches = 0
    
    for (const [lang, keywords] of Object.entries(moodKeywords)) {
      let matches = 0
      Object.values(keywords).flat().forEach(keyword => {
        if (lowerText.includes(keyword)) matches++
      })
      if (matches > maxMatches) {
        maxMatches = matches
        detectedLanguage = lang
      }
    }
    
    const keywords = moodKeywords[detectedLanguage as keyof typeof moodKeywords]
    
    let mood = 5 // Default neutral
    let energy = 5 // Default neutral
    let stress = 5 // Default neutral
    
    // Analyze mood
    if (keywords.veryPositive.some(word => lowerText.includes(word))) {
      mood = 9
    } else if (keywords.positive.some(word => lowerText.includes(word))) {
      mood = 7
    } else if (keywords.veryNegative.some(word => lowerText.includes(word))) {
      mood = 2
    } else if (keywords.negative.some(word => lowerText.includes(word))) {
      mood = 3
    } else if (keywords.neutral.some(word => lowerText.includes(word))) {
      mood = 5
    }
    
    // Analyze energy
    if (keywords.highEnergy.some(word => lowerText.includes(word))) {
      energy = 8
    } else if (keywords.lowEnergy.some(word => lowerText.includes(word))) {
      energy = 3
    }
    
    // Analyze stress
    if (keywords.highStress.some(word => lowerText.includes(word))) {
      stress = 8
    } else if (keywords.lowStress.some(word => lowerText.includes(word))) {
      stress = 2
    }
    
    return { mood, energy, stress, language: detectedLanguage }
  }, [])

  // Helper function to get mood label
  const getMoodLabel = useCallback((score: number): string => {
    if (score >= 8) return 'Excellent'
    if (score >= 6) return 'Good'
    if (score >= 4) return 'Neutral'
    if (score >= 2) return 'Low'
    return 'Very Low'
  }, [])

  const handleCulturalMoodSubmit = useCallback((mood: number, expression: string, celebration?: string) => {
    const culturalEntry: MoodEntry = {
      mood_score: mood,
      energy_level: mood, // Use same value for simplicity
      stress_level: Math.max(1, 11 - mood), // Inverse relationship
      notes: `${expression}${celebration ? ` | Celebrating: ${celebration}` : ''}`,
      timestamp: new Date().toISOString()
    }

    handleMoodEntryAdded(culturalEntry)
  }, [handleMoodEntryAdded])

  const handleWeatherUpdate = useCallback((data: EmotionalWeatherData) => {
    setWeatherData(data)
  }, [])

  const handleCulturalContextChange = useCallback((context: CulturalMoodContext) => {
    setCurrentCulturalContext(context)
    onCulturalContextChange?.(context)
  }, [onCulturalContextChange])

  const getGreeting = useMemo(() => {
    const hour = new Date().getHours()
    const culturalGreetings = currentCulturalContext?.language === 'ja-JP' 
      ? { morning: 'おはようございます', afternoon: 'こんにちは', evening: 'こんばんは' }
      : currentCulturalContext?.language === 'es-ES'
      ? { morning: 'Buenos días', afternoon: 'Buenas tardes', evening: 'Buenas noches' }
      : currentCulturalContext?.language === 'fr-FR'
      ? { morning: 'Bonjour', afternoon: 'Bon après-midi', evening: 'Bonsoir' }
      : { morning: 'Good morning', afternoon: 'Good afternoon', evening: 'Good evening' }

    if (hour < 12) return culturalGreetings.morning
    if (hour < 18) return culturalGreetings.afternoon
    return culturalGreetings.evening
  }, [currentCulturalContext?.language])

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header with Settings */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div>
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <Heart className="text-red-500" />
            {getGreeting}
          </h2>
          <p className="text-muted-foreground">
            {isFirstEntryToday 
              ? "Let's track your mood for today!" 
              : `${todayEntryCount} ${todayEntryCount === 1 ? 'entry' : 'entries'} logged today`}
          </p>
        </div>
        
        <div className="flex items-center gap-4">
          {realtimeEnabled && (
            <Badge variant="outline" className="text-green-600">
              <div className="w-2 h-2 bg-green-500 rounded-full mr-1 animate-pulse" />
              Live
            </Badge>
          )}
          <Button variant="ghost" size="sm">
            <Gear size={16} />
          </Button>
        </div>
      </motion.div>

      {/* Feature Toggles */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Enhanced Features</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Microphone size={16} className="text-blue-500" />
                <span className="text-sm">Voice Input</span>
              </div>
              <Switch 
                key="voice-switch"
                checked={voiceEnabled} 
                onCheckedChange={handleVoiceEnabledChange}
              />
            </div>
            
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <CloudRain size={16} className="text-purple-500" />
                <span className="text-sm">Weather Forecast</span>
              </div>
              <Switch 
                key="weather-switch"
                checked={weatherEnabled} 
                onCheckedChange={handleWeatherEnabledChange}
              />
            </div>
            
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <TrendUp size={16} className="text-green-500" />
                <span className="text-sm">Real-time Sync</span>
              </div>
              <Switch 
                key="realtime-switch"
                checked={realtimeEnabled} 
                onCheckedChange={handleRealtimeEnabledChange}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Emotional Weather Widget */}
      <AnimatePresence>
        {weatherEnabled && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
          >
            <EmotionalWeatherWidget
              showDetails={true}
              autoRefresh={realtimeEnabled}
              onWeatherUpdate={handleWeatherUpdate}
              culturalContext={memoizedCulturalContext}
            />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Mood Tracking Interface */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Heart size={20} />
            Mood Tracking
            {lastMoodEntry && (
              <Badge variant="outline" className="ml-auto">
                <CheckCircle size={12} className="mr-1" />
                Last: {lastMoodEntryTime}
              </Badge>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Tabs value={activeTab} onValueChange={handleActiveTabChange} className="w-full">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="quick" className="flex items-center gap-2">
                <Clock size={16} />
                Quick Entry
              </TabsTrigger>
              <TabsTrigger 
                value="voice" 
                disabled={!voiceEnabled}
                className="flex items-center gap-2"
              >
                <Microphone size={16} />
                Voice Entry
              </TabsTrigger>
            </TabsList>

            <TabsContent value="quick" className="mt-6">
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3 }}
              >
                <MoodQuickEntry 
                  onEntryAdded={handleMoodEntryAdded}
                />
                
                {/* Integrated Cultural Context Display */}
                {currentCulturalContext && (
                  <motion.div 
                    className="mt-4 p-3 bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg border border-purple-200"
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.2 }}
                  >
                    <div className="flex items-center gap-2 text-sm text-purple-700 mb-2">
                      <Globe size={16} />
                      Cultural Context: {currentCulturalContext.region} ({currentCulturalContext.language})
                    </div>
                    {currentCulturalContext.culturalEmotions.length > 0 && (
                      <div className="flex flex-wrap gap-2">
                        {currentCulturalContext.culturalEmotions.slice(0, 3).map((emotion) => (
                          <Badge key={emotion} variant="outline" className="text-purple-600 border-purple-300">
                            {emotion}
                          </Badge>
                        ))}
                      </div>
                    )}
                  </motion.div>
                )}
              </motion.div>
            </TabsContent>

            <TabsContent value="voice" className="mt-6">
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3 }}
              >
                {voiceEnabled ? (
                  <VoiceMoodEntry
                    onVoiceInput={handleVoiceInput}
                    onVoiceComplete={handleVoiceComplete}
                    currentLanguage={currentCulturalContext?.language || 'en-US'}
                    culturalContext={memoizedVoiceCulturalContext}
                  />
                ) : (
                  <div className="text-center py-8 text-muted-foreground">
                    Voice input is disabled. Enable it in the settings above.
                  </div>
                )}
              </motion.div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      {/* Quick Stats */}
      {todayEntryCount > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="grid grid-cols-1 md:grid-cols-3 gap-4"
        >
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-2">
                <CheckCircle size={16} className="text-green-500" />
                <div>
                  <div className="text-sm text-muted-foreground">Today's Entries</div>
                  <div className="text-lg font-bold">{todayEntryCount}</div>
                </div>
              </div>
            </CardContent>
          </Card>

          {lastMoodEntry && (
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center gap-2">
                  <Heart size={16} className="text-red-500" />
                  <div>
                    <div className="text-sm text-muted-foreground">Current Mood</div>
                    <div className="text-lg font-bold">{lastMoodEntry?.mood_score}/10</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {weatherData && (
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center gap-2">
                  <span className="text-lg">{weatherData?.weather_emoji}</span>
                  <div>
                    <div className="text-sm text-muted-foreground">Forecast</div>
                    <div className="text-sm font-medium">{weatherData?.weather_description}</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </motion.div>
      )}
    </div>
  )
}
