import React, { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { useRealtimeInsights, useMoodInsights, useJournalInsights, useChallengeInsights } from '@/hooks/useRealtimeInsights'
import { useComprehensiveInsights } from '@/hooks/useComprehensiveInsights'
import { Separator } from '@/components/ui/separator'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

/**
 * E4 Real-Time Testing Component
 * This component allows testing the real-time insight pipeline
 */
export function RealtimeInsightsTest() {
  const { insights, isConnected, connectionError, updateInsightsFromDelta } = useRealtimeInsights()
  const moodInsights = useMoodInsights()
  const journalInsights = useJournalInsights()
  const challengeInsights = useChallengeInsights()
  const comprehensiveInsights = useComprehensiveInsights()
  
  const [testMoodScore, setTestMoodScore] = useState(7)
  const [testSentiment, setTestSentiment] = useState('positive')
  const [testStreakCount, setTestStreakCount] = useState(5)

  const handleTestMoodDelta = () => {
    updateInsightsFromDelta({
      type: 'mood_update',
      timestamp: new Date().toISOString(),
      changes: {
        latest_mood: testMoodScore,
        days_tracked_increment: 1,
        mood_streak: insights.moodStreak + 1
      }
    })
  }

  const handleTestJournalDelta = () => {
    updateInsightsFromDelta({
      type: 'journal_update',
      timestamp: new Date().toISOString(),
      changes: {
        journal_entries_increment: 1,
        latest_sentiment: testSentiment,
        sentiment_score: testSentiment === 'positive' ? 0.8 : testSentiment === 'negative' ? -0.6 : 0.1
      }
    })
  }

  const handleTestChallengeDelta = () => {
    updateInsightsFromDelta({
      type: 'challenge_update',
      timestamp: new Date().toISOString(),
      changes: {
        challenge_completed: true,
        streak_count: testStreakCount,
        engagement_increment: 1
      }
    })
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">E4 Real-Time Insights Testing</h2>
        <div className="flex items-center gap-2">
          <Badge variant={isConnected ? "default" : "destructive"}>
            {isConnected ? "Connected" : "Disconnected"}
          </Badge>
          {connectionError && (
            <Badge variant="outline" className="text-red-600">
              {connectionError}
            </Badge>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {/* Current Real-time Insights */}
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Real-time Insights</CardTitle>
            <CardDescription>Live updates from WebSocket</CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="flex justify-between">
              <span className="text-sm">Days Tracked:</span>
              <Badge variant="outline">{insights.daysTracked}</Badge>
            </div>
            <div className="flex justify-between">
              <span className="text-sm">Mood Streak:</span>
              <Badge variant="outline">{insights.moodStreak}</Badge>
            </div>
            <div className="flex justify-between">
              <span className="text-sm">Journal Entries:</span>
              <Badge variant="outline">{insights.journalEntries}</Badge>
            </div>
            <div className="flex justify-between">
              <span className="text-sm">Latest Mood:</span>
              <Badge variant="outline">{insights.latestMood || 'N/A'}</Badge>
            </div>
            <div className="flex justify-between">
              <span className="text-sm">Challenge Streak:</span>
              <Badge variant="outline">{insights.challengeStreak}</Badge>
            </div>
            <div className="flex justify-between">
              <span className="text-sm">Engagement:</span>
              <Badge variant="outline">{insights.engagementLevel}</Badge>
            </div>
            {insights.lastUpdated && (
              <div className="text-xs text-muted-foreground mt-2">
                Last updated: {new Date(insights.lastUpdated).toLocaleTimeString()}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Test Controls */}
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Test Delta Updates</CardTitle>
            <CardDescription>Simulate real-time events</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="mood-score">Mood Score</Label>
              <Input
                id="mood-score"
                type="number"
                min="1"
                max="10"
                value={testMoodScore}
                onChange={(e) => setTestMoodScore(parseInt(e.target.value))}
              />
              <Button onClick={handleTestMoodDelta} size="sm" className="w-full">
                Test Mood Update
              </Button>
            </div>

            <Separator />

            <div className="space-y-2">
              <Label htmlFor="sentiment">Sentiment</Label>
              <select
                id="sentiment"
                value={testSentiment}
                onChange={(e) => setTestSentiment(e.target.value)}
                className="w-full p-2 border border-input rounded-md"
              >
                <option value="positive">Positive</option>
                <option value="neutral">Neutral</option>
                <option value="negative">Negative</option>
              </select>
              <Button onClick={handleTestJournalDelta} size="sm" className="w-full">
                Test Journal Update
              </Button>
            </div>

            <Separator />

            <div className="space-y-2">
              <Label htmlFor="streak-count">Challenge Streak</Label>
              <Input
                id="streak-count"
                type="number"
                min="0"
                value={testStreakCount}
                onChange={(e) => setTestStreakCount(parseInt(e.target.value))}
              />
              <Button onClick={handleTestChallengeDelta} size="sm" className="w-full">
                Test Challenge Update
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Comprehensive Insights Status */}
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Comprehensive Insights</CardTitle>
            <CardDescription>Backend vs Real-time comparison</CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="flex justify-between">
              <span className="text-sm">Loading:</span>
              <Badge variant={comprehensiveInsights.loading ? "default" : "outline"}>
                {comprehensiveInsights.loading ? "Yes" : "No"}
              </Badge>
            </div>
            <div className="flex justify-between">
              <span className="text-sm">Using Unified:</span>
              <Badge variant={comprehensiveInsights.isUsingUnifiedEndpoint ? "default" : "secondary"}>
                {comprehensiveInsights.isUsingUnifiedEndpoint ? "Yes" : "Legacy"}
              </Badge>
            </div>
            <div className="flex justify-between">
              <span className="text-sm">RT Connected:</span>
              <Badge variant={comprehensiveInsights.isRealtimeConnected ? "default" : "destructive"}>
                {comprehensiveInsights.isRealtimeConnected ? "Yes" : "No"}
              </Badge>
            </div>
            {comprehensiveInsights.insights?.dashboard?.weeklySummary && (
              <>
                <Separator />
                <div className="flex justify-between">
                  <span className="text-sm">Backend Days:</span>
                  <Badge variant="outline">
                    {comprehensiveInsights.insights.dashboard.weeklySummary.daysTracked}
                  </Badge>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm">Backend Mood:</span>
                  <Badge variant="outline">
                    {comprehensiveInsights.insights.dashboard.currentStatus?.moodScore || 'N/A'}
                  </Badge>
                </div>
              </>
            )}
            <div className="text-xs text-muted-foreground mt-2">
              Last backend update: {comprehensiveInsights.lastUpdated?.toLocaleTimeString() || 'Never'}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Additional Test Info */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm">Real-time Pipeline Status</CardTitle>
          <CardDescription>E4 Implementation verification</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-lg font-semibold">{isConnected ? '✅' : '❌'}</div>
              <div className="text-xs">WebSocket</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-semibold">{insights.lastUpdated ? '✅' : '⏳'}</div>
              <div className="text-xs">Deltas Received</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-semibold">{comprehensiveInsights.isUsingUnifiedEndpoint ? '✅' : '⚠️'}</div>
              <div className="text-xs">Unified Backend</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-semibold">{comprehensiveInsights.realtimeInsights ? '✅' : '❌'}</div>
              <div className="text-xs">RT Integration</div>
            </div>
          </div>
          
          {comprehensiveInsights.error && (
            <div className="mt-4 p-2 bg-destructive/10 border border-destructive/20 rounded-md">
              <div className="text-sm text-destructive">Error: {comprehensiveInsights.error}</div>
            </div>
          )}
          
          {comprehensiveInsights.realtimeError && (
            <div className="mt-4 p-2 bg-orange-50 border border-orange-200 rounded-md">
              <div className="text-sm text-orange-600">Real-time Error: {comprehensiveInsights.realtimeError}</div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
