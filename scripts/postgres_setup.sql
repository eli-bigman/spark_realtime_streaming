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
    metadata JSONB,
    -- New fields for enhanced analytics
    price DECIMAL(10, 2),
    quantity INTEGER,
    discount_applied BOOLEAN,
    product_category VARCHAR(50),
    session_id VARCHAR(50)
);
-- Index on timestamp for time-based queries
CREATE INDEX IF NOT EXISTS idx_timestamp ON ecommerce_events(timestamp);
-- Index on session_id for session analytics
CREATE INDEX IF NOT EXISTS idx_session_id ON ecommerce_events(session_id);
-- Index on product_category for category analytics
CREATE INDEX IF NOT EXISTS idx_product_category ON ecommerce_events(product_category);