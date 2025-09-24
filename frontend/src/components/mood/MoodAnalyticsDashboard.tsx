/**
 * Fixed Mood Analytics Dashboard
 * Displays mood patterns, insights, and analytics
 */

import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  TrendingUp, 
  TrendingDown, 
  Activity, 
  Calendar,
  RefreshCw,
  Loader2
} from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { moodService } from '../../services/moodService';

interface MoodAnalytics {
  total_entries: number;
  average_mood: number;
  mood_trend: string;
  stress_average?: number;
  energy_average?: number;
  mood_distribution: Record<string, number>;
  recent_patterns: any[];
}

interface MoodAnalyticsDashboardProps {
  className?: string;
}

export const MoodAnalyticsDashboard: React.FC<MoodAnalyticsDashboardProps> = ({
  className = ''
}) => {
  const [analytics, setAnalytics] = useState<MoodAnalytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAnalytics = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const analyticsData = await moodService.getMoodAnalytics(30);
      setAnalytics(analyticsData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load analytics');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAnalytics();
  }, [fetchAnalytics]);

  const getTrendIcon = (trend: string) => {
    switch (trend.toLowerCase()) {
      case 'improving':
        return <TrendingUp className="w-4 h-4 text-green-600" />;
      case 'declining':
        return <TrendingDown className="w-4 h-4 text-red-600" />;
      default:
        return <Activity className="w-4 h-4 text-gray-600" />;
    }
  };

  if (loading) {
    return (
      <div className={`flex justify-center items-center h-64 ${className}`}>
        <Loader2 className="w-8 h-8 animate-spin" />
        <span className="ml-2">Loading analytics...</span>
      </div>
    );
  }

  if (error) {
    return (
      <Alert className={className}>
        <AlertDescription>
          <div className="flex justify-between items-center">
            <span>{error}</span>
            <Button onClick={fetchAnalytics} variant="outline" size="sm">
              <RefreshCw className="w-4 h-4 mr-2" />
              Retry
            </Button>
          </div>
        </AlertDescription>
      </Alert>
    );
  }

  if (!analytics) {
    return <div className={className}>No analytics data available</div>;
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Total Entries</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{analytics.total_entries}</div>
            <p className="text-xs text-muted-foreground">
              Mood tracking sessions
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Average Mood</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {analytics.average_mood.toFixed(1)}
            </div>
            <p className="text-xs text-muted-foreground">
              Out of 10 scale
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Mood Trend</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center">
              {getTrendIcon(analytics.mood_trend)}
              <span className="text-lg font-semibold ml-2 capitalize">
                {analytics.mood_trend}
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Stress Average</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {analytics.stress_average?.toFixed(1) || 'N/A'}
            </div>
            <p className="text-xs text-muted-foreground">
              Lower is better
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Mood Distribution */}
      {analytics.mood_distribution && Object.keys(analytics.mood_distribution).length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Mood Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {Object.entries(analytics.mood_distribution).map(([range, count]) => {
                const maxCount = Math.max(...Object.values(analytics.mood_distribution));
                const percentage = maxCount > 0 ? (count / maxCount) * 100 : 0;
                
                return (
                  <div key={range} className="flex items-center justify-between">
                    <span className="text-sm font-medium min-w-0">{range}</span>
                    <div className="flex items-center gap-3 flex-1 max-w-xs">
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                          style={{ width: `${Math.max(5, percentage)}%` }}
                        />
                      </div>
                      <span className="text-sm text-muted-foreground min-w-0 w-8 text-right">
                        {count}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Refresh Button */}
      <div className="flex justify-center">
        <Button onClick={fetchAnalytics} variant="outline">
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh Analytics
        </Button>
      </div>
    </div>
  );
};