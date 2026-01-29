# User Guide

## Step-by-Step Execution

### 1. Prerequisites
- Docker and Docker Compose installed.
- Git (optional).

### 2. Setup
Clone the repo and enter the directory:
```bash
cd pyspark-realtime
```

### 3. Service Lifecycle
Start the environment:
```bash
docker-compose up -d
```
Stop the environment:
```bash
docker-compose down
```

### 4. Running the Pipeline

**Step A: Start Data Generation**
1. Enter Spark container: `docker exec -it spark-realtime-app /bin/bash`
2. Run generator: `python src/data_generator.py`
3. *Process runs in foreground. Open a new terminal for the next step.*

**Step B: Submit Spark Job**
1. Enter Spark container (new terminal): `docker exec -it spark-realtime-app /bin/bash`
2. Submit job:
   ```bash
   spark-submit --packages org.postgresql:postgresql:42.7.2 src/spark_streaming_to_postgres.py
   ```

**Step C: Verify Output**
1. Enter Postgres container: `docker exec -it postgres-db psql -U spark_user -d ecommerce_db`
2. Run Query: `SELECT * FROM ecommerce_events ORDER BY timestamp DESC LIMIT 10;`

### 5. Troubleshooting
- **No data in DB**: Check if `data_generator.py` is running and creating files in `data/input`.
- **Spark Error**: Ensure the postgres JDBC jar is downloaded (the `--packages` flag handles this on first run, requires internet).
