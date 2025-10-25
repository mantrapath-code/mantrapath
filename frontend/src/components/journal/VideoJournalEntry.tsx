import { useState, useRef, useEffect } from 'react'
import * as faceapi from 'face-api.js'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Video, Stop, CircleNotch, Warning, Camera } from '@phosphor-icons/react'
import { toast } from 'sonner'
import { FaceOverlay } from './FaceOverlay'
import { EmotionTimeline } from './EmotionTimeline'
import type { EmotionSnapshot } from '@/types/journal'
import { getDominantEmotion, getEmotionColor, getEmotionLabel, calculateFacialSummary } from '@/utils/emotionAnalysis'
import { apiService } from '@/services/api'

interface VideoJournalEntryProps {
  onSuccess?: () => void
}

export function VideoJournalEntry({ onSuccess }: VideoJournalEntryProps) {
  const [isRecording, setIsRecording] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [modelsLoaded, setModelsLoaded] = useState(false)
  const [recordingDuration, setRecordingDuration] = useState(0)
  const [emotionSnapshots, setEmotionSnapshots] = useState<EmotionSnapshot[]>([])
  const [currentEmotion, setCurrentEmotion] = useState<EmotionSnapshot | null>(null)
  const [currentDetection, setCurrentDetection] = useState<any | null>(null)
  const [error, setError] = useState<string | null>(null)
  
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const chunksRef = useRef<Blob[]>([])
  const detectionIntervalRef = useRef<NodeJS.Timeout | null>(null)
  const durationIntervalRef = useRef<NodeJS.Timeout | null>(null)
  const streamRef = useRef<MediaStream | null>(null)

  // Load face-api.js models
  useEffect(() => {
    const loadModels = async () => {
      try {
        const MODEL_URL = 'https://cdn.jsdelivr.net/npm/@vladmandic/face-api/model'
        
        await faceapi.nets.tinyFaceDetector.loadFromUri(MODEL_URL)
        await faceapi.nets.faceExpressionNet.loadFromUri(MODEL_URL)
        await faceapi.nets.faceLandmark68Net.loadFromUri(MODEL_URL)
        
        setModelsLoaded(true)
      } catch (err) {
        console.error('Failed to load face-api models:', err)
        setError('Failed to load emotion detection models')
        toast.error('Could not load emotion detection models. Please refresh the page.')
      }
    }

    loadModels()
  }, [])

  // Start recording
  const startRecording = async () => {
    try {
      setError(null)
      
      // Request camera and microphone access
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'user', width: 640, height: 480 },
        audio: true
      })

      streamRef.current = stream

      if (videoRef.current) {
        videoRef.current.srcObject = stream
        videoRef.current.play()
      }

      // Initialize MediaRecorder
      const options = { mimeType: 'video/webm;codecs=vp9,opus' }
      const mediaRecorder = new MediaRecorder(stream, options)
      mediaRecorderRef.current = mediaRecorder
      chunksRef.current = []

      mediaRecorder.ondataavailable = (event) => {
        console.log('MediaRecorder ondataavailable called, data.size:', event.data.size)
        if (event.data.size > 0) {
          chunksRef.current.push(event.data)
          console.log('Added chunk, total chunks now:', chunksRef.current.length)
        }
      }

      mediaRecorder.start()
      setIsRecording(true)

      // Start emotion detection loop (every 500ms)
      const startTime = Date.now()
      detectionIntervalRef.current = setInterval(() => {
        detectEmotions()
      }, 500)

      // Start duration timer
      durationIntervalRef.current = setInterval(() => {
        setRecordingDuration(prev => prev + 0.5)
      }, 500)

    } catch (err) {
      console.error('Failed to start recording:', err)
      setError('Camera access denied. Please enable camera permissions.')
      toast.error('Could not access camera. Please check permissions.')
    }
  }

  // Detect emotions using face-api.js
  const detectEmotions = async () => {
    if (!videoRef.current || !modelsLoaded) return

    try {
      const detection = await faceapi
        .detectSingleFace(videoRef.current, new faceapi.TinyFaceDetectorOptions())
        .withFaceLandmarks()
        .withFaceExpressions()

      if (detection) {
        setCurrentDetection(detection)
        
        const expressions = detection.expressions as any
        const { emotion: dominant, confidence } = getDominantEmotion(expressions)
        
        const snapshot: EmotionSnapshot = {
          timestamp: recordingDuration,
          expressions: {
            neutral: expressions.neutral,
            happy: expressions.happy,
            sad: expressions.sad,
            angry: expressions.angry,
            fearful: expressions.fearful,
            disgusted: expressions.disgusted,
            surprised: expressions.surprised
          },
          dominant,
          confidence
        }

        setCurrentEmotion(snapshot)
        setEmotionSnapshots(prev => [...prev, snapshot])
      } else {
        setCurrentDetection(null)
        setCurrentEmotion(null)
      }
    } catch (err) {
      console.error('Emotion detection error:', err)
    }
  }

  // Stop recording - async to wait for MediaRecorder to fully stop
  const stopRecording = async () => {
    return new Promise<void>((resolve) => {
      if (!mediaRecorderRef.current) {
        console.warn('stopRecording called but mediaRecorderRef.current is null')
        resolve()
        return
      }
      
      const recorder = mediaRecorderRef.current
      
      console.log('Stopping MediaRecorder, current state:', recorder.state)
      
      // Add event listener for when recording actually stops
      const onStop = () => {
        console.log('MediaRecorder stop event fired, chunksRef.current.length:', chunksRef.current.length)
        recorder.removeEventListener('stop', onStop)
        resolve()
      }
      
      recorder.addEventListener('stop', onStop)
      
      // Stop MediaRecorder
      if (recorder.state !== 'inactive') {
        console.log('Calling recorder.stop()')
        recorder.stop()
      } else {
        console.warn('MediaRecorder already inactive')
        resolve()
      }
    })
  }

  // Handle stop recording and cleanup
  const handleStopRecording = async () => {
    try {
      console.log('handleStopRecording called, chunksRef.current.length:', chunksRef.current.length)
      
      // Wait for MediaRecorder to actually stop and emit final chunks
      await stopRecording()
      
      console.log('After stopRecording(), chunksRef.current.length:', chunksRef.current.length)
      
      // Clear intervals
      if (detectionIntervalRef.current) {
        clearInterval(detectionIntervalRef.current)
        detectionIntervalRef.current = null
      }
      
      if (durationIntervalRef.current) {
        clearInterval(durationIntervalRef.current)
        durationIntervalRef.current = null
      }
      
      // Stop camera stream
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop())
        streamRef.current = null
      }
      
      setIsRecording(false)
      
      // Process and save video - check after MediaRecorder has stopped
      if (chunksRef.current.length > 0) {
        console.log('Processing video with', chunksRef.current.length, 'chunks')
        await processAndSaveVideo()
      } else {
        console.error('No video data after stopping recording. Recording duration was:', recordingDuration)
        toast.error('No video data recorded. Please try recording for at least a few seconds.')
        // Reset state
        setEmotionSnapshots([])
        setCurrentEmotion(null)
        setRecordingDuration(0)
      }
    } catch (err) {
      console.error('Error stopping recording:', err)
      toast.error('Failed to stop recording properly')
    }
  }

  // Process video and save journal entry
  const processAndSaveVideo = async () => {
    setIsProcessing(true)

    try {
      // Create video blob
      const videoBlob = new Blob(chunksRef.current, { type: 'video/webm' })
      console.log('Processing video blob, size:', videoBlob.size, 'bytes')

      // 1. Send to Voice Service for STT
      toast.loading('Transcribing video...')
      const sttResult = await apiService.transcribeVideo(videoBlob)
      console.log('STT result:', sttResult)
      
      // 2. Get text emotion from AI Event Processor
      toast.loading('Analyzing emotions...')
      const textEmotion = await apiService.analyzeTextEmotion(sttResult.transcript, sttResult.language)
      console.log('Text emotion result:', textEmotion)
      
      // 3. Calculate facial summary
      const facialSummary = calculateFacialSummary(emotionSnapshots)
      console.log('Facial summary:', facialSummary)
      
      // 4. Create journal entry
      const journalData = {
        title: `Video Journal - ${new Date().toLocaleDateString()}`,
        content: sttResult.transcript,
        entry_type: 'video' as const,
        is_private: true,
        video_analysis: {
          facial_emotions: emotionSnapshots,
          facial_summary: facialSummary,
          text_emotion: {
            emotion: textEmotion.emotion,
            confidence: textEmotion.confidence,
            all_emotions: textEmotion.all_emotions
          },
          stt_confidence: sttResult.confidence,
          language: sttResult.language,
          video_duration: recordingDuration,
          has_face_detected: emotionSnapshots.length > 0
        }
      }
      console.log('Creating journal entry with data:', journalData)
      
      await apiService.createVideoJournalEntry(journalData)

      toast.dismiss()
      toast.success('Video journal entry saved successfully!')
      
      if (onSuccess) {
        onSuccess()
      }

      // Reset state only after successful save
      setEmotionSnapshots([])
      setCurrentEmotion(null)
      setRecordingDuration(0)
      chunksRef.current = [] // Clear video chunks
      
    } catch (err: any) {
      console.error('Error processing video:', err)
      toast.dismiss()
      const errorMessage = err?.message || 'Failed to save video journal entry'
      toast.error(`Failed to save video journal entry: ${errorMessage}`)
      
      // Don't reset state on error - let user see what was recorded
      // setEmotionSnapshots([])
      // setCurrentEmotion(null)
      // setRecordingDuration(0)
    } finally {
      setIsProcessing(false)
    }
  }

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Video className="text-primary" size={24} />
          Video Journal Entry
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Error Message */}
        {error && (
          <div className="p-3 bg-destructive/10 border border-destructive/20 rounded-lg flex items-center gap-2 text-sm text-destructive">
            <Warning size={16} />
            {error}
          </div>
        )}

        {/* Models Loading */}
        {!modelsLoaded && (
          <div className="text-center py-8">
            <CircleNotch className="animate-spin mx-auto mb-2 text-primary" size={32} />
            <p className="text-sm text-muted-foreground">Loading emotion detection models...</p>
          </div>
        )}

        {/* Video Preview */}
        {modelsLoaded && (
          <>
            <div className="relative aspect-video bg-black rounded-lg overflow-hidden">
              <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                className="w-full h-full object-cover"
              />
              <canvas
                ref={canvasRef}
                className="absolute top-0 left-0 w-full h-full pointer-events-none"
              />
              <FaceOverlay
                videoRef={videoRef}
                canvasRef={canvasRef}
                detection={currentDetection}
                currentEmotion={currentEmotion}
              />
              
              {/* Processing Overlay */}
              {isProcessing && (
                <div className="absolute inset-0 bg-black/70 flex items-center justify-center z-10">
                  <div className="text-center">
                    <CircleNotch className="animate-spin mx-auto mb-3 text-white" size={48} />
                    <p className="text-white text-lg font-semibold">Processing Video...</p>
                    <p className="text-white/70 text-sm mt-1">Transcribing and analyzing emotions</p>
                  </div>
                </div>
              )}
            </div>

            {/* Live Emotion Display */}
            {currentEmotion && (
              <div className="flex items-center justify-center gap-3">
                <div 
                  className="px-4 py-2 rounded-lg text-lg font-semibold flex items-center gap-2"
                  style={{ backgroundColor: getEmotionColor(currentEmotion.dominant) + '20', color: getEmotionColor(currentEmotion.dominant) }}
                >
                  {getEmotionLabel(currentEmotion.dominant)}
                  <span className="text-sm opacity-80">
                    ({(currentEmotion.confidence * 100).toFixed(1)}%)
                  </span>
                </div>
              </div>
            )}

            {/* Timeline */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium">Emotion Timeline</span>
                {recordingDuration > 0 && (
                  <span className="text-xs text-muted-foreground">
                    {formatDuration(recordingDuration)}
                  </span>
                )}
              </div>
              <EmotionTimeline snapshots={emotionSnapshots} interactive />
            </div>

            {/* Recording Duration */}
            {isRecording && (
              <div className="text-center text-lg font-mono">
                {formatDuration(recordingDuration)}
              </div>
            )}

            {/* Controls */}
            <div className="flex gap-2 justify-center">
              {!isRecording && !isProcessing ? (
                <Button
                  onClick={startRecording}
                  disabled={!modelsLoaded}
                  className="gap-2"
                  size="lg"
                >
                  <Camera size={20} />
                  Start Recording
                </Button>
              ) : (
                <Button
                  onClick={handleStopRecording}
                  variant="destructive"
                  className="gap-2"
                  size="lg"
                  disabled={isProcessing}
                >
                  <Stop size={20} />
                  {isProcessing ? 'Processing...' : 'Stop Recording'}
                </Button>
              )}
            </div>
          </>
        )}
      </CardContent>
    </Card>
  )
}
