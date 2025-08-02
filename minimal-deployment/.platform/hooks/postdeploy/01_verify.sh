#!/bin/bash
# Postdeploy hook to verify deployment

echo "Starting postdeploy verification..."

# Wait for application to start
sleep 10

# Test the application
curl -f http://localhost:8000/api/health || {
    echo "Health check failed"
    exit 1
}

echo "Postdeploy verification completed successfully." 