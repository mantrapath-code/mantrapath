import { useEffect, useState, useRef, useCallback } from 'react'

export interface PerformanceMetrics {
  renderTime: number
  memoryUsage: number
  batteryLevel?: number
  networkLatency: number
  realTimeUpdateLatency: number
  webSocketLatency: number
  uiResponseTime: number
  fps: number
  domNodes: number
  eventLoopDelay: number
}

export interface PerformanceThresholds {
  renderTime: number
  memoryUsage: number
  networkLatency: number
  realTimeUpdateLatency: number
  webSocketLatency: number
  uiResponseTime: number
  fps: number
}

export interface PerformanceAlert {
  type: 'warning' | 'error' | 'critical'
  metric: keyof PerformanceMetrics
  value: number
  threshold: number
  message: string
  timestamp: number
}

const DEFAULT_THRESHOLDS: PerformanceThresholds = {
  renderTime: 300, // 300ms
  memoryUsage: 150 * 1024 * 1024, // 150MB (increased from 100MB)
  networkLatency: 500, // 500ms
  realTimeUpdateLatency: 300, // 300ms
  webSocketLatency: 200, // 200ms
  uiResponseTime: 300, // 300ms
  fps: 25 // Lowered from 30 to 25 FPS minimum to reduce false alerts
}

export function usePerformanceMonitor(
  thresholds: Partial<PerformanceThresholds> = {},
  monitoringInterval: number = 10000 // Increased from 5000ms to 10000ms to reduce frequency
) {
  const [metrics, setMetrics] = useState<PerformanceMetrics>({
    renderTime: 0,
    memoryUsage: 0,
    batteryLevel: undefined,
    networkLatency: 0,
    realTimeUpdateLatency: 0,
    webSocketLatency: 0,
    uiResponseTime: 0,
    fps: 60,
    domNodes: 0,
    eventLoopDelay: 0
  })
  
  const [alerts, setAlerts] = useState<PerformanceAlert[]>([])
  const [isMonitoring, setIsMonitoring] = useState(false)
  
  const frameCountRef = useRef(0)
  const lastFrameTimeRef = useRef(performance.now())
  const intervalRef = useRef<NodeJS.Timeout | null>(null)
  const rafRef = useRef<number | null>(null)
  const networkFailureCountRef = useRef(0) // Track network failures
  
  const mergedThresholds = { ...DEFAULT_THRESHOLDS, ...thresholds }

  const measureRenderTime = useCallback(() => {
    const start = performance.now()
    return () => {
      const end = performance.now()
      const renderTime = end - start
      setMetrics(prev => ({ ...prev, renderTime }))
      return renderTime
    }
  }, [])

  const measureMemoryUsage = useCallback(() => {
    if ('memory' in performance) {
      const memory = (performance as any).memory
      return {
        used: memory.usedJSHeapSize,
        total: memory.totalJSHeapSize,
        limit: memory.jsHeapSizeLimit
      }
    }
    return null
  }, [])

  const measureNetworkLatency = useCallback(async () => {
    // Circuit breaker: if we've failed too many times, skip network measurement
    if (networkFailureCountRef.current > 5) {
      console.log('🚫 Network latency measurement disabled due to repeated failures')
      return 0
    }
    
    const start = performance.now()
    try {
      // Use the favicon.ico which should always exist, or try current origin
      const response = await fetch('/favicon.ico', { 
        method: 'HEAD',
        cache: 'no-cache'
      })
      const end = performance.now()
      
      // Reset failure count on success
      networkFailureCountRef.current = 0
      return end - start
    } catch (error) {
      // Increment failure count
      networkFailureCountRef.current++
      
      // Try a simpler approach on first few failures
      if (networkFailureCountRef.current <= 3) {
        try {
          const start2 = performance.now()
          await fetch(window.location.origin, { 
            method: 'HEAD',
            cache: 'no-cache'
          })
          const end2 = performance.now()
          
          // Reset failure count on success
          networkFailureCountRef.current = 0
          return end2 - start2
        } catch (error2) {
          console.log(`Network latency measurement failed (${networkFailureCountRef.current}/5)`)
          return 0
        }
      } else {
        console.log(`Network latency measurement disabled after ${networkFailureCountRef.current} failures`)
        return 0
      }
    }
  }, [])

  const measureFPS = useCallback(() => {
    frameCountRef.current++
    const currentTime = performance.now()
    
    // Measure FPS over a longer period (2 seconds instead of 1) for more stable readings
    if (currentTime - lastFrameTimeRef.current >= 2000) {
      const fps = Math.round((frameCountRef.current * 1000) / (currentTime - lastFrameTimeRef.current))
      
      // Only update if FPS is significantly different to avoid micro-fluctuations
      setMetrics(prev => {
        const fpsDiff = Math.abs(prev.fps - fps)
        if (fpsDiff > 5) { // Only update if difference is more than 5 FPS
          return { ...prev, fps }
        }
        return prev
      })
      
      frameCountRef.current = 0
      lastFrameTimeRef.current = currentTime
    }
    
    rafRef.current = requestAnimationFrame(measureFPS)
  }, [])

  const measureEventLoopDelay = useCallback(() => {
    const start = performance.now()
    setTimeout(() => {
      const end = performance.now()
      const delay = end - start - 16.67 // 16.67ms is the target frame time (60fps)
      setMetrics(prev => ({ ...prev, eventLoopDelay: Math.max(0, delay) }))
    }, 0)
  }, [])

  const measureDOMNodes = useCallback(() => {
    const nodeCount = document.querySelectorAll('*').length
    setMetrics(prev => ({ ...prev, domNodes: nodeCount }))
  }, [])

  const checkThresholds = useCallback((currentMetrics: PerformanceMetrics): PerformanceAlert[] => {
    const newAlerts: PerformanceAlert[] = []
    
    Object.entries(mergedThresholds).forEach(([metric, threshold]) => {
      const value = currentMetrics[metric as keyof PerformanceMetrics] as number
      
      // FPS is different - LOW values are bad, HIGH values are good
      const isThresholdExceeded = metric === 'fps' 
        ? value < threshold  // For FPS, alert when below threshold
        : value > threshold  // For other metrics, alert when above threshold
      
      if (typeof value === 'number' && isThresholdExceeded) {
        let type: PerformanceAlert['type'] = 'warning'
        
        if (metric === 'fps') {
          // For FPS: lower = worse
          if (value < threshold * 0.5) type = 'critical'
          else if (value < threshold * 0.75) type = 'error'
        } else {
          // For other metrics: higher = worse
          if (value > threshold * 2) type = 'critical'
          else if (value > threshold * 1.5) type = 'error'
        }
        
        // Create user-friendly alert messages
        let message = ''
        switch (metric) {
          case 'memoryUsage':
            const memoryMB = Math.round(value / (1024 * 1024))
            const thresholdMB = Math.round(threshold / (1024 * 1024))
            message = `Memory usage is ${memoryMB}MB (limit: ${thresholdMB}MB). Auto-optimization will trigger to free up memory.`
            break
          case 'renderTime':
            message = `Page rendering is taking ${value.toFixed(0)}ms (target: <${threshold}ms). Consider reducing active components.`
            break
          case 'networkLatency':
            message = `Network connection is slow (${value.toFixed(0)}ms response time). Check your internet connection.`
            break
          case 'fps':
            message = `Frame rate dropped to ${value} FPS (target: >${threshold} FPS). Performance may feel sluggish.`
            break
          default:
            const comparison = metric === 'fps' ? `${value} < ${threshold}` : `${value} > ${threshold}`
            message = `${metric} performance issue: ${comparison}`
        }
        
        newAlerts.push({
          type,
          metric: metric as keyof PerformanceMetrics,
          value,
          threshold,
          message,
          timestamp: Date.now()
        })
      }
    })
    
    return newAlerts
  }, [mergedThresholds])

  const startMonitoring = useCallback(() => {
    if (isMonitoring) return
    
    setIsMonitoring(true)
    
    // Start FPS monitoring
    rafRef.current = requestAnimationFrame(measureFPS)
    
    // Start periodic monitoring
    intervalRef.current = setInterval(async () => {
      // Measure memory usage
      const memory = measureMemoryUsage()
      if (memory) {
        setMetrics(prev => ({ 
          ...prev, 
          memoryUsage: memory.used 
        }))
      }
      
      // Measure network latency
      const networkLatency = await measureNetworkLatency()
      setMetrics(prev => ({ ...prev, networkLatency }))
      
      // Measure DOM nodes
      measureDOMNodes()
      
      // Measure event loop delay
      measureEventLoopDelay()
      
      // Check thresholds and generate alerts - use prev state to avoid stale closure
      setMetrics(prev => {
        const currentMetrics = { ...prev, memoryUsage: memory?.used || 0, networkLatency }
        const newAlerts = checkThresholds(currentMetrics)
        if (newAlerts.length > 0) {
          setAlerts(alertsPrev => {
            const allAlerts = [...alertsPrev, ...newAlerts]
            
            // Auto-optimize if too many alerts (more than 15)
            if (allAlerts.length > 15) {
              console.log('🚨 Too many performance alerts, triggering auto-optimization...')
              setTimeout(optimizeMemory, 500)
              return allAlerts.slice(-10) // Keep only recent alerts
            }
            
            return allAlerts
          })
          
          // Auto-optimize memory if memory threshold exceeded
          const memoryAlert = newAlerts.find(alert => alert.metric === 'memoryUsage')
          if (memoryAlert) {
            console.log('💾 Memory threshold exceeded, triggering optimization...')
            setTimeout(optimizeMemory, 1000) // Delay to avoid blocking UI
          }
        }
        return currentMetrics
      })
    }, monitoringInterval)
  }, [isMonitoring, measureFPS, measureMemoryUsage, measureNetworkLatency, measureDOMNodes, measureEventLoopDelay, checkThresholds, monitoringInterval])

  const stopMonitoring = useCallback(() => {
    setIsMonitoring(false)
    
    if (rafRef.current) {
      cancelAnimationFrame(rafRef.current)
      rafRef.current = null
    }
    
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
      intervalRef.current = null
    }
  }, [])

  const recordMetric = useCallback((metric: keyof PerformanceMetrics, value: number) => {
    setMetrics(prev => ({ ...prev, [metric]: value }))
  }, [])

  const clearAlerts = useCallback(() => {
    setAlerts([])
  }, [])

  // Memory optimization function
  const optimizeMemory = useCallback(() => {
    console.log('🧹 Starting memory optimization...')
    
    // Clear old alerts more aggressively (keep only last 3)
    setAlerts(prev => {
      const recentAlerts = prev.slice(-3)
      console.log(`Cleared ${prev.length - recentAlerts.length} old performance alerts`)
      return recentAlerts
    })
    
    // Reset metrics to baseline values
    setMetrics(prev => ({
      ...prev,
      eventLoopDelay: 0,
      domNodes: Math.min(prev.domNodes, 500), // Cap DOM nodes reporting more aggressively
      renderTime: Math.min(prev.renderTime, 100), // Reset render time if too high
    }))
    
    // Clear performance timeline data
    frameCountRef.current = 0
    lastFrameTimeRef.current = performance.now()
    
    // Force garbage collection if available (Chrome DevTools)
    if (typeof window !== 'undefined' && window.gc) {
      try {
        window.gc()
        console.log('✅ Manual garbage collection triggered')
      } catch (e) {
        console.log('⚠️ Manual GC not available')
      }
    }
    
    // Clear browser performance measurements and marks
    if ('performance' in window) {
      try {
        if ('clearMarks' in performance) performance.clearMarks()
        if ('clearMeasures' in performance) performance.clearMeasures()
        if ('clearResourceTimings' in performance) performance.clearResourceTimings()
        console.log('✅ Performance timeline cleared')
      } catch (e) {
        console.log('⚠️ Could not clear performance timeline:', e)
      }
    }
    
    // Clear any cached images or large objects
    if ('caches' in window) {
      caches.keys().then(cacheNames => {
        if (cacheNames.length > 0) {
          console.log(`Found ${cacheNames.length} cache(s), consider clearing if memory issues persist`)
        }
      }).catch(() => {})
    }
    
    console.log('🎯 Memory optimization completed')
  }, [])

  const getPerformanceScore = useCallback((currentMetrics?: PerformanceMetrics): number => {
    const metricsToUse = currentMetrics || metrics
    let score = 100
    
    // Deduct points for each metric that exceeds thresholds
    Object.entries(mergedThresholds).forEach(([metric, threshold]) => {
      const value = metricsToUse[metric as keyof PerformanceMetrics] as number
      if (typeof value === 'number') {
        let shouldDeduct = false
        let ratio = 1
        
        if (metric === 'fps') {
          // For FPS, low values are bad
          if (value < threshold) {
            shouldDeduct = true
            ratio = threshold / value // Inverted ratio for FPS
          }
        } else {
          // For other metrics, high values are bad
          if (value > threshold) {
            shouldDeduct = true
            ratio = value / threshold
          }
        }
        
        if (shouldDeduct) {
          if (ratio > 2) score -= 30
          else if (ratio > 1.5) score -= 20
          else score -= 10
        }
      }
    })
    
    return Math.max(0, score)
  }, [mergedThresholds])

  useEffect(() => {
    // Auto-start monitoring only once when component mounts
    let mounted = true
    
    const initializeMonitoring = () => {
      if (mounted && !isMonitoring) {
        setIsMonitoring(true)
        
        // Start FPS monitoring
        rafRef.current = requestAnimationFrame(measureFPS)
        
        // Start periodic monitoring
        intervalRef.current = setInterval(async () => {
          // Measure memory usage
          const memory = measureMemoryUsage()
          if (memory) {
            setMetrics(prev => ({ 
              ...prev, 
              memoryUsage: memory.used 
            }))
          }
          
          // Measure network latency
          const networkLatency = await measureNetworkLatency()
          setMetrics(prev => ({ ...prev, networkLatency }))
          
          // Measure DOM nodes
          measureDOMNodes()
          
          // Measure event loop delay
          measureEventLoopDelay()
          
          // Check thresholds and generate alerts - use prev state to avoid stale closure
          setMetrics(prev => {
            const currentMetrics = { ...prev, memoryUsage: memory?.used || 0, networkLatency }
            const newAlerts = checkThresholds(currentMetrics)
            if (newAlerts.length > 0) {
              setAlerts(alertsPrev => [...alertsPrev, ...newAlerts])
            }
            return currentMetrics
          })
        }, monitoringInterval)
      }
    }
    
    initializeMonitoring()
    
    return () => {
      mounted = false
      if (rafRef.current) {
        cancelAnimationFrame(rafRef.current)
        rafRef.current = null
      }
      
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
        intervalRef.current = null
      }
      
      setIsMonitoring(false)
    }
  }, []) // Empty dependency array to run only once

  return {
    metrics,
    alerts,
    isMonitoring,
    startMonitoring,
    stopMonitoring,
    recordMetric,
    clearAlerts,
    optimizeMemory,
    getPerformanceScore,
    measureRenderTime
  }
}

// Utility hook for measuring component render performance
export function useRenderPerformance(componentName: string) {
  const { measureRenderTime, recordMetric } = usePerformanceMonitor()
  
  useEffect(() => {
    const endMeasure = measureRenderTime()
    return () => {
      const renderTime = endMeasure()
      recordMetric('renderTime', renderTime)
    }
  }, [componentName, measureRenderTime, recordMetric])
}

// Utility hook for measuring real-time update performance
export function useRealTimePerformance() {
  const { recordMetric } = usePerformanceMonitor()
  
  const measureUpdateTime = useCallback((startTime: number) => {
    const endTime = performance.now()
    const updateTime = endTime - startTime
    recordMetric('realTimeUpdateLatency', updateTime)
    return updateTime
  }, [recordMetric])
  
  const startUpdateMeasurement = useCallback(() => {
    return performance.now()
  }, [])
  
  return {
    startUpdateMeasurement,
    measureUpdateTime
  }
}
