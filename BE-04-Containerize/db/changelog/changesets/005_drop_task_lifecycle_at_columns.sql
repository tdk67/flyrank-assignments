-- liquibase formatted sql

-- changeset developer:5
ALTER TABLE tasks DROP COLUMN assigned_at;
ALTER TABLE tasks DROP COLUMN started_at;
ALTER TABLE tasks DROP COLUMN finished_at;
ALTER TABLE tasks DROP COLUMN failed_at;
