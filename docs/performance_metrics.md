# Performance Metrics

## System Performance Report

**Test Date**: [Current Date]
**Hardware**: Docker on [Host OS]

### Metrics

| Metric | Value | Notes |
|--------|-------|-------|
| **Input Rate** | ~2 events/sec | Configurable in `.env` |
| **Processing Latency** | ~2-5 seconds | Time from file creation to availability in DB |
| **Throughput** | ~2 events/sec | Matches input rate (stable system) |
| **Database Writes** | Micro-batch | Using JDBC `foreachBatch` |

### Observations
- **Latency**: The file-based streaming source has a slight overhead compared to Kafka, but stays within seconds for this use case.
- **Scalability**: Spark can scale to handle much higher throughputs by increasing executor count, provided the Database can handle the write load.
