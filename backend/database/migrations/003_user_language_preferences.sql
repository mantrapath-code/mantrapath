-- Migration 003: User Language Preferences
-- Canonical dialect: PostgreSQL
-- Adds per-user language preference table supporting multilingual foundation (E1)

CREATE TABLE IF NOT EXISTS user_language_preferences (
    id VARCHAR PRIMARY KEY DEFAULT (gen_random_uuid()::text),
    user_id VARCHAR NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    primary_language VARCHAR(10) NOT NULL DEFAULT 'en',            -- ISO 639-1 primary language
    secondary_languages JSONB DEFAULT '[]',                        -- JSONB array of ISO 639-1 codes
    auto_detect_language BOOLEAN DEFAULT TRUE,                     -- Allow automatic detection fallback
    cultural_region VARCHAR(10),                                   -- ISO 3166-1 alpha-2 (e.g. IN, US, CA)
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Ensure one row per user
CREATE UNIQUE INDEX IF NOT EXISTS uq_user_language_preferences_user ON user_language_preferences(user_id);
CREATE INDEX IF NOT EXISTS idx_user_language_pref_primary_lang ON user_language_preferences(primary_language);

-- (Optional future) trigger for auto updating updated_at could be added if needed
-- For now application layer will manage updates.

-- Seed: backfill rows for existing users without creating duplicates (defaults only)
INSERT INTO user_language_preferences (id, user_id)
SELECT gen_random_uuid()::text, u.id
FROM users u
LEFT JOIN user_language_preferences ulp ON ulp.user_id = u.id
WHERE ulp.user_id IS NULL;

-- Migration complete
