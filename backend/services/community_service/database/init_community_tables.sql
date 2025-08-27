-- Community Service Database Tables
-- Psychology-Based Community System

-- Community Hubs table - Central hub for different community types
CREATE TABLE IF NOT EXISTS community_hubs (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    hub_type VARCHAR(50) DEFAULT 'public', -- 'public', 'private', 'interest_based', 'location_based'
    color_theme VARCHAR(50) DEFAULT 'calm_blue',
    psychological_focus JSONB, -- Array of focus areas like ["anxiety", "depression", "mindfulness"]
    member_count INTEGER DEFAULT 0,
    activity_level VARCHAR(50) DEFAULT 'low', -- 'low', 'medium', 'high'
    wellness_score DECIMAL(3,2) DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Community Hub Membership table - Track user memberships
CREATE TABLE IF NOT EXISTS community_hub_membership (
    id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL, -- References shared.models.User
    community_hub_id VARCHAR(255) NOT NULL REFERENCES community_hubs(id) ON DELETE CASCADE,
    role VARCHAR(50) DEFAULT 'member', -- 'member', 'moderator', 'admin'
    joined_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true,
    psychological_preferences JSONB, -- User's preferences in this community
    UNIQUE(user_id, community_hub_id)
);

-- Community Conversations table - Forum-style discussions
CREATE TABLE IF NOT EXISTS community_conversations (
    id VARCHAR(255) PRIMARY KEY,
    community_hub_id VARCHAR(255) NOT NULL REFERENCES community_hubs(id) ON DELETE CASCADE,
    user_id VARCHAR(255) NOT NULL, -- References shared.models.User
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    conversation_type VARCHAR(50) DEFAULT 'discussion', -- 'discussion', 'question', 'support_request'
    psychological_tone VARCHAR(50), -- 'supportive', 'calming', 'encouraging'
    calming_score DECIMAL(3,2) DEFAULT 0.0,
    mood_tags JSONB, -- Array of mood-related tags
    is_crisis BOOLEAN DEFAULT false,
    is_pinned BOOLEAN DEFAULT false,
    reply_count INTEGER DEFAULT 0,
    like_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Community Events table - Wellness events and sessions
CREATE TABLE IF NOT EXISTS community_events (
    id VARCHAR(255) PRIMARY KEY,
    community_hub_id VARCHAR(255) NOT NULL REFERENCES community_hubs(id) ON DELETE CASCADE,
    organizer_id VARCHAR(255) NOT NULL, -- References shared.models.User
    title VARCHAR(255) NOT NULL,
    description TEXT,
    event_type VARCHAR(50) NOT NULL, -- 'mindfulness', 'support_group', 'workshop', 'webinar'
    color_theme VARCHAR(50) DEFAULT 'calm_blue',
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    duration_minutes INTEGER,
    location VARCHAR(255), -- Can be virtual or physical
    max_participants INTEGER,
    current_participants INTEGER DEFAULT 0,
    calming_score DECIMAL(3,2) DEFAULT 0.0,
    wellness_focus JSONB, -- Array of wellness focuses
    registration_required BOOLEAN DEFAULT true,
    is_virtual BOOLEAN DEFAULT true,
    meeting_link VARCHAR(500),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Community Challenges table - Wellness challenges
CREATE TABLE IF NOT EXISTS community_challenges (
    id VARCHAR(255) PRIMARY KEY,
    community_hub_id VARCHAR(255) NOT NULL REFERENCES community_hubs(id) ON DELETE CASCADE,
    creator_id VARCHAR(255) NOT NULL, -- References shared.models.User
    title VARCHAR(255) NOT NULL,
    description TEXT,
    challenge_type VARCHAR(50) NOT NULL, -- 'mindfulness', 'gratitude', 'breathing', 'exercise'
    color_theme VARCHAR(50) DEFAULT 'forest_green',
    duration_days INTEGER NOT NULL,
    start_date DATE,
    end_date DATE,
    difficulty VARCHAR(20) DEFAULT 'beginner', -- 'beginner', 'intermediate', 'advanced'
    participants_count INTEGER DEFAULT 0,
    completion_rate DECIMAL(5,2) DEFAULT 0.0,
    wellness_focus JSONB, -- Array of wellness focuses
    calming_score DECIMAL(3,2) DEFAULT 0.0,
    daily_tasks JSONB, -- Array of daily task descriptions
    rewards JSONB, -- Achievement rewards
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Community Feed Items table - Unified feed system
CREATE TABLE IF NOT EXISTS community_feed_items (
    id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL, -- References shared.models.User (feed owner)
    content_type VARCHAR(50) NOT NULL, -- 'forum_post', 'challenge_update', 'event', 'conversation'
    content_id VARCHAR(255) NOT NULL, -- References the actual content
    community_hub_id VARCHAR(255) NOT NULL REFERENCES community_hubs(id) ON DELETE CASCADE,
    psychological_relevance_score DECIMAL(3,2) DEFAULT 0.0,
    engagement_prediction DECIMAL(3,2) DEFAULT 0.0,
    calming_effect_rating DECIMAL(3,2) DEFAULT 0.0,
    is_personalized BOOLEAN DEFAULT false,
    priority_score INTEGER DEFAULT 0,
    shown_at TIMESTAMP,
    interacted_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- User Feed Preferences table - Personalization settings
CREATE TABLE IF NOT EXISTS user_feed_preferences (
    user_id VARCHAR(255) PRIMARY KEY, -- References shared.models.User
    psychological_profile JSONB, -- User's psychological preferences and needs
    interaction_patterns JSONB, -- Historical interaction data
    calming_preferences JSONB, -- Preferred calming techniques and colors
    wellness_goals JSONB, -- Array of wellness goals
    mood_responsive_feed BOOLEAN DEFAULT true,
    crisis_support_enabled BOOLEAN DEFAULT true,
    notification_preferences JSONB,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Community Resources table - Wellness resources and materials
CREATE TABLE IF NOT EXISTS community_resources (
    id VARCHAR(255) PRIMARY KEY,
    community_hub_id VARCHAR(255) NOT NULL REFERENCES community_hubs(id) ON DELETE CASCADE,
    contributor_id VARCHAR(255) NOT NULL, -- References shared.models.User
    title VARCHAR(255) NOT NULL,
    description TEXT,
    resource_type VARCHAR(50) NOT NULL, -- 'article', 'video', 'audio', 'exercise', 'technique'
    content_url VARCHAR(500),
    content_text TEXT,
    color_theme VARCHAR(50) DEFAULT 'sage_green',
    psychological_benefits JSONB, -- Array of psychological benefits
    calming_score DECIMAL(3,2) DEFAULT 0.0,
    difficulty_level VARCHAR(20) DEFAULT 'beginner',
    duration_minutes INTEGER,
    tags JSONB, -- Array of searchable tags
    download_count INTEGER DEFAULT 0,
    rating DECIMAL(3,2) DEFAULT 0.0,
    is_featured BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Community Mood Analytics table - Track community emotional climate
CREATE TABLE IF NOT EXISTS community_mood_analytics (
    id VARCHAR(255) PRIMARY KEY,
    community_hub_id VARCHAR(255) NOT NULL REFERENCES community_hubs(id) ON DELETE CASCADE,
    analysis_date DATE NOT NULL,
    average_mood_score DECIMAL(3,2),
    dominant_emotions JSONB, -- Array of dominant emotions with percentages
    stress_indicators JSONB, -- Stress level indicators
    support_needed_level VARCHAR(20), -- 'low', 'medium', 'high', 'critical'
    calming_interventions_suggested JSONB, -- Suggested interventions
    community_wellness_score DECIMAL(3,2),
    engagement_metrics JSONB, -- Engagement statistics
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_community_hubs_type ON community_hubs(hub_type);
CREATE INDEX IF NOT EXISTS idx_community_hubs_psychological_focus ON community_hubs USING GIN(psychological_focus);
CREATE INDEX IF NOT EXISTS idx_community_membership_user ON community_hub_membership(user_id);
CREATE INDEX IF NOT EXISTS idx_community_membership_hub ON community_hub_membership(community_hub_id);
CREATE INDEX IF NOT EXISTS idx_community_conversations_hub ON community_conversations(community_hub_id);
CREATE INDEX IF NOT EXISTS idx_community_conversations_user ON community_conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_community_conversations_created ON community_conversations(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_community_events_hub ON community_events(community_hub_id);
CREATE INDEX IF NOT EXISTS idx_community_events_start_time ON community_events(start_time);
CREATE INDEX IF NOT EXISTS idx_community_challenges_hub ON community_challenges(community_hub_id);
CREATE INDEX IF NOT EXISTS idx_community_challenges_active ON community_challenges(is_active, start_date);
CREATE INDEX IF NOT EXISTS idx_community_feed_user ON community_feed_items(user_id);
CREATE INDEX IF NOT EXISTS idx_community_feed_hub ON community_feed_items(community_hub_id);
CREATE INDEX IF NOT EXISTS idx_community_feed_content ON community_feed_items(content_type, content_id);
CREATE INDEX IF NOT EXISTS idx_community_resources_hub ON community_resources(community_hub_id);
CREATE INDEX IF NOT EXISTS idx_community_resources_type ON community_resources(resource_type);
CREATE INDEX IF NOT EXISTS idx_community_mood_analytics_date ON community_mood_analytics(analysis_date DESC);

-- Insert default community hubs for immediate functionality
INSERT INTO community_hubs (id, name, description, hub_type, color_theme, psychological_focus, wellness_score) 
VALUES 
    ('wellness-support', 'Wellness Support', 'A supportive space for mental wellness discussions', 'public', 'calm_blue', '["anxiety", "depression", "stress"]', 8.5),
    ('mindfulness-community', 'Mindfulness Community', 'Sharing mindfulness practices and experiences', 'public', 'sage_green', '["mindfulness", "meditation", "peace"]', 9.0),
    ('crisis-support', 'Crisis Support', 'Immediate support for those in crisis', 'public', 'lavender', '["crisis", "immediate_support", "safety"]', 7.0),
    ('gratitude-circle', 'Gratitude Circle', 'Daily gratitude practice and sharing', 'public', 'sunset_orange', '["gratitude", "positivity", "joy"]', 8.8),
    ('breathing-techniques', 'Breathing Techniques', 'Learn and practice breathing exercises', 'public', 'gentle_teal', '["breathing", "anxiety_relief", "calm"]', 9.2)
ON CONFLICT (id) DO NOTHING;

-- Insert default events
INSERT INTO community_events (id, community_hub_id, organizer_id, title, description, event_type, color_theme, start_time, duration_minutes, max_participants, calming_score, wellness_focus, is_virtual, meeting_link)
VALUES 
    ('mindfulness-monday', 'mindfulness-community', 'system', 'Mindfulness Monday Session', 'Weekly guided mindfulness practice', 'mindfulness', 'sage_green', '2025-08-04 18:00:00', 60, 20, 9.0, '["stress_reduction", "awareness", "calm"]', true, 'https://meet.example.com/mindfulness-monday'),
    ('wellness-wednesday', 'wellness-support', 'system', 'Wellness Check-in Wednesday', 'Group wellness discussion and support', 'support_group', 'calm_blue', '2025-08-06 19:00:00', 90, 15, 8.5, '["mental_health", "support", "connection"]', true, 'https://meet.example.com/wellness-wednesday'),
    ('breathing-friday', 'breathing-techniques', 'system', 'Friday Breathing Workshop', 'Learn new breathing techniques for stress relief', 'workshop', 'gentle_teal', '2025-08-08 17:00:00', 45, 25, 9.0, '["anxiety_relief", "breathing", "relaxation"]', true, 'https://meet.example.com/breathing-friday')
ON CONFLICT (id) DO NOTHING;

-- Insert default challenges
INSERT INTO community_challenges (id, community_hub_id, creator_id, title, description, challenge_type, color_theme, duration_days, start_date, end_date, difficulty, calming_score, wellness_focus, daily_tasks, is_active)
VALUES 
    ('7-day-mindfulness', 'mindfulness-community', 'system', '7-Day Mindfulness Challenge', 'Practice mindfulness for 10 minutes daily for a week', 'mindfulness', 'forest_green', 7, '2025-08-04', '2025-08-10', 'beginner', 8.0, '["stress_reduction", "awareness", "calm"]', '["Day 1: Basic breathing awareness", "Day 2: Body scan meditation", "Day 3: Mindful walking", "Day 4: Loving-kindness meditation", "Day 5: Mindful eating", "Day 6: Gratitude practice", "Day 7: Integration reflection"]', true),
    ('gratitude-week', 'gratitude-circle', 'system', 'Weekly Gratitude Practice', 'Share three things you are grateful for each day', 'gratitude', 'sunset_orange', 7, '2025-08-04', '2025-08-10', 'beginner', 7.5, '["positivity", "mindfulness", "joy"]', '["Write 3 gratitudes", "Share with community", "Reflect on positive moments", "Practice appreciation meditation"]', true),
    ('breathing-mastery', 'breathing-techniques', 'system', 'Breathing Technique Mastery', 'Learn and practice different breathing techniques', 'breathing', 'gentle_teal', 14, '2025-08-04', '2025-08-17', 'intermediate', 9.0, '["anxiety_relief", "calm", "focus"]', '["4-7-8 breathing", "Box breathing", "Belly breathing", "Alternate nostril breathing"]', true)
ON CONFLICT (id) DO NOTHING;

-- Create a function to update timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at columns
CREATE TRIGGER update_community_hubs_updated_at BEFORE UPDATE ON community_hubs FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_community_conversations_updated_at BEFORE UPDATE ON community_conversations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_community_events_updated_at BEFORE UPDATE ON community_events FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_community_challenges_updated_at BEFORE UPDATE ON community_challenges FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_community_resources_updated_at BEFORE UPDATE ON community_resources FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_user_feed_preferences_updated_at BEFORE UPDATE ON user_feed_preferences FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
