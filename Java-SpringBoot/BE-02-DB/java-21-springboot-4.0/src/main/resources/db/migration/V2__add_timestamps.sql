-- Migration V2: Add created_at and updated_at timestamp columns to tasks table
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS created_at VARCHAR(64) DEFAULT CURRENT_TIMESTAMP NOT NULL;
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS updated_at VARCHAR(64) DEFAULT CURRENT_TIMESTAMP NOT NULL;
