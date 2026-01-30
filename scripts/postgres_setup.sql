-- Create the table for storing e-commerce events
-- DROP TABLE IF EXISTS ecommerce_events;
CREATE TABLE IF NOT EXISTS ecommerce_events (
    event_id VARCHAR(50) PRIMARY KEY,
    event_type VARCHAR(20),
    user_id VARCHAR(50),
    product_id VARCHAR(50),
    timestamp TIMESTAMP,
    device VARCHAR(20),
    browser VARCHAR(20),
    location VARCHAR(10),
    ingestion_timestamp TIMESTAMP,
    metadata JSONB
);
-- Index on timestamp for time-based queries
CREATE INDEX IF NOT EXISTS idx_timestamp ON ecommerce_events(timestamp);