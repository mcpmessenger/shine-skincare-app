#!/bin/bash
# Predeploy hook to ensure proper setup

echo "Starting predeploy setup..."

# Ensure proper permissions
chmod +x /var/app/staging/app.py

# Create necessary directories
mkdir -p /var/app/staging/logs

# Set proper ownership
chown -R webapp:webapp /var/app/staging

echo "Predeploy setup completed." 