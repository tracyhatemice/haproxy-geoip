#!/bin/bash

# Development runner script
# Runs the service with hot reload enabled

echo "Starting GeoIP service in development mode..."
echo "Service will be available at: http://localhost:6970"
echo "Interactive docs at: http://localhost:6970/docs"
echo ""

# Install dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
fi

# Run with uvicorn in development mode
uvicorn geoip_lookup:app \
    --host 0.0.0.0 \
    --port 6970 \
    --reload \
    --log-level info
