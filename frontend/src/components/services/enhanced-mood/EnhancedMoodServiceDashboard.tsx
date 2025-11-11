import { useState, useEffect } from "react"
import { motion } from "framer-motion"
import { 
  Heart, 
  Activity, 
  TrendingUp,
  Calendar,
  Zap,
  BookOpen,
  Plus,
  BarChart3,
  Smile,
  Frown,
  Meh,
  Sun,
  Cloud,
  CloudRain
} from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Slider } from "@/components/ui/slider"
import { useAuth } from "@/hooks/useAuth"
import { toast } from "sonner"

interface MoodEntry {
  id: string
  user_id: string
  mood_score: number
  energy_level: number
  stress_level: number
  sleep_quality: number
  primary_emotion: string
  primary_sentiment: string
  input_text: string
  created_at: string
  emotion_analysis?: {
    top_emotions: Array<{
      emotion: string
      sentiment: string
      confidence: number
      color: string
    }>
    primary_emotion: string
    primary_sentiment: string
    confidence_score: number
  }
}

interface EmotionalWeather {
  current_mood: string
  weather_analogy: string
  forecast: string
  recommendations: string[]
}

export function EnhancedMoodServiceDashboard() {
  const { user } = useAuth()
  const [moodEntries, setMoodEntries] = useState<MoodEntry[]>([])
  const [emotionalWeather, setEmotionalWeather] = useState<EmotionalWeather | null>(null)
  const [loading, setLoading] = useState(true)
  const [creating, setCreating] = useState(false)
  const [showCreateForm, setShowCreateForm] = useState(false)
  
  // Form state
  const [formData, setFormData] = useState({
    mood_score: [7],
    energy_level: [6],
    stress_level: [3],
    sleep_quality: [7],
    input_text: ""
  })

  const API_BASE = import.meta.env.VITE_API_BASE_URL
  const token = localStorage.getItem('mantrapath_token')

  useEffect(() => {
    if (user?.id) {
      fetchMoodData()
    }
  }, [user])

  const fetchMoodData = async () => {
    if (!user?.id) return

    try {
      // Fetch recent mood entries
      const entriesResponse = await fetch(`${API_BASE}/mood-service/api/v1/mood/entries?limit=10`, {
        headers: token ? { 'Authorization': `Bearer ${token}` } : {}
      })
      
      if (entriesResponse.ok) {
        const entriesData = await entriesResponse.json()
        setMoodEntries(entriesData.entries || [])
      }

      // Fetch emotional weather
      const weatherResponse = await fetch(`${API_BASE}/mood-service/api/v1/analytics/emotional-weather`, {
        headers: token ? { 'Authorization': `Bearer ${token}` } : {}
      })
      
      if (weatherResponse.ok) {
        const weatherData = await weatherResponse.json()
        setEmotionalWeather(weatherData)
      }

    } catch (error) {
      console.error('Error fetching mood data:', error)
      toast.error('Failed to load mood data')
    } finally {
      setLoading(false)
    }
  }

  const createMoodEntry = async () => {
    if (!user?.id) return

    setCreating(true)
    try {
      const response = await fetch(`${API_BASE}/mood-service/api/v1/mood/entries`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        },
        body: JSON.stringify({
          mood_score: formData.mood_score[0],
          energy_level: formData.energy_level[0],
          stress_level: formData.stress_level[0],
          sleep_quality: formData.sleep_quality[0],
          input_text: formData.input_text
        })
      })
      
      if (response.ok) {
        const newEntry = await response.json()
        setMoodEntries(prev => [newEntry, ...prev])
        setShowCreateForm(false)
        setFormData({
          mood_score: [7],
          energy_level: [6],
          stress_level: [3],
          sleep_quality: [7],
          input_text: ""
        })
        toast.success('Mood entry created successfully!')
      } else {
        throw new Error('Failed to create mood entry')
      }
    } catch (error) {
      console.error('Error creating mood entry:', error)
      toast.error('Failed to create mood entry')
    } finally {
      setCreating(false)
    }
  }

  const getMoodIcon = (score: number) => {
    if (score >= 7) return <Smile className="h-5 w-5 text-green-600" />
    if (score >= 4) return <Meh className="h-5 w-5 text-yellow-600" />
    return <Frown className="h-5 w-5 text-red-600" />
  }

  const getMoodColor = (score: number) => {
    if (score >= 7) return "text-green-600"
    if (score >= 4) return "text-yellow-600"
    return "text-red-600"
  }

  const getWeatherIcon = (weather: string) => {
    if (weather.includes('sunny') || weather.includes('clear')) {
      return <Sun className="h-6 w-6 text-yellow-500" />
    }
    if (weather.includes('cloudy') || weather.includes('overcast')) {
      return <Cloud className="h-6 w-6 text-gray-500" />
    }
    if (weather.includes('rain') || weather.includes('storm')) {
      return <CloudRain className="h-6 w-6 text-blue-500" />
    }
    return <Sun className="h-6 w-6 text-yellow-500" />
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-accent-6"></div>
      </div>
    )
  }

  const latestMood = moodEntries[0]
  const avgMoodScore = moodEntries.reduce((acc, entry) => acc + entry.mood_score, 0) / Math.max(moodEntries.length, 1)

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Enhanced Mood Tracking</h1>
          <p className="text-neutral-11 mt-1">
            Advanced mood analysis with AI-powered emotional intelligence
          </p>
        </div>
        <Button onClick={() => setShowCreateForm(true)} className="bg-gradient-to-r from-pink-500 to-purple-600">
          <Plus className="h-4 w-4 mr-2" />
          Track Mood
        </Button>
      </div>

      {/* Emotional Weather */}
      {emotionalWeather && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <Card className="bg-gradient-to-r from-blue-50 to-purple-50 border-l-4 border-l-purple-500">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                {getWeatherIcon(emotionalWeather.weather_analogy)}
                Emotional Weather Forecast
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <p className="text-sm font-medium mb-1">Current Mood</p>
                  <p className="text-lg font-semibold">{emotionalWeather.current_mood}</p>
                </div>
                <div>
                  <p className="text-sm font-medium mb-1">Weather Analogy</p>
                  <p className="text-lg font-semibold">{emotionalWeather.weather_analogy}</p>
                </div>
                <div>
                  <p className="text-sm font-medium mb-1">Forecast</p>
                  <p className="text-sm text-neutral-11">{emotionalWeather.forecast}</p>
                </div>
              </div>
              {emotionalWeather.recommendations && emotionalWeather.recommendations.length > 0 && (
                <div className="mt-4">
                  <p className="text-sm font-medium mb-2">Recommendations</p>
                  <div className="flex flex-wrap gap-2">
                    {emotionalWeather.recommendations.map((rec, index) => (
                      <Badge key={index} variant="secondary">
                        {rec}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium">Current Mood</p>
                <p className={`text-2xl font-bold ${getMoodColor(latestMood?.mood_score || 0)}`}>
                  {latestMood?.mood_score || 0}/10
                </p>
              </div>
              {getMoodIcon(latestMood?.mood_score || 0)}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium">Average Mood</p>
                <p className={`text-2xl font-bold ${getMoodColor(avgMoodScore)}`}>
                  {avgMoodScore.toFixed(1)}/10
                </p>
              </div>
              <TrendingUp className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium">Energy Level</p>
                <p className="text-2xl font-bold text-green-600">
                  {latestMood?.energy_level || 0}/10
                </p>
              </div>
              <Zap className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium">Total Entries</p>
                <p className="text-2xl font-bold text-purple-600">
                  {moodEntries.length}
                </p>
              </div>
              <Calendar className="h-8 w-8 text-purple-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="entries" className="space-y-4">
        <TabsList>
          <TabsTrigger value="entries">Recent Entries</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
          <TabsTrigger value="emotions">Emotion Analysis</TabsTrigger>
        </TabsList>

        <TabsContent value="entries" className="space-y-4">
          {moodEntries.length > 0 ? (
            <div className="space-y-3">
              {moodEntries.map((entry) => (
                <motion.div
                  key={entry.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                >
                  <Card className="hover:shadow-lg transition-shadow">
                    <CardContent className="p-4">
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex items-center gap-3">
                          {getMoodIcon(entry.mood_score)}
                          <div>
                            <p className={`font-semibold ${getMoodColor(entry.mood_score)}`}>
                              Mood: {entry.mood_score}/10
                            </p>
                            <p className="text-sm text-neutral-11">
                              {new Date(entry.created_at).toLocaleString()}
                            </p>
                          </div>
                        </div>
                        <Badge variant="outline" className="capitalize">
                          {entry.primary_emotion || 'Unknown'}
                        </Badge>
                      </div>

                      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-3">
                        <div className="text-center">
                          <p className="text-xs text-neutral-11">Energy</p>
                          <p className="font-semibold text-green-600">{entry.energy_level}/10</p>
                        </div>
                        <div className="text-center">
                          <p className="text-xs text-neutral-11">Stress</p>
                          <p className="font-semibold text-red-600">{entry.stress_level}/10</p>
                        </div>
                        <div className="text-center">
                          <p className="text-xs text-neutral-11">Sleep</p>
                          <p className="font-semibold text-blue-600">{entry.sleep_quality}/10</p>
                        </div>
                        <div className="text-center">
                          <p className="text-xs text-neutral-11">Sentiment</p>
                          <Badge 
                            variant="outline"
                            className={
                              entry.primary_sentiment === 'positive' ? 'text-green-600' :
                              entry.primary_sentiment === 'negative' ? 'text-red-600' :
                              'text-yellow-600'
                            }
                          >
                            {entry.primary_sentiment || 'Neutral'}
                          </Badge>
                        </div>
                      </div>

                      {entry.input_text && (
                        <p className="text-sm text-neutral-11 bg-neutral-2 p-3 rounded-lg">
                          {entry.input_text}
                        </p>
                      )}

                      {entry.emotion_analysis?.top_emotions && (
                        <div className="mt-3">
                          <p className="text-xs font-medium mb-2">Emotion Analysis</p>
                          <div className="flex flex-wrap gap-1">
                            {entry.emotion_analysis.top_emotions.slice(0, 3).map((emotion, index) => (
                              <Badge 
                                key={index} 
                                variant="outline" 
                                className="text-xs"
                                style={{ 
                                  borderColor: emotion.color,
                                  color: emotion.color 
                                }}
                              >
                                {emotion.emotion} ({emotion.confidence.toFixed(1)}%)
                              </Badge>
                            ))}
                          </div>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </div>
          ) : (
            <Alert>
              <Heart className="h-4 w-4" />
              <AlertDescription>
                No mood entries yet. Start tracking your mood to see insights and patterns.
              </AlertDescription>
            </Alert>
          )}
        </TabsContent>

        <TabsContent value="analytics" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="h-5 w-5" />
                Mood Analytics
              </CardTitle>
              <CardDescription>
                Detailed insights into your emotional patterns
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-neutral-11">
                Analytics dashboard is being enhanced. Check back soon for detailed mood trends and correlations.
              </p>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="emotions" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity className="h-5 w-5" />
                Emotion Intelligence
              </CardTitle>
              <CardDescription>
                AI-powered emotion detection and analysis
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-neutral-11">
                Emotion intelligence features are being developed. Soon you'll see detailed emotion breakdowns and patterns.
              </p>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Create Mood Entry Modal */}
      {showCreateForm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-white rounded-lg p-6 w-full max-w-md mx-4"
          >
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold">Track Your Mood</h2>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowCreateForm(false)}
              >
                ×
              </Button>
            </div>

            <div className="space-y-4">
              <div>
                <Label htmlFor="mood-score">Mood Score: {formData.mood_score[0]}/10</Label>
                <Slider
                  id="mood-score"
                  min={1}
                  max={10}
                  step={1}
                  value={formData.mood_score}
                  onValueChange={(value) => setFormData(prev => ({ ...prev, mood_score: value }))}
                  className="mt-2"
                />
              </div>

              <div>
                <Label htmlFor="energy-level">Energy Level: {formData.energy_level[0]}/10</Label>
                <Slider
                  id="energy-level"
                  min={1}
                  max={10}
                  step={1}
                  value={formData.energy_level}
                  onValueChange={(value) => setFormData(prev => ({ ...prev, energy_level: value }))}
                  className="mt-2"
                />
              </div>

              <div>
                <Label htmlFor="stress-level">Stress Level: {formData.stress_level[0]}/10</Label>
                <Slider
                  id="stress-level"
                  min={1}
                  max={10}
                  step={1}
                  value={formData.stress_level}
                  onValueChange={(value) => setFormData(prev => ({ ...prev, stress_level: value }))}
                  className="mt-2"
                />
              </div>

              <div>
                <Label htmlFor="sleep-quality">Sleep Quality: {formData.sleep_quality[0]}/10</Label>
                <Slider
                  id="sleep-quality"
                  min={1}
                  max={10}
                  step={1}
                  value={formData.sleep_quality}
                  onValueChange={(value) => setFormData(prev => ({ ...prev, sleep_quality: value }))}
                  className="mt-2"
                />
              </div>

              <div>
                <Label htmlFor="notes">How are you feeling? (Optional)</Label>
                <Textarea
                  id="notes"
                  placeholder="Describe your mood, thoughts, or what's happening today..."
                  value={formData.input_text}
                  onChange={(e) => setFormData(prev => ({ ...prev, input_text: e.target.value }))}
                  className="mt-2"
                />
              </div>
            </div>

            <div className="flex gap-2 mt-6">
              <Button
                variant="outline"
                onClick={() => setShowCreateForm(false)}
                className="flex-1"
              >
                Cancel
              </Button>
              <Button
                onClick={createMoodEntry}
                disabled={creating}
                className="flex-1 bg-gradient-to-r from-pink-500 to-purple-600"
              >
                {creating ? 'Saving...' : 'Save Entry'}
              </Button>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  )
}