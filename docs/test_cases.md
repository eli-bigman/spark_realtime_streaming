# Test plan

## Manual Test Cases

| Test Case ID | Description | Steps | Expected Outcome | Actual Outcome |
|--------------|-------------|-------|------------------|----------------|
| TC-01 | Data Generation | Run `src/data_generator.py` | JSON files appear in `data/input` directory. | Pass |
| TC-02 | Database Schema | Run `scripts/postgres_setup.sql` | Table `ecommerce_events` is created in Postgres. | Pass |
| TC-03 | Spark Ingestion | Submit Spark job pointing to `data/input` | Spark logs show batch processing (Batch 0, Batch 1...). | Pass |
| TC-04 | Data Persistence | Query Postgres after Spark job runs | Row count in `ecommerce_events` increases. | Pass |
| TC-05 | Data Accuracy | Compare a generated JSON content with DB row | Fields (user_id, timestamp) match exactly. | Pass |
| TC-06 | Data Types | Verify `timestamp` column in DB | Column type is TIMESTAMP (not varchar). | Pass |
