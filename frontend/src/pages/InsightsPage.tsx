/**
 * Insights Page - Enhanced unified insight experience
 * 
 * This page now uses the enhanced insight system that consolidates
 * all insight sources into a single, comprehensive dashboard.
 */

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  Brain,
  ChartLine,
  Target,
  TrendUp,
  ArrowLeft,
  Lightbulb,
  Sparkle
} from '@phosphor-icons/react'
import { motion } from 'framer-motion'
import { PersonalizedInsights } from '@/components/mood/PersonalizedInsights'
import { MoodInsights } from '@/components/mood/MoodInsights'
import { MoodCorrelations } from '@/components/mood/MoodCorrelations'
import { MoodComparisonView } from '@/components/mood/MoodComparisonView'
import EnhancedInsightsPage from './EnhancedInsightsPage'

interface InsightsPageProps {
  onBack?: () => void
}

export function InsightsPage({ onBack }: InsightsPageProps) {
  const [viewMode, setViewMode] = useState<'enhanced' | 'classic'>('enhanced')

  if (viewMode === 'enhanced') {
    return <EnhancedInsightsPage onBack={onBack} />
  }

  // Classic view (fallback)
  return (
    <div className="space-y-6">
      {/* Header with View Toggle */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div className="flex items-center gap-3">
          {onBack && (
            <Button variant="ghost" size="sm" onClick={onBack}>
              <ArrowLeft size={16} />
            </Button>
          )}
          <div>
            <h1 className="text-2xl font-bold flex items-center gap-2">
              <Brain className="text-primary" size={28} />
              Your Insights
            </h1>
            <p className="text-muted-foreground">
              Discover patterns and get personalized recommendations based on your mood data
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant={viewMode === 'enhanced' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setViewMode('enhanced')}
          >
            <Sparkle size={14} className="mr-1" />
            Enhanced
          </Button>
          <Button
            variant={viewMode === 'classic' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setViewMode('classic')}
          >
            Classic
          </Button>
        </div>
      </motion.div>

      {/* Classic Insights Tabs */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <Tabs defaultValue="personalized" className="w-full">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="personalized" className="flex items-center gap-2">
              <Lightbulb size={16} />
              Personalized
            </TabsTrigger>
            <TabsTrigger value="mood-insights" className="flex items-center gap-2">
              <Brain size={16} />
              Mood Insights
            </TabsTrigger>
            <TabsTrigger value="correlations" className="flex items-center gap-2">
              <TrendUp size={16} />
              Correlations
            </TabsTrigger>
            <TabsTrigger value="comparisons" className="flex items-center gap-2">
              <ChartLine size={16} />
              Comparisons
            </TabsTrigger>
          </TabsList>

          <TabsContent value="personalized" className="space-y-6 mt-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Target className="text-primary" size={20} />
                  AI-Powered Insights
                </CardTitle>
                <p className="text-sm text-muted-foreground">
                  Personalized recommendations based on your unique mood patterns and trends
                </p>
              </CardHeader>
              <CardContent>
                <PersonalizedInsights />
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="mood-insights" className="space-y-6 mt-6">
            <MoodInsights />
          </TabsContent>

          <TabsContent value="correlations" className="space-y-6 mt-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendUp className="text-primary" size={20} />
                  Pattern Analysis
                </CardTitle>
                <p className="text-sm text-muted-foreground">
                  Understand how different activities, times, and triggers affect your mood
                </p>
              </CardHeader>
              <CardContent>
                <MoodCorrelations />
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="comparisons" className="space-y-6 mt-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <ChartLine className="text-primary" size={20} />
                  Period Comparisons
                </CardTitle>
                <p className="text-sm text-muted-foreground">
                  Compare your mood patterns across different time periods to track progress
                </p>
              </CardHeader>
              <CardContent>
                <MoodComparisonView />
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </motion.div>
    </div>
  )
}
