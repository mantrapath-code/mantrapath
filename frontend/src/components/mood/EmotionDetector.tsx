/**
 * AI-Powered Emotion Detection Component
 * Integrates with the modular mood service for real-time emotion analysis
 */

import React, { useState, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Loader2, Heart, Brain, AlertCircle, Lightbulb } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';

interface EmotionAnalysis {
  emotion: string;
  sentiment: 'positive' | 'negative' | 'neutral' | 'ambiguous';
  confidence: number;
  color: string;
}

interface MoodAnalysisResult {
  top_emotions: EmotionAnalysis[];
  primary_emotion: string;
  primary_sentiment: string;
  confidence_score: number;
}

interface EmotionDetectorProps {
  onMoodEntry?: (data: any) => void;
  className?: string;
}

export const EmotionDetector: React.FC<EmotionDetectorProps> = ({ 
  onMoodEntry, 
  className = '' 
}) => {
  const [text, setText] = useState('');
  const [analysis, setAnalysis] = useState<MoodAnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const analyzeEmotion = useCallback(async () => {
    if (!text.trim()) {
      setError('Please enter some text to analyze');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/v1/mood/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          text: text.trim(),
          include_mood_entry: false
        })
      });

      if (!response.ok) {
        throw new Error(`Analysis failed: ${response.statusText}`);
      }

      const result = await response.json();
      setAnalysis(result);
      
      // Callback for parent component
      if (onMoodEntry) {
        onMoodEntry(result);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed');
    } finally {
      setLoading(false);
    }
  }, [text, onMoodEntry]);

  const getSentimentIcon = (sentiment: string) => {
    switch (sentiment) {
      case 'positive': return <Heart className="w-4 h-4" />;
      case 'negative': return <AlertCircle className="w-4 h-4" />;
      case 'ambiguous': return <Lightbulb className="w-4 h-4" />;
      default: return <Brain className="w-4 h-4" />;
    }
  };

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case 'positive': return 'bg-green-100 text-green-800 border-green-200';
      case 'negative': return 'bg-red-100 text-red-800 border-red-200';
      case 'ambiguous': return 'bg-orange-100 text-orange-800 border-orange-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  return (
    <Card className={`w-full max-w-4xl mx-auto ${className}`}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Brain className="w-5 h-5 text-blue-600" />
          AI Emotion Detection
        </CardTitle>
        <p className="text-sm text-gray-600">
          Analyze emotions in your text with advanced AI
        </p>
      </CardHeader>
      
      <CardContent className="space-y-6">
        {/* Input Section */}
        <div className="space-y-3">
          <Textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Enter your text here to analyze emotions..."
            className="min-h-[120px] resize-y"
            maxLength={1000}
          />
          
          <div className="flex justify-between items-center">
            <span className="text-xs text-gray-500">
              {text.length}/1000 characters
            </span>
            
            <Button 
              onClick={analyzeEmotion}
              disabled={loading || !text.trim()}
              className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Analyzing...
                </>
              ) : (
                'Analyze Emotions'
              )}
            </Button>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <Alert className="border-red-200 bg-red-50">
            <AlertCircle className="h-4 w-4 text-red-600" />
            <AlertDescription className="text-red-800">
              {error}
            </AlertDescription>
          </Alert>
        )}

        {/* Results Display */}
        {analysis && (
          <div className="space-y-6">
            {/* Primary Result */}
            <div 
              className="text-center p-6 rounded-xl text-white font-semibold text-lg"
              style={{ backgroundColor: analysis.top_emotions[0]?.color || '#6b7280' }}
            >
              Primary Emotion: {analysis.primary_emotion.toUpperCase()} ({analysis.primary_sentiment})
            </div>

            {/* Emotion Visualization Bar */}
            <div className="space-y-3">
              <h3 className="font-semibold text-gray-700 flex items-center gap-2">
                <Brain className="w-4 h-4" />
                Emotion Analysis
              </h3>
              
              <div className="relative h-20 bg-gray-100 rounded-lg overflow-hidden">
                {/* Emotion dots positioned on the bar */}
                {analysis.top_emotions.map((emotion, index) => {
                  // Position emotions proportionally across the bar
                  const position = (index + 1) * (100 / (analysis.top_emotions.length + 1));
                  
                  return (
                    <div
                      key={emotion.emotion}
                      className="absolute top-1/2 transform -translate-y-1/2 -translate-x-1/2 group cursor-pointer"
                      style={{ 
                        left: `${position}%`,
                        backgroundColor: emotion.color 
                      }}
                    >
                      <div 
                        className="w-12 h-12 rounded-full flex items-center justify-center text-white font-bold text-xs border-2 border-white shadow-lg transition-transform group-hover:scale-125"
                        style={{ backgroundColor: emotion.color }}
                      >
                        {emotion.emotion.substring(0, 2).toUpperCase()}
                      </div>
                      
                      {/* Tooltip */}
                      <div className="absolute bottom-14 left-1/2 transform -translate-x-1/2 opacity-0 group-hover:opacity-100 transition-opacity">
                        <div className="bg-black text-white p-2 rounded text-xs whitespace-nowrap">
                          <div className="font-semibold">{emotion.emotion.toUpperCase()}</div>
                          <div>Sentiment: {emotion.sentiment.toUpperCase()}</div>
                          <div>Confidence: {emotion.confidence}%</div>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Emotion Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {analysis.top_emotions.map((emotion) => (
                <Card 
                  key={emotion.emotion} 
                  className="hover:shadow-lg transition-shadow"
                  style={{ borderLeftColor: emotion.color, borderLeftWidth: '4px' }}
                >
                  <CardContent className="p-4 text-center">
                    <div className="flex items-center justify-center mb-2">
                      {getSentimentIcon(emotion.sentiment)}
                    </div>
                    
                    <h4 className="font-semibold text-lg capitalize mb-1">
                      {emotion.emotion}
                    </h4>
                    
                    <Badge 
                      className={`mb-3 ${getSentimentColor(emotion.sentiment)}`}
                      variant="outline"
                    >
                      {emotion.sentiment}
                    </Badge>
                    
                    <div className="text-2xl font-bold text-gray-800">
                      {emotion.confidence}%
                    </div>
                    <div className="text-xs text-gray-500">
                      confidence
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* Analysis Summary */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h4 className="font-semibold text-blue-800 mb-2">Analysis Summary</h4>
              <p className="text-sm text-blue-700">
                Your text shows a primary emotion of <strong>{analysis.primary_emotion}</strong> with {' '}
                <strong>{analysis.primary_sentiment}</strong> sentiment. The AI model is {' '}
                <strong>{Math.round(analysis.confidence_score)}%</strong> confident in this analysis.
              </p>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default EmotionDetector;