#!/bin/bash
echo "Stopping Spark Realtime Streaming Pipeline..."

# Stop and remove containers, networks created by up
docker compose down

echo "Pipeline stopped."
