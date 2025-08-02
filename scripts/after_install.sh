#!/bin/bash
set -e

echo "=== AFTER INSTALL SCRIPT ==="
echo "Building application in us-east-1..."

cd /var/www/html

# Install dependencies
echo "Installing dependencies..."
npm ci

# Install Tailwind CSS globally
echo "Installing Tailwind CSS..."
npm install -g tailwindcss@latest

# Build Tailwind CSS
echo "Building Tailwind CSS..."
npx tailwindcss -i ./app/globals.css -o ./app/output.css --minify

# Build Next.js application
echo "Building Next.js application..."
npm run build

# Set proper permissions
sudo chown -R ec2-user:ec2-user /var/www/html

echo "✓ Application build completed" 