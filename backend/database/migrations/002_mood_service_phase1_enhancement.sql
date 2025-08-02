-- Migration: Phase 1 Mood Service Enhancement
-- Date: 2025-08-01
-- Description: Add Phase 1 enhancement columns to mood_entries and create new enhancement tables

-- Add Phase 1 enhancement columns to mood_entries table
ALTER TABLE mood_entries 
ADD COLUMN IF NOT EXISTS emotional_granularity INTEGER DEFAULT 3,
ADD COLUMN IF NOT EXISTS environmental_context JSONB DEFAULT '{}',
ADD COLUMN IF NOT EXISTS mood_confidence FLOAT DEFAULT 1.0,
ADD COLUMN IF NOT EXISTS collection_method VARCHAR(50) DEFAULT 'manual',
ADD COLUMN IF NOT EXISTS follow_up_responses JSONB DEFAULT '[]',
ADD COLUMN IF NOT EXISTS celebration_triggers JSONB DEFAULT '[]';

-- Create emotional_weather_forecasts table
CREATE TABLE IF NOT EXISTS emotional_weather_forecasts (
    id VARCHAR PRIMARY KEY DEFAULT (gen_random_uuid()::text),
    user_id VARCHAR NOT NULL REFERENCES users(id),
    forecast_date TIMESTAMP WITH TIME ZONE NOT NULL,
    predicted_mood_range JSONB,
    risk_factors JSONB DEFAULT '[]',
    protective_factors JSONB DEFAULT '[]',
    recommendations JSONB DEFAULT '[]',
    confidence_score FLOAT DEFAULT 0.5,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create celebration_moments table
CREATE TABLE IF NOT EXISTS celebration_moments (
    id VARCHAR PRIMARY KEY DEFAULT (gen_random_uuid()::text),
    user_id VARCHAR NOT NULL REFERENCES users(id),
    celebration_type VARCHAR(100) NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    achievement_level VARCHAR(20) DEFAULT 'bronze',
    reward_type VARCHAR(50),
    reward_data JSONB,
    is_shown BOOLEAN DEFAULT FALSE,
    shown_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create adaptive_questions table
CREATE TABLE IF NOT EXISTS adaptive_questions (
    id VARCHAR PRIMARY KEY DEFAULT (gen_random_uuid()::text),
    user_id VARCHAR NOT NULL REFERENCES users(id),
    question_type VARCHAR(100) NOT NULL,
    question_text TEXT NOT NULL,
    question_options JSONB,
    trigger_pattern VARCHAR(200),
    is_active BOOLEAN DEFAULT TRUE,
    usage_count INTEGER DEFAULT 0,
    effectiveness_score FLOAT DEFAULT 0.5,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create environmental_data table
CREATE TABLE IF NOT EXISTS environmental_data (
    id VARCHAR PRIMARY KEY DEFAULT (gen_random_uuid()::text),
    user_id VARCHAR NOT NULL REFERENCES users(id),
    data_date TIMESTAMP WITH TIME ZONE NOT NULL,
    weather_data JSONB,
    calendar_events JSONB,
    location_data JSONB,
    digital_context JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_emotional_weather_forecasts_user_date ON emotional_weather_forecasts(user_id, forecast_date);
CREATE INDEX IF NOT EXISTS idx_celebration_moments_user_shown ON celebration_moments(user_id, is_shown);
CREATE INDEX IF NOT EXISTS idx_adaptive_questions_user_active ON adaptive_questions(user_id, is_active);
CREATE INDEX IF NOT EXISTS idx_environmental_data_user_date ON environmental_data(user_id, data_date);
CREATE INDEX IF NOT EXISTS idx_mood_entries_enhanced ON mood_entries(user_id, created_at, collection_method);

-- Add constraints
ALTER TABLE mood_entries 
ADD CONSTRAINT chk_emotional_granularity CHECK (emotional_granularity BETWEEN 1 AND 5),
ADD CONSTRAINT chk_mood_confidence CHECK (mood_confidence BETWEEN 0.0 AND 1.0);

ALTER TABLE emotional_weather_forecasts
ADD CONSTRAINT chk_confidence_score CHECK (confidence_score BETWEEN 0.0 AND 1.0);

ALTER TABLE adaptive_questions
ADD CONSTRAINT chk_effectiveness_score CHECK (effectiveness_score BETWEEN 0.0 AND 1.0);

-- Insert default adaptive questions
INSERT INTO adaptive_questions (user_id, question_type, question_text, question_options, trigger_pattern) 
SELECT DISTINCT users.id, 'stress_exploration', 'What specific aspect of your stress feels most challenging right now?', 
'[{"value": "workload", "label": "Heavy workload"}, {"value": "relationships", "label": "Relationship challenges"}, {"value": "uncertainty", "label": "Uncertainty about future"}, {"value": "health", "label": "Health concerns"}, {"value": "finances", "label": "Financial worries"}]'::jsonb, 
'high_stress_pattern'
FROM users
WHERE NOT EXISTS (
    SELECT 1 FROM adaptive_questions 
    WHERE adaptive_questions.user_id = users.id 
    AND adaptive_questions.question_type = 'stress_exploration'
);

INSERT INTO adaptive_questions (user_id, question_type, question_text, question_options, trigger_pattern) 
SELECT DISTINCT users.id, 'energy_context', 'What usually helps boost your energy when you feel this way?', 
'[{"value": "movement", "label": "Physical movement"}, {"value": "nature", "label": "Time in nature"}, {"value": "social", "label": "Social connection"}, {"value": "rest", "label": "Quality rest"}, {"value": "nutrition", "label": "Nourishing food"}]'::jsonb, 
'low_energy_pattern'
FROM users
WHERE NOT EXISTS (
    SELECT 1 FROM adaptive_questions 
    WHERE adaptive_questions.user_id = users.id 
    AND adaptive_questions.question_type = 'energy_context'
);

-- Update existing mood entries with default values if they have NULL values
UPDATE mood_entries 
SET 
    emotional_granularity = 3,
    environmental_context = '{}',
    mood_confidence = 1.0,
    collection_method = 'manual',
    follow_up_responses = '[]',
    celebration_triggers = '[]'
WHERE 
    emotional_granularity IS NULL 
    OR environmental_context IS NULL 
    OR mood_confidence IS NULL 
    OR collection_method IS NULL 
    OR follow_up_responses IS NULL 
    OR celebration_triggers IS NULL;
