-- Migration: Add Video Journal Support
-- Description: Adds entry_type and video_analysis columns to journal_entries table
-- Date: 2024-10-16

-- Add entry_type column
ALTER TABLE journal_entries 
ADD COLUMN IF NOT EXISTS entry_type VARCHAR(20) DEFAULT 'text';

-- Add comment for entry_type column
COMMENT ON COLUMN journal_entries.entry_type IS 'Type of journal entry: "text" or "video"';

-- Add video_analysis column
ALTER TABLE journal_entries 
ADD COLUMN IF NOT EXISTS video_analysis JSONB DEFAULT NULL;

-- Add comment for video_analysis column
COMMENT ON COLUMN journal_entries.video_analysis IS 'Contains facial emotions array, text emotion, and metadata for video journals';

-- Add index for faster queries on video journals
CREATE INDEX IF NOT EXISTS idx_journal_entries_entry_type 
ON journal_entries(entry_type);

-- Update existing entries to have entry_type = 'text' if NULL
UPDATE journal_entries 
SET entry_type = 'text' 
WHERE entry_type IS NULL;
