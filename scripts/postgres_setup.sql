-- Create the table for storing e-commerce events
CREATE TABLE IF NOT EXISTS ecommerce_events (
    event_id VARCHAR(50) PRIMARY KEY,
    event_type VARCHAR(20),
    user_id VARCHAR(50),
    product_id VARCHAR(50),
    timestamp TIMESTAMP,
    metadata JSONB
);
-- Index on timestamp for time-based queries
CREATE INDEX IF NOT EXISTS idx_timestamp ON ecommerce_events(timestamp);