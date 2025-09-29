/**
 * Enhanced Mood Entry Component
 * Integrates with the new modular mood service API
 */

import React, { useState, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Slider } from '@/components/ui/slider';
import { Label } from '@/components/ui/label';
import { 
  Heart, 
  MapPin, 
  Activity, 
  Tag, 
  Loader2, 
  CheckCircle,
  AlertCircle 
} from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { EmotionDetector } from './EmotionDetector';
import { moodService, MoodEntry } from '../../services/moodService';

interface MoodEntryData {
  mood_score: number;
  description?: string;
  location?: string;
  activity?: string;
  context_tags?: string[];
}

interface MoodEntryComponentProps {
  onMoodSaved?: (entry: any) => void;
  className?: string;
  showEmotionAnalysis?: boolean;
}

export const MoodEntryComponent: React.FC<MoodEntryComponentProps> = ({
  onMoodSaved,
  className = '',
  showEmotionAnalysis = true
}) => {
  const [moodData, setMoodData] = useState<MoodEntryData>({
    mood_score: 5,
    description: '',
    location: '',
    activity: '',
    context_tags: []
  });
  
  const [newTag, setNewTag] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const moodLabels = {
    1: 'Very Low',
    2: 'Low', 
    3: 'Poor',
    4: 'Below Average',
    5: 'Neutral',
    6: 'Good',
    7: 'Very Good',
    8: 'Great',
    9: 'Excellent',
    10: 'Amazing'
  };

  const getMoodColor = (score: number) => {
    if (score <= 3) return 'text-red-600';
    if (score <= 5) return 'text-orange-500';
    if (score <= 7) return 'text-yellow-500';
    return 'text-green-600';
  };

  const addTag = useCallback(() => {
    if (newTag.trim() && !moodData.context_tags?.includes(newTag.trim())) {
      setMoodData(prev => ({
        ...prev,
        context_tags: [...(prev.context_tags || []), newTag.trim()]
      }));
      setNewTag('');
    }
  }, [newTag, moodData.context_tags]);

  const removeTag = useCallback((tagToRemove: string) => {
    setMoodData(prev => ({
      ...prev,
      context_tags: prev.context_tags?.filter(tag => tag !== tagToRemove) || []
    }));
  }, []);

  const handleSaveMood = async () => {
    if (!moodData.mood_score) {
      setError('Please select a mood score');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const payload = {
        mood_score: moodData.mood_score,
        description: moodData.description || undefined,
        location: moodData.location || undefined,
        activity: moodData.activity || undefined,
        tags: moodData.context_tags?.length ? moodData.context_tags : undefined
      };

      const savedEntry = await moodService.createMoodEntry(payload);
      setSuccess(true);
      
      // Reset form
      setMoodData({
        mood_score: 5,
        description: '',
        location: '',
        activity: '',
        context_tags: []
      });

      // Notify parent component
      if (onMoodSaved) {
        onMoodSaved(savedEntry);
      }

      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save mood entry');
    } finally {
      setLoading(false);
    }
  };

  const handleEmotionAnalysis = useCallback((analysis: any) => {
    // Auto-fill description if empty
    if (!moodData.description && analysis.primary_emotion) {
      setMoodData(prev => ({
        ...prev,
        description: `Feeling ${analysis.primary_emotion} with ${analysis.primary_sentiment} sentiment`
      }));
    }
  }, [moodData.description]);

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Mood Entry Form */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Heart className="w-5 h-5 text-pink-600" />
            Track Your Mood
          </CardTitle>
          <p className="text-sm text-gray-600">
            Record how you're feeling and add context
          </p>
        </CardHeader>
        
        <CardContent className="space-y-6">
          {/* Mood Score Slider */}
          <div className="space-y-3">
            <Label className="text-base font-medium">How are you feeling?</Label>
            <div className="px-3">
              <Slider
                value={[moodData.mood_score]}
                onValueChange={(value) => setMoodData(prev => ({ ...prev, mood_score: value[0] }))}
                max={10}
                min={1}
                step={1}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-2">
                <span>1</span>
                <span>5</span>
                <span>10</span>
              </div>
            </div>
            <div className="text-center">
              <span className={`text-2xl font-bold ${getMoodColor(moodData.mood_score)}`}>
                {moodData.mood_score}/10
              </span>
              <div className="text-sm text-gray-600 mt-1">
                {moodLabels[moodData.mood_score as keyof typeof moodLabels]}
              </div>
            </div>
          </div>

          {/* Description */}
          <div className="space-y-2">
            <Label htmlFor="description">Description (Optional)</Label>
            <Textarea
              id="description"
              value={moodData.description}
              onChange={(e) => setMoodData(prev => ({ ...prev, description: e.target.value }))}
              placeholder="How are you feeling? What's on your mind?"
              className="min-h-[80px]"
              maxLength={1000}
            />
            <div className="text-xs text-gray-500 text-right">
              {moodData.description?.length || 0}/1000
            </div>
          </div>

          {/* Location and Activity */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="location" className="flex items-center gap-1">
                <MapPin className="w-4 h-4" />
                Location
              </Label>
              <Input
                id="location"
                value={moodData.location}
                onChange={(e) => setMoodData(prev => ({ ...prev, location: e.target.value }))}
                placeholder="Where are you?"
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="activity" className="flex items-center gap-1">
                <Activity className="w-4 h-4" />
                Activity
              </Label>
              <Input
                id="activity"
                value={moodData.activity}
                onChange={(e) => setMoodData(prev => ({ ...prev, activity: e.target.value }))}
                placeholder="What are you doing?"
              />
            </div>
          </div>

          {/* Tags */}
          <div className="space-y-3">
            <Label className="flex items-center gap-1">
              <Tag className="w-4 h-4" />
              Context Tags
            </Label>
            
            <div className="flex gap-2">
              <Input
                value={newTag}
                onChange={(e) => setNewTag(e.target.value)}
                placeholder="Add a tag..."
                onKeyPress={(e) => e.key === 'Enter' && addTag()}
              />
              <Button type="button" onClick={addTag} variant="outline">
                Add
              </Button>
            </div>
            
            {moodData.context_tags && moodData.context_tags.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {moodData.context_tags.map((tag) => (
                  <Badge 
                    key={tag} 
                    variant="secondary" 
                    className="cursor-pointer hover:bg-gray-200"
                    onClick={() => removeTag(tag)}
                  >
                    {tag} ×
                  </Badge>
                ))}
              </div>
            )}
          </div>

          {/* Success/Error Messages */}
          {success && (
            <Alert className="border-green-200 bg-green-50">
              <CheckCircle className="h-4 w-4 text-green-600" />
              <AlertDescription className="text-green-800">
                Mood entry saved successfully!
              </AlertDescription>
            </Alert>
          )}

          {error && (
            <Alert className="border-red-200 bg-red-50">
              <AlertCircle className="h-4 w-4 text-red-600" />
              <AlertDescription className="text-red-800">
                {error}
              </AlertDescription>
            </Alert>
          )}

          {/* Save Button */}
          <Button 
            onClick={handleSaveMood}
            disabled={loading}
            className="w-full bg-gradient-to-r from-pink-600 to-purple-600 hover:from-pink-700 hover:to-purple-700"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Saving...
              </>
            ) : (
              'Save Mood Entry'
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Emotion Detection */}
      {showEmotionAnalysis && (
        <EmotionDetector onMoodEntry={handleEmotionAnalysis} />
      )}
    </div>
  );
};

export default MoodEntryComponent;