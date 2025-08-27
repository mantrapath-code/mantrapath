import { useState, useEffect, useCallback } from 'react'
import { useDeviceCapabilities } from './useDeviceCapabilities'

export interface Layout {
  name: string
  breakpoint: string
  deviceType: 'mobile' | 'tablet' | 'desktop'
  grid: GridSystem
  navigation: NavigationPattern
  interactions: InteractionPattern
  spacing: SpacingSystem
  typography: TypographySystem
}

export interface GridSystem {
  columns: number
  gap: string
  padding: string
  maxWidth: string
  containerPadding: string
}

export interface NavigationPattern {
  type: 'tabs' | 'sidebar' | 'bottom-nav' | 'floating' | 'breadcrumb'
  position: 'top' | 'bottom' | 'left' | 'right' | 'floating'
  sticky: boolean
  collapsible: boolean
  showLabels: boolean
}

export interface InteractionPattern {
  touchFriendly: boolean
  gestureSupport: boolean
  hoverEffects: boolean
  keyboardNavigation: boolean
  focusIndicators: boolean
}

export interface SpacingSystem {
  xs: string
  sm: string
  md: string
  lg: string
  xl: string
  xxl: string
}

export interface TypographySystem {
  baseSize: string
  lineHeight: string
  headingSizes: {
    h1: string
    h2: string
    h3: string
    h4: string
    h5: string
    h6: string
  }
  bodySize: string
}

export interface ResponsiveLayoutManager {
  currentLayout: Layout
  layouts: Map<string, Layout>
  updateLayout: (device: any) => void
  getOptimalLayout: (device: any) => Layout
  adaptComponent: (component: string, device: any) => any
  getSpacing: (size: keyof SpacingSystem) => string
  getTypography: (element: keyof TypographySystem | keyof TypographySystem['headingSizes']) => string
}

// Predefined layouts for different device types
const LAYOUTS: Layout[] = [
  // Mobile Layout
  {
    name: 'Mobile',
    breakpoint: 'mobile',
    deviceType: 'mobile',
    grid: {
      columns: 1,
      gap: '1rem',
      padding: '1rem',
      maxWidth: '100%',
      containerPadding: '1rem'
    },
    navigation: {
      type: 'bottom-nav',
      position: 'bottom',
      sticky: true,
      collapsible: false,
      showLabels: true
    },
    interactions: {
      touchFriendly: true,
      gestureSupport: true,
      hoverEffects: false,
      keyboardNavigation: false,
      focusIndicators: true
    },
    spacing: {
      xs: '0.25rem',
      sm: '0.5rem',
      md: '1rem',
      lg: '1.5rem',
      xl: '2rem',
      xxl: '3rem'
    },
    typography: {
      baseSize: '14px',
      lineHeight: '1.5',
      headingSizes: {
        h1: '1.75rem',
        h2: '1.5rem',
        h3: '1.25rem',
        h4: '1.125rem',
        h5: '1rem',
        h6: '0.875rem'
      },
      bodySize: '14px'
    }
  },
  
  // Tablet Layout
  {
    name: 'Tablet',
    breakpoint: 'tablet',
    deviceType: 'tablet',
    grid: {
      columns: 2,
      gap: '1.5rem',
      padding: '1.5rem',
      maxWidth: '100%',
      containerPadding: '2rem'
    },
    navigation: {
      type: 'sidebar',
      position: 'left',
      sticky: true,
      collapsible: true,
      showLabels: true
    },
    interactions: {
      touchFriendly: true,
      gestureSupport: true,
      hoverEffects: true,
      keyboardNavigation: true,
      focusIndicators: true
    },
    spacing: {
      xs: '0.375rem',
      sm: '0.75rem',
      md: '1.5rem',
      lg: '2rem',
      xl: '2.5rem',
      xxl: '3.5rem'
    },
    typography: {
      baseSize: '16px',
      lineHeight: '1.6',
      headingSizes: {
        h1: '2rem',
        h2: '1.75rem',
        h3: '1.5rem',
        h4: '1.25rem',
        h5: '1.125rem',
        h6: '1rem'
      },
      bodySize: '16px'
    }
  },
  
  // Desktop Layout
  {
    name: 'Desktop',
    breakpoint: 'desktop',
    deviceType: 'desktop',
    grid: {
      columns: 3,
      gap: '2rem',
      padding: '2rem',
      maxWidth: '1200px',
      containerPadding: '2rem'
    },
    navigation: {
      type: 'tabs',
      position: 'top',
      sticky: true,
      collapsible: false,
      showLabels: true
    },
    interactions: {
      touchFriendly: false,
      gestureSupport: false,
      hoverEffects: true,
      keyboardNavigation: true,
      focusIndicators: true
    },
    spacing: {
      xs: '0.5rem',
      sm: '1rem',
      md: '2rem',
      lg: '3rem',
      xl: '4rem',
      xxl: '5rem'
    },
    typography: {
      baseSize: '18px',
      lineHeight: '1.7',
      headingSizes: {
        h1: '2.5rem',
        h2: '2rem',
        h3: '1.75rem',
        h4: '1.5rem',
        h5: '1.25rem',
        h6: '1.125rem'
      },
      bodySize: '18px'
    }
  },
  
  // Large Desktop Layout
  {
    name: 'Large Desktop',
    breakpoint: 'xlarge',
    deviceType: 'desktop',
    grid: {
      columns: 4,
      gap: '2.5rem',
      padding: '2.5rem',
      maxWidth: '1600px',
      containerPadding: '3rem'
    },
    navigation: {
      type: 'tabs',
      position: 'top',
      sticky: true,
      collapsible: false,
      showLabels: true
    },
    interactions: {
      touchFriendly: false,
      gestureSupport: false,
      hoverEffects: true,
      keyboardNavigation: true,
      focusIndicators: true
    },
    spacing: {
      xs: '0.75rem',
      sm: '1.5rem',
      md: '2.5rem',
      lg: '3.5rem',
      xl: '4.5rem',
      xxl: '6rem'
    },
    typography: {
      baseSize: '20px',
      lineHeight: '1.7',
      headingSizes: {
        h1: '3rem',
        h2: '2.5rem',
        h3: '2rem',
        h4: '1.75rem',
        h5: '1.5rem',
        h6: '1.25rem'
      },
      bodySize: '20px'
    }
  }
]

export function useResponsiveLayout() {
  const deviceCapabilities = useDeviceCapabilities()
  const [currentLayout, setCurrentLayout] = useState<Layout>(LAYOUTS[0])
  const [layouts] = useState<Map<string, Layout>>(new Map(
    LAYOUTS.map(layout => [layout.breakpoint, layout])
  ))

  const getOptimalLayout = useCallback((device: any): Layout => {
    if (device.isMobile) {
      return layouts.get('mobile') || LAYOUTS[0]
    } else if (device.isTablet) {
      return layouts.get('tablet') || LAYOUTS[1]
    } else if (device.screenSize === 'xlarge') {
      return layouts.get('xlarge') || LAYOUTS[3]
    } else {
      return layouts.get('desktop') || LAYOUTS[2]
    }
  }, [layouts])

  const updateLayout = useCallback((device: any) => {
    const optimalLayout = getOptimalLayout(device)
    setCurrentLayout(optimalLayout)
  }, [getOptimalLayout])

  const adaptComponent = useCallback((component: string, device: any) => {
    const layout = getOptimalLayout(device)
    
    // Component-specific adaptations
    switch (component) {
      case 'navigation':
        return {
          type: layout.navigation.type,
          position: layout.navigation.position,
          sticky: layout.navigation.sticky,
          collapsible: layout.navigation.collapsible,
          showLabels: layout.navigation.showLabels
        }
      
      case 'grid':
        return {
          columns: layout.grid.columns,
          gap: layout.grid.gap,
          padding: layout.grid.padding,
          maxWidth: layout.grid.maxWidth,
          containerPadding: layout.grid.containerPadding
        }
      
      case 'interactions':
        return {
          touchFriendly: layout.interactions.touchFriendly,
          gestureSupport: layout.interactions.gestureSupport,
          hoverEffects: layout.interactions.hoverEffects,
          keyboardNavigation: layout.interactions.keyboardNavigation,
          focusIndicators: layout.interactions.focusIndicators
        }
      
      default:
        return layout
    }
  }, [getOptimalLayout])

  const getSpacing = useCallback((size: keyof SpacingSystem): string => {
    return currentLayout.spacing[size]
  }, [currentLayout.spacing])

  const getTypography = useCallback((element: keyof TypographySystem | keyof TypographySystem['headingSizes']): string => {
    if (element in currentLayout.typography.headingSizes) {
      return currentLayout.typography.headingSizes[element as keyof TypographySystem['headingSizes']]
    }
    return currentLayout.typography[element as keyof TypographySystem] || currentLayout.typography.baseSize
  }, [currentLayout.typography])

  // Update layout when device capabilities change
  useEffect(() => {
    updateLayout(deviceCapabilities)
  }, [deviceCapabilities, updateLayout])

  return {
    currentLayout,
    layouts,
    updateLayout,
    getOptimalLayout,
    adaptComponent,
    getSpacing,
    getTypography
  }
}

// Hook for responsive grid system
export function useResponsiveGrid() {
  const { currentLayout } = useResponsiveLayout()
  
  const getGridClasses = useCallback(() => {
    const { columns, gap, padding } = currentLayout.grid
    
    return {
      container: `grid grid-cols-${columns} gap-${gap} p-${padding}`,
      item: `col-span-1`,
      fullWidth: `col-span-${columns}`,
      halfWidth: `col-span-${Math.ceil(columns / 2)}`,
      thirdWidth: `col-span-${Math.ceil(columns / 3)}`
    }
  }, [currentLayout.grid])
  
  return {
    columns: currentLayout.grid.columns,
    gap: currentLayout.grid.gap,
    padding: currentLayout.grid.padding,
    getGridClasses
  }
}

// Hook for responsive navigation
export function useResponsiveNavigation() {
  const { currentLayout } = useResponsiveLayout()
  
  const getNavigationConfig = useCallback(() => {
    return {
      type: currentLayout.navigation.type,
      position: currentLayout.navigation.position,
      sticky: currentLayout.navigation.sticky,
      collapsible: currentLayout.navigation.collapsible,
      showLabels: currentLayout.navigation.showLabels
    }
  }, [currentLayout.navigation])
  
  return {
    navigationType: currentLayout.navigation.type,
    navigationPosition: currentLayout.navigation.position,
    isSticky: currentLayout.navigation.sticky,
    isCollapsible: currentLayout.navigation.collapsible,
    showLabels: currentLayout.navigation.showLabels,
    getNavigationConfig
  }
}

// Hook for responsive interactions
export function useResponsiveInteractions() {
  const { currentLayout } = useResponsiveLayout()
  
  const getInteractionConfig = useCallback(() => {
    return {
      touchFriendly: currentLayout.interactions.touchFriendly,
      gestureSupport: currentLayout.interactions.gestureSupport,
      hoverEffects: currentLayout.interactions.hoverEffects,
      keyboardNavigation: currentLayout.interactions.keyboardNavigation,
      focusIndicators: currentLayout.interactions.focusIndicators
    }
  }, [currentLayout.interactions])
  
  return {
    isTouchFriendly: currentLayout.interactions.touchFriendly,
    hasGestureSupport: currentLayout.interactions.gestureSupport,
    hasHoverEffects: currentLayout.interactions.hoverEffects,
    hasKeyboardNavigation: currentLayout.interactions.keyboardNavigation,
    hasFocusIndicators: currentLayout.interactions.focusIndicators,
    getInteractionConfig
  }
}

// Hook for responsive spacing
export function useResponsiveSpacing() {
  const { getSpacing } = useResponsiveLayout()
  
  return {
    xs: getSpacing('xs'),
    sm: getSpacing('sm'),
    md: getSpacing('md'),
    lg: getSpacing('lg'),
    xl: getSpacing('xl'),
    xxl: getSpacing('xxl'),
    getSpacing
  }
}

// Hook for responsive typography
export function useResponsiveTypography() {
  const { getTypography } = useResponsiveLayout()
  
  return {
    baseSize: getTypography('baseSize'),
    lineHeight: getTypography('lineHeight'),
    h1: getTypography('h1'),
    h2: getTypography('h2'),
    h3: getTypography('h3'),
    h4: getTypography('h4'),
    h5: getTypography('h5'),
    h6: getTypography('h6'),
    bodySize: getTypography('bodySize'),
    getTypography
  }
}
