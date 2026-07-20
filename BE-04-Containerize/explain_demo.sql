-- ===========================================================================
-- BE-04-Containerize: Indexing & EXPLAIN ANALYZE Demonstration
-- ===========================================================================
-- This script seeds the 'users' table with 100,000 mock records, 
-- and runs queries before and after creating an index on the 'email' column
-- to demonstrate the performance difference using EXPLAIN ANALYZE.
--
-- How to run this inside the PostgreSQL container:
-- 1. Ensure containers are running: docker compose up -d
-- 2. Execute this script inside psql:
--    docker exec -i user_service_db psql -U postgres -d user_db < explain_demo.sql
-- ===========================================================================

-- 1. Clear any existing records to keep results clean
TRUNCATE TABLE users;

-- 2. Seed 100,000 mock records using generate_series
-- We generate UUIDs dynamically using md5/uuid functions or casting
INSERT INTO users (id, first_name, last_name, email, telephone)
SELECT 
    gen_random_uuid(),
    'FirstName_' || i,
    'LastName_' || i,
    'user_' || i || '@example.com',
    '+1-555-' || lpad(i::text, 6, '0')
FROM generate_series(1, 100000) AS i;

-- Confirming row count
SELECT count(*) AS total_seeded_users FROM users;

-- ===========================================================================
-- STEP A: Query WITHOUT Index
-- ===========================================================================
-- We search for a user near the end of the table to force a long scan.
\echo '---------------------------------------------------------'
\echo 'RUNNING EXPLAIN ANALYZE WITHOUT INDEX'
\echo '---------------------------------------------------------'
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'user_95000@example.com';

-- ===========================================================================
-- STEP B: Create the Index on the email column
-- ===========================================================================
\echo '\nCreating index on users(email)...'
CREATE INDEX idx_users_email ON users(email);

-- ===========================================================================
-- STEP C: Query WITH Index
-- ===========================================================================
\echo '---------------------------------------------------------'
\echo 'RUNNING EXPLAIN ANALYZE WITH INDEX'
\echo '---------------------------------------------------------'
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'user_95000@example.com';

-- ===========================================================================
-- Cleanup (Optional: uncomment if you want to revert to clean schema)
-- ===========================================================================
-- DROP INDEX idx_users_email;
