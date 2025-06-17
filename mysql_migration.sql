-- MySQL migration script
-- Run this locally in your MySQL client

-- Add funding-related columns to document table
ALTER TABLE document ADD COLUMN IF NOT EXISTS is_funding_enabled BOOLEAN DEFAULT false;
ALTER TABLE document ADD COLUMN IF NOT EXISTS funding_goal FLOAT;

-- Add stripe_session_id column to funding table if it exists
ALTER TABLE funding ADD COLUMN IF NOT EXISTS stripe_session_id VARCHAR(255);
