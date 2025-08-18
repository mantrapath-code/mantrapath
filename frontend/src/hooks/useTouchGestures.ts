import { useEffect, useRef, useCallback, useState } from 'react'

export interface TouchPoint {
  x: number
  y: number
  id: number
  timestamp: number
}

export interface Gesture {
  type: 'swipe' | 'pinch' | 'rotate' | 'tap' | 'doubleTap' | 'longPress' | 'pan'
  direction?: 'left' | 'right' | 'up' | 'down'
  distance?: number
  scale?: number
  angle?: number
  duration: number
  center: { x: number; y: number }
  startTime: number
  endTime: number
}

export interface GestureRecognizer {
  type: string
  threshold: number
  recognize: (events: TouchEvent[]) => Gesture | null
  onGesture: (gesture: Gesture) => void
}

export interface GestureHandlers {
  onSwipeLeft?: (gesture: Gesture) => void
  onSwipeRight?: (gesture: Gesture) => void
  onSwipeUp?: (gesture: Gesture) => void
  onSwipeDown?: (gesture: Gesture) => void
  onPinch?: (gesture: Gesture) => void
  onRotate?: (gesture: Gesture) => void
  onTap?: (gesture: Gesture) => void
  onDoubleTap?: (gesture: Gesture) => void
  onLongPress?: (gesture: Gesture) => void
  onPan?: (gesture: Gesture) => void
}

export interface TouchGestureOptions {
  swipeThreshold?: number
  pinchThreshold?: number
  rotateThreshold?: number
  longPressDelay?: number
  doubleTapDelay?: number
  enableHaptic?: boolean
  preventDefault?: boolean
}

const DEFAULT_OPTIONS: TouchGestureOptions = {
  swipeThreshold: 50,
  pinchThreshold: 0.1,
  rotateThreshold: 15,
  longPressDelay: 500,
  doubleTapDelay: 300,
  enableHaptic: true,
  preventDefault: true
}

export function useTouchGestures(
  elementRef: React.RefObject<HTMLElement>,
  handlers: GestureHandlers,
  options: TouchGestureOptions = {}
) {
  const [isTracking, setIsTracking] = useState(false)
  const [activeTouches, setActiveTouches] = useState<TouchPoint[]>([])
  
  const mergedOptions = { ...DEFAULT_OPTIONS, ...options }
  const touchStartTimeRef = useRef<number>(0)
  const lastTapTimeRef = useRef<number>(0)
  const longPressTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const gestureStartRef = useRef<{ touches: TouchPoint[]; center: { x: number; y: number } } | null>(null)

  // Haptic feedback
  const triggerHaptic = useCallback(() => {
    if (mergedOptions.enableHaptic && 'vibrate' in navigator) {
      try {
        (navigator as any).vibrate(50)
      } catch (error) {
        console.log('Haptic feedback not available')
      }
    }
  }, [mergedOptions.enableHaptic])

  // Touch event handlers
  const handleTouchStart = useCallback((event: TouchEvent) => {
    if (mergedOptions.preventDefault) {
      event.preventDefault()
    }
    
    setIsTracking(true)
    touchStartTimeRef.current = Date.now()
    
    const touches: TouchPoint[] = Array.from(event.touches).map(touch => ({
      x: touch.clientX,
      y: touch.clientY,
      id: touch.identifier,
      timestamp: Date.now()
    }))
    
    setActiveTouches(touches)
    
    // Calculate center point
    const center = calculateCenter(touches)
    gestureStartRef.current = { touches, center }
    
    // Start long press timer
    if (touches.length === 1) {
      longPressTimeoutRef.current = setTimeout(() => {
        if (handlers.onLongPress && gestureStartRef.current) {
          const gesture: Gesture = {
            type: 'longPress',
            duration: Date.now() - touchStartTimeRef.current,
            center,
            startTime: touchStartTimeRef.current,
            endTime: Date.now()
          }
          handlers.onLongPress(gesture)
          triggerHaptic()
        }
      }, mergedOptions.longPressDelay)
    }
  }, [handlers, mergedOptions, triggerHaptic])

  const handleTouchMove = useCallback((event: TouchEvent) => {
    if (mergedOptions.preventDefault) {
      event.preventDefault()
    }
    
    const currentTouches: TouchPoint[] = Array.from(event.touches).map(touch => ({
      x: touch.clientX,
      y: touch.clientY,
      id: touch.identifier,
      timestamp: Date.now()
    }))
    
    setActiveTouches(currentTouches)
    
    // Handle pan gesture
    if (handlers.onPan && gestureStartRef.current && currentTouches.length === 1) {
      const startTouch = gestureStartRef.current.touches[0]
      const currentTouch = currentTouches[0]
      
      if (startTouch && currentTouch) {
        const distance = calculateDistance(startTouch, currentTouch)
        if (distance > mergedOptions.swipeThreshold) {
          const gesture: Gesture = {
            type: 'pan',
            distance,
            duration: Date.now() - touchStartTimeRef.current,
            center: calculateCenter(currentTouches),
            startTime: touchStartTimeRef.current,
            endTime: Date.now()
          }
          handlers.onPan(gesture)
        }
      }
    }
  }, [handlers, mergedOptions])

  const handleTouchEnd = useCallback((event: TouchEvent) => {
    if (mergedOptions.preventDefault) {
      event.preventDefault()
    }
    
    setIsTracking(false)
    
    // Clear long press timeout
    if (longPressTimeoutRef.current) {
      clearTimeout(longPressTimeoutRef.current)
      longPressTimeoutRef.current = null
    }
    
    if (!gestureStartRef.current) return
    
    const endTime = Date.now()
    const duration = endTime - touchStartTimeRef.current
    const startTouches = gestureStartRef.current.touches
    const endTouches = Array.from(event.changedTouches).map(touch => ({
      x: touch.clientX,
      y: touch.clientY,
      id: touch.identifier,
      timestamp: endTime
    }))
    
    // Handle single touch gestures
    if (startTouches.length === 1 && endTouches.length === 1) {
      const startTouch = startTouches[0]
      const endTouch = endTouches[0]
      
      if (startTouch && endTouch) {
        const distance = calculateDistance(startTouch, endTouch)
        const direction = calculateDirection(startTouch, endTouch)
        
        // Swipe gesture
        if (distance > mergedOptions.swipeThreshold && duration < 500) {
          const gesture: Gesture = {
            type: 'swipe',
            direction,
            distance,
            duration,
            center: calculateCenter([startTouch, endTouch]),
            startTime: touchStartTimeRef.current,
            endTime
          }
          
          switch (direction) {
            case 'left':
              handlers.onSwipeLeft?.(gesture)
              break
            case 'right':
              handlers.onSwipeRight?.(gesture)
              break
            case 'up':
              handlers.onSwipeUp?.(gesture)
              break
            case 'down':
              handlers.onSwipeDown?.(gesture)
              break
          }
          
          triggerHaptic()
        }
        
        // Tap gesture
        if (distance < mergedOptions.swipeThreshold && duration < 200) {
          const now = Date.now()
          const timeSinceLastTap = now - lastTapTimeRef.current
          
          if (timeSinceLastTap < mergedOptions.doubleTapDelay) {
            // Double tap
            if (handlers.onDoubleTap) {
              const gesture: Gesture = {
                type: 'doubleTap',
                duration: timeSinceLastTap,
                center: calculateCenter([startTouch]),
                startTime: lastTapTimeRef.current,
                endTime: now
              }
              handlers.onDoubleTap(gesture)
              triggerHaptic()
            }
          } else {
            // Single tap
            if (handlers.onTap) {
              const gesture: Gesture = {
                type: 'tap',
                duration,
                center: calculateCenter([startTouch]),
                startTime: touchStartTimeRef.current,
                endTime
              }
              handlers.onTap(gesture)
            }
          }
          
          lastTapTimeRef.current = now
        }
      }
    }
    
    // Handle multi-touch gestures
    if (startTouches.length === 2 && endTouches.length === 2) {
      const startCenter = calculateCenter(startTouches)
      const endCenter = calculateCenter(endTouches)
      
      // Pinch gesture
      const startDistance = calculateDistance(startTouches[0], startTouches[1])
      const endDistance = calculateDistance(endTouches[0], endTouches[1])
      const scale = endDistance / startDistance
      
      if (Math.abs(scale - 1) > mergedOptions.pinchThreshold && handlers.onPinch) {
        const gesture: Gesture = {
          type: 'pinch',
          scale,
          distance: Math.abs(endDistance - startDistance),
          duration,
          center: endCenter,
          startTime: touchStartTimeRef.current,
          endTime
        }
        handlers.onPinch(gesture)
        triggerHaptic()
      }
      
      // Rotate gesture
      const startAngle = calculateAngle(startTouches[0], startTouches[1])
      const endAngle = calculateAngle(endTouches[0], endTouches[1])
      const rotation = endAngle - startAngle
      
      if (Math.abs(rotation) > mergedOptions.rotateThreshold && handlers.onRotate) {
        const gesture: Gesture = {
          type: 'rotate',
          angle: rotation,
          duration,
          center: endCenter,
          startTime: touchStartTimeRef.current,
          endTime
        }
        handlers.onRotate(gesture)
        triggerHaptic()
      }
    }
    
    // Reset gesture state
    gestureStartRef.current = null
    setActiveTouches([])
  }, [handlers, mergedOptions, triggerHaptic])

  // Utility functions
  const calculateCenter = useCallback((touches: TouchPoint[]) => {
    const sumX = touches.reduce((sum, touch) => sum + touch.x, 0)
    const sumY = touches.reduce((sum, touch) => sum + touch.y, 0)
    return {
      x: sumX / touches.length,
      y: sumY / touches.length
    }
  }, [])

  const calculateDistance = useCallback((touch1: TouchPoint, touch2: TouchPoint) => {
    const dx = touch2.x - touch1.x
    const dy = touch2.y - touch1.y
    return Math.sqrt(dx * dx + dy * dy)
  }, [])

  const calculateDirection = useCallback((start: TouchPoint, end: TouchPoint) => {
    const dx = end.x - start.x
    const dy = end.y - start.y
    
    if (Math.abs(dx) > Math.abs(dy)) {
      return dx > 0 ? 'right' : 'left'
    } else {
      return dy > 0 ? 'down' : 'up'
    }
  }, [])

  const calculateAngle = useCallback((touch1: TouchPoint, touch2: TouchPoint) => {
    const dx = touch2.x - touch1.x
    const dy = touch2.y - touch1.y
    return Math.atan2(dy, dx) * (180 / Math.PI)
  }, [])

  // Set up event listeners
  useEffect(() => {
    const element = elementRef.current
    if (!element) return
    
    element.addEventListener('touchstart', handleTouchStart, { passive: !mergedOptions.preventDefault })
    element.addEventListener('touchmove', handleTouchMove, { passive: !mergedOptions.preventDefault })
    element.addEventListener('touchend', handleTouchEnd, { passive: !mergedOptions.preventDefault })
    element.addEventListener('touchcancel', handleTouchEnd, { passive: !mergedOptions.preventDefault })
    
    return () => {
      element.removeEventListener('touchstart', handleTouchStart)
      element.removeEventListener('touchmove', handleTouchMove)
      element.removeEventListener('touchend', handleTouchEnd)
      element.removeEventListener('touchcancel', handleTouchEnd)
      
      // Cleanup timeouts
      if (longPressTimeoutRef.current) {
        clearTimeout(longPressTimeoutRef.current)
      }
    }
  }, [elementRef, handleTouchStart, handleTouchMove, handleTouchEnd, mergedOptions.preventDefault])

  return {
    isTracking,
    activeTouches,
    triggerHaptic
  }
}

// Hook for common gesture patterns
export function useSwipeNavigation(
  elementRef: React.RefObject<HTMLElement>,
  onNavigate: (direction: 'left' | 'right' | 'up' | 'down') => void
) {
  const handlers: GestureHandlers = {
    onSwipeLeft: () => onNavigate('left'),
    onSwipeRight: () => onNavigate('right'),
    onSwipeUp: () => onNavigate('up'),
    onSwipeDown: () => onNavigate('down')
  }
  
  return useTouchGestures(elementRef, handlers, {
    swipeThreshold: 80,
    enableHaptic: true
  })
}

// Hook for pinch zoom
export function usePinchZoom(
  elementRef: React.RefObject<HTMLElement>,
  onZoom: (scale: number) => void
) {
  const handlers: GestureHandlers = {
    onPinch: (gesture) => onZoom(gesture.scale || 1)
  }
  
  return useTouchGestures(elementRef, handlers, {
    pinchThreshold: 0.05,
    enableHaptic: false
  })
}

// Hook for rotation
export function useRotation(
  elementRef: React.RefObject<HTMLElement>,
  onRotate: (angle: number) => void
) {
  const handlers: GestureHandlers = {
    onRotate: (gesture) => onRotate(gesture.angle || 0)
  }
  
  return useTouchGestures(elementRef, handlers, {
    rotateThreshold: 10,
    enableHaptic: false
  })
}
