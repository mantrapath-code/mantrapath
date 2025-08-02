import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { 
  Cloud,
  CloudRain,
  Sun,
  CloudSnow,
  Lightning,
  Eye,
  TrendUp,
  Shield,
  Warning,
  Calendar,
  ArrowClockwise
} from "@phosphor-icons/react"
import { motion, AnimatePresence } from "framer-motion"
import { apiService } from "@/services/api"

interface EmotionalWeather {
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

interface WeeklyOutlook {
  user_id: string
  week_outlook: Array<{
    date: string
    day: string
    emoji: string
    description: string
  }>
  confidence_score: number
  generated_at: string
}

export function EmotionalWeatherWidget({ compact = false }: { compact?: boolean }) {
  const [todaysForecast, setTodaysForecast] = useState<EmotionalWeather | null>(null)
  const [weeklyOutlook, setWeeklyOutlook] = useState<WeeklyOutlook | null>(null)
  const [loading, setLoading] = useState(true)
  const [showWeekly, setShowWeekly] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)

  useEffect(() => {
    loadEmotionalWeather()
  }, [])

  const loadEmotionalWeather = async () => {
    try {
      setLoading(true)
      setError(null)

      // Load today's forecast
      const forecast = await apiService.getEmotionalWeather()
      setTodaysForecast(forecast)

      // Load weekly outlook
      const weekly = await apiService.getWeeklyWeather()
      setWeeklyOutlook(weekly)

      setLastUpdated(new Date())
      
    } catch (err) {
      console.error('Failed to load emotional weather:', err)
      setError("Unable to load weather forecast. Please try again later.")
    } finally {
      setLoading(false)
    }
  }

  const getWeatherIcon = (emoji: string) => {
    switch (emoji) {
      case "☀️": return <Sun size={32} className="text-yellow-500" />
      case "🌤️": return <Cloud size={32} className="text-blue-400" />
      case "⛅": return <CloudRain size={32} className="text-gray-500" />
      case "🌧️": return <CloudRain size={32} className="text-blue-600" />
      case "⛈️": return <Lightning size={32} className="text-purple-600" />
      default: return <Cloud size={32} className="text-gray-400" />
    }
  }

  const formatMoodRange = (range: { min: number, max: number }) => {
    const formatScore = (score: number) => {
      if (score >= 8) return "High"
      if (score >= 6) return "Good"
      if (score >= 4) return "Moderate"
      if (score >= 2) return "Low"
      return "Very Low"
    }
    
    if (Math.abs(range.max - range.min) <= 1) {
      return formatScore((range.min + range.max) / 2)
    }
    
    return `${formatScore(range.min)} to ${formatScore(range.max)}`
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'bg-destructive/10 text-destructive border-destructive/20'
      case 'urgent': return 'bg-destructive/20 text-destructive border-destructive/30'
      case 'normal': return 'bg-primary/10 text-primary border-primary/20'
      case 'low': return 'bg-muted text-muted-foreground border-border'
      default: return 'bg-primary/10 text-primary border-primary/20'
    }
  }

  const getConfidenceDescription = (score: number) => {
    if (score >= 0.8) return "High confidence"
    if (score >= 0.6) return "Good confidence"
    if (score >= 0.4) return "Moderate confidence"
    return "Building confidence"
  }

  if (loading) {
    return (
      <Card className="h-full">
        <CardHeader className={compact ? "pb-2" : ""}>
          <CardTitle className={`flex items-center gap-2 ${compact ? "text-base" : ""}`}>
            <ArrowClockwise size={compact ? 20 : 24} className="animate-spin text-primary" />
            {compact ? "Loading Weather..." : "Loading Weather Forecast..."}
          </CardTitle>
        </CardHeader>
        <CardContent className={compact ? "pt-0" : ""}>
          <div className="space-y-3">
            <div className="h-4 bg-muted rounded animate-pulse"></div>
            <div className="h-4 bg-muted rounded animate-pulse w-3/4"></div>
            <div className="h-4 bg-muted rounded animate-pulse w-1/2"></div>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (error) {
    return (
      <Card className={`h-full border-destructive/20 ${compact ? "" : "border-dashed"}`}>
        <CardHeader className={compact ? "pb-2" : ""}>
          <CardTitle className={`flex items-center gap-2 text-destructive ${compact ? "text-base" : ""}`}>
            <Warning size={compact ? 20 : 24} />
            {compact ? "Weather Error" : "Weather Unavailable"}
          </CardTitle>
        </CardHeader>
        <CardContent className={compact ? "pt-0" : ""}>
          <p className="text-sm text-muted-foreground mb-3">{error}</p>
          <Button onClick={loadEmotionalWeather} size="sm" variant="outline" className="w-full">
            <ArrowClockwise size={16} className="mr-2" />
            Try Again
          </Button>
        </CardContent>
      </Card>
    )
  }

  if (!todaysForecast) {
    return (
      <Card className={compact ? "h-full" : "emotional-weather-card border-dashed"}>
        <CardHeader className={compact ? "pb-2" : ""}>
          <CardTitle className={`flex items-center gap-2 ${compact ? "text-base" : ""}`}>
            <Cloud size={compact ? 20 : 24} className="text-gray-400" />
            {compact ? "Weather" : "Building Your Weather Profile"}
          </CardTitle>
        </CardHeader>
        <CardContent className={compact ? "pt-0" : ""}>
          <p className="text-sm text-muted-foreground">
            {compact 
              ? "Track more moods for forecasts" 
              : "Keep tracking your mood for a few more days to get personalized weather forecasts!"
            }
          </p>
        </CardContent>
      </Card>
    )
  }

  if (compact) {
    return (
      <Card className="h-full bg-gradient-to-br from-background to-muted/50 border-border shadow-sm">
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2 text-base">
              {getWeatherIcon(todaysForecast.weather_emoji)}
              Emotional Weather
            </CardTitle>
            <Button
              variant="ghost"
              size="sm"
              onClick={loadEmotionalWeather}
              disabled={loading}
              className="h-7 w-7 p-0"
            >
              <ArrowClockwise size={14} className={loading ? "animate-spin" : ""} />
            </Button>
          </div>
        </CardHeader>

        <CardContent className="pt-0 space-y-3">
          {/* Compact Today's Forecast */}
          <div className="bg-card/70 backdrop-blur-sm rounded-lg p-3 border border-border/50">
            <p className="text-sm font-medium text-center mb-1">
              {todaysForecast.weather_description}
            </p>
            <p className="text-xs text-center text-muted-foreground">
              Expected: {formatMoodRange(todaysForecast.predicted_mood_range)}
            </p>
            <div className="flex items-center justify-center mt-2">
              <Badge variant="outline" className="text-xs">
                {Math.round(todaysForecast.confidence_score * 100)}% confidence
              </Badge>
            </div>
          </div>

          {/* Quick Risk/Protective Summary */}
          <div className="grid grid-cols-2 gap-2 text-xs">
            {todaysForecast.risk_factors.length > 0 && (
              <div className="bg-destructive/10 text-destructive-foreground p-2 rounded border border-destructive/20">
                <div className="flex items-center gap-1 font-medium text-destructive mb-1">
                  <Warning size={12} />
                  Watch
                </div>
                <div className="text-destructive">
                  {todaysForecast.risk_factors.length} factor{todaysForecast.risk_factors.length !== 1 ? 's' : ''}
                </div>
              </div>
            )}
            
            {todaysForecast.protective_factors.length > 0 && (
              <div className="bg-green-500/10 text-green-900 dark:text-green-100 p-2 rounded border border-green-500/20">
                <div className="flex items-center gap-1 font-medium text-green-700 dark:text-green-400 mb-1">
                  <Shield size={12} />
                  Strengths
                </div>
                <div className="text-green-600 dark:text-green-300">
                  {todaysForecast.protective_factors.length} strength{todaysForecast.protective_factors.length !== 1 ? 's' : ''}
                </div>
              </div>
            )}
          </div>

          {/* Quick Recommendation */}
          {todaysForecast.recommendations.length > 0 && (
            <div className="bg-primary/10 text-primary-foreground p-2 rounded border border-primary/20">
              <div className="text-xs font-medium text-primary mb-1">
                💡 Quick Tip
              </div>
              <div className="text-xs text-primary/80">
                {todaysForecast.recommendations[0].text.slice(0, 80)}
                {todaysForecast.recommendations[0].text.length > 80 ? '...' : ''}
              </div>
            </div>
          )}

          {/* View More Link */}
          <Button 
            variant="outline" 
            size="sm" 
            className="w-full h-7 text-xs"
            onClick={() => setShowWeekly(!showWeekly)}
          >
            {showWeekly ? "Show Today" : "View Weekly"}
          </Button>
        </CardContent>
      </Card>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-4"
    >
      <Card className="bg-gradient-to-br from-background to-muted/50 border-border shadow-sm">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              {getWeatherIcon(todaysForecast.weather_emoji)}
              Emotional Weather
            </CardTitle>
            <div className="flex gap-2">
              <Button
                variant={showWeekly ? "default" : "outline"}
                size="sm"
                onClick={() => setShowWeekly(!showWeekly)}
              >
                <Calendar size={16} className="mr-1" />
                {showWeekly ? "Today" : "Week"}
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={loadEmotionalWeather}
                disabled={loading}
              >
                <ArrowClockwise size={16} className={loading ? "animate-spin" : ""} />
              </Button>
            </div>
          </div>
          
          {lastUpdated && (
            <p className="text-xs text-muted-foreground">
              Updated {lastUpdated.toLocaleTimeString([], { 
                hour: '2-digit', 
                minute: '2-digit' 
              })}
            </p>
          )}
        </CardHeader>

        <CardContent>
          <AnimatePresence mode="wait">
            {!showWeekly ? (
              <motion.div
                key="today"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                className="space-y-6"
              >
                {/* Today's Forecast */}
                <div className="today-forecast space-y-3">
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-semibold">Tomorrow's Outlook</h3>
                    <Badge variant="outline" className="text-xs">
                      {getConfidenceDescription(todaysForecast.confidence_score)}
                    </Badge>
                  </div>
                  
                  <div className="bg-card/70 backdrop-blur-sm rounded-lg p-4 space-y-2 border border-border/50">
                    <p className="text-lg font-medium text-center">
                      {todaysForecast.weather_description}
                    </p>
                    <p className="text-center text-muted-foreground">
                      Expected mood: <span className="font-medium">
                        {formatMoodRange(todaysForecast.predicted_mood_range)}
                      </span>
                    </p>
                  </div>
                </div>

                {/* Risk Factors */}
                {todaysForecast.risk_factors.length > 0 && (
                  <div className="risk-factors space-y-2">
                    <h4 className="flex items-center gap-2 text-sm font-medium text-destructive">
                      <Warning size={16} />
                      Watch out for:
                    </h4>
                    <ul className="space-y-1">
                      {todaysForecast.risk_factors.map((factor, index) => (
                        <li key={index} className="text-sm text-destructive bg-destructive/10 p-2 rounded border border-destructive/20">
                          {factor}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Protective Factors */}
                {todaysForecast.protective_factors.length > 0 && (
                  <div className="protective-factors space-y-2">
                    <h4 className="flex items-center gap-2 text-sm font-medium text-green-700 dark:text-green-400">
                      <Shield size={16} />
                      Your strengths:
                    </h4>
                    <ul className="space-y-1">
                      {todaysForecast.protective_factors.map((factor, index) => (
                        <li key={index} className="text-sm text-green-600 dark:text-green-300 bg-green-500/10 p-2 rounded border border-green-500/20">
                          {factor}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Recommendations */}
                {todaysForecast.recommendations.length > 0 && (
                  <div className="recommendations space-y-2">
                    <h4 className="flex items-center gap-2 text-sm font-medium text-primary">
                      <TrendUp size={16} />
                      Recommendations:
                    </h4>
                    <div className="space-y-2">
                      {todaysForecast.recommendations.map((rec, index) => (
                        <div 
                          key={rec.id || index} 
                          className={`text-sm p-3 rounded-lg border ${getPriorityColor(rec.priority)}`}
                        >
                          <div className="flex items-start justify-between gap-2">
                            <span>{rec.text}</span>
                            {rec.priority === 'high' || rec.priority === 'urgent' ? (
                              <Badge variant="destructive" className="text-xs">
                                {rec.priority}
                              </Badge>
                            ) : null}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </motion.div>
            ) : (
              <motion.div
                key="weekly"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className="space-y-4"
              >
                <h3 className="text-lg font-semibold">7-Day Outlook</h3>
                
                {weeklyOutlook ? (
                  <div className="space-y-3">
                    {weeklyOutlook.week_outlook.map((day, index) => (
                      <div 
                        key={day.date}
                        className="flex items-center justify-between p-3 bg-card/70 backdrop-blur-sm rounded-lg border border-border/50"
                      >
                        <div className="flex items-center gap-3">
                          <span className="text-2xl">{day.emoji}</span>
                          <div>
                            <div className="font-medium">{day.day}</div>
                            <div className="text-xs text-muted-foreground">
                              {new Date(day.date).toLocaleDateString([], { 
                                month: 'short', 
                                day: 'numeric' 
                              })}
                            </div>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-sm">{day.description}</div>
                        </div>
                      </div>
                    ))}
                    
                    <div className="text-center">
                      <Badge variant="outline" className="text-xs">
                        {getConfidenceDescription(weeklyOutlook.confidence_score)} prediction
                      </Badge>
                    </div>
                  </div>
                ) : (
                  <div className="text-center text-muted-foreground">
                    <p>Weekly outlook not available yet.</p>
                    <p className="text-xs">Keep tracking to unlock weekly predictions!</p>
                  </div>
                )}
              </motion.div>
            )}
          </AnimatePresence>
        </CardContent>
      </Card>
    </motion.div>
  )
}
