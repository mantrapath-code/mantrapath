-- Initialize MantraPath database with default data
-- This script creates initial tables and seeds essential data

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create databases for each service if they don't exist
-- (In practice, you might want separate databases per service)

-- Insert default content
INSERT INTO content (
    id, title, content, content_type, category, author, difficulty_level, tags, is_published, created_at, updated_at
) VALUES 
(
    uuid_generate_v4(),
    'Understanding Anxiety: A Beginner''s Guide',
    'Anxiety is a natural response to stress, but when it becomes overwhelming, it can interfere with daily life. This guide will help you understand what anxiety is, how it affects your body and mind, and practical steps you can take to manage it.',
    'article',
    'anxiety',
    'Dr. Sarah Johnson',
    'beginner',
    '["anxiety", "coping", "mental-health", "beginner"]',
    true,
    NOW(),
    NOW()
),
(
    uuid_generate_v4(),
    '5-Minute Morning Mindfulness Routine',
    'Start your day with intention and calm with this simple 5-minute mindfulness practice. Perfect for beginners and busy schedules.',
    'exercise',
    'mindfulness',
    'Mindfulness Center',
    'beginner',
    '["mindfulness", "morning", "routine", "meditation"]',
    true,
    NOW(),
    NOW()
),
(
    uuid_generate_v4(),
    'Building Resilience Through Difficult Times',
    'Resilience is the ability to bounce back from adversity, adapt to challenge, and grow stronger through difficult experiences. Learn practical strategies to build your resilience.',
    'article',
    'resilience',
    'Dr. Michael Chen',
    'intermediate',
    '["resilience", "coping", "growth", "adversity"]',
    true,
    NOW(),
    NOW()
);

-- Insert default affirmations
INSERT INTO affirmations (
    id, text, category, mood_context, created_at, updated_at
) VALUES
(
    uuid_generate_v4(),
    'I am capable of handling whatever comes my way today.',
    'confidence',
    '["anxious", "stressed"]',
    NOW(),
    NOW()
),
(
    uuid_generate_v4(),
    'My feelings are valid, and it''s okay to take time to process them.',
    'self-compassion',
    '["sad", "overwhelmed"]',
    NOW(),
    NOW()
),
(
    uuid_generate_v4(),
    'I choose to focus on what I can control and let go of what I cannot.',
    'acceptance',
    '["worried", "anxious"]',
    NOW(),
    NOW()
),
(
    uuid_generate_v4(),
    'I am growing stronger through every challenge I face.',
    'resilience',
    '["difficult", "challenging"]',
    NOW(),
    NOW()
),
(
    uuid_generate_v4(),
    'I deserve love, kindness, and compassion, especially from myself.',
    'self-love',
    '["low", "critical"]',
    NOW(),
    NOW()
);

-- Insert default forums
INSERT INTO forums (
    id, name, description, category, is_public, requires_approval, moderator_ids, created_at, updated_at
) VALUES
(
    uuid_generate_v4(),
    'Anxiety Support',
    'A safe space to discuss anxiety, share coping strategies, and support each other.',
    'mental-health',
    true,
    false,
    '[]',
    NOW(),
    NOW()
),
(
    uuid_generate_v4(),
    'Mindfulness & Meditation',
    'Share your mindfulness journey, meditation techniques, and peaceful moments.',
    'mindfulness',
    true,
    false,
    '[]',
    NOW(),
    NOW()
),
(
    uuid_generate_v4(),
    'Daily Check-ins',
    'Share how you''re feeling today and connect with others on their wellness journey.',
    'general',
    true,
    false,
    '[]',
    NOW(),
    NOW()
),
(
    uuid_generate_v4(),
    'Success Stories',
    'Celebrate your victories, big and small, and inspire others with your progress.',
    'motivation',
    true,
    false,
    '[]',
    NOW(),
    NOW()
);

-- Create admin user (default password: admin123 - change in production!)
-- Note: This would typically be done through the API, but including for initial setup
DO $$
DECLARE
    admin_id UUID := uuid_generate_v4();
BEGIN
    -- Insert admin user
    INSERT INTO users (
        id, email, hashed_password, full_name, is_active, is_verified, role, created_at, updated_at
    ) VALUES (
        admin_id,
        'admin@mantrapath.com',
        '$2b$12$LQv3c1yqBwmndiL8aFuaNe6vTjNz3BhzqyJ0GTKcx0DhFhgJJ.3C6', -- hashed 'admin123'
        'MantraPath Administrator',
        true,
        true,
        'admin',
        NOW(),
        NOW()
    );

    -- Create admin profile
    INSERT INTO user_profiles (
        id, user_id, timezone, theme, privacy_level, 
        email_notifications, push_notifications, mood_reminders, weekly_reports,
        created_at, updated_at
    ) VALUES (
        uuid_generate_v4(),
        admin_id,
        'UTC',
        'light',
        'private',
        true,
        true,
        true,
        true,
        NOW(),
        NOW()
    );
END $$;

-- Insert sample positive content for different categories
INSERT INTO content (
    id, title, content, content_type, category, author, difficulty_level, tags, is_published, created_at, updated_at
) VALUES
(
    uuid_generate_v4(),
    'Breathing Techniques for Instant Calm',
    'When stress hits, your breath is your most powerful tool. Here are three breathing techniques you can use anywhere, anytime to find instant calm.',
    'exercise',
    'stress-relief',
    'Wellness Team',
    'beginner',
    '["breathing", "stress-relief", "techniques", "instant"]',
    true,
    NOW(),
    NOW()
),
(
    uuid_generate_v4(),
    'The Science of Gratitude',
    'Research shows that practicing gratitude can improve your mood, strengthen relationships, and boost overall well-being. Learn how to incorporate gratitude into your daily life.',
    'article',
    'gratitude',
    'Dr. Lisa Rodriguez',
    'beginner',
    '["gratitude", "science", "well-being", "daily-practice"]',
    true,
    NOW(),
    NOW()
),
(
    uuid_generate_v4(),
    'Progressive Muscle Relaxation Guide',
    'Progressive muscle relaxation is a technique that can help reduce anxiety and improve sleep. This step-by-step guide will teach you how to practice it effectively.',
    'exercise',
    'relaxation',
    'Sleep Foundation',
    'intermediate',
    '["relaxation", "muscle", "sleep", "anxiety"]',
    true,
    NOW(),
    NOW()
);

-- Add some motivational affirmations for different situations
INSERT INTO affirmations (
    id, text, category, mood_context, created_at, updated_at
) VALUES
(
    uuid_generate_v4(),
    'Today is a new day full of possibilities and opportunities.',
    'motivation',
    '["morning", "fresh-start"]',
    NOW(),
    NOW()
),
(
    uuid_generate_v4(),
    'I trust in my ability to navigate through uncertainty.',
    'confidence',
    '["uncertain", "confused"]',
    NOW(),
    NOW()
),
(
    uuid_generate_v4(),
    'It''s okay to rest. Taking breaks is part of productivity, not the opposite.',
    'self-care',
    '["tired", "burnout"]',
    NOW(),
    NOW()
),
(
    uuid_generate_v4(),
    'My progress matters, no matter how small the steps.',
    'progress',
    '["slow", "frustrated"]',
    NOW(),
    NOW()
),
(
    uuid_generate_v4(),
    'I am exactly where I need to be in this moment.',
    'presence',
    '["rushing", "impatient"]',
    NOW(),
    NOW()
);

-- Success message
\echo 'Database initialized successfully with default content!'
\echo 'Admin user created: admin@mantrapath.com / admin123'
\echo 'Please change the admin password after first login!'