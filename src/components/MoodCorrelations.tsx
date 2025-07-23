import { useMemo } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { BarChart3, TrendUp, TrendDown } from '@phosphor-icons/react'
import { useMoods } from '@/hooks/useWellness'
import { motion } from 'framer-motion'

export function MoodCorrelations() {
  const { moods } = useMoods()

  const correlations = useMemo(() => {
    if (moods.length < 14) return []

    const moodValues = { 'very-low': 1, 'low': 2, 'neutral': 3, 'good': 4, 'excellent': 5 }
    
    // Analyze correlations with day of week
    const dayCorrelations = Array.from({ length: 7 }, (_, day) => {
      const dayMoods = moods.filter(m => (m.dayOfWeek ?? new Date(m.timestamp).getDay()) === day)
      if (dayMoods.length < 2) return null
      
      const avg = dayMoods.reduce((sum, m) => sum + moodValues[m.mood], 0) / dayMoods.length
      const dayName = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'][day]
      
      return {
        type: 'day',
        label: dayName,
        value: avg,
        count: dayMoods.length,
        trend: avg > 3 ? 'positive' : avg < 3 ? 'negative' : 'neutral'
      }
    }).filter(Boolean)

    // Analyze correlations with time of day
    const timeCorrelations = ['morning', 'afternoon', 'evening', 'night'].map(time => {
      const timeMoods = moods.filter(m => m.timeOfDay === time)
      if (timeMoods.length < 2) return null
      
      const avg = timeMoods.reduce((sum, m) => sum + moodValues[m.mood], 0) / timeMoods.length
      
      return {
        type: 'time',
        label: time.charAt(0).toUpperCase() + time.slice(1),
        value: avg,
        count: timeMoods.length,
        trend: avg > 3 ? 'positive' : avg < 3 ? 'negative' : 'neutral'
      }
    }).filter(Boolean)

    // Analyze correlations with energy levels
    const energyCorrelations = ['high', 'medium', 'low'].map(energy => {
      const energyMoods = moods.filter(m => m.energy === energy)
      if (energyMoods.length < 2) return null
      
      const avg = energyMoods.reduce((sum, m) => sum + moodValues[m.mood], 0) / energyMoods.length
      
      return {
        type: 'energy',
        label: `${energy.charAt(0).toUpperCase() + energy.slice(1)} Energy`,
        value: avg,
        count: energyMoods.length,
        trend: avg > 3 ? 'positive' : avg < 3 ? 'negative' : 'neutral'
      }
    }).filter(Boolean)

    return [...dayCorrelations, ...timeCorrelations, ...energyCorrelations]
      .sort((a, b) => Math.abs(b.value - 3) - Math.abs(a.value - 3)) // Sort by deviation from neutral
      .slice(0, 6) // Top 6 correlations
  }, [moods])

  if (correlations.length === 0) return null

  const getValueColor = (value: number) => {
    if (value >= 4) return 'text-green-600 bg-green-50'
    if (value >= 3.5) return 'text-blue-600 bg-blue-50'
    if (value >= 2.5) return 'text-yellow-600 bg-yellow-50'
    return 'text-red-600 bg-red-50'
  }

  const getBarWidth = (value: number) => {
    return `${(value / 5) * 100}%`
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.4 }}
    >
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="text-indigo-600" size={24} />
            Mood Correlations
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {correlations.map((correlation, index) => (
              <motion.div
                key={`${correlation.type}-${correlation.label}`}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="space-y-2"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium">{correlation.label}</span>
                    <Badge variant="outline" className="text-xs">
                      {correlation.count} entries
                    </Badge>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge className={`text-xs ${getValueColor(correlation.value)}`}>
                      {correlation.value.toFixed(1)}/5
                    </Badge>
                    {correlation.trend === 'positive' && <TrendUp size={16} className="text-green-600" />}
                    {correlation.trend === 'negative' && <TrendDown size={16} className="text-red-600" />}
                  </div>
                </div>
                
                <div className="relative h-2 bg-gray-100 rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: getBarWidth(correlation.value) }}
                    transition={{ delay: index * 0.1 + 0.2, duration: 0.5 }}
                    className={`h-full rounded-full ${
                      correlation.value >= 4 ? 'bg-green-500' :
                      correlation.value >= 3.5 ? 'bg-blue-500' :
                      correlation.value >= 2.5 ? 'bg-yellow-500' :
                      'bg-red-500'
                    }`}
                  />
                </div>
              </motion.div>
            ))}
            
            <div className="pt-4 text-xs text-muted-foreground">
              <p>💡 These correlations show how different factors relate to your mood. Higher values indicate better moods during those times or conditions.</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}