-- Migration 002: Add created_at and updated_at timestamp columns to tasks table
ALTER TABLE tasks ADD COLUMN created_at TIMESTAMP;
ALTER TABLE tasks ADD COLUMN updated_at TIMESTAMP;
UPDATE tasks SET created_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP WHERE created_at IS NULL;
