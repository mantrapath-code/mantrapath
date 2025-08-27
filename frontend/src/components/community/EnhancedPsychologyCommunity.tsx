/**
 * Enhanced Community Component with Psychology-Based Design
 * Unified community management with calming colors and supportive interactions
 */

import React, { useState, useEffect, useMemo } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Separator } from '@/components/ui/separator';
import { Progress } from '@/components/ui/progress';
import { Heart, MessageCircle, Users, Calendar, Target, Lightbulb, Shield } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { usePsychologyTheme } from '@/utils/psychologyTheme';
import { useAuth } from '@/hooks/useAuth';
import { communityApi } from '@/services/api';
import { toast } from 'sonner';

interface CommunityHub {
  id: string;
  name: string;
  description: string;
  hub_type: string;
  psychological_focus: string;
  member_count: number;
  activity_level: string;
  wellness_score: number;
  calming_score: number;
  support_quality_rating: number;
  crisis_support_available: boolean;
  recent_activity: FeedItem[];
}

interface FeedItem {
  id: string;
  content_type: string;
  title: string;
  preview: string;
  author: { name: string; id: string };
  created_at: string;
  psychological_relevance_score: number;
  calming_effect_rating: number;
  interaction_count: number;
  urgency_level: string;
  wellness_tags: string[];
}

interface PersonalizedFeed {
  user_id: string;
  feed_items: FeedItem[];
  psychological_wellness_tips: string[];
  calming_suggestions: string[];
  community_recommendations: CommunityRecommendation[];
  crisis_resources: any[];
  mood_check_prompt?: string;
}

interface CommunityRecommendation {
  community_hub_id: string;
  name: string;
  psychological_match_score: number;
  description: string;
  member_count: number;
  recommended_reason: string;
  calming_score: number;
  support_quality_rating: number;
}

export function EnhancedPsychologyCommunity() {
  const { user } = useAuth();
  const { setMood, getMoodColors, getCalmingScore, generateCSS, theme } = usePsychologyTheme();
  
  const [activeTab, setActiveTab] = useState('feed');
  const [currentMood, setCurrentMood] = useState('neutral');
  const [stressLevel, setStressLevel] = useState(0.5);
  const [communityHubs, setCommunityHubs] = useState<CommunityHub[]>([]);
  const [personalizedFeed, setPersonalizedFeed] = useState<PersonalizedFeed | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // Apply psychology-based theme when mood changes
  useEffect(() => {
    setMood(currentMood, stressLevel);
    
    // Apply custom CSS for community components
    const style = document.createElement('style');
    style.textContent = generateCSS(currentMood);
    document.head.appendChild(style);
    
    return () => {
      if (document.head.contains(style)) {
        document.head.removeChild(style);
      }
    };
  }, [currentMood, stressLevel, setMood, generateCSS]);

  // Get mood-appropriate colors
  const moodColors = useMemo(() => getMoodColors(currentMood), [currentMood, getMoodColors]);
  const calmingScore = useMemo(() => getCalmingScore(moodColors), [moodColors, getCalmingScore]);

  // Load personalized feed
  useEffect(() => {
    loadPersonalizedFeed();
  }, [currentMood, user?.id]);

  const loadPersonalizedFeed = async () => {
    if (!user?.id) return;
    
    setIsLoading(true);
    try {
      // Load actual community feed from backend
      const feedData = await communityApi.getPersonalizedFeed(user.id, {
        mood: currentMood,
        calming_score: calmingScore,
        psychological_preferences: {
          focus_areas: ['anxiety', 'stress', 'mindfulness'],
          calming_preference: 'high'
        }
      });
      
      setPersonalizedFeed(feedData);
      
      // Show calming notification
      toast.success('Your personalized, calming community feed is ready', {
        description: `Optimized for ${currentMood} mood with ${(calmingScore * 100).toFixed(0)}% calming score`
      });
      
    } catch (error) {
      console.error('Error loading feed:', error);
      toast.error('Unable to load community feed', {
        description: 'Please try again in a moment'
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleMoodChange = (mood: string) => {
    setCurrentMood(mood);
    toast.info(`Theme updated for ${mood} mood`, {
      description: 'Colors and interactions adjusted for your comfort'
    });
  };

  const handleStressLevelChange = (level: number) => {
    setStressLevel(level);
    if (level > 0.7) {
      toast.warning('High stress detected', {
        description: 'Switching to ultra-calming colors and interactions'
      });
    }
  };

  const getFeedItemIcon = (contentType: string) => {
    switch (contentType) {
      case 'forum_post': return <MessageCircle className="w-4 h-4" />;
      case 'challenge_update': return <Target className="w-4 h-4" />;
      case 'event': return <Calendar className="w-4 h-4" />;
      default: return <Heart className="w-4 h-4" />;
    }
  };

  const getUrgencyColor = (urgencyLevel: string) => {
    switch (urgencyLevel) {
      case 'high': return theme.getColorHex('sunset_orange');
      case 'medium': return theme.getColorHex('warm_yellow');
      default: return theme.getColorHex('calm_blue');
    }
  };

  return (
    <div className="community-calming-theme p-6 min-h-screen">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-6xl mx-auto space-y-6"
      >
        {/* Mood Context Header */}
        <Card className="community-card-calming">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="community-text-calming">
                  Your Wellness Community
                </CardTitle>
                <CardDescription>
                  Personalized for your {currentMood} mood • Calming Score: {(calmingScore * 100).toFixed(0)}%
                </CardDescription>
              </div>
              <div className="flex items-center gap-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Current Mood</label>
                  <select
                    value={currentMood}
                    onChange={(e) => handleMoodChange(e.target.value)}
                    className="community-input-calming"
                  >
                    <option value="neutral">Neutral</option>
                    <option value="anxious">Anxious</option>
                    <option value="depressed">Down</option>
                    <option value="stressed">Stressed</option>
                    <option value="happy">Happy</option>
                    <option value="peaceful">Peaceful</option>
                  </select>
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Stress Level</label>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.1"
                    value={stressLevel}
                    onChange={(e) => handleStressLevelChange(parseFloat(e.target.value))}
                    className="w-20"
                  />
                </div>
              </div>
            </div>
          </CardHeader>
        </Card>

        {/* Wellness Tips Banner */}
        {personalizedFeed?.psychological_wellness_tips && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="warning-bg-calming p-4 rounded-lg"
          >
            <div className="flex items-start gap-3">
              <Lightbulb className="w-5 h-5 mt-0.5" style={{ color: theme.getColorHex('warm_yellow') }} />
              <div>
                <h4 className="font-medium mb-2">Wellness Tips for You</h4>
                <ul className="text-sm space-y-1">
                  {personalizedFeed.psychological_wellness_tips.map((tip, index) => (
                    <li key={index} className="opacity-90">• {tip}</li>
                  ))}
                </ul>
              </div>
            </div>
          </motion.div>
        )}

        {/* Main Community Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="feed" className="community-button-calming">
              <Heart className="w-4 h-4 mr-2" />
              Personalized Feed
            </TabsTrigger>
            <TabsTrigger value="communities" className="community-button-calming">
              <Users className="w-4 h-4 mr-2" />
              Communities
            </TabsTrigger>
            <TabsTrigger value="challenges" className="community-button-calming">
              <Target className="w-4 h-4 mr-2" />
              Challenges
            </TabsTrigger>
            <TabsTrigger value="events" className="community-button-calming">
              <Calendar className="w-4 h-4 mr-2" />
              Events
            </TabsTrigger>
          </TabsList>

          <TabsContent value="feed" className="space-y-4">
            <AnimatePresence>
              {isLoading ? (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="text-center py-8"
                >
                  Loading your personalized, calming feed...
                </motion.div>
              ) : (
                personalizedFeed?.feed_items.map((item, index) => (
                  <motion.div
                    key={item.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                  >
                    <Card className="community-card-calming">
                      <CardHeader>
                        <div className="flex items-start justify-between">
                          <div className="flex items-center gap-3">
                            {getFeedItemIcon(item.content_type)}
                            <div>
                              <CardTitle className="text-lg">{item.title}</CardTitle>
                              <CardDescription className="flex items-center gap-2 mt-1">
                                <Avatar className="w-6 h-6">
                                  <AvatarFallback className="text-xs">
                                    {item.author.name.split(' ').map(n => n[0]).join('')}
                                  </AvatarFallback>
                                </Avatar>
                                {item.author.name}
                              </CardDescription>
                            </div>
                          </div>
                          <div className="text-right space-y-1">
                            <div 
                              className="text-xs px-2 py-1 rounded-full"
                              style={{ 
                                backgroundColor: getUrgencyColor(item.urgency_level) + '20',
                                color: getUrgencyColor(item.urgency_level)
                              }}
                            >
                              {item.urgency_level} priority
                            </div>
                            <div className="text-xs text-muted-foreground">
                              Calming: {(item.calming_effect_rating * 100).toFixed(0)}%
                            </div>
                          </div>
                        </div>
                      </CardHeader>
                      <CardContent>
                        <p className="text-muted-foreground mb-4">{item.preview}</p>
                        <div className="flex items-center justify-between">
                          <div className="flex gap-2">
                            {item.wellness_tags.map((tag) => (
                              <Badge key={tag} variant="secondary" className="text-xs">
                                {tag}
                              </Badge>
                            ))}
                          </div>
                          <div className="flex items-center gap-4 text-sm text-muted-foreground">
                            <span className="flex items-center gap-1">
                              <MessageCircle className="w-4 h-4" />
                              {item.interaction_count}
                            </span>
                            <Button size="sm" className="community-button-calming">
                              Engage Mindfully
                            </Button>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  </motion.div>
                ))
              )}
            </AnimatePresence>

            {/* Community Recommendations */}
            {personalizedFeed?.community_recommendations && (
              <Card className="community-card-calming">
                <CardHeader>
                  <CardTitle>Recommended Communities</CardTitle>
                  <CardDescription>
                    Based on your wellness journey and psychological profile
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {personalizedFeed.community_recommendations.map((rec) => (
                    <div key={rec.community_hub_id} className="flex items-center justify-between p-4 border rounded-lg community-divider-calming">
                      <div className="flex-1">
                        <h4 className="font-medium">{rec.name}</h4>
                        <p className="text-sm text-muted-foreground mb-2">{rec.description}</p>
                        <div className="flex items-center gap-4 text-xs text-muted-foreground">
                          <span>{rec.member_count} members</span>
                          <span>Match: {(rec.psychological_match_score * 100).toFixed(0)}%</span>
                          <span>Calming: {(rec.calming_score * 100).toFixed(0)}%</span>
                        </div>
                      </div>
                      <Button className="community-button-calming">
                        Join Mindfully
                      </Button>
                    </div>
                  ))}
                </CardContent>
              </Card>
            )}
          </TabsContent>

          <TabsContent value="communities">
            <Card className="community-card-calming">
              <CardHeader>
                <CardTitle>Your Supportive Communities</CardTitle>
                <CardDescription>
                  Unified spaces for forums, challenges, and events
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-center py-8 text-muted-foreground">
                  Community hubs implementation coming soon...
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="challenges">
            <Card className="community-card-calming">
              <CardHeader>
                <CardTitle>Wellness Challenges</CardTitle>
                <CardDescription>
                  Gentle challenges designed for your psychological well-being
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-center py-8 text-muted-foreground">
                  Psychology-based challenges coming soon...
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="events">
            <Card className="community-card-calming">
              <CardHeader>
                <CardTitle>Community Events</CardTitle>
                <CardDescription>
                  Supportive events and gatherings in your communities
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-center py-8 text-muted-foreground">
                  Community events integration coming soon...
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* Crisis Support Access */}
        <Card className="community-card-calming border-l-4" style={{ borderLeftColor: theme.getColorHex('soft_pink') }}>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <Shield className="w-5 h-5" style={{ color: theme.getColorHex('soft_pink') }} />
              <div>
                <h4 className="font-medium">Crisis Support Available 24/7</h4>
                <p className="text-sm text-muted-foreground">
                  If you're in crisis: Call 988 • Text HOME to 741741 • Emergency: 911
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Mood Check Prompt */}
        {personalizedFeed?.mood_check_prompt && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center p-4 rounded-lg"
            style={{ backgroundColor: theme.getColorHex(moodColors[0]) + '10' }}
          >
            <p className="text-sm font-medium mb-2">{personalizedFeed.mood_check_prompt}</p>
            <Button size="sm" variant="outline" className="community-button-calming">
              Check In With Myself
            </Button>
          </motion.div>
        )}
      </motion.div>
    </div>
  );
}
