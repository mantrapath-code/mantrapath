-- MantraPath Enhanced AI Context Tables Migration
-- Run this to add new tables for AI context management

-- User Context Summary Table
CREATE TABLE IF NOT EXISTS user_context_summaries (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL UNIQUE,
    personality_profile JSON,
    writing_style JSON,
    mood_patterns JSON,
    engagement_patterns JSON,
    crisis_indicators JSON,
    preferred_language VARCHAR(10) DEFAULT 'en',
    communication_style VARCHAR(20) DEFAULT 'empathetic',
    ai_interaction_level VARCHAR(20) DEFAULT 'full',
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    context_version VARCHAR(10) DEFAULT '1.0',
    data_sources JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Conversation Context Table
CREATE TABLE IF NOT EXISTS conversation_contexts (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    session_id VARCHAR(36) NOT NULL,
    key_topics JSON,
    emotional_journey JSON,
    support_requests JSON,
    breakthrough_moments JSON,
    response_effectiveness JSON,
    intervention_triggers JSON,
    conversation_summary TEXT,
    last_message_timestamp TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (session_id) REFERENCES chat_sessions(id) ON DELETE CASCADE
);

-- AI Personality Table
CREATE TABLE IF NOT EXISTS ai_personalities (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL UNIQUE,
    empathy_level FLOAT DEFAULT 0.8,
    directness_level FLOAT DEFAULT 0.6,
    encouragement_style VARCHAR(20) DEFAULT 'gentle',
    humor_usage FLOAT DEFAULT 0.3,
    response_length VARCHAR(10) DEFAULT 'medium',
    question_frequency FLOAT DEFAULT 0.5,
    suggestion_style VARCHAR(20) DEFAULT 'collaborative',
    greeting_style VARCHAR(20) DEFAULT 'warm',
    farewell_style VARCHAR(20) DEFAULT 'supportive',
    crisis_response_style VARCHAR(20) DEFAULT 'immediate',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Journal Assistance Sessions (for future journal assistant service)
CREATE TABLE IF NOT EXISTS journal_assistance_sessions (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    session_type VARCHAR(20) DEFAULT 'writing_prompt',
    language_detected VARCHAR(10),
    prompt_generated TEXT,
    user_input TEXT,
    ai_assistance TEXT,
    writing_style_analysis JSON,
    mood_before INTEGER,
    mood_after INTEGER,
    session_metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Personalized Insights (for future intelligent feeds)
CREATE TABLE IF NOT EXISTS personalized_insights (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    insight_type VARCHAR(30) NOT NULL,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    insight_data JSON,
    confidence_score FLOAT DEFAULT 0.5,
    priority_level VARCHAR(10) DEFAULT 'medium',
    is_delivered BOOLEAN DEFAULT FALSE,
    delivered_at TIMESTAMP NULL,
    user_interaction VARCHAR(20) DEFAULT 'pending',
    effectiveness_score FLOAT DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Smart Notifications Enhancement
CREATE TABLE IF NOT EXISTS smart_notifications (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    notification_type VARCHAR(30) NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    optimal_send_time TIMESTAMP NOT NULL,
    personalization_factors JSON,
    predicted_engagement_score FLOAT DEFAULT 0.5,
    actual_engagement_score FLOAT DEFAULT 0.0,
    delivery_status VARCHAR(20) DEFAULT 'scheduled',
    sent_at TIMESTAMP NULL,
    opened_at TIMESTAMP NULL,
    acted_upon_at TIMESTAMP NULL,
    user_feedback VARCHAR(20) DEFAULT 'none',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- AI Interaction Logs for learning and improvement
CREATE TABLE IF NOT EXISTS ai_interaction_logs (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    service_type VARCHAR(20) NOT NULL,
    interaction_type VARCHAR(30) NOT NULL,
    user_input TEXT,
    ai_response TEXT,
    context_used JSON,
    personalization_score FLOAT DEFAULT 0.0,
    user_satisfaction_rating INTEGER DEFAULT NULL,
    response_effectiveness VARCHAR(20) DEFAULT 'unknown',
    processing_time_ms INTEGER DEFAULT 0,
    model_version VARCHAR(20) DEFAULT '1.0',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_user_context_user_id ON user_context_summaries(user_id);
CREATE INDEX IF NOT EXISTS idx_user_context_updated ON user_context_summaries(last_updated);

CREATE INDEX IF NOT EXISTS idx_conversation_context_user_id ON conversation_contexts(user_id);
CREATE INDEX IF NOT EXISTS idx_conversation_context_session_id ON conversation_contexts(session_id);
CREATE INDEX IF NOT EXISTS idx_conversation_context_updated ON conversation_contexts(updated_at);

CREATE INDEX IF NOT EXISTS idx_ai_personality_user_id ON ai_personalities(user_id);

CREATE INDEX IF NOT EXISTS idx_journal_sessions_user_id ON journal_assistance_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_journal_sessions_created ON journal_assistance_sessions(created_at);

CREATE INDEX IF NOT EXISTS idx_personalized_insights_user_id ON personalized_insights(user_id);
CREATE INDEX IF NOT EXISTS idx_personalized_insights_type ON personalized_insights(insight_type);
CREATE INDEX IF NOT EXISTS idx_personalized_insights_delivered ON personalized_insights(is_delivered);

CREATE INDEX IF NOT EXISTS idx_smart_notifications_user_id ON smart_notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_smart_notifications_send_time ON smart_notifications(optimal_send_time);
CREATE INDEX IF NOT EXISTS idx_smart_notifications_status ON smart_notifications(delivery_status);

CREATE INDEX IF NOT EXISTS idx_ai_logs_user_id ON ai_interaction_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_logs_service ON ai_interaction_logs(service_type);
CREATE INDEX IF NOT EXISTS idx_ai_logs_created ON ai_interaction_logs(created_at);

-- Add constraints
ALTER TABLE user_context_summaries 
ADD CONSTRAINT chk_empathy_level CHECK (JSON_EXTRACT(personality_profile, '$.empathy_level') BETWEEN 0 AND 1);

ALTER TABLE ai_personalities 
ADD CONSTRAINT chk_empathy_level_range CHECK (empathy_level BETWEEN 0 AND 1),
ADD CONSTRAINT chk_directness_level_range CHECK (directness_level BETWEEN 0 AND 1),
ADD CONSTRAINT chk_humor_usage_range CHECK (humor_usage BETWEEN 0 AND 1),
ADD CONSTRAINT chk_question_frequency_range CHECK (question_frequency BETWEEN 0 AND 1);

ALTER TABLE personalized_insights 
ADD CONSTRAINT chk_confidence_score_range CHECK (confidence_score BETWEEN 0 AND 1);

ALTER TABLE smart_notifications 
ADD CONSTRAINT chk_engagement_score_range CHECK (predicted_engagement_score BETWEEN 0 AND 1);

-- Insert default AI personalities for existing users (optional)
INSERT IGNORE INTO ai_personalities (id, user_id, empathy_level, directness_level, encouragement_style)
SELECT 
    UUID() as id,
    id as user_id,
    0.8 as empathy_level,
    0.6 as directness_level,
    'gentle' as encouragement_style
FROM users 
WHERE id NOT IN (SELECT user_id FROM ai_personalities);

-- Migration complete
SELECT 'Enhanced AI Context Tables Migration Complete' as status;
