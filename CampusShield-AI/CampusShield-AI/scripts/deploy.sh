#!/bin/bash

# This script deploys the CampusShield AI application.

# Set environment variables
export APP_ENV=production
export DATABASE_URL="your_database_url"
export REDIS_URL="your_redis_url"

# Build the Docker image
docker build -t campusshield-ai .

# Run database migrations
docker run --rm campusshield-ai alembic upgrade head

# Start the application
docker run -d -p 80:80 campusshield-ai

# Output deployment status
echo "CampusShield AI deployed successfully!"