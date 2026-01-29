# Spark Realtime Streaming - Complete Walkthrough

This guide explains how to spin up the project, generate data, and verify the realtime pipeline.

## 1. Environment Setup

### Prerequisites
- **Docker Desktop** must be running.
- **Python 3.x** (optional, if running scripts locally).

### Configuration
The project relies on environment variables defined in [.env](file:///d:/xcode/Amalitech/spark_realtime_streaming/.env).
A [.env](file:///d:/xcode/Amalitech/spark_realtime_streaming/.env) file has been created with the following defaults:
```ini
POSTGRES_USER=spark_user
POSTGRES_PASSWORD=spark_password
POSTGRES_DB=ecommerce_db
POSTGRES_HOST=localhost # Hostname for local execution; docker-compose overrides this for containers
POSTGRES_PORT=5432
INPUT_DATA_DIR=./data/input
EVENTS_PER_SECOND=2.0
```

## 2. Startup Instructions

### Step 1: Start Infrastructure
Spin up the PostgreSQL and Spark containers in detached mode. Since we have a custom Dockerfile, we build it first:
```bash
docker-compose up -d --build
```
*Wait a few moments for the database to initialize.*

### Step 2: Generate Data
You need to generate dummy JSON events. The generator script creates files in `data/input`.
Run this locally (if Python is installed) or inside the Spark container.

**Option A: Inside Docker (Recommended)**
```bash
docker exec -d spark-realtime-app python src/data_generator.py
```
*The `-d` flag runs it in the background.*

### Step 3: Run Spark Streaming Job
Submit the Spark job to the Spark container. This job monitors `data/input` and writes to Postgres.

```bash
docker exec -it spark-realtime-app spark-submit --packages org.postgresql:postgresql:42.7.2 src/spark_streaming_to_postgres.py
```
*The job will start processing batches. You should see "Processing Batch ID: x..." logs.*

## 3. Verification & Testing

### Test 1: Verify Input Data
Check if files are being created in the input directory:
```bash
ls -l data/input
```

### Test 2: Verify Database Connection & Data
Connect to the PostgreSQL container and query the `ecommerce_events` table.

```bash
docker exec -it postgres-db psql -U spark_user -d ecommerce_db
```

Run the following SQL commands:
```sql
-- Check iteration count
SELECT count(*) FROM ecommerce_events;

-- View recent events
SELECT * FROM ecommerce_events ORDER BY timestamp DESC LIMIT 5;
```

### Test 3: Monitor Latency (Optional)
Watch the count increase in real-time:
```sql
\watch 2
SELECT count(*) FROM ecommerce_events;
```
*(Press Ctrl+C to exit watch mode)*

## 4. Troubleshooting
- **No data in DB?** Check Spark logs for connection errors. Ensure `POSTGRES_HOST` is correct (it should be [postgres](file:///d:/xcode/Amalitech/spark_realtime_streaming/src/spark_streaming_to_postgres.py#29-54) within the docker network, handled automatically by `docker-compose`).
- **Permission errors?** Ensure `data/input` is writable.
