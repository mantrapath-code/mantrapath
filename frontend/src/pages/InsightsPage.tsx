/**
 * Insights Page - Real analytics and insights from backend data
 */

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { motion } from 'framer-motion'
import { 
  Brain,
  ChartLine,
  Target,
  TrendUp,
  ArrowLeft,
  Spinner
} from '@phosphor-icons/react'
import { useComprehensiveInsights } from '@/hooks/useComprehensiveInsights'

interface InsightsPageProps {
  onBack?: () => void
}

export function InsightsPage({ onBack }: InsightsPageProps) {
  const { 
    insights, 
    unifiedData, 
    loading, 
    error, 
    refresh, 
    refreshUnified, 
    isUsingUnifiedEndpoint 
  } = useComprehensiveInsights()

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center space-y-4">
          <Spinner className="h-8 w-8 animate-spin mx-auto" />
          <p className="text-muted-foreground">
            {isUsingUnifiedEndpoint 
              ? 'Loading unified insights from ML service...' 
              : 'Loading insights...'}
          </p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center space-y-4">
          <p className="text-red-500">Failed to load insights: {error}</p>
          <div className="space-x-2">
            <Button onClick={refresh} variant="outline">
              Try Again
            </Button>
            {isUsingUnifiedEndpoint && (
              <Button onClick={refreshUnified} variant="outline">
                Refresh Unified
              </Button>
            )}
          </div>
        </div>
      </div>
    )
  }

  const dashboard = insights?.dashboard
  const metadata = insights?.metadata
  const recommendedActions = insights?.recommendedActions || []

  return (
    <div className="space-y-6">
      {onBack && (
        <Button variant="ghost" onClick={onBack} className="mb-4">
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back
        </Button>
      )}

      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div>
          <h1 className="text-3xl font-bold">Insights & Analytics</h1>
          <p className="text-muted-foreground mt-2">
            {(metadata?.insightCount ?? 0) > 0 
              ? `Discover patterns and insights from your wellness journey (${metadata?.insightCount ?? 0} insights available)`
              : 'Start tracking your mood to see personalized insights'}
          </p>
          {/* Show data source info */}
          {isUsingUnifiedEndpoint && unifiedData && (
            <div className="mt-2 text-xs text-muted-foreground bg-blue-50 dark:bg-blue-950 px-3 py-1 rounded-md inline-block">
              🤖 AI-Powered Unified Insights
              {unifiedData.cache_info?.hit ? ' • Cached' : ' • Fresh'}
              {unifiedData.version && ` • ${unifiedData.version}`}
            </div>
          )}
        </div>
        <div className="flex space-x-2">
          <Button onClick={refresh} variant="outline" size="sm">
            Refresh
          </Button>
          {isUsingUnifiedEndpoint && (
            <Button onClick={refreshUnified} variant="outline" size="sm">
              🔄 AI Refresh
            </Button>
          )}
        </div>
      </motion.div>

      {/* Analytics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                Insights Available
              </CardTitle>
              <Brain className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {recommendedActions.length || 0}
              </div>
              <p className="text-xs text-muted-foreground">
                Personalized recommendations
              </p>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                Weekly Score
              </CardTitle>
              <TrendUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {dashboard?.weeklySummary?.currentWeekScore || 0}
              </div>
              <p className="text-xs text-muted-foreground">
                {dashboard?.weeklySummary?.trend === 'improving' ? '↗ Improving' :
                 dashboard?.weeklySummary?.trend === 'declining' ? '↘ Declining' : '→ Stable'}
              </p>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                Days Tracked
              </CardTitle>
              <Target className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {dashboard?.weeklySummary?.daysTracked || 0}
              </div>
              <p className="text-xs text-muted-foreground">
                This week
              </p>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                Data Quality
              </CardTitle>
              <ChartLine className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {metadata?.dataQuality || 0}%
              </div>
              <p className="text-xs text-muted-foreground">
                Insight confidence
              </p>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Detailed Insights */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="grid grid-cols-1 lg:grid-cols-2 gap-6"
      >
        <Card>
          <CardHeader>
            <CardTitle>Weekly Patterns</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {dashboard?.topHighlights?.bestDay ? (
                <div className="space-y-2">
                  <p className="text-sm font-medium">Best Day: {dashboard.topHighlights.bestDay}</p>
                  <p className="text-sm font-medium">Energy Peak: {dashboard.topHighlights.energyPeak}</p>
                  <p className="text-sm font-medium">Mood Streak: {dashboard.topHighlights.moodStreak} days</p>
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">
                  Track your mood for a few more days to see weekly patterns and insights.
                </p>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Engagement Insights</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {(dashboard?.weeklySummary?.achievements?.length ?? 0) > 0 ? (
                <div className="space-y-2">
                  <p className="text-sm font-medium">Recent Achievements:</p>
                  <ul className="text-sm text-muted-foreground space-y-1">
                    {dashboard?.weeklySummary?.achievements?.map((achievement, index) => (
                      <li key={index}>• {achievement}</li>
                    ))}
                  </ul>
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">
                  Continue tracking your wellness journey to unlock engagement insights and achievements.
                </p>
              )}
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Recommendations */}
      {recommendedActions.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
        >
          <Card>
            <CardHeader>
              <CardTitle>Personalized Recommendations</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {recommendedActions.slice(0, 3).map((action, index) => (
                  <div key={action.id} className="border-l-4 border-blue-500 pl-4">
                    <h4 className="font-medium">{action.title}</h4>
                    <p className="text-sm text-muted-foreground">{action.description}</p>
                    <p className="text-xs text-blue-600 mt-1">
                      {action.estimatedTime} • {action.expectedBenefit}
                    </p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}
    </div>
  )
}
