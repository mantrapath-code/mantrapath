import { useEffect, useState, useCallback } from 'react'

export interface DeviceCapabilities {
  isMobile: boolean
  isTablet: boolean
  isDesktop: boolean
  hasTouch: boolean
  hasHaptic: boolean
  orientation: 'portrait' | 'landscape'
  screenSize: 'small' | 'medium' | 'large' | 'xlarge'
  performance: 'low' | 'medium' | 'high'
  batteryLevel?: number
  networkType?: 'wifi' | '4g' | '3g' | '2g'
  pixelRatio: number
  colorScheme: 'light' | 'dark'
  reducedMotion: boolean
}

export interface Breakpoint {
  name: string
  minWidth: number
  maxWidth?: number
  deviceType: 'mobile' | 'tablet' | 'desktop'
}

const BREAKPOINTS: Breakpoint[] = [
  { name: 'mobile', minWidth: 0, maxWidth: 767, deviceType: 'mobile' },
  { name: 'tablet', minWidth: 768, maxWidth: 1023, deviceType: 'tablet' },
  { name: 'desktop', minWidth: 1024, maxWidth: 1439, deviceType: 'desktop' },
  { name: 'xlarge', minWidth: 1440, maxWidth: undefined, deviceType: 'desktop' }
]

export function useDeviceCapabilities(): DeviceCapabilities {
  const [capabilities, setCapabilities] = useState<DeviceCapabilities>({
    isMobile: false,
    isTablet: false,
    isDesktop: false,
    hasTouch: false,
    hasHaptic: false,
    orientation: 'portrait',
    screenSize: 'medium',
    performance: 'medium',
    pixelRatio: 1,
    colorScheme: 'light',
    reducedMotion: false
  })

  const detectCapabilities = useCallback(async () => {
    const width = window.innerWidth
    const height = window.innerHeight
    
    // Determine device type based on breakpoints
    const currentBreakpoint = BREAKPOINTS.find(bp => 
      width >= bp.minWidth && (!bp.maxWidth || width <= bp.maxWidth)
    ) || BREAKPOINTS[0]

    // Touch detection
    const hasTouch = 'ontouchstart' in window || navigator.maxTouchPoints > 0
    
    // Haptic feedback detection
    const hasHaptic = 'vibrate' in navigator || 'getGamepads' in navigator
    
    // Orientation detection
    const orientation = width > height ? 'landscape' : 'portrait'
    
    // Screen size classification
    let screenSize: DeviceCapabilities['screenSize'] = 'medium'
    if (width < 480) screenSize = 'small'
    else if (width < 768) screenSize = 'small'
    else if (width < 1024) screenSize = 'medium'
    else if (width < 1440) screenSize = 'large'
    else screenSize = 'xlarge'
    
    // Performance estimation based on device capabilities
    let performance: DeviceCapabilities['performance'] = 'medium'
    const memory = (navigator as any).deviceMemory
    const cores = (navigator as any).hardwareConcurrency
    
    if (memory && cores) {
      if (memory >= 8 && cores >= 8) performance = 'high'
      else if (memory >= 4 && cores >= 4) performance = 'medium'
      else performance = 'low'
    }
    
    // Pixel ratio
    const pixelRatio = window.devicePixelRatio || 1
    
    // Color scheme detection
    const colorScheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
    
    // Reduced motion detection
    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    
    // Battery level detection (if available)
    let batteryLevel: number | undefined
    if ('getBattery' in navigator) {
      try {
        const battery = await (navigator as any).getBattery()
        batteryLevel = battery.level * 100
      } catch (error) {
        console.log('Battery API not available')
      }
    }
    
    // Network type detection (if available)
    let networkType: DeviceCapabilities['networkType'] | undefined
    if ('connection' in navigator) {
      const connection = (navigator as any).connection
      if (connection) {
        networkType = connection.effectiveType || connection.type
      }
    }

    setCapabilities({
      isMobile: currentBreakpoint.deviceType === 'mobile',
      isTablet: currentBreakpoint.deviceType === 'tablet',
      isDesktop: currentBreakpoint.deviceType === 'desktop',
      hasTouch,
      hasHaptic,
      orientation,
      screenSize,
      performance,
      batteryLevel,
      networkType,
      pixelRatio,
      colorScheme,
      reducedMotion
    })
  }, [])

  useEffect(() => {
    // Initial detection
    detectCapabilities()
    
    // Set up event listeners
    const handleResize = () => detectCapabilities()
    const handleOrientationChange = () => detectCapabilities()
    const handleColorSchemeChange = (e: MediaQueryListEvent) => {
      setCapabilities(prev => ({
        ...prev,
        colorScheme: e.matches ? 'dark' : 'light'
      }))
    }
    const handleReducedMotionChange = (e: MediaQueryListEvent) => {
      setCapabilities(prev => ({
        ...prev,
        reducedMotion: e.matches
      }))
    }
    
    // Add event listeners
    window.addEventListener('resize', handleResize)
    window.addEventListener('orientationchange', handleOrientationChange)
    
    // Media query listeners
    const colorSchemeQuery = window.matchMedia('(prefers-color-scheme: dark)')
    const reducedMotionQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
    
    colorSchemeQuery.addEventListener('change', handleColorSchemeChange)
    reducedMotionQuery.addEventListener('change', handleReducedMotionChange)
    
    // Cleanup
    return () => {
      window.removeEventListener('resize', handleResize)
      window.removeEventListener('orientationchange', handleOrientationChange)
      colorSchemeQuery.removeEventListener('change', handleColorSchemeChange)
      reducedMotionQuery.removeEventListener('change', handleReducedMotionChange)
    }
  }, [detectCapabilities])

  return capabilities
}

// Utility functions for responsive design
export function useResponsiveBreakpoint() {
  const capabilities = useDeviceCapabilities()
  
  if (capabilities.isMobile) return 'mobile'
  if (capabilities.isTablet) return 'tablet'
  if (capabilities.isDesktop) return 'desktop'
  return 'desktop'
}

export function useIsTouchDevice() {
  const capabilities = useDeviceCapabilities()
  return capabilities.hasTouch
}

export function useOrientation() {
  const capabilities = useDeviceCapabilities()
  return capabilities.orientation
}

export function usePerformanceMode() {
  const capabilities = useDeviceCapabilities()
  return capabilities.performance
}
