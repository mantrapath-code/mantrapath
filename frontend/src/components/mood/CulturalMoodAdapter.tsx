import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Slider } from '@/components/ui/slider'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Globe, 
  Heart, 
  Star, 
  Confetti, 
  Translate,
  MapPin,
  CalendarBlank,
  Palette
} from '@phosphor-icons/react'

interface CulturalMoodContext {
  region: string
  language: string
  culturalEmotions: string[]
  moodExpressionPatterns: Record<string, any>
  celebrationTriggers: string[]
  weatherMetaphors: Record<string, string>
  colorAssociations: Record<string, string>
}

interface CulturalMoodAdapterProps {
  context?: Partial<CulturalMoodContext>
  onContextChange?: (context: CulturalMoodContext) => void
  onMoodSubmit?: (mood: number, culturalExpression: string, celebration?: string) => void
  currentMood?: number
  showRegionSelector?: boolean
  showLanguageSelector?: boolean
  showCelebrationTriggers?: boolean
}

// Cultural data configurations
const CULTURAL_CONFIGS: Record<string, CulturalMoodContext> = {
  'en-US': {
    region: 'North America',
    language: 'en-US',
    culturalEmotions: ['happy', 'excited', 'calm', 'energetic', 'peaceful', 'grateful', 'motivated'],
    moodExpressionPatterns: {
      high: ['feeling great', 'on top of the world', 'fantastic', 'amazing'],
      medium: ['doing okay', 'pretty good', 'alright', 'decent'],
      low: ['feeling down', 'not great', 'struggling', 'having a tough time']
    },
    celebrationTriggers: ['achievement', 'milestone', 'breakthrough', 'success'],
    weatherMetaphors: {
      'sunny': 'bright and cheerful',
      'cloudy': 'feeling uncertain',
      'stormy': 'going through challenges',
      'rainbow': 'hope after difficulties'
    },
    colorAssociations: {
      'high': '#10B981', // green
      'medium': '#F59E0B', // amber
      'low': '#EF4444' // red
    }
  },
  'ja-JP': {
    region: 'Japan',
    language: 'ja-JP',
    culturalEmotions: ['穏やか (calm)', '元気 (energetic)', '幸せ (happy)', '感謝 (grateful)', '安心 (peaceful)', '楽しい (joyful)'],
    moodExpressionPatterns: {
      high: ['元気です', '調子がいいです', '気分が良い', '幸せです'],
      medium: ['まあまあです', '普通です', '大丈夫です'],
      low: ['少し疲れています', '気分が下がっています', '調子が悪い']
    },
    celebrationTriggers: ['達成', '成功', '進歩', '改善'],
    weatherMetaphors: {
      'sunny': '晴れやかな気持ち',
      'cloudy': '曇った心',
      'stormy': '嵐のような時期',
      'rainbow': '希望の光'
    },
    colorAssociations: {
      'high': '#059669',
      'medium': '#D97706',
      'low': '#DC2626'
    }
  },
  'es-ES': {
    region: 'Spain',
    language: 'es-ES',
    culturalEmotions: ['feliz', 'tranquilo', 'energético', 'agradecido', 'en paz', 'motivado', 'alegre'],
    moodExpressionPatterns: {
      high: ['me siento genial', 'estoy muy bien', 'fantástico', 'maravilloso'],
      medium: ['estoy bien', 'regular', 'normal', 'así así'],
      low: ['me siento mal', 'no muy bien', 'triste', 'difícil']
    },
    celebrationTriggers: ['logro', 'éxito', 'progreso', 'mejora'],
    weatherMetaphors: {
      'sunny': 'radiante como el sol',
      'cloudy': 'algo nublado',
      'stormy': 'tiempo tormentoso',
      'rainbow': 'esperanza tras la tormenta'
    },
    colorAssociations: {
      'high': '#059669',
      'medium': '#D97706',
      'low': '#DC2626'
    }
  },
  'fr-FR': {
    region: 'France',
    language: 'fr-FR',
    culturalEmotions: ['heureux', 'calme', 'énergique', 'reconnaissant', 'paisible', 'motivé', 'joyeux'],
    moodExpressionPatterns: {
      high: ['je me sens formidable', 'excellent', 'fantastique', 'merveilleux'],
      medium: ['ça va bien', 'correct', 'pas mal', 'convenable'],
      low: ['je ne me sens pas bien', 'difficile', 'triste', 'fatigué']
    },
    celebrationTriggers: ['accomplissement', 'succès', 'progrès', 'amélioration'],
    weatherMetaphors: {
      'sunny': 'radieux comme le soleil',
      'cloudy': 'un peu nuageux',
      'stormy': 'temps orageux',
      'rainbow': 'arc-en-ciel après la pluie'
    },
    colorAssociations: {
      'high': '#059669',
      'medium': '#D97706',
      'low': '#DC2626'
    }
  },
  'hi-IN': {
    region: 'India',
    language: 'hi-IN',
    culturalEmotions: ['खुश (happy)', 'शांत (peaceful)', 'उत्साहित (energetic)', 'आभारी (grateful)', 'संतुष्ट (content)', 'प्रेरित (motivated)'],
    moodExpressionPatterns: {
      high: ['बहुत अच्छा', 'शानदार', 'उत्कृष्ट', 'बेहतरीन'],
      medium: ['ठीक है', 'अच्छा', 'सामान्य', 'ओके'],
      low: ['अच्छा नहीं', 'परेशान', 'उदास', 'कठिन']
    },
    celebrationTriggers: ['उपलब्धि', 'सफलता', 'प्रगति', 'सुधार'],
    weatherMetaphors: {
      'sunny': 'धूप की तरह चमकदार',
      'cloudy': 'बादलों से घिरा',
      'stormy': 'तूफानी समय',
      'rainbow': 'बारिश के बाद इंद्रधनुष'
    },
    colorAssociations: {
      'high': '#059669',
      'medium': '#D97706',
      'low': '#DC2626'
    }
  }
}

const REGION_OPTIONS = [
  { value: 'en-US', label: '🇺🇸 North America', flag: '🇺🇸' },
  { value: 'ja-JP', label: '🇯🇵 Japan', flag: '🇯🇵' },
  { value: 'es-ES', label: '🇪🇸 Spain', flag: '🇪🇸' },
  { value: 'fr-FR', label: '🇫🇷 France', flag: '🇫🇷' },
  { value: 'hi-IN', label: '🇮🇳 India', flag: '🇮🇳' }
]

export function CulturalMoodAdapter({
  context,
  onContextChange,
  onMoodSubmit,
  currentMood = 5,
  showRegionSelector = true,
  showLanguageSelector = true,
  showCelebrationTriggers = true
}: CulturalMoodAdapterProps) {
  const [selectedRegion, setSelectedRegion] = useState(context?.language || 'en-US')
  const [mood, setMood] = useState([currentMood])
  const [selectedExpression, setSelectedExpression] = useState<string>('')
  const [selectedCelebration, setSelectedCelebration] = useState<string>('')
  const [culturalContext, setCulturalContext] = useState<CulturalMoodContext>(
    CULTURAL_CONFIGS[selectedRegion] || CULTURAL_CONFIGS['en-US']
  )

  useEffect(() => {
    const newContext = CULTURAL_CONFIGS[selectedRegion] || CULTURAL_CONFIGS['en-US']
    setCulturalContext(newContext)
    onContextChange?.(newContext)
    
    // Reset selections when region changes
    setSelectedExpression('')
    setSelectedCelebration('')
  }, [selectedRegion, onContextChange])

  useEffect(() => {
    setMood([currentMood])
  }, [currentMood])

  const getMoodCategory = (moodValue: number): 'high' | 'medium' | 'low' => {
    if (moodValue >= 7) return 'high'
    if (moodValue >= 4) return 'medium'
    return 'low'
  }

  const getCulturalMoodExpressions = (moodValue: number) => {
    const category = getMoodCategory(moodValue)
    return culturalContext.moodExpressionPatterns[category] || []
  }

  const getMoodColor = (moodValue: number) => {
    const category = getMoodCategory(moodValue)
    return culturalContext.colorAssociations[category]
  }

  const handleMoodChange = (newMood: number[]) => {
    setMood(newMood)
    setSelectedExpression('') // Reset expression when mood changes
  }

  const handleSubmit = () => {
    const expression = selectedExpression || getCulturalMoodExpressions(mood[0])[0] || ''
    onMoodSubmit?.(mood[0], expression, selectedCelebration)
  }

  const shouldShowCelebration = (moodValue: number) => {
    return moodValue >= 7 && showCelebrationTriggers
  }

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Globe size={20} className="text-blue-500" />
            <span>Cultural Mood Expression</span>
          </div>
          <Badge variant="outline" className="flex items-center gap-1">
            <MapPin size={12} />
            {REGION_OPTIONS.find(r => r.value === selectedRegion)?.flag}
            {culturalContext.region}
          </Badge>
        </CardTitle>
      </CardHeader>

      <CardContent className="space-y-6">
        {/* Region Selector */}
        {showRegionSelector && (
          <div className="space-y-2">
            <label className="text-sm font-medium flex items-center gap-2">
              <Translate size={16} />
              Cultural Region & Language
            </label>
            <Select value={selectedRegion} onValueChange={setSelectedRegion}>
              <SelectTrigger>
                <SelectValue placeholder="Select your cultural region" />
              </SelectTrigger>
              <SelectContent>
                {REGION_OPTIONS.map((option) => (
                  <SelectItem key={option.value} value={option.value}>
                    {option.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        )}

        {/* Mood Slider with Cultural Colors */}
        <div className="space-y-4">
          <label className="text-sm font-medium flex items-center gap-2">
            <Heart size={16} />
            How are you feeling? (Cultural Expression)
          </label>
          
          <div className="space-y-3">
            <Slider
              value={mood}
              onValueChange={handleMoodChange}
              max={10}
              min={1}
              step={1}
              className="w-full"
            />
            
            <div className="flex items-center justify-between text-xs text-muted-foreground">
              <span>1 - Low</span>
              <motion.div
                animate={{ 
                  backgroundColor: getMoodColor(mood[0]),
                  scale: mood[0] >= 7 ? 1.1 : 1
                }}
                transition={{ duration: 0.3 }}
                className="px-3 py-1 rounded-full text-white font-medium"
                style={{ backgroundColor: getMoodColor(mood[0]) }}
              >
                {mood[0]}
              </motion.div>
              <span>10 - High</span>
            </div>
          </div>
        </div>

        {/* Cultural Mood Expressions */}
        <div className="space-y-3">
          <label className="text-sm font-medium flex items-center gap-2">
            <Palette size={16} />
            Express in your cultural way:
          </label>
          
          <div className="grid grid-cols-2 gap-2">
            {getCulturalMoodExpressions(mood[0]).map((expression, index) => (
              <motion.div
                key={expression}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <Button
                  variant={selectedExpression === expression ? "default" : "outline"}
                  size="sm"
                  onClick={() => setSelectedExpression(expression)}
                  className="w-full justify-start text-left h-auto py-2 px-3"
                >
                  <span className="text-xs">{expression}</span>
                </Button>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Cultural Emotions Vocabulary */}
        <div className="space-y-3">
          <label className="text-sm font-medium">
            Cultural emotion vocabulary:
          </label>
          <div className="flex flex-wrap gap-2">
            {culturalContext.culturalEmotions.map((emotion, index) => (
              <motion.div
                key={emotion}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: index * 0.05 }}
              >
                <Badge 
                  variant="outline" 
                  className="text-xs cursor-pointer hover:bg-primary hover:text-primary-foreground transition-colors"
                  onClick={() => setSelectedExpression(emotion)}
                >
                  {emotion}
                </Badge>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Celebration Triggers */}
        <AnimatePresence>
          {shouldShowCelebration(mood[0]) && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="space-y-3"
            >
              <label className="text-sm font-medium flex items-center gap-2">
                <Confetti size={16} className="text-yellow-500" />
                What are you celebrating?
              </label>
              <div className="grid grid-cols-2 gap-2">
                {culturalContext.celebrationTriggers.map((trigger) => (
                  <Button
                    key={trigger}
                    variant={selectedCelebration === trigger ? "default" : "outline"}
                    size="sm"
                    onClick={() => setSelectedCelebration(trigger)}
                    className="w-full justify-start text-left h-auto py-2 px-3"
                  >
                    <Star size={12} className="mr-2" />
                    <span className="text-xs">{trigger}</span>
                  </Button>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Weather Metaphor */}
        <div className="p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg">
          <div className="text-sm">
            <span className="font-medium">Cultural weather metaphor: </span>
            <span className="italic">
              {culturalContext.weatherMetaphors[getMoodCategory(mood[0])] || 
               culturalContext.weatherMetaphors['sunny']}
            </span>
          </div>
        </div>

        {/* Submit Button */}
        <Button 
          onClick={handleSubmit}
          className="w-full"
          style={{ backgroundColor: getMoodColor(mood[0]) }}
        >
          <Heart size={16} className="mr-2" />
          Express My {culturalContext.region} Mood
        </Button>

        {/* Cultural Context Info */}
        <div className="text-xs text-muted-foreground bg-gray-50 p-3 rounded-lg">
          <div className="flex items-center gap-2 mb-2">
            <CalendarBlank size={12} />
            <span className="font-medium">Cultural Context Active</span>
          </div>
          <div className="space-y-1">
            <div>Region: {culturalContext.region}</div>
            <div>Language: {culturalContext.language}</div>
            <div>Expressions: {culturalContext.culturalEmotions.length} available</div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
