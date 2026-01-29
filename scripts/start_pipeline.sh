#!/bin/bash
set -e

echo "Starting Spark Realtime Streaming Pipeline..."

# 1. Start Infrastructure
echo "Building and starting Docker containers..."
docker compose build --no-cache
docker compose up -d

# 2. Wait for Postgres
echo "Waiting for Postgres to be ready..."
# Loop until health status is 'healthy'
until [ "$(docker inspect -f '{{.State.Health.Status}}' postgres-db)" == "healthy" ]; do
    sleep 2
    echo -n "."
done
echo -e "\nPostgres is ready!"

# 3. Submit Spark Job
echo "Submitting Spark Streaming Job..."
docker exec -w //home/jovyan/work -d spark-realtime-app spark-submit --packages org.postgresql:postgresql:42.7.2 src/spark_streaming_to_postgres.py
echo "Spark job submitted in background."

# 4. Start Data Generator
echo "Starting Data Generator..."
docker exec -w //home/jovyan/work -d spark-realtime-app python src/data_generator.py
echo "Data generator started in background."

echo "------------------------------------------------"
echo "Pipeline is running!"
echo "Use 'docker logs -f spark-realtime-app' to monitor Spark logs."
echo "Use 'cat data/input/*.json' to see generated data."
