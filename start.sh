#!/bin/bash
set -e

echo "Deploying Hermes..."

# Stop running containers
docker compose down

# Build and start containers with orphans removal
docker compose up -d --build --remove-orphans

echo "Deployment successful."
