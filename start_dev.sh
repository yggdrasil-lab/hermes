#!/bin/bash
set -e

# Define stack name
STACK_NAME="hermes-dev"

echo "Starting Hermes in Development mode..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Error: .env file not found. Please create it by copying .env.example:"
    echo "  cp .env.example .env"
    echo "Then update it with your configuration and secrets."
    exit 1
fi

# Build image specifically (stack deploy doesn't build)
echo "Building hermes:latest..."
docker build -t hermes:latest .

# Remove existing stack
if docker stack ls | grep -q "$STACK_NAME"; then
    echo "Removing existing stack..."
    docker stack rm "$STACK_NAME"
    echo "Waiting for stack removal..."
    while docker stack ls | grep -q "$STACK_NAME"; do
        sleep 2
    done
    echo "Stack removed."
fi

# Deploy stack
echo "Deploying stack with docker-compose.yml..."
docker stack deploy --prune -c docker-compose.yml "$STACK_NAME"

echo "Development environment started."
echo "To view logs, run: docker service logs -f ${STACK_NAME}_hermes"