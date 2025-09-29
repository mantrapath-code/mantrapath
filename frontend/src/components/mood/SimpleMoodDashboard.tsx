/**
 * Simple Mood Analytics Dashboard for testing integration
 */

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Loader2, TrendingUp, Activity, RefreshCw } from 'lucide-react';
import { moodService, MoodAnalytics } from '../../services/moodService';

interface MoodAnalyticsDashboardProps {
  className?: string;
}

export const SimpleMoodDashboard: React.FC<MoodAnalyticsDashboardProps> = ({
  className = ''
}) => {
  const [analytics, setAnalytics] = useState<MoodAnalytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await moodService.getMoodAnalytics(30);
      setAnalytics(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load analytics');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <Loader2 className="w-8 h-8 animate-spin" />
        <span className="ml-2">Loading analytics...</span>
      </div>
    );
  }

  if (error) {
    return (
      <Card className={className}>
        <CardContent className="pt-6">
          <div className="text-center">
            <p className="text-red-600 mb-4">{error}</p>
            <Button onClick={fetchAnalytics} variant="outline">
              <RefreshCw className="w-4 h-4 mr-2" />
              Try Again
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className={`space-y-6 ${className}`}>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Total Entries */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="w-5 h-5 text-blue-600" />
              Total Entries
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{analytics?.total_entries || 0}</div>
            <p className="text-sm text-muted-foreground mt-1">
              Mood tracking sessions
            </p>
          </CardContent>
        </Card>

        {/* Average Mood */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-green-600" />
              Average Mood
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              {analytics?.average_mood?.toFixed(1) || '0.0'}
            </div>
            <p className="text-sm text-muted-foreground mt-1">
              Out of 10 scale
            </p>
          </CardContent>
        </Card>

        {/* Mood Trend */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="w-5 h-5 text-purple-600" />
              Trend
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold capitalize">
              {analytics?.mood_trend || 'Unknown'}
            </div>
            <p className="text-sm text-muted-foreground mt-1">
              Recent pattern
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Mood Distribution */}
      {analytics?.mood_distribution && Object.keys(analytics.mood_distribution).length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Mood Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {Object.entries(analytics.mood_distribution).map(([range, count]) => (
                <div key={range} className="flex justify-between items-center">
                  <span className="text-sm">{range}</span>
                  <div className="flex items-center gap-2">
                    <div 
                      className="bg-blue-500 h-2 rounded"
                      style={{ 
                        width: `${Math.max(10, (count / Math.max(...Object.values(analytics.mood_distribution))) * 100)}px` 
                      }}
                    />
                    <span className="text-sm text-muted-foreground w-8">{count}</span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Refresh Button */}
      <div className="flex justify-center">
        <Button onClick={fetchAnalytics} variant="outline">
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh Data
        </Button>
      </div>
    </div>
  );
};