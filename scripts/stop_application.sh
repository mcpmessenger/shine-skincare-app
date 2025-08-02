#!/bin/bash
set -e

echo "=== STOP APPLICATION SCRIPT ==="
echo "Stopping application in us-east-1..."

# Stop PM2 processes
pm2 stop shine-app || true
pm2 delete shine-app || true

echo "✓ Application stopped successfully" 