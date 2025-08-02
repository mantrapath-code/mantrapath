-- MantraPath Enhanced AI Context Tables Migration for SQLite
-- Run this to add new tables for AI context management

-- User Context Summary Table
CREATE TABLE IF NOT EXISTS user_context_summaries (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL UNIQUE,
    personality_profile TEXT, -- JSON stored as TEXT in SQLite
    writing_style TEXT, -- JSON stored as TEXT in SQLite
    mood_patterns TEXT, -- JSON stored as TEXT in SQLite
    engagement_patterns TEXT, -- JSON stored as TEXT in SQLite
    crisis_indicators TEXT, -- JSON stored as TEXT in SQLite
    preferred_language TEXT DEFAULT 'en',
    communication_style TEXT DEFAULT 'empathetic',
    ai_interaction_level TEXT DEFAULT 'full',
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
    context_version TEXT DEFAULT '1.0',
    data_sources TEXT, -- JSON stored as TEXT in SQLite
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Conversation Context Table
CREATE TABLE IF NOT EXISTS conversation_contexts (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    session_id TEXT NOT NULL,
    key_topics TEXT, -- JSON stored as TEXT in SQLite
    emotional_journey TEXT, -- JSON stored as TEXT in SQLite
    support_requests TEXT, -- JSON stored as TEXT in SQLite
    breakthrough_moments TEXT, -- JSON stored as TEXT in SQLite
    response_effectiveness TEXT, -- JSON stored as TEXT in SQLite
    intervention_triggers TEXT, -- JSON stored as TEXT in SQLite
    conversation_summary TEXT,
    last_message_timestamp DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (session_id) REFERENCES chat_sessions(id) ON DELETE CASCADE
);

-- AI Personality Table
CREATE TABLE IF NOT EXISTS ai_personalities (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL UNIQUE,
    empathy_level REAL DEFAULT 0.8,
    directness_level REAL DEFAULT 0.6,
    encouragement_style TEXT DEFAULT 'gentle',
    humor_usage REAL DEFAULT 0.3,
    response_length TEXT DEFAULT 'medium',
    question_frequency REAL DEFAULT 0.5,
    suggestion_style TEXT DEFAULT 'collaborative',
    greeting_style TEXT DEFAULT 'warm',
    farewell_style TEXT DEFAULT 'supportive',
    crisis_response_style TEXT DEFAULT 'immediate',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Journal Assistance Sessions (for future journal assistant service)
CREATE TABLE IF NOT EXISTS journal_assistance_sessions (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    session_type TEXT DEFAULT 'writing_prompt',
    language_detected TEXT,
    prompt_generated TEXT,
    user_input TEXT,
    ai_assistance TEXT,
    writing_style_analysis TEXT, -- JSON stored as TEXT in SQLite
    mood_before INTEGER,
    mood_after INTEGER,
    session_metadata TEXT, -- JSON stored as TEXT in SQLite
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Personalized Insights (for future intelligent feeds)
CREATE TABLE IF NOT EXISTS personalized_insights (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    insight_type TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    insight_data TEXT, -- JSON stored as TEXT in SQLite
    confidence_score REAL DEFAULT 0.5,
    priority_level TEXT DEFAULT 'medium',
    is_delivered INTEGER DEFAULT 0, -- SQLite uses INTEGER for BOOLEAN (0=FALSE, 1=TRUE)
    delivered_at DATETIME NULL,
    user_interaction TEXT DEFAULT 'pending',
    effectiveness_score REAL DEFAULT 0.0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Smart Notifications Enhancement
CREATE TABLE IF NOT EXISTS smart_notifications (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    notification_type TEXT NOT NULL,
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    optimal_send_time DATETIME NOT NULL,
    personalization_factors TEXT, -- JSON stored as TEXT in SQLite
    predicted_engagement_score REAL DEFAULT 0.5,
    actual_engagement_score REAL DEFAULT 0.0,
    delivery_status TEXT DEFAULT 'scheduled',
    sent_at DATETIME NULL,
    opened_at DATETIME NULL,
    acted_upon_at DATETIME NULL,
    user_feedback TEXT DEFAULT 'none',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- AI Interaction Logs for learning and improvement
CREATE TABLE IF NOT EXISTS ai_interaction_logs (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    service_type TEXT NOT NULL,
    interaction_type TEXT NOT NULL,
    user_input TEXT,
    ai_response TEXT,
    context_used TEXT, -- JSON stored as TEXT in SQLite
    personalization_score REAL DEFAULT 0.0,
    user_satisfaction_rating INTEGER DEFAULT NULL,
    response_effectiveness TEXT DEFAULT 'unknown',
    processing_time_ms INTEGER DEFAULT 0,
    model_version TEXT DEFAULT '1.0',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
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

-- SQLite doesn't support ALTER TABLE ADD CONSTRAINT, so we skip those

-- Insert default AI personalities for existing users using SQLite syntax
INSERT OR IGNORE INTO ai_personalities (id, user_id, empathy_level, directness_level, encouragement_style)
SELECT 
    lower(hex(randomblob(16))) as id,
    id as user_id,
    0.8 as empathy_level,
    0.6 as directness_level,
    'gentle' as encouragement_style
FROM users 
WHERE id NOT IN (SELECT user_id FROM ai_personalities);

-- Migration complete
SELECT 'Enhanced AI Context Tables Migration Complete for SQLite' as status;
