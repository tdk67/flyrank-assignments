-- liquibase formatted sql

-- changeset developer:1
CREATE TABLE users (
    id UUID PRIMARY KEY,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    telephone VARCHAR(50)
);
