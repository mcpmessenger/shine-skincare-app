#!/bin/bash
set -e

echo "=== START APPLICATION SCRIPT ==="
echo "Starting application in us-east-1..."

cd /var/www/html

# Set environment variables for us-east-1
export NODE_ENV=production
export AWS_REGION=us-east-1
export NEXT_PUBLIC_API_URL=https://your-api-url.us-east-1.amazonaws.com

# Start the application with PM2
echo "Starting Next.js application..."
pm2 start npm --name "shine-app" -- start

# Save PM2 configuration
pm2 save

# Setup PM2 to start on boot
pm2 startup

echo "✓ Application started successfully" 