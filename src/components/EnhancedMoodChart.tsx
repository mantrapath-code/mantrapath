import { useState, useRef, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { 
  Calendar, 
  TrendUp, 
  TrendDown, 
  Minus, 
  ZoomIn, 
  ZoomOut,
  RotateCcw,
  ArrowUp,
  ArrowDown
} from "@phosphor-icons/react"
import { useMoods } from "@/hooks/useMoods"
import { MoodEntry } from "@/types"
import { motion, AnimatePresence } from "framer-motion"

interface TooltipData {
  mood: MoodEntry
  x: number
  y: number
  visible: boolean
}

interface ChartProps {
  className?: string
}

export function EnhancedMoodChart({ className }: ChartProps) {
  const { moods } = useMoods()
  const [timeRange, setTimeRange] = useState<'week' | 'month' | 'quarter'>('week')
  const [tooltip, setTooltip] = useState<TooltipData>({ 
    mood: {} as MoodEntry, 
    x: 0, 
    y: 0, 
    visible: false 
  })
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null)
  const svgRef = useRef<SVGSVGElement>(null)

  // Get data based on time range
  const getFilteredMoods = () => {
    const now = new Date()
    let cutoffDate: Date
    
    switch (timeRange) {
      case 'week':
        cutoffDate = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
        break
      case 'month':
        cutoffDate = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000)
        break
      case 'quarter':
        cutoffDate = new Date(now.getTime() - 90 * 24 * 60 * 60 * 1000)
        break
    }
    
    return moods
      .filter(mood => new Date(mood.timestamp) >= cutoffDate)
      .sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime())
  }

  const filteredMoods = getFilteredMoods()

  const getMoodValue = (mood: string) => {
    switch (mood) {
      case 'excellent': return 5
      case 'good': return 4
      case 'neutral': return 3
      case 'low': return 2
      case 'very-low': return 1
      default: return 3
    }
  }

  const getMoodColor = (mood: string) => {
    const colors = {
      'excellent': '#22c55e',
      'good': '#3b82f6',
      'neutral': '#eab308',
      'low': '#f97316',
      'very-low': '#ef4444'
    }
    return colors[mood] || colors.neutral
  }

  // Calculate trend for the period
  const calculateTrend = () => {
    if (filteredMoods.length < 2) return { direction: 'neutral', change: 0 }
    
    const midPoint = Math.floor(filteredMoods.length / 2)
    const firstHalf = filteredMoods.slice(0, midPoint)
    const secondHalf = filteredMoods.slice(midPoint)
    
    const firstAvg = firstHalf.reduce((sum, mood) => sum + getMoodValue(mood.mood), 0) / firstHalf.length
    const secondAvg = secondHalf.reduce((sum, mood) => sum + getMoodValue(mood.mood), 0) / secondHalf.length
    
    const change = secondAvg - firstAvg
    const direction = change > 0.2 ? 'up' : change < -0.2 ? 'down' : 'neutral'
    
    return { direction, change: Math.abs(change) }
  }

  const trend = calculateTrend()

  const handleMouseMove = (event: React.MouseEvent<SVGSVGElement>, mood: MoodEntry, index: number) => {
    if (!svgRef.current) return
    
    const rect = svgRef.current.getBoundingClientRect()
    const x = event.clientX - rect.left
    const y = event.clientY - rect.top
    
    setTooltip({
      mood,
      x: x + 10,
      y: y - 10,
      visible: true
    })
    setHoveredIndex(index)
  }

  const handleMouseLeave = () => {
    setTooltip(prev => ({ ...prev, visible: false }))
    setHoveredIndex(null)
  }

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp)
    const timeOptions: Intl.DateTimeFormatOptions = { 
      hour: '2-digit', 
      minute: '2-digit' 
    }
    
    if (timeRange === 'week') {
      return `${date.toLocaleDateString('en-US', { weekday: 'short' })} ${date.toLocaleTimeString('en-US', timeOptions)}`
    } else {
      return `${date.toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric' 
      })} ${date.toLocaleTimeString('en-US', timeOptions)}`
    }
  }

  const chartWidth = 400
  const chartHeight = 200
  const padding = 40

  if (filteredMoods.length === 0) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Calendar className="text-primary" size={20} />
            Mood Timeline
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center text-muted-foreground py-8">
            <Calendar size={48} className="mx-auto mb-2 opacity-50" />
            <p>No mood data for this period</p>
            <p className="text-sm">Start tracking your mood to see patterns</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className={className}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Calendar className="text-primary" size={20} />
            Mood Timeline
            {trend.direction !== 'neutral' && (
              <Badge 
                variant={trend.direction === 'up' ? 'default' : 'secondary'}
                className="ml-2 text-xs"
              >
                {trend.direction === 'up' ? (
                  <ArrowUp size={12} className="mr-1" />
                ) : (
                  <ArrowDown size={12} className="mr-1" />
                )}
                {trend.direction === 'up' ? 'Improving' : 'Declining'} 
                ({(trend.change * 20).toFixed(0)}%)
              </Badge>
            )}
          </CardTitle>
          
          <div className="flex items-center gap-2">
            <div className="flex rounded-lg border p-1">
              {['week', 'month', 'quarter'].map((range) => (
                <Button
                  key={range}
                  variant={timeRange === range ? 'default' : 'ghost'}
                  size="sm"
                  onClick={() => setTimeRange(range as typeof timeRange)}
                  className="text-xs h-7 px-2"
                >
                  {range === 'week' ? '7D' : range === 'month' ? '30D' : '90D'}
                </Button>
              ))}
            </div>
            
            <Button
              variant="outline"
              size="sm"
              onClick={() => setTimeRange('week')}
              className="text-xs h-7 px-2"
            >
              <RotateCcw size={12} />
            </Button>
          </div>
        </div>
      </CardHeader>
      
      <CardContent>
        <div className="relative">
          <svg
            ref={svgRef}
            width="100%"
            height={chartHeight}
            viewBox={`0 0 ${chartWidth} ${chartHeight}`}
            className="overflow-visible"
          >
            {/* Grid lines */}
            <defs>
              <linearGradient id="moodAreaGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stopColor="var(--primary)" stopOpacity="0.2" />
                <stop offset="100%" stopColor="var(--primary)" stopOpacity="0.05" />
              </linearGradient>
            </defs>
            
            {/* Y-axis grid lines */}
            {[1, 2, 3, 4, 5].map((level) => (
              <line
                key={level}
                x1={padding}
                y1={chartHeight - padding - ((level - 1) / 4) * (chartHeight - 2 * padding)}
                x2={chartWidth - padding}
                y2={chartHeight - padding - ((level - 1) / 4) * (chartHeight - 2 * padding)}
                stroke="var(--border)"
                strokeWidth="0.5"
                opacity="0.3"
              />
            ))}
            
            {/* Area chart fill */}
            <path
              d={(() => {
                if (filteredMoods.length === 0) return ""
                
                const points = filteredMoods.map((mood, index) => {
                  const x = padding + (index / Math.max(filteredMoods.length - 1, 1)) * (chartWidth - 2 * padding)
                  const y = chartHeight - padding - ((getMoodValue(mood.mood) - 1) / 4) * (chartHeight - 2 * padding)
                  return `${x},${y}`
                })
                
                const firstX = padding
                const lastX = padding + (chartWidth - 2 * padding)
                const bottomY = chartHeight - padding
                
                return `M ${firstX},${bottomY} L ${points.join(' L ')} L ${lastX},${bottomY} Z`
              })()}
              fill="url(#moodAreaGradient)"
            />
            
            {/* Mood line */}
            <path
              d={(() => {
                const points = filteredMoods.map((mood, index) => {
                  const x = padding + (index / Math.max(filteredMoods.length - 1, 1)) * (chartWidth - 2 * padding)
                  const y = chartHeight - padding - ((getMoodValue(mood.mood) - 1) / 4) * (chartHeight - 2 * padding)
                  return `${x},${y}`
                })
                
                return `M ${points.join(' L ')}`
              })()}
              fill="none"
              stroke="var(--primary)"
              strokeWidth="2.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            
            {/* Data points */}
            {filteredMoods.map((mood, index) => {
              const x = padding + (index / Math.max(filteredMoods.length - 1, 1)) * (chartWidth - 2 * padding)
              const y = chartHeight - padding - ((getMoodValue(mood.mood) - 1) / 4) * (chartHeight - 2 * padding)
              const isHovered = hoveredIndex === index
              
              return (
                <motion.g key={mood.id}>
                  {/* Hover area */}
                  <circle
                    cx={x}
                    cy={y}
                    r="12"
                    fill="transparent"
                    className="cursor-pointer"
                    onMouseMove={(e) => handleMouseMove(e, mood, index)}
                    onMouseLeave={handleMouseLeave}
                  />
                  
                  {/* Hover ring */}
                  <AnimatePresence>
                    {isHovered && (
                      <motion.circle
                        initial={{ scale: 0.8, opacity: 0 }}
                        animate={{ scale: 1.2, opacity: 0.3 }}
                        exit={{ scale: 0.8, opacity: 0 }}
                        cx={x}
                        cy={y}
                        r="8"
                        fill={getMoodColor(mood.mood)}
                      />
                    )}
                  </AnimatePresence>
                  
                  {/* Data point */}
                  <motion.circle
                    initial={{ scale: 0 }}
                    animate={{ scale: isHovered ? 1.2 : 1 }}
                    cx={x}
                    cy={y}
                    r="4"
                    fill={getMoodColor(mood.mood)}
                    stroke="white"
                    strokeWidth="2"
                    className="cursor-pointer"
                  />
                </motion.g>
              )
            })}
          </svg>
          
          {/* Y-axis labels */}
          <div className="absolute left-0 top-0 h-full flex flex-col justify-between text-xs text-muted-foreground py-10">
            <span>Excellent</span>
            <span>Good</span>
            <span>Neutral</span>
            <span>Low</span>
            <span>Very Low</span>
          </div>
          
          {/* Tooltip */}
          <AnimatePresence>
            {tooltip.visible && (
              <motion.div
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.8 }}
                className="absolute z-50 pointer-events-none"
                style={{
                  left: Math.min(tooltip.x, chartWidth - 200),
                  top: Math.max(tooltip.y - 10, 10)
                }}
              >
                <div className="bg-card border shadow-lg rounded-lg p-3 max-w-xs">
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <div 
                        className="w-3 h-3 rounded-full" 
                        style={{ backgroundColor: getMoodColor(tooltip.mood.mood) }}
                      />
                      <span className="font-medium capitalize">{tooltip.mood.mood}</span>
                    </div>
                    
                    <div className="text-xs text-muted-foreground">
                      <div>{formatTimestamp(tooltip.mood.timestamp)}</div>
                      <div className="mt-1">
                        ID: {tooltip.mood.id?.slice(-6)}
                      </div>
                    </div>
                    
                    {tooltip.mood.note && (
                      <div className="text-xs border-t pt-2">
                        <div className="font-medium">Note:</div>
                        <div className="text-muted-foreground italic">
                          "{tooltip.mood.note.slice(0, 100)}{tooltip.mood.note.length > 100 ? '...' : ''}"
                        </div>
                      </div>
                    )}
                    
                    {tooltip.mood.triggers && tooltip.mood.triggers.length > 0 && (
                      <div className="text-xs border-t pt-2">
                        <div className="font-medium mb-1">Triggers:</div>
                        <div className="flex flex-wrap gap-1">
                          {tooltip.mood.triggers.slice(0, 3).map((trigger, index) => (
                            <Badge key={index} variant="outline" className="text-xs h-5">
                              {trigger}
                            </Badge>
                          ))}
                          {tooltip.mood.triggers.length > 3 && (
                            <Badge variant="outline" className="text-xs h-5">
                              +{tooltip.mood.triggers.length - 3}
                            </Badge>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
        
        {/* Time range labels */}
        <div className="flex justify-between text-xs text-muted-foreground mt-4 px-10">
          <span>
            {timeRange === 'week' ? '7 days ago' : 
             timeRange === 'month' ? '30 days ago' : 
             '90 days ago'}
          </span>
          <span>Today</span>
        </div>
        
        {/* Chart statistics */}
        <div className="grid grid-cols-3 gap-4 mt-6 p-4 bg-muted/30 rounded-lg">
          <div className="text-center">
            <div className="text-sm font-medium">Average</div>
            <div className="text-xs text-muted-foreground">
              {(filteredMoods.reduce((sum, mood) => sum + getMoodValue(mood.mood), 0) / filteredMoods.length).toFixed(1)}/5
            </div>
          </div>
          <div className="text-center">
            <div className="text-sm font-medium">Entries</div>
            <div className="text-xs text-muted-foreground">
              {filteredMoods.length} mood{filteredMoods.length !== 1 ? 's' : ''}
            </div>
          </div>
          <div className="text-center">
            <div className="text-sm font-medium">Trend</div>
            <div className={`text-xs flex items-center justify-center gap-1 ${
              trend.direction === 'up' ? 'text-green-600' : 
              trend.direction === 'down' ? 'text-red-600' : 
              'text-muted-foreground'
            }`}>
              {trend.direction === 'up' ? <TrendUp size={12} /> :
               trend.direction === 'down' ? <TrendDown size={12} /> :
               <Minus size={12} />}
              {trend.direction === 'neutral' ? 'Stable' : `${(trend.change * 20).toFixed(0)}%`}
            </div>
          </div>
        </div>
        
        {/* Legend */}
        <div className="flex items-center justify-center gap-4 mt-4 text-xs">
          {[
            { mood: 'excellent', color: '#22c55e', label: 'Excellent' },
            { mood: 'good', color: '#3b82f6', label: 'Good' },
            { mood: 'neutral', color: '#eab308', label: 'Neutral' },
            { mood: 'low', color: '#f97316', label: 'Low' },
            { mood: 'very-low', color: '#ef4444', label: 'Very Low' }
          ].map(({ mood, color, label }) => (
            <div key={mood} className="flex items-center gap-1">
              <div 
                className="w-3 h-3 rounded-full" 
                style={{ backgroundColor: color }}
              />
              <span>{label}</span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}