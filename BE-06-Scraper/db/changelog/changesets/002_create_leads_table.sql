--liquibase formatted sql

--changeset flyrank:002_create_leads_table
CREATE TABLE IF NOT EXISTS leads (
    id VARCHAR(128) PRIMARY KEY,
    business_name VARCHAR(256) NOT NULL,
    category_industry VARCHAR(128),
    street_name VARCHAR(128) NOT NULL,
    house_number VARCHAR(32),
    postal_code VARCHAR(16),
    city VARCHAR(128) NOT NULL,
    phone_number VARCHAR(64),
    website_url VARCHAR(512),
    is_business BOOLEAN NOT NULL DEFAULT TRUE,
    raw_json_ld_type VARCHAR(128),
    detail_page_url VARCHAR(1024),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_leads_city_street ON leads(city, street_name);
CREATE INDEX idx_leads_is_business ON leads(is_business);
