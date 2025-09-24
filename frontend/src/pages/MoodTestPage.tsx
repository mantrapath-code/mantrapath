/**
 * Mood Service Test Page
 * Testing AI-powered MantraPath Mood Service integration
 */

import React, { useState, useEffect } from 'react';
import { MoodEntryComponent } from '../components/mood/MoodEntryComponent';
import { SimpleMoodDashboard } from '../components/mood/SimpleMoodDashboard';
import { MoodAnalyticsDashboard } from '../components/mood/MoodAnalyticsDashboard';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Heart, Brain, Zap, Loader2 } from 'lucide-react';
import { MoodServiceClient } from '@/services/moodService';
import { setDevToken, isDevMode } from '@/utils/auth';

const moodService = new MoodServiceClient();

interface EmotionResult {
  top_emotions: Array<{
    emotion: string;
    sentiment: string;
    confidence: number;
    color: string;
  }>;
  primary_emotion: string;
  primary_sentiment: string;
  confidence_score: number;
}

export const MoodTestPage: React.FC = () => {
  const [refreshKey, setRefreshKey] = useState(0);
  const [emotionText, setEmotionText] = useState('');
  const [emotionResult, setEmotionResult] = useState<EmotionResult | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleMoodSaved = (entry: any) => {
    console.log('Mood entry saved:', entry);
    // Trigger refresh of dashboard components
    setRefreshKey(prev => prev + 1);
  };

  const analyzeEmotion = async () => {
    if (!emotionText.trim()) {
      setError('Please enter some text to analyze');
      return;
    }

    setIsAnalyzing(true);
    setError(null);

    try {
      const result = await moodService.analyzeEmotion(emotionText);
      
      setEmotionResult(result as any);
    } catch (err) {
      setError(`Failed to analyze emotion: ${err}`);
      console.error('Error analyzing emotion:', err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case 'positive': return 'bg-green-100 text-green-800';
      case 'negative': return 'bg-red-100 text-red-800';
      case 'ambiguous': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-8">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Mood Service Integration Test
        </h1>
        <p className="text-gray-600">
          Testing the new modular mood service with AI-powered emotion detection
        </p>
      </div>

      {/* Development Utilities */}
      {isDevMode() && (
        <Alert>
          <AlertDescription>
            <div className="flex items-center justify-between">
              <span>Development Mode: Set authentication token for testing</span>
              <Button 
                onClick={() => {
                  setDevToken();
                  setRefreshKey(prev => prev + 1);
                }} 
                size="sm"
              >
                Set Dev Token
              </Button>
            </div>
          </AlertDescription>
        </Alert>
      )}

      {/* Mood Entry Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Heart className="w-6 h-6 text-pink-600" />
            Create Mood Entry
          </CardTitle>
        </CardHeader>
        <CardContent>
          <MoodEntryComponent 
            onMoodSaved={handleMoodSaved}
            showEmotionAnalysis={true}
          />
        </CardContent>
      </Card>

      {/* AI Emotion Analysis Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="w-6 h-6 text-purple-600" />
            AI Emotion Analysis
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {error && (
            <Alert className="border-red-200 bg-red-50">
              <AlertDescription className="text-red-800">{error}</AlertDescription>
            </Alert>
          )}
          
          <div>
            <label className="text-sm font-medium mb-2 block">
              Enter text to analyze emotions:
            </label>
            <Textarea
              value={emotionText}
              onChange={(e) => setEmotionText(e.target.value)}
              placeholder="Type something like: 'I feel amazing today! Everything is going perfectly and I'm so grateful for this opportunity.'"
              rows={3}
              className="w-full"
            />
          </div>

          <Button onClick={analyzeEmotion} disabled={isAnalyzing || !emotionText.trim()}>
            {isAnalyzing ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Zap className="w-4 h-4 mr-2" />}
            Analyze Emotions
          </Button>

          {emotionResult && (
            <div className="space-y-4 p-4 bg-gray-50 rounded-lg">
              <div>
                <p className="text-sm font-medium mb-2">Primary Emotion:</p>
                <Badge className={getSentimentColor(emotionResult.primary_sentiment)}>
                  {emotionResult.primary_emotion} ({emotionResult.confidence_score.toFixed(1)}%)
                </Badge>
              </div>

              <div>
                <p className="text-sm font-medium mb-2">Detected Emotions:</p>
                <div className="flex flex-wrap gap-2">
                  {emotionResult.top_emotions?.map((emotion, index) => (
                    <Badge key={index} className={getSentimentColor(emotion.sentiment)}>
                      {emotion.emotion} ({emotion.confidence.toFixed(1)}%)
                    </Badge>
                  ))}
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Analytics Dashboard */}
      <Card>
        <CardHeader>
          <CardTitle>Mood Analytics Dashboard</CardTitle>
        </CardHeader>
        <CardContent>
          <SimpleMoodDashboard key={refreshKey} />
        </CardContent>
      </Card>

      {/* Advanced Analytics */}
      <Card>
        <CardHeader>
          <CardTitle>Advanced Analytics</CardTitle>
        </CardHeader>
        <CardContent>
          <MoodAnalyticsDashboard key={refreshKey} />
        </CardContent>
      </Card>
    </div>
  );
};