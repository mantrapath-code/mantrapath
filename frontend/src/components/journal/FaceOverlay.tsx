import { useEffect, useRef } from 'react'
import type { EmotionSnapshot } from '@/types/journal'
import { getEmotionColor, getEmotionLabel } from '@/utils/emotionAnalysis'

interface FaceOverlayProps {
  videoRef: React.RefObject<HTMLVideoElement | null>
  canvasRef: React.RefObject<HTMLCanvasElement | null>
  detection: any | null  // face-api.js detection result
  currentEmotion: EmotionSnapshot | null
}

export function FaceOverlay({ videoRef, canvasRef, detection, currentEmotion }: FaceOverlayProps) {
  const animationFrameRef = useRef<number>()

  // Match canvas size to video dimensions
  useEffect(() => {
    if (videoRef.current && canvasRef.current) {
      const video = videoRef.current
      const canvas = canvasRef.current
      canvas.width = video.videoWidth
      canvas.height = video.videoHeight
    }
  }, [videoRef, canvasRef])

  // Draw detection overlay
  useEffect(() => {
    if (!canvasRef.current || !detection || !currentEmotion) {
      // Clear canvas if no detection
      if (canvasRef.current) {
        const ctx = canvasRef.current.getContext('2d')
        if (ctx) {
          ctx.clearRect(0, 0, canvasRef.current.width, canvasRef.current.height)
        }
      }
      return
    }

    const ctx = canvasRef.current.getContext('2d')
    if (!ctx) return

    const draw = () => {
      // Clear previous drawings
      ctx.clearRect(0, 0, canvasRef.current!.width, canvasRef.current!.height)

      const box = detection.detection.box

      // Draw bounding box
      ctx.strokeStyle = getEmotionColor(currentEmotion.dominant)
      ctx.lineWidth = 3
      ctx.strokeRect(box.x, box.y, box.width, box.height)

      // Draw emotion label
      const label = getEmotionLabel(currentEmotion.dominant)
      const confidenceText = `${(currentEmotion.confidence * 100).toFixed(1)}%`
      
      // Background for label
      ctx.fillStyle = 'rgba(0, 0, 0, 0.7)'
      const textWidth = ctx.measureText(`${label} ${confidenceText}`).width
      const labelY = box.y - 25
      ctx.fillRect(box.x - 2, labelY - 18, textWidth + 8, 20)

      // Label text
      ctx.fillStyle = '#ffffff'
      ctx.font = '16px system-ui'
      ctx.fillText(label, box.x + 2, labelY - 2)

      // Confidence percentage
      ctx.font = 'bold 16px system-ui'
      ctx.fillText(confidenceText, box.x + 2 + ctx.measureText(`${label} `).width, labelY - 2)

      // Optional: Draw landmarks (68 facial points)
      if (detection.landmarks) {
        ctx.strokeStyle = 'rgba(0, 255, 0, 0.5)'
        ctx.fillStyle = 'rgba(0, 255, 0, 0.8)'
        ctx.lineWidth = 1

        detection.landmarks.positions.forEach((point: { x: number; y: number }) => {
          ctx.beginPath()
          ctx.arc(point.x, point.y, 2, 0, 2 * Math.PI)
          ctx.fill()
        })
      }
    }

    draw()

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current)
      }
    }
  }, [canvasRef, detection, currentEmotion])

  return null // Canvas is rendered by parent component
}
