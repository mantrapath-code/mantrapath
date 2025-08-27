import { useState, useEffect, useCallback } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { 
  Cloud, 
  Sun, 
  CloudRain, 
  CloudSnow, 
  Lightning, 
  ArrowClockwise,
  TrendUp,
  TrendDown,
  Minus,
  Warning,
  Shield,
  Lightbulb
} from '@phosphor-icons/react'
import { motion, AnimatePresence } from 'framer-motion'
import { toast } from 'sonner'
import { apiService } from '@/services/api'

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
    type: string
    title: string
    description: string
  }>
  confidence_score: number
}

interface EmotionalWeatherWidgetProps {
  className?: string
  size?: string
  showDetails?: boolean
  autoRefresh?: boolean
  onWeatherUpdate?: (data: EmotionalWeatherData) => void
  culturalContext?: {
    region?: string
    language?: string
    weatherMetaphors?: Record<string, string>
  }
}

const weatherIcons: Record<string, React.ComponentType<any>> = {
  '☀️': Sun,
  '⛅': Cloud,
  '🌧️': CloudRain,
  '⛈️': Lightning,
  '❄️': CloudSnow,
  'default': Cloud
}

export function EmotionalWeatherWidget({ 
  className = "", 
  size = "default", 
  showDetails = true, 
  autoRefresh = false, // Disabled by default to prevent flickering
  onWeatherUpdate,
  culturalContext 
}: EmotionalWeatherWidgetProps) {
  const [weatherData, setWeatherData] = useState<EmotionalWeatherData | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)
  const [isRefreshing, setIsRefreshing] = useState(false)

  const fetchWeatherData = useCallback(async () => {
    try {
      setIsLoading(true)
      setError(null)
      
      const response = await apiService.getEmotionalWeather()
      
      // Handle different response formats (API Gateway vs direct service)
      let data = response
      if (response && typeof response === 'object' && 'body' in response) {
        // API Gateway format - parse the body
        data = typeof response.body === 'string' ? JSON.parse(response.body) : response.body
      }
      
      if (data) {
        // Transform data to match expected format
        const transformedData: EmotionalWeatherData = {
          forecast_date: data.forecast_date,
          predicted_mood_range: data.predicted_mood_range,
          weather_emoji: data.weather_emoji,
          weather_description: data.weather_description,
          risk_factors: data.risk_factors || [],
          protective_factors: data.protective_factors || [],
          recommendations: (data.recommendations || []).map((rec: any) => ({
            type: rec.type || 'general',
            title: rec.title || rec.text || 'Recommendation',
            description: rec.description || rec.text || ''
          })),
          confidence_score: data.confidence_score
        }
        
        setWeatherData(transformedData)
        const now = new Date()
        setLastUpdated(now)
        onWeatherUpdate?.(transformedData)
        
        // Only show toast for manual refreshes, not initial loads
        if (lastUpdated && (now.getTime() - lastUpdated.getTime()) > 5000) {
          toast.success('Emotional weather updated', {
            description: `${data.weather_emoji} ${data.weather_description}`
          })
        }
      } else {
        setError('No weather data available. Please ensure you are logged in.')
        setWeatherData(null)
      }
    } catch (err: any) {
      console.error('Failed to fetch emotional weather:', err)
      
      if (err.status === 401) {
        setError('Please log in to view your emotional weather forecast.')
      } else if (err.status === 403) {
        setError('Please verify your email to access weather forecasts.')
      } else {
        setError('Unable to load emotional weather. Please try again.')
      }
      
      setWeatherData(null)
      
      toast.error('Emotional weather temporarily unavailable', {
        description: 'Using sample data. Please check your connection.'
      })
    } finally {
      setIsLoading(false)
    }
  }, [onWeatherUpdate]) // Removed lastUpdated from dependencies to prevent infinite loop

  useEffect(() => {
    fetchWeatherData()
    
    // Auto-refresh every 30 minutes if enabled
    let interval: NodeJS.Timeout | null = null
    if (autoRefresh) {
      interval = setInterval(fetchWeatherData, 30 * 60 * 1000)
    }
    
    return () => {
      if (interval) {
        clearInterval(interval)
      }
      // Clean up state to prevent memory leaks
      setWeatherData(null)
      setError(null)
    }
  }, [fetchWeatherData, autoRefresh])

  const getWeatherIcon = (emoji: string) => {
    const IconComponent = weatherIcons[emoji] || weatherIcons.default
    return IconComponent
  }

  const getMoodTrend = () => {
    if (!weatherData?.predicted_mood_range) return null
    
    const { min, max } = weatherData.predicted_mood_range
    const average = (min + max) / 2
    
    if (average >= 7) return { icon: TrendUp, color: 'text-green-600', label: 'Rising' }
    if (average >= 5) return { icon: Minus, color: 'text-yellow-600', label: 'Stable' }
    return { icon: TrendDown, color: 'text-red-600', label: 'Declining' }
  }

  const formatRelativeTime = (date: Date) => {
    const now = new Date()
    const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60))
    
    if (diffInMinutes < 1) return 'Just now'
    if (diffInMinutes < 60) return `${diffInMinutes}m ago`
    if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)}h ago`
    return date.toLocaleDateString()
  }

  const getLocalizedWeatherDescription = (description: string) => {
    if (!culturalContext?.weatherMetaphors) return description
    return culturalContext.weatherMetaphors[description] || description
  }

  if (error && !weatherData) {
    return (
      <Card className="w-full">
        <CardContent className="p-6">
          <Alert>
            <Warning className="h-4 w-4" />
            <AlertDescription>
              {error}
              <Button 
                variant="outline" 
                size="sm" 
                onClick={fetchWeatherData}
                className="ml-2"
              >
                <ArrowClockwise size={14} />
                Retry
              </Button>
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {weatherData && (
              <>
                <span className="text-2xl">{weatherData.weather_emoji}</span>
                <span>Emotional Weather</span>
              </>
            )}
            {isLoading && (
              <>
                <Cloud className="animate-pulse" size={20} />
                <span>Emotional Weather</span>
              </>
            )}
          </div>
          <div className="flex items-center gap-2">
            {lastUpdated && (
              <Badge variant="outline" className="text-xs">
                {formatRelativeTime(lastUpdated)}
              </Badge>
            )}
            <Button
              variant="ghost"
              size="sm"
              onClick={async () => {
                setIsRefreshing(true)
                await fetchWeatherData()
                setIsRefreshing(false)
              }}
              disabled={isLoading || isRefreshing}
            >
              <ArrowClockwise size={14} className={isLoading || isRefreshing ? 'animate-spin' : ''} />
            </Button>
          </div>
        </CardTitle>
      </CardHeader>

      <CardContent className="space-y-4">
        {isLoading ? (
          <div className="space-y-3">
            <Skeleton className="h-4 w-3/4" />
            <Skeleton className="h-4 w-1/2" />
            <div className="flex gap-2">
              <Skeleton className="h-6 w-20" />
              <Skeleton className="h-6 w-24" />
            </div>
          </div>
        ) : weatherData ? (
          <AnimatePresence mode="wait">
            <motion.div
              key={weatherData.forecast_date}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              className="space-y-4"
            >
              {/* Main Weather Description */}
              <div className="text-center p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg">
                <p className="text-lg font-medium text-gray-800">
                  {getLocalizedWeatherDescription(weatherData.weather_description)}
                </p>
                <div className="flex items-center justify-center gap-2 mt-2">
                  <span className="text-sm text-gray-600">Mood Range:</span>
                  <Badge variant="outline">
                    {weatherData.predicted_mood_range?.min || 1} - {weatherData.predicted_mood_range?.max || 10}
                  </Badge>
                  {(() => {
                    const trend = getMoodTrend()
                    if (trend) {
                      const TrendIcon = trend.icon
                      return (
                        <Badge variant="outline" className={trend.color}>
                          <TrendIcon size={12} className="mr-1" />
                          {trend.label}
                        </Badge>
                      )
                    }
                    return null
                  })()}
                </div>
              </div>

              {showDetails && (
                <>
                  {/* Risk Factors */}
                  {weatherData.risk_factors && weatherData.risk_factors.length > 0 && (
                    <div>
                      <h4 className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
                        <Warning size={16} className="text-amber-500" />
                        Watch Out For
                      </h4>
                      <div className="flex flex-wrap gap-2">
                        {weatherData.risk_factors.map((factor, index) => (
                          <Badge 
                            key={index} 
                            variant="outline"
                            className="bg-amber-50 text-amber-700 border-amber-200"
                          >
                            {factor}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Protective Factors */}
                  {weatherData.protective_factors && weatherData.protective_factors.length > 0 && (
                    <div>
                      <h4 className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
                        <Shield size={16} className="text-green-500" />
                        Your Strengths
                      </h4>
                      <div className="flex flex-wrap gap-2">
                        {weatherData.protective_factors.map((factor, index) => (
                          <Badge 
                            key={index} 
                            variant="outline"
                            className="bg-green-50 text-green-700 border-green-200"
                          >
                            {factor}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Recommendations */}
                  {weatherData.recommendations && weatherData.recommendations.length > 0 && (
                    <div>
                      <h4 className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
                        <Lightbulb size={16} className="text-blue-500" />
                        Recommendations
                      </h4>
                      <div className="space-y-2">
                        {weatherData.recommendations.map((rec, index) => (
                          <div 
                            key={index}
                            className={`p-3 rounded-lg border text-sm ${
                              rec.type === 'activity' ? 'bg-green-50 border-green-200 text-green-800' :
                              rec.type === 'self_care' ? 'bg-blue-50 border-blue-200 text-blue-800' :
                              rec.type === 'social' ? 'bg-purple-50 border-purple-200 text-purple-800' :
                              rec.type === 'support' ? 'bg-yellow-50 border-yellow-200 text-yellow-800' :
                              'bg-gray-50 border-gray-200 text-gray-800'
                            }`}
                          >
                            <div className="font-medium mb-1">{rec.title}</div>
                            <div className="text-xs opacity-80">{rec.description}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Confidence Score */}
                  <div className="flex items-center justify-between text-xs text-gray-500 pt-2 border-t">
                    <span>Forecast Confidence</span>
                    <Badge variant="outline">
                      {Math.round(weatherData.confidence_score * 100)}%
                    </Badge>
                  </div>
                </>
              )}
            </motion.div>
          </AnimatePresence>
        ) : null}
      </CardContent>
    </Card>
  )
}
