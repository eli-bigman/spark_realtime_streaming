
### 1. Setup Environment
Clone the repository and navigate to the project folder.

```bash
# Clone project
git clone https://github.com/eli-bigman/spark_realtime_streaming.git

cd spark_realtime_streaming.git
```

### 2. Start Services
Launch the entire pipeline (Spark, Postgres, Data Generator) automatically:

```bash
docker compose up --build
```
*Note: You can also use `./scripts/start_pipeline.sh` for a guided startup.*

### 3. Monitor Pipeline
The system starts generating and processing data immediately. Here is how to monitor it:

**A. Access Spark UI**
Go to [http://localhost:4040](http://localhost:4040) to view the streaming job status, input rates, and processing metrics.

**B. Watch Database Growth (Real-time)**
1. Connect to the database:
   ```bash
   docker exec -it postgres-db psql -U spark_user -d ecommerce_db
   ```
2. Run the count query:
   ```sql
   SELECT count(*) FROM ecommerce_events;
   ```
3. Turn on watch mode (updates every 1 second):
   ```sql
   \watch 1
   ```
*(Press Ctrl+C to exit)*

**C. Query Data (SQL Shell)**
Connect to the database manually:
```bash
docker exec -it postgres-db psql -U spark_user -d ecommerce_db
```
Run queries:
```sql
SELECT * FROM ecommerce_events ORDER BY timestamp DESC LIMIT 5;
```

**D. View Logs**
- **Spark Job**: `docker logs -f spark-streaming-job`
- **Data Generator**: `docker logs -f data-generator`

## Project Structure

```
├── config/             # Configuration settings
│   └── settings.py
├── data/               # Data volume (gitignored)
│   ├── input/          # Generated JSON events land here
│   └── output/         # Checkpoints/logs
├── docs/               # Documentation (Overview, Guides)
├── scripts/            # Database initialization scripts
│   └── postgres_setup.sql
├── src/                # Source code
│   ├── data_generator.py
│   └── spark_streaming_to_postgres.py
├── .env                # Environment variables (Credentials)
├── docker-compose.yml  # Application orchestration
└── requirements.txt    # Python dependencies
```

## Testing

System tests are integrated into the Docker pipeline.

### Run Automated Tests
To run the end-to-end test suite (`pytest`), use the `test` profile:
```bash
docker compose run --rm tests
```
This will:
1. Start Postgres (if not running).
2. Run the `tests/test_pipeline.py` script.
3. Verify database connectivity, table creation, and real-time data ingestion.
