/**
 * Emotional Weather Page - Phase 2 Enhancement
 * Dedicated page for emotional weather forecasting and mood climate analysis
 */

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  Cloud,
  Sun,
  CloudRain,
  Thermometer,
  Wind,
  ArrowLeft,
  Calendar,
  TrendUp,
  Eye
} from '@phosphor-icons/react'
import { motion } from 'framer-motion'
import { EmotionalWeatherWidget } from '@/components/mood/EmotionalWeatherWidget'
import { useMoods } from '@/hooks/useMoods'

interface WeatherPageProps {
  onBack?: () => void
}

export function WeatherPage({ onBack }: WeatherPageProps) {
  const { moods } = useMoods()
  const [activeWeatherTab, setActiveWeatherTab] = useState('current')

  // Get current emotional weather
  const getCurrentWeather = () => {
    if (moods.length === 0) return { condition: 'neutral', temp: 50 }
    
    const recentMood = moods[0]
    const moodValues = {
      'excellent': { condition: 'sunny', temp: 85 },
      'good': { condition: 'partly-cloudy', temp: 70 },
      'neutral': { condition: 'cloudy', temp: 55 },
      'low': { condition: 'rainy', temp: 35 },
      'very-low': { condition: 'stormy', temp: 20 }
    }
    
    return moodValues[recentMood.mood] || { condition: 'neutral', temp: 50 }
  }

  const currentWeather = getCurrentWeather()

  const getWeatherIcon = (condition: string) => {
    switch (condition) {
      case 'sunny': return <Sun className="text-yellow-500" size={24} />
      case 'partly-cloudy': return <Cloud className="text-blue-400" size={24} />
      case 'cloudy': return <Cloud className="text-gray-500" size={24} />
      case 'rainy': return <CloudRain className="text-blue-600" size={24} />
      case 'stormy': return <CloudRain className="text-purple-600" size={24} />
      default: return <Cloud className="text-gray-400" size={24} />
    }
  }

  const getWeatherDescription = (condition: string) => {
    switch (condition) {
      case 'sunny': return 'Clear emotional skies with positive energy'
      case 'partly-cloudy': return 'Mixed emotions with overall stability'
      case 'cloudy': return 'Neutral emotional climate'
      case 'rainy': return 'Emotional clouds with some difficulty'
      case 'stormy': return 'Challenging emotional weather ahead'
      default: return 'Stable emotional conditions'
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div className="flex items-center gap-3">
          {onBack && (
            <Button variant="ghost" size="sm" onClick={onBack}>
              <ArrowLeft size={16} />
            </Button>
          )}
          <div>
            <h1 className="text-2xl font-bold flex items-center gap-2">
              {getWeatherIcon(currentWeather.condition)}
              Emotional Weather
            </h1>
            <p className="text-muted-foreground">
              Your personal emotional climate forecast and mood patterns
            </p>
          </div>
        </div>
        <Badge variant="secondary" className="text-sm">
          {currentWeather.temp}°M (Mood Temperature)
        </Badge>
      </motion.div>

      {/* Current Weather Summary */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <Card className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-950/20 dark:to-indigo-950/20">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Thermometer className="text-primary" size={20} />
              Current Emotional Climate
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                {getWeatherIcon(currentWeather.condition)}
                <div>
                  <h3 className="font-semibold capitalize">{currentWeather.condition.replace('-', ' ')}</h3>
                  <p className="text-sm text-muted-foreground">
                    {getWeatherDescription(currentWeather.condition)}
                  </p>
                </div>
              </div>
              <div className="text-right">
                <div className="text-3xl font-bold text-primary">{currentWeather.temp}°M</div>
                <div className="text-xs text-muted-foreground">Emotional Temperature</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Weather Tabs */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <Tabs value={activeWeatherTab} onValueChange={setActiveWeatherTab} className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="current" className="flex items-center gap-2">
              <Eye size={16} />
              Current
            </TabsTrigger>
            <TabsTrigger value="forecast" className="flex items-center gap-2">
              <Calendar size={16} />
              Forecast
            </TabsTrigger>
            <TabsTrigger value="trends" className="flex items-center gap-2">
              <TrendUp size={16} />
              Climate Trends
            </TabsTrigger>
          </TabsList>

          <TabsContent value="current" className="space-y-6 mt-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Wind className="text-primary" size={20} />
                  Today's Emotional Weather
                </CardTitle>
                <p className="text-sm text-muted-foreground">
                  Real-time emotional climate based on your recent mood patterns
                </p>
              </CardHeader>
              <CardContent>
                <EmotionalWeatherWidget compact={false} />
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="forecast" className="space-y-6 mt-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Calendar className="text-primary" size={20} />
                  7-Day Emotional Forecast
                </CardTitle>
                <p className="text-sm text-muted-foreground">
                  Predicted emotional weather based on your patterns and upcoming events
                </p>
              </CardHeader>
              <CardContent>
                <EmotionalWeatherWidget compact={false} />
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="trends" className="space-y-6 mt-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendUp className="text-primary" size={20} />
                  Emotional Climate Patterns
                </CardTitle>
                <p className="text-sm text-muted-foreground">
                  Long-term emotional weather patterns and seasonal changes in your mood
                </p>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="text-center text-muted-foreground py-8">
                    <Cloud size={48} className="mx-auto mb-4 opacity-50" />
                    <p>Climate trend analysis coming soon</p>
                    <p className="text-xs mt-2">Continue tracking your mood to unlock seasonal patterns</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </motion.div>
    </div>
  )
}
