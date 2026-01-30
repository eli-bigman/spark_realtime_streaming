#!/bin/bash
set -e

echo "Starting Spark Realtime Streaming Pipeline..."

# 1. Start Infrastructure
echo "Building and starting Docker containers..."
echo "This will start: Postgres, Data Generator, and Spark Streaming Job"
docker compose up -d --build

echo "------------------------------------------------"
echo "Pipeline is running in the background!"
echo ""
echo "MONITORING COMMANDS:"
echo "-------------------"
echo "1. Monitor Spark Logs (Processing):"
echo "   docker logs -f spark-streaming-job"
echo ""
echo "2. Monitor Data Generator:"
echo "   docker logs -f data-generator"
echo ""
echo "3. Connect to Database (SQL Shell):"
echo "   docker exec -it postgres-db psql -U spark_user -d ecommerce_db"
echo ""
echo "4. Watch Row Count (Real-time):"
echo "   a. Connect: docker exec -it postgres-db psql -U spark_user -d ecommerce_db"
echo "   b. Run:     SELECT count(*) FROM ecommerce_events;"
echo "   c. Type:    \watch 1"
echo ""
echo "5. Access Spark UI:"
echo "   http://localhost:4040"
echo ""
echo "To stop the pipeline:"
echo "   ./scripts/stop_pipeline.sh"


