#!/bin/bash
set -e

echo "=== BEFORE INSTALL SCRIPT ==="
echo "Setting up environment for us-east-1 region..."

# Update system packages
sudo yum update -y

# Install Node.js 18
curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
sudo yum install -y nodejs

# Install PM2 for process management
sudo npm install -g pm2

# Create application directory
sudo mkdir -p /var/www/html
sudo chown -R ec2-user:ec2-user /var/www/html

echo "✓ Environment setup completed" 