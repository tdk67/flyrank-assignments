--liquibase formatted sql

--changeset flyrank:001_create_books_table
CREATE TABLE IF NOT EXISTS books (
    upc VARCHAR(64) PRIMARY KEY,
    title VARCHAR(512) NOT NULL,
    category VARCHAR(128) NOT NULL,
    price_excl_tax NUMERIC(10, 2) NOT NULL,
    price_incl_tax NUMERIC(10, 2) NOT NULL,
    tax NUMERIC(10, 2) NOT NULL,
    currency VARCHAR(8) NOT NULL DEFAULT 'GBP',
    availability_status VARCHAR(64) NOT NULL,
    stock_quantity INT NOT NULL,
    rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
    description TEXT,
    product_page_url VARCHAR(1024) NOT NULL,
    cover_image_url VARCHAR(1024),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_books_category ON books(category);
CREATE INDEX idx_books_rating ON books(rating);
