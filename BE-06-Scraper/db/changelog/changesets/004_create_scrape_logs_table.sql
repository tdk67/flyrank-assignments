--liquibase formatted sql

--changeset flyrank:004_create_scrape_logs_table
CREATE TABLE IF NOT EXISTS scrape_logs (
    session_id VARCHAR(64) PRIMARY KEY,
    target_name VARCHAR(64) NOT NULL,
    start_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP WITH TIME ZONE,
    total_pages_scraped INT DEFAULT 0,
    total_records_extracted INT DEFAULT 0,
    error_count INT DEFAULT 0,
    status VARCHAR(32) NOT NULL DEFAULT 'RUNNING'
);

CREATE INDEX idx_scrape_logs_target ON scrape_logs(target_name);
