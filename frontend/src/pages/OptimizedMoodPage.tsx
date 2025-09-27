/**
 * Optimized Mood Page - Clean and User-Friendly
 * Single comprehensive mood tracking interface
 */

import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Slider } from '@/components/ui/slider';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Heart, 
  Brain, 
  TrendingUp, 
  TrendingDown, 
  Activity, 
  Zap,
  Target,
  Calendar,
  RefreshCw,
  Loader2,
  CheckCircle,
  AlertCircle,
  Sun,
  Moon,
  Cloud
} from 'lucide-react';
import { moodService, MoodAnalytics } from '../services/moodService';
import { useMoodAnalytics, useEmotionAnalysis } from '@/hooks/useMoodAnalytics';
import { calculateWellness } from '@/utils/wellness';
import { setDevToken, isDevMode } from '../utils/auth';

interface WellnessMetrics {
  overall_score: number;
  mood_stability: number;
  stress_level: number;
  energy_level: number;
  improvement_trend: number;
}

interface MoodTheme {
  name: string;
  colors: {
    primary: string;
    secondary: string;
    background: string;
    text: string;
  };
  icon: React.ReactNode;
}

const getMoodTheme = (averageMood: number): MoodTheme => {
  if (averageMood >= 8) {
    return {
      name: 'Excellent',
      colors: {
        primary: 'bg-gradient-to-r from-green-400 to-emerald-500',
        secondary: 'bg-green-50 border-green-200',
        background: 'bg-green-50',
        text: 'text-green-800'
      },
      icon: <Sun className="w-5 h-5 text-yellow-500" />
    };
  } else if (averageMood >= 6) {
    return {
      name: 'Good',
      colors: {
        primary: 'bg-gradient-to-r from-blue-400 to-cyan-500',
        secondary: 'bg-blue-50 border-blue-200',
        background: 'bg-blue-50',
        text: 'text-blue-800'
      },
      icon: <Cloud className="w-5 h-5 text-blue-500" />
    };
  } else if (averageMood >= 4) {
    return {
      name: 'Moderate',
      colors: {
        primary: 'bg-gradient-to-r from-yellow-400 to-orange-500',
        secondary: 'bg-yellow-50 border-yellow-200',
        background: 'bg-yellow-50',
        text: 'text-yellow-800'
      },
      icon: <Cloud className="w-5 h-5 text-yellow-600" />
    };
  } else {
    return {
      name: 'Needs Attention',
      colors: {
        primary: 'bg-gradient-to-r from-red-400 to-pink-500',
        secondary: 'bg-red-50 border-red-200',
        background: 'bg-red-50',
        text: 'text-red-800'
      },
      icon: <Moon className="w-5 h-5 text-gray-500" />
    };
  }
};

const calculateWellnessScore = (analytics: MoodAnalytics | null): WellnessMetrics => {
  if (!analytics || analytics.total_entries === 0) {
    return {
      overall_score: 0,
      mood_stability: 0,
      stress_level: 10,
      energy_level: 0,
      improvement_trend: 0
    };
  }

  // Calculate mood stability (less variation = higher stability)
  const moodVariation = Object.keys(analytics.mood_distribution).length;
  const moodStability = Math.max(0, 100 - (moodVariation * 10));

  // Convert stress to inverted scale (lower stress = higher wellness)
  const stressLevel = analytics.stress_average || 5;
  const stressWellness = Math.max(0, 100 - (stressLevel * 10));

  // Energy contribution
  const energyLevel = (analytics.energy_average || 5) * 10;

  // Mood contribution (scaled to 0-100)
  const moodContribution = (analytics.average_mood / 10) * 100;

  // Trend bonus/penalty
  let trendMultiplier = 1;
  if (analytics.mood_trend === 'improving') trendMultiplier = 1.1;
  if (analytics.mood_trend === 'declining') trendMultiplier = 0.9;

  // Overall wellness score
  const overallScore = Math.min(100, Math.max(0, 
    (moodContribution * 0.4 + stressWellness * 0.3 + energyLevel * 0.2 + moodStability * 0.1) * trendMultiplier
  ));

  return {
    overall_score: Math.round(overallScore),
    mood_stability: Math.round(moodStability),
    stress_level: Math.round(stressLevel),
    energy_level: Math.round(energyLevel),
    improvement_trend: analytics.improvement_trend || 0
  };
};

export const OptimizedMoodPage: React.FC = () => {
  const { analytics, loading, error, refresh } = useMoodAnalytics({ days: 30, autoFetch: true });
  const [wellnessMetrics, setWellnessMetrics] = useState<WellnessMetrics | null>(null);
  const [currentTheme, setCurrentTheme] = useState<MoodTheme | null>(null);
  
  // Mood entry form state
  const [moodScore, setMoodScore] = useState([5]);
  const [stressLevel, setStressLevel] = useState([5]);
  const [energyLevel, setEnergyLevel] = useState([5]);
  const [description, setDescription] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);

  // Emotion analysis hook
  const { result: emotionResult, loading: analyzingEmotion, error: emotionError, analyze } = useEmotionAnalysis();

  const submitMoodEntry = async () => {
    try {
      setSubmitting(true);
      // Save entry first (description optional) then refresh
      
      await moodService.createMoodEntry({
        mood_score: moodScore[0],
        stress_level: stressLevel[0],
        energy_level: energyLevel[0],
        description: description.trim() || undefined
      });
      
      setSuccess(true);
      setDescription('');
      
      // Refresh analytics
      setTimeout(() => {
        refresh();
        setSuccess(false);
      }, 1500);
      
    } catch (err) {
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

  // Recompute wellness + theme when analytics change
  useEffect(() => {
    if (analytics) {
      const wellness = calculateWellnessScore(analytics);
      setWellnessMetrics(wellness);
      setCurrentTheme(getMoodTheme(analytics.average_mood || 0));
    }
  }, [analytics]);

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="flex justify-center items-center h-64">
          <Loader2 className="w-8 h-8 animate-spin" />
          <span className="ml-2">Loading your mood dashboard...</span>
        </div>
      </div>
    );
  }

  const theme = currentTheme || getMoodTheme(5);

  return (
    <div className={`max-w-4xl mx-auto p-6 space-y-6 ${theme.colors.background} min-h-screen`}>
      {/* Header */}
      <div className="text-center mb-8">
        <div className="flex items-center justify-center gap-3 mb-4">
          {theme.icon}
          <h1 className={`text-3xl font-bold ${theme.colors.text}`}>
            Your Mood Journey
          </h1>
          {theme.icon}
        </div>
        <p className={`text-lg ${theme.colors.text} opacity-80`}>
          Mood Status: <span className="font-semibold">{theme.name}</span>
        </p>
      </div>

      {/* Development Mode Alert */}
      {isDevMode() && (
        <Alert>
          <AlertDescription>
            <div className="flex items-center justify-between">
              <span>Development Mode: Set authentication token for testing</span>
              <Button 
                onClick={() => {
                  setDevToken();
                  refresh();
                }} 
                size="sm"
              >
                Set Dev Token
              </Button>
            </div>
          </AlertDescription>
        </Alert>
      )}

      {error && (
        <Alert className="border-red-200 bg-red-50">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription className="text-red-800">{error}</AlertDescription>
        </Alert>
      )}

      {success && (
        <Alert className="border-green-200 bg-green-50">
          <CheckCircle className="h-4 w-4" />
          <AlertDescription className="text-green-800">
            Mood entry saved successfully! Analytics updated.
          </AlertDescription>
        </Alert>
      )}

      {/* Wellness Score Dashboard */}
      {wellnessMetrics && (
        <Card className={`${theme.colors.secondary} shadow-lg`}>
          <CardHeader>
            <CardTitle className={`flex items-center gap-2 ${theme.colors.text}`}>
              <Target className="w-6 h-6" />
              Wellness Overview
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
              <div className="text-center">
                <div className={`text-3xl font-bold ${theme.colors.text}`}>
                  {wellnessMetrics.overall_score}%
                </div>
                <div className="text-sm opacity-70">Overall Wellness</div>
                <Progress value={wellnessMetrics.overall_score} className="mt-2" />
              </div>
              
              <div className="text-center">
                <div className={`text-2xl font-semibold ${theme.colors.text}`}>
                  {analytics?.average_mood.toFixed(1)}/10
                </div>
                <div className="text-sm opacity-70">Average Mood</div>
                <Progress value={(analytics?.average_mood || 0) * 10} className="mt-2" />
              </div>
              
              <div className="text-center">
                <div className={`text-2xl font-semibold ${theme.colors.text}`}>
                  {10 - wellnessMetrics.stress_level}/10
                </div>
                <div className="text-sm opacity-70">Stress Management</div>
                <Progress value={(10 - wellnessMetrics.stress_level) * 10} className="mt-2" />
              </div>
              
              <div className="text-center">
                <div className={`text-2xl font-semibold ${theme.colors.text}`}>
                  {wellnessMetrics.energy_level/10}/10
                </div>
                <div className="text-sm opacity-70">Energy Level</div>
                <Progress value={wellnessMetrics.energy_level} className="mt-2" />
              </div>
            </div>

            {/* Quick Stats */}
            <div className="flex justify-between items-center text-sm opacity-70">
              <span>Total Entries: {analytics?.total_entries || 0}</span>
              <span className="flex items-center gap-1">
                {analytics?.mood_trend === 'improving' && <TrendingUp className="w-4 h-4 text-green-600" />}
                {analytics?.mood_trend === 'declining' && <TrendingDown className="w-4 h-4 text-red-600" />}
                {analytics?.mood_trend === 'stable' && <Activity className="w-4 h-4 text-gray-600" />}
                Trend: {analytics?.mood_trend || 'Unknown'}
              </span>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Quick Mood Entry + Optional Emotion Analysis */}
      <Card className={`${theme.colors.secondary} shadow-lg`}>
        <CardHeader>
          <CardTitle className={`flex items-center gap-2 ${theme.colors.text}`}>
            <Heart className="w-6 h-6" />
            How are you feeling today?
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Mood Score */}
          <div>
            <div className="flex justify-between items-center mb-3">
              <label className={`text-sm font-medium ${theme.colors.text}`}>
                Mood Score
              </label>
              <Badge variant="outline" className={theme.colors.text}>
                {moodScore[0]}/10
              </Badge>
            </div>
            <Slider
              value={moodScore}
              onValueChange={setMoodScore}
              max={10}
              min={1}
              step={1}
              className="w-full"
            />
            <div className="flex justify-between text-xs opacity-60 mt-1">
              <span>Very Low</span>
              <span>Excellent</span>
            </div>
          </div>

          {/* Stress Level */}
          <div>
            <div className="flex justify-between items-center mb-3">
              <label className={`text-sm font-medium ${theme.colors.text}`}>
                Stress Level
              </label>
              <Badge variant="outline" className={theme.colors.text}>
                {stressLevel[0]}/10
              </Badge>
            </div>
            <Slider
              value={stressLevel}
              onValueChange={setStressLevel}
              max={10}
              min={1}
              step={1}
              className="w-full"
            />
            <div className="flex justify-between text-xs opacity-60 mt-1">
              <span>Very Relaxed</span>
              <span>Very Stressed</span>
            </div>
          </div>

          {/* Energy Level */}
          <div>
            <div className="flex justify-between items-center mb-3">
              <label className={`text-sm font-medium ${theme.colors.text}`}>
                Energy Level
              </label>
              <Badge variant="outline" className={theme.colors.text}>
                {energyLevel[0]}/10
              </Badge>
            </div>
            <Slider
              value={energyLevel}
              onValueChange={setEnergyLevel}
              max={10}
              min={1}
              step={1}
              className="w-full"
            />
            <div className="flex justify-between text-xs opacity-60 mt-1">
              <span>Very Tired</span>
              <span>Very Energetic</span>
            </div>
          </div>

          {/* Optional Description */}
          <div>
            <label className={`text-sm font-medium ${theme.colors.text} block mb-2`}>
              What's on your mind? (Optional)
            </label>
            <Textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Share your thoughts, feelings, or what happened today..."
              rows={3}
            />
          </div>

          {/* Emotion Analysis (inline) */}
          <div className="space-y-3">
            <Button
              type="button"
              variant="outline"
              disabled={analyzingEmotion || !description.trim()}
              onClick={() => analyze(description, false)}
              className="w-full"
            >
              {analyzingEmotion ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Zap className="w-4 h-4 mr-2" />}
              {analyzingEmotion ? 'Analyzing...' : 'Analyze Emotions'}
            </Button>
            {emotionError && <p className="text-xs text-red-600">{emotionError}</p>}
            {emotionResult && (
              <div className="bg-white/60 rounded-md p-3 border space-y-2">
                <p className="text-xs font-medium">Primary Emotion: <span className="font-semibold">{emotionResult.primary_emotion}</span> ({emotionResult.primary_sentiment})</p>
                <div className="flex flex-wrap gap-2">
                  {emotionResult.top_emotions.slice(0,4).map(e => (
                    <Badge key={e.emotion} variant="outline" className="text-xs">
                      {e.emotion} {e.confidence.toFixed(1)}%
                    </Badge>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Submit Button */}
          <Button
            onClick={submitMoodEntry}
            disabled={submitting}
            className={`w-full ${theme.colors.primary} text-white hover:opacity-90`}
          >
            {submitting ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin mr-2" />
                Saving...
              </>
            ) : (
              <>
                <Heart className="w-4 h-4 mr-2" />
                Save Mood Entry
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Mood Pattern Insights */}
      {analytics && analytics.mood_distribution && Object.keys(analytics.mood_distribution).length > 0 && (
        <Card className={`${theme.colors.secondary} shadow-lg`}>
          <CardHeader>
            <CardTitle className={`flex items-center gap-2 ${theme.colors.text}`}>
              <Brain className="w-6 h-6" />
              Your Mood Patterns
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {Object.entries(analytics.mood_distribution)
                .sort((a, b) => b[1] - a[1])
                .map(([range, count]) => {
                  const maxCount = Math.max(...Object.values(analytics.mood_distribution));
                  const percentage = maxCount > 0 ? (count / maxCount) * 100 : 0;
                  
                  return (
                    <div key={range} className="flex items-center justify-between">
                      <span className={`text-sm font-medium ${theme.colors.text}`}>{range}</span>
                      <div className="flex items-center gap-3 flex-1 max-w-xs">
                        <div className="w-full bg-gray-200 rounded-full h-3">
                          <div 
                            className={`h-3 rounded-full transition-all duration-300 ${theme.colors.primary}`}
                            style={{ width: `${Math.max(5, percentage)}%` }}
                          />
                        </div>
                        <span className={`text-sm ${theme.colors.text} opacity-70 min-w-0 w-8 text-right`}>
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

      {/* Footer Actions */}
      <div className="flex justify-center space-x-4">
        <Button onClick={refresh} variant="outline" className={theme.colors.text}>
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh Data
        </Button>
        <Button variant="outline" className={theme.colors.text}>
          <Calendar className="w-4 h-4 mr-2" />
          View History
        </Button>
      </div>
    </div>
  );
};

export default OptimizedMoodPage;