import { useEffect, useState } from 'react'
import { useWellness } from './useWellness'
import { useUserStats } from './useWellness'

export interface MoodTheme {
  name: string
  description: string
  cssVariables: Record<string, string>
  moodRange: Array<'very-low' | 'low' | 'neutral' | 'good' | 'excellent'>
}

export const moodThemes: Record<string, MoodTheme> = {
  // Calming, therapeutic theme for very low moods - soft blues and gentle greens
  healing: {
    name: 'Healing',
    description: 'Soft, therapeutic colors designed to provide comfort and reduce stress',
    moodRange: ['very-low'],
    cssVariables: {
      '--background': 'oklch(0.98 0.01 220)',
      '--foreground': 'oklch(0.35 0.04 220)',
      '--card': 'oklch(0.99 0.005 220)',
      '--card-foreground': 'oklch(0.35 0.04 220)',
      '--popover': 'oklch(0.99 0.005 220)',
      '--popover-foreground': 'oklch(0.35 0.04 220)',
      '--primary': 'oklch(0.6 0.08 220)', // Soft blue-purple
      '--primary-foreground': 'oklch(0.98 0.01 220)',
      '--secondary': 'oklch(0.95 0.015 220)',
      '--secondary-foreground': 'oklch(0.4 0.04 220)',
      '--accent': 'oklch(0.7 0.06 180)', // Gentle teal
      '--accent-foreground': 'oklch(0.25 0.03 180)',
      '--destructive': 'oklch(0.7 0.08 15)', // Muted coral instead of red
      '--destructive-foreground': 'oklch(0.98 0.01 220)',
      '--muted': 'oklch(0.96 0.01 220)',
      '--muted-foreground': 'oklch(0.55 0.04 220)',
      '--border': 'oklch(0.9 0.015 220)',
      '--input': 'oklch(0.92 0.015 220)',
      '--ring': 'oklch(0.6 0.08 220)',
    }
  },
  
  // Supportive theme for low moods - warm but gentle earth tones
  supportive: {
    name: 'Supportive',
    description: 'Warm, nurturing earth tones for gentle comfort and stability',
    moodRange: ['low'],
    cssVariables: {
      '--background': 'oklch(0.97 0.015 50)',
      '--foreground': 'oklch(0.3 0.05 50)',
      '--card': 'oklch(0.99 0.008 50)',
      '--card-foreground': 'oklch(0.3 0.05 50)',
      '--popover': 'oklch(0.99 0.008 50)',
      '--popover-foreground': 'oklch(0.3 0.05 50)',
      '--primary': 'oklch(0.65 0.08 50)', // Warm sage
      '--primary-foreground': 'oklch(0.98 0.01 50)',
      '--secondary': 'oklch(0.93 0.02 50)',
      '--secondary-foreground': 'oklch(0.35 0.05 50)',
      '--accent': 'oklch(0.72 0.08 80)', // Soft golden green
      '--accent-foreground': 'oklch(0.2 0.03 80)',
      '--destructive': 'oklch(0.68 0.08 25)', // Muted terracotta
      '--destructive-foreground': 'oklch(0.98 0.01 50)',
      '--muted': 'oklch(0.94 0.015 50)',
      '--muted-foreground': 'oklch(0.5 0.05 50)',
      '--border': 'oklch(0.88 0.02 50)',
      '--input': 'oklch(0.9 0.02 50)',
      '--ring': 'oklch(0.65 0.08 50)',
    }
  },
  
  // Balanced theme for neutral moods - clean and clear
  balanced: {
    name: 'Balanced',
    description: 'Clean, balanced colors for steady and peaceful moments',
    moodRange: ['neutral'],
    cssVariables: {
      '--background': 'oklch(0.98 0.008 200)',
      '--foreground': 'oklch(0.25 0.06 200)',
      '--card': 'oklch(1 0 0)',
      '--card-foreground': 'oklch(0.25 0.06 200)',
      '--popover': 'oklch(1 0 0)',
      '--popover-foreground': 'oklch(0.25 0.06 200)',
      '--primary': 'oklch(0.6 0.12 200)', // Calm blue
      '--primary-foreground': 'oklch(0.98 0.01 200)',
      '--secondary': 'oklch(0.94 0.015 200)',
      '--secondary-foreground': 'oklch(0.35 0.06 200)',
      '--accent': 'oklch(0.7 0.1 160)', // Fresh teal
      '--accent-foreground': 'oklch(0.2 0.04 160)',
      '--destructive': 'oklch(0.65 0.12 20)',
      '--destructive-foreground': 'oklch(0.98 0.01 200)',
      '--muted': 'oklch(0.96 0.008 200)',
      '--muted-foreground': 'oklch(0.5 0.06 200)',
      '--border': 'oklch(0.89 0.015 200)',
      '--input': 'oklch(0.91 0.015 200)',
      '--ring': 'oklch(0.6 0.12 200)',
    }
  },
  
  // Uplifting theme for good moods - vibrant but not overwhelming
  uplifting: {
    name: 'Uplifting',
    description: 'Vibrant yet balanced colors to enhance and sustain positive energy',
    moodRange: ['good'],
    cssVariables: {
      '--background': 'oklch(0.98 0.015 120)',
      '--foreground': 'oklch(0.2 0.06 120)',
      '--card': 'oklch(1 0 0)',
      '--card-foreground': 'oklch(0.2 0.06 120)',
      '--popover': 'oklch(1 0 0)',
      '--popover-foreground': 'oklch(0.2 0.06 120)',
      '--primary': 'oklch(0.65 0.14 120)', // Vibrant green
      '--primary-foreground': 'oklch(0.98 0.01 120)',
      '--secondary': 'oklch(0.92 0.03 120)',
      '--secondary-foreground': 'oklch(0.3 0.06 120)',
      '--accent': 'oklch(0.75 0.12 80)', // Golden yellow-green
      '--accent-foreground': 'oklch(0.2 0.04 80)',
      '--destructive': 'oklch(0.65 0.12 20)',
      '--destructive-foreground': 'oklch(0.98 0.01 120)',
      '--muted': 'oklch(0.94 0.02 120)',
      '--muted-foreground': 'oklch(0.45 0.06 120)',
      '--border': 'oklch(0.87 0.03 120)',
      '--input': 'oklch(0.89 0.03 120)',
      '--ring': 'oklch(0.65 0.14 120)',
    }
  },
  
  // Energetic theme for excellent moods - bold but harmonious
  radiant: {
    name: 'Radiant',
    description: 'Confident, energizing colors that celebrate peak emotional wellness',
    moodRange: ['excellent'],
    cssVariables: {
      '--background': 'oklch(0.97 0.02 60)',
      '--foreground': 'oklch(0.15 0.08 60)',
      '--card': 'oklch(0.99 0.01 60)',
      '--card-foreground': 'oklch(0.15 0.08 60)',
      '--popover': 'oklch(0.99 0.01 60)',
      '--popover-foreground': 'oklch(0.15 0.08 60)',
      '--primary': 'oklch(0.7 0.16 60)', // Warm golden
      '--primary-foreground': 'oklch(0.98 0.01 60)',
      '--secondary': 'oklch(0.9 0.04 60)',
      '--secondary-foreground': 'oklch(0.25 0.08 60)',
      '--accent': 'oklch(0.8 0.14 40)', // Bright orange-yellow
      '--accent-foreground': 'oklch(0.15 0.04 40)',
      '--destructive': 'oklch(0.65 0.12 20)',
      '--destructive-foreground': 'oklch(0.98 0.01 60)',
      '--muted': 'oklch(0.93 0.03 60)',
      '--muted-foreground': 'oklch(0.4 0.08 60)',
      '--border': 'oklch(0.85 0.04 60)',
      '--input': 'oklch(0.87 0.04 60)',
      '--ring': 'oklch(0.7 0.16 60)',
    }
  },
  
  // Default fallback theme - neutral and accessible
  default: {
    name: 'Classic',
    description: 'Clean, neutral theme suitable for any mood',
    moodRange: ['very-low', 'low', 'neutral', 'good', 'excellent'],
    cssVariables: {
      '--background': 'oklch(0.98 0.005 180)',
      '--foreground': 'oklch(0.3 0.05 180)',
      '--card': 'oklch(1 0 0)',
      '--card-foreground': 'oklch(0.25 0.04 220)',
      '--popover': 'oklch(1 0 0)',
      '--popover-foreground': 'oklch(0.25 0.04 220)',
      '--primary': 'oklch(0.7 0.08 180)',
      '--primary-foreground': 'oklch(1 0 0)',
      '--secondary': 'oklch(0.95 0.01 180)',
      '--secondary-foreground': 'oklch(0.4 0.05 180)',
      '--accent': 'oklch(0.8 0.08 60)',
      '--accent-foreground': 'oklch(0.2 0.03 60)',
      '--destructive': 'oklch(0.65 0.12 20)',
      '--destructive-foreground': 'oklch(1 0 0)',
      '--muted': 'oklch(0.96 0.005 180)',
      '--muted-foreground': 'oklch(0.5 0.04 180)',
      '--border': 'oklch(0.9 0.01 180)',
      '--input': 'oklch(0.92 0.01 180)',
      '--ring': 'oklch(0.7 0.08 180)',
    }
  }
}

export function useMoodBasedTheme() {
  const { moodEntries } = useWellness()
  const { stats } = useUserStats()
  const [isThemeChanging, setIsThemeChanging] = useState(false)
  const [localTheme, setLocalTheme] = useState<string>('default')

  const convertMoodScore = (score: number): 'very-low' | 'low' | 'neutral' | 'good' | 'excellent' => {
    if (score <= 2) return 'very-low'
    if (score <= 4) return 'low'
    if (score <= 6) return 'neutral'
    if (score <= 8) return 'good'
    return 'excellent'
  }

  const getCurrentMood = () => {
    // Handle case when mood entries array is empty or backend is not available
    if (!moodEntries || moodEntries.length === 0) return 'neutral'
    return convertMoodScore(moodEntries[0].mood)
  }

  const getRecommendedTheme = (mood: string) => {
    for (const [themeKey, theme] of Object.entries(moodThemes)) {
      if (theme.moodRange.includes(mood as any)) {
        return themeKey
      }
    }
    return 'default'
  }

  const applyTheme = (themeName: string) => {
    const theme = moodThemes[themeName]
    if (!theme) return

    setIsThemeChanging(true)

    // Apply CSS variables to document root
    const root = document.documentElement
    Object.entries(theme.cssVariables).forEach(([property, value]) => {
      root.style.setProperty(property, value)
    })

    // Store theme locally and update local state
    localStorage.setItem('mantrapath_theme', themeName)
    setLocalTheme(themeName)

    // Visual feedback for theme change
    setTimeout(() => setIsThemeChanging(false), 1000)
  }

  const autoApplyMoodTheme = () => {
    const currentMood = getCurrentMood()
    const recommendedTheme = getRecommendedTheme(currentMood)
    
    // Only apply if the theme actually changes
    if (recommendedTheme !== localTheme) {
      applyTheme(recommendedTheme)
      return true // Theme was changed
    }
    return false // No change needed
  }

  const resetToDefaultTheme = () => {
    applyTheme('default')
  }

  // Auto-apply theme when mood changes and on initial load
  useEffect(() => {
    if (moodEntries.length > 0) {
      const latestMood = moodEntries[0]
      const timeSinceLastMood = Date.now() - new Date(latestMood.timestamp).getTime()
      
      // Only auto-apply if mood was logged within last hour
      if (timeSinceLastMood < 60 * 60 * 1000) {
        autoApplyMoodTheme()
      }
    }
  }, [moodEntries])

  // Initialize theme from localStorage on mount
  useEffect(() => {
    const savedTheme = localStorage.getItem('mantrapath_theme') || stats?.currentTheme || 'default'
    setLocalTheme(savedTheme)
    
    const theme = moodThemes[savedTheme]
    if (theme) {
      const root = document.documentElement
      Object.entries(theme.cssVariables).forEach(([property, value]) => {
        root.style.setProperty(property, value)
      })
    }
  }, [stats?.currentTheme])

  // Auto-apply mood theme when mood entries change
  useEffect(() => {
    if (moodEntries && moodEntries.length > 0) {
      const currentMood = getCurrentMood()
      if (currentMood !== 'neutral') {
        autoApplyMoodTheme()
      }
    }
  }, [moodEntries])

  return {
    currentTheme: localTheme,
    availableThemes: moodThemes,
    applyTheme,
    autoApplyMoodTheme,
    resetToDefaultTheme,
    getCurrentMood,
    getRecommendedTheme,
    isThemeChanging
  }
}