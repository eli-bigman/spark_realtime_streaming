# Test Plan

## Automated Tests (Pytest)

These tests are executed automatically via `docker compose run --rm tests`. The source code is located in `tests/test_pipeline.py`.

| Test function              | ID Mapping | Description                  | Implementation Details                                                                          | Status   |
| :------------------------- | :--------- | :--------------------------- | :---------------------------------------------------------------------------------------------- | :------- |
| `test_postgres_connection` | TC-INT-01  | Verify Database Connectivity | Connects to Postgres using credentials from `.env` and executes `SELECT 1`.                     | **PASS** |
| `test_table_existence`     | TC-02      | Verify Schema Initialization | Queries `information_schema.tables` to ensure `ecommerce_events` exists.                        | **PASS** |
| `test_data_ingestion`      | TC-04      | Verify Real-time Ingestion   | Polls the `ecommerce_events` table for 60s until rows appear, confirming Spark is writing data. | **PASS** |

## Manual Test Cases

| Test Case ID | Description     | Steps                                        | Expected Outcome                                        | Actual Outcome |
| :----------- | :-------------- | :------------------------------------------- | :------------------------------------------------------ | :------------- |
| TC-01        | Data Generation | Run `src/data_generator.py`                  | JSON files appear in `data/input` directory.            | Pass           |
| TC-03        | Spark Ingestion | Submit Spark job pointing to `data/input`    | Spark logs show batch processing (Batch 0, Batch 1...). | Pass           |
| TC-05        | Data Accuracy   | Compare a generated JSON content with DB row | Fields (user_id, timestamp) match exactly.              | Pass           |
| TC-06        | Data Types      | Verify `timestamp` column in DB              | Column type is TIMESTAMP (not varchar).                 | Pass           |

### Unit Testing (Pending)

| Test Case ID | Description     | Steps                                        | Expected Outcome                                                                          | Actual Outcome |
| :----------- | :-------------- | :------------------------------------------- | :---------------------------------------------------------------------------------------- | :------------- |
| TC-UNIT-01   | Event Structure | Call `generate_event()` in Python shell      | Dictionary contains keys: event_id, event_type, user_id, product_id, timestamp, metadata. |                |
| TC-UNIT-02   | JSONL Format    | Call `save_batch_to_file` with sample events | File created in `data/input` is valid JSONL (one JSON object per line).                   |                |
| TC-UNIT-03   | Randomness      | Call `generate_event` multiple times         | `event_id` and `timestamp` are unique for each call.                                      |                |

### Integration Testing (Covered by Automation)

| Test Case ID | Description          | Steps                                        | Expected Outcome                                                               | Actual Outcome |
| :----------- | :------------------- | :------------------------------------------- | :----------------------------------------------------------------------------- | :------------- |
| TC-INT-02    | Schema Validation    | Place file with extra fields in `data/input` | Spark processes file, ignoring extra fields unless schema is set to drop/fail. |                |
| TC-INT-03    | Data Type Conversion | Place file with valid timestamp string       | Spark correctly converts string to TimestampType in DataFrame.                 |                |

### End-to-End Testing

| Test Case ID | Description   | Steps                                                     | Expected Outcome                                                                 | Actual Outcome                             |
| :----------- | :------------ | :-------------------------------------------------------- | :------------------------------------------------------------------------------- | :----------------------------------------- |
| TC-E2E-01    | Complete Flow | 1. Run Generator<br>2. Run Spark Job<br>3. Check Postgres | Records from JSONL files appear in `ecommerce_events` table with correct values. | Pass (via Automated `test_data_ingestion`) |
| TC-E2E-02    | Deduplication | Send same `event_id` in two different batches             | (If implemented) Duplicate event is ignored or handled according to logic.       |                                            |

### Error Handling & Edge Cases

| Test Case ID | Description             | Steps                                                                     | Expected Outcome                                                                          | Actual Outcome |
| :----------- | :---------------------- | :------------------------------------------------------------------------ | :---------------------------------------------------------------------------------------- | :------------- |
| TC-ERR-01    | Malformed JSON          | Create file with broken JSON in `data/input`                              | Spark job logs error but continues processing valid files (or halts depending on config). |                |
| TC-ERR-02    | Missing Required Fields | Create event without `user_id`                                            | Spark processes row with null `user_id` or drops it based on schema.                      |                |
| TC-ERR-03    | Database Constraints    | Manually insert row with existing PK into DB, then send same ID via Spark | Spark job handles primary key violation (e.g., updates, ignores, or logs error).          |                |

### Performance Testing

| Test Case ID | Description  | Steps                                           | Expected Outcome                                          | Actual Outcome |
| :----------- | :----------- | :---------------------------------------------- | :-------------------------------------------------------- | :------------- |
| TC-PERF-01   | Volume Test  | Set `EVENTS_PER_SECOND` to 50, run for 5 mins   | System remains stable, no memory leaks in Spark/Postgres. |                |
| TC-PERF-02   | Latency Test | Measure time from file creation to DB insertion | Latency should be under X seconds (e.g., < 10s).          |                |
