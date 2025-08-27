-- SQLite Database Initialization Script
-- Simple version without schemas and extensions

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    email TEXT UNIQUE NOT NULL,
    username TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    first_name TEXT,
    last_name TEXT,
    is_active BOOLEAN DEFAULT 1,
    is_verified BOOLEAN DEFAULT 0,
    verification_token TEXT UNIQUE,
    verification_token_expires DATETIME,
    role TEXT DEFAULT 'user',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login_at DATETIME
);

-- User profiles table
CREATE TABLE IF NOT EXISTS user_profiles (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    avatar_url TEXT,
    bio TEXT,
    timezone TEXT DEFAULT 'UTC',
    notifications_enabled BOOLEAN DEFAULT 1,
    daily_reminder_enabled BOOLEAN DEFAULT 1,
    daily_reminder_time TEXT DEFAULT '20:00',
    weekly_report_enabled BOOLEAN DEFAULT 1,
    theme_preference TEXT DEFAULT 'default',
    privacy_mode BOOLEAN DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id)
);

-- Mood entries table
CREATE TABLE IF NOT EXISTS mood_entries (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    mood_score INTEGER NOT NULL,
    energy_level INTEGER DEFAULT 5,
    stress_level INTEGER DEFAULT 5,
    sleep_quality INTEGER DEFAULT 5,
    notes TEXT,
    context_tags TEXT, -- JSON as TEXT
    emotional_granularity INTEGER DEFAULT 3,
    environmental_context TEXT DEFAULT '{}', -- JSON as TEXT
    mood_confidence REAL DEFAULT 1.0,
    collection_method TEXT DEFAULT 'manual',
    follow_up_responses TEXT DEFAULT '[]', -- JSON as TEXT
    celebration_triggers TEXT DEFAULT '[]', -- JSON as TEXT
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Journal entries table
CREATE TABLE IF NOT EXISTS journal_entries (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title TEXT,
    content TEXT NOT NULL,
    mood_before INTEGER,
    mood_after INTEGER,
    sentiment_score REAL,
    sentiment_label TEXT,
    themes TEXT, -- JSON as TEXT
    is_private BOOLEAN DEFAULT 1,
    word_count INTEGER DEFAULT 0,
    reading_time INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Chat sessions table
CREATE TABLE IF NOT EXISTS chat_sessions (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title TEXT DEFAULT 'Chat Session',
    session_type TEXT DEFAULT 'general',
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Language preferences table (E1)
CREATE TABLE IF NOT EXISTS user_language_preferences (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    primary_language TEXT NOT NULL DEFAULT 'en',
    secondary_languages TEXT DEFAULT '[]', -- JSON as TEXT
    auto_detect_language BOOLEAN DEFAULT 1,
    cultural_region TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active);
CREATE INDEX IF NOT EXISTS idx_user_profiles_user_id ON user_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_mood_entries_user_id ON mood_entries(user_id);
CREATE INDEX IF NOT EXISTS idx_mood_entries_created ON mood_entries(created_at);
CREATE INDEX IF NOT EXISTS idx_journal_entries_user_id ON journal_entries(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_id ON chat_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_language_pref_user ON user_language_preferences(user_id);

-- Insert test user Ramesh with password Dev@#123
-- Password hash for Dev@#123 using bcrypt (cost 12)
INSERT OR IGNORE INTO users (
    id, email, username, password_hash, first_name, last_name, is_active, is_verified
) VALUES (
    'test-user-ramesh-001', 
    'ramesh@example.com', 
    'Ramesh', 
    '$2b$12$8Hqn7LmKrJXQZzN.vFGkPuK8Qj7VqFHlzT3mGfCcAaEe1nNpPzTxe', -- Dev@#123
    'Ramesh',
    'Kumar',
    1,
    1
);

-- Create default profile for test user
INSERT OR IGNORE INTO user_profiles (
    id, user_id, timezone, theme_preference, privacy_mode
) VALUES (
    'profile-ramesh-001',
    'test-user-ramesh-001',
    'Asia/Kolkata',
    'light',
    0
);

-- Create default language preferences for test user
INSERT OR IGNORE INTO user_language_preferences (
    id, user_id, primary_language, secondary_languages, cultural_region
) VALUES (
    'lang-pref-ramesh-001',
    'test-user-ramesh-001',
    'en',
    '["hi","ta"]',
    'IN'
);
