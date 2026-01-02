#!/bin/bash
set -e

# Define stack name
STACK_NAME="hermes"

echo "Deploying $STACK_NAME..."

# Remove existing stack to ensure clean state
if docker stack ls | grep -q "$STACK_NAME"; then
    echo "Removing existing stack..."
    docker stack rm "$STACK_NAME"
    echo "Waiting for stack removal..."
    while docker stack ls | grep -q "$STACK_NAME"; do
        sleep 2
    done
    echo "Stack removed."
fi

# Build image locally (required as stack deploy ignores build context)
echo "Building hermes:latest..."
docker build -t hermes:latest .

# Deploy stack
echo "Deploying stack with docker-compose.yml..."
docker stack deploy --prune -c docker-compose.yml "$STACK_NAME"

echo "Deployment successful."
