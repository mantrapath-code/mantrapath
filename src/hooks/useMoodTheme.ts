import { useEffect } from 'react'
import { useMoods, useUserStats } from './useWellness'

export interface MoodTheme {
  name: string
  description: string
  cssVariables: Record<string, string>
  moodRange: Array<'very-low' | 'low' | 'neutral' | 'good' | 'excellent'>
}

export const moodThemes: Record<string, MoodTheme> = {
  supportive: {
    name: 'Supportive',
    description: 'Warm, nurturing colors for when you need comfort',
    moodRange: ['very-low', 'low'],
    cssVariables: {
      '--background': 'oklch(0.97 0.02 350)',
      '--foreground': 'oklch(0.25 0.06 350)',
      '--card': 'oklch(0.99 0.01 350)',
      '--primary': 'oklch(0.65 0.12 350)',
      '--primary-foreground': 'oklch(0.98 0.01 350)',
      '--secondary': 'oklch(0.93 0.03 350)',
      '--accent': 'oklch(0.75 0.15 20)',
      '--muted': 'oklch(0.95 0.02 350)',
      '--border': 'oklch(0.88 0.03 350)',
    }
  },
  calm: {
    name: 'Calm',
    description: 'Peaceful blues and greens for balanced moments',
    moodRange: ['neutral'],
    cssVariables: {
      '--background': 'oklch(0.98 0.01 200)',
      '--foreground': 'oklch(0.25 0.08 200)',
      '--card': 'oklch(1 0 0)',
      '--primary': 'oklch(0.6 0.15 200)',
      '--primary-foreground': 'oklch(0.98 0.01 200)',
      '--secondary': 'oklch(0.94 0.02 200)',
      '--accent': 'oklch(0.7 0.12 160)',
      '--muted': 'oklch(0.96 0.01 200)',
      '--border': 'oklch(0.89 0.02 200)',
    }
  },
  energetic: {
    name: 'Energetic',
    description: 'Vibrant and uplifting colors for good days',
    moodRange: ['good'],
    cssVariables: {
      '--background': 'oklch(0.98 0.02 120)',
      '--foreground': 'oklch(0.2 0.08 120)',
      '--card': 'oklch(1 0 0)',
      '--primary': 'oklch(0.65 0.18 120)',
      '--primary-foreground': 'oklch(0.98 0.01 120)',
      '--secondary': 'oklch(0.92 0.04 120)',
      '--accent': 'oklch(0.75 0.15 80)',
      '--muted': 'oklch(0.94 0.03 120)',
      '--border': 'oklch(0.87 0.04 120)',
    }
  },
  dynamic: {
    name: 'Dynamic',
    description: 'Bold, confident colors for excellent moods',
    moodRange: ['excellent'],
    cssVariables: {
      '--background': 'oklch(0.97 0.03 60)',
      '--foreground': 'oklch(0.15 0.1 60)',
      '--card': 'oklch(0.99 0.01 60)',
      '--primary': 'oklch(0.7 0.2 60)',
      '--primary-foreground': 'oklch(0.98 0.01 60)',
      '--secondary': 'oklch(0.9 0.05 60)',
      '--accent': 'oklch(0.8 0.18 40)',
      '--muted': 'oklch(0.93 0.04 60)',
      '--border': 'oklch(0.85 0.05 60)',
    }
  },
  default: {
    name: 'Default',
    description: 'Clean, neutral theme',
    moodRange: ['very-low', 'low', 'neutral', 'good', 'excellent'],
    cssVariables: {
      '--background': 'oklch(0.98 0.01 180)',
      '--foreground': 'oklch(0.3 0.08 180)',
      '--card': 'oklch(1 0 0)',
      '--primary': 'oklch(0.7 0.1 180)',
      '--primary-foreground': 'oklch(1 0 0)',
      '--secondary': 'oklch(0.95 0.02 180)',
      '--accent': 'oklch(0.8 0.1 60)',
      '--muted': 'oklch(0.96 0.01 180)',
      '--border': 'oklch(0.9 0.02 180)',
    }
  }
}

export function useMoodBasedTheme() {
  const { moods } = useMoods()
  const { stats, updateStats } = useUserStats()

  const getCurrentMood = () => {
    if (moods.length === 0) return 'neutral'
    return moods[0].mood
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

    const root = document.documentElement
    Object.entries(theme.cssVariables).forEach(([property, value]) => {
      root.style.setProperty(property, value)
    })

    updateStats({ currentTheme: themeName as any })
  }

  const autoApplyMoodTheme = () => {
    const currentMood = getCurrentMood()
    const recommendedTheme = getRecommendedTheme(currentMood)
    applyTheme(recommendedTheme)
  }

  const resetToDefaultTheme = () => {
    applyTheme('default')
  }

  // Auto-apply theme when mood changes
  useEffect(() => {
    if (moods.length > 0) {
      const latestMood = moods[0]
      const timeSinceLastMood = Date.now() - latestMood.timestamp
      
      // Only auto-apply if mood was logged within last hour
      if (timeSinceLastMood < 60 * 60 * 1000) {
        autoApplyMoodTheme()
      }
    }
  }, [moods])

  return {
    currentTheme: stats.currentTheme || 'default',
    availableThemes: moodThemes,
    applyTheme,
    autoApplyMoodTheme,
    resetToDefaultTheme,
    getCurrentMood,
    getRecommendedTheme
  }
}