import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip'
import type { EmotionSnapshot } from '@/types/journal'
import { getEmotionColor } from '@/utils/emotionAnalysis'

interface EmotionTimelineProps {
  snapshots: EmotionSnapshot[]
  height?: number
  showLabels?: boolean
  interactive?: boolean
}

export function EmotionTimeline({ 
  snapshots, 
  height = 40, 
  showLabels = false,
  interactive = false 
}: EmotionTimelineProps) {
  if (snapshots.length === 0) {
    return (
      <div 
        className="w-full bg-gray-200 rounded"
        style={{ height: `${height}px` }}
      >
        <div className="flex items-center justify-center h-full text-sm text-gray-500">
          No recording data yet
        </div>
      </div>
    )
  }

  // Each snapshot gets equal width
  const segmentWidth = 100 / snapshots.length

  return (
    <TooltipProvider>
      <div className="w-full rounded overflow-hidden" style={{ height: `${height}px` }}>
        <div className="flex h-full">
          {snapshots.map((snap, index) => {
            const color = getEmotionColor(snap.dominant)
            const timestamp = `${Math.floor(snap.timestamp)}s`
            const emotionLabel = snap.dominant
            const confidence = `${(snap.confidence * 100).toFixed(1)}%`

            const segment = (
              <div
                key={index}
                className="transition-all hover:opacity-80 cursor-pointer"
                style={{
                  width: `${segmentWidth}%`,
                  height: '100%',
                  backgroundColor: color,
                  opacity: Math.max(snap.confidence, 0.3), // Fade based on confidence
                  borderRight: index < snapshots.length - 1 ? '1px solid rgba(255,255,255,0.2)' : 'none'
                }}
                title={interactive ? `${timestamp}: ${emotionLabel} (${confidence})` : undefined}
              />
            )

            if (interactive) {
              return (
                <Tooltip key={index}>
                  <TooltipTrigger asChild>
                    {segment}
                  </TooltipTrigger>
                  <TooltipContent>
                    <div className="text-center">
                      <div className="font-medium">{emotionLabel}</div>
                      <div className="text-xs text-muted-foreground">
                        {timestamp} • {confidence}
                      </div>
                    </div>
                  </TooltipContent>
                </Tooltip>
              )
            }

            return segment
          })}
        </div>
      </div>

      {/* Optional: Legend */}
      {showLabels && (
        <div className="mt-2 flex flex-wrap gap-2 justify-center text-xs">
          {['neutral', 'happy', 'sad', 'angry', 'fearful', 'disgusted', 'surprised'].map(emotion => {
            const color = getEmotionColor(emotion)
            const count = snapshots.filter(s => s.dominant === emotion).length
            if (count === 0) return null
            
            return (
              <div key={emotion} className="flex items-center gap-1">
                <div 
                  className="w-3 h-3 rounded"
                  style={{ backgroundColor: color }}
                />
                <span className="capitalize">{emotion}: {count}</span>
              </div>
            )
          })}
        </div>
      )}
    </TooltipProvider>
  )
}
