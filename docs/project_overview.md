# Project Overview

## System Components

### 1. Data Generator (`src/data_generator.py`)
- **Function**: Simulates user traffic on an e-commerce website.
- **Output**: Generates JSON files containing event data (view, click, purchase, etc.) effectively acting as a producer.
- **Rate**: Configurable (default: 1-2 events/sec) to emulate real-time traffic.

### 2. Streaming Engine (`spark_streaming_to_postgres.py`)
- **Technology**: Apache Spark Structured Streaming.
- **Function**: data ingestion and processing.
- **Process**:
    - Monitors the `data/input` directory for new files.
    - Reads JSON data with a predefined schema.
    - Performs transformations (timestamp parsing/formatting).
    - Writes data to PostgreSQL in micro-batches.

### 3. Storage Layer (PostgreSQL)
- **Table**: `ecommerce_events`.
- **Storage**: Persists processed events for downstream analytics.
- **Schema**:
    - `event_id`: Unique identifier.
    - `event_type`: Categorical (view, purchase).
    - `user_id`: Simulated User ID.
    - `product_id`: Simulated Product ID.
    - `timestamp`: Event time.
    - `metadata`: JSONB field for flexible attributes (device, browser).

## Data Flow
1. **Generation**: `data_generator.py` produces `event_UUID.json` -> `data/input/`.
2. **Ingestion**: Spark reads new JSON files from `data/input/`.
3. **Processing**: Spark transforms data (types, cleaning).
4. **Loading**: Spark (via JDBC) inserts rows into Postgres `ecommerce_events` table.
