--liquibase formatted sql

--changeset flyrank:003_create_datasets_table
CREATE TABLE IF NOT EXISTS datasets (
    dataset_url VARCHAR(512) PRIMARY KEY,
    dataset_title VARCHAR(256) NOT NULL,
    creator_username VARCHAR(128),
    upvotes_count INT DEFAULT 0,
    views_count INT DEFAULT 0,
    downloads_count INT DEFAULT 0,
    license_name VARCHAR(128),
    summary_description TEXT,
    tags TEXT,
    last_updated_date VARCHAR(64),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_datasets_title ON datasets(dataset_title);
