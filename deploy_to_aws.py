#!/usr/bin/env python3
"""
AWS Deployment Script for Shine Backend
Deploys the working backend to AWS Elastic Beanstalk
"""

import os
import subprocess
import sys
import time
from datetime import datetime

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🚀 {description}")
    print(f"   Command: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ {description} - Success")
            if result.stdout:
                print(f"   Output: {result.stdout[:200]}...")
            return True
        else:
            print(f"❌ {description} - Failed")
            print(f"   Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"💥 {description} - Exception: {str(e)}")
        return False

def check_aws_cli():
    """Check if AWS CLI is installed and configured"""
    print("🔍 Checking AWS CLI...")
    
    # Check if aws is installed
    if not run_command("aws --version", "AWS CLI version check"):
        print("❌ AWS CLI not found. Please install it first.")
        print("   Install: pip install awscli")
        return False
    
    # Check if configured
    if not run_command("aws sts get-caller-identity", "AWS credentials check"):
        print("❌ AWS not configured. Please run 'aws configure' first.")
        return False
    
    return True

def deploy_backend():
    """Deploy the backend to AWS Elastic Beanstalk"""
    print("🚀 Starting AWS Backend Deployment")
    print("=" * 50)
    
    # Check prerequisites
    if not check_aws_cli():
        return False
    
    # Navigate to backend directory
    os.chdir("backend")
    
    # Initialize EB application (if not already done)
    print("📦 Initializing Elastic Beanstalk application...")
    
    # Create new environment
    env_name = f"shine-backend-{datetime.now().strftime('%Y%m%d-%H%M')}"
    
    commands = [
        f"eb init shine-backend-poc --region us-east-1 --platform python-3.11",
        f"eb create {env_name} --instance-type c5.2xlarge --single-instance",
        f"eb deploy {env_name}"
    ]
    
    for command in commands:
        if not run_command(command, f"Running: {command}"):
            print("❌ Deployment failed. Check the error above.")
            return False
    
    # Get the environment URL
    print("🔍 Getting environment URL...")
    result = subprocess.run(f"eb status {env_name}", shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        # Parse the URL from output
        for line in result.stdout.split('\n'):
            if 'CNAME' in line:
                url = line.split(':')[1].strip()
                print(f"✅ Backend deployed successfully!")
                print(f"   URL: https://{url}")
                print(f"   Environment: {env_name}")
                
                # Update frontend configuration
                update_frontend_config(url)
                return True
    
    print("❌ Could not get environment URL")
    return False

def update_frontend_config(backend_url):
    """Update frontend configuration with new backend URL"""
    print("🔧 Updating frontend configuration...")
    
    # Go back to root directory
    os.chdir("..")
    
    # Update API configuration
    api_file = "lib/api.ts"
    if os.path.exists(api_file):
        with open(api_file, 'r') as f:
            content = f.read()
        
        # Update the default backend URL
        new_content = content.replace(
            "this.baseUrl = process.env.NEXT_PUBLIC_BACKEND_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';",
            f"this.baseUrl = process.env.NEXT_PUBLIC_BACKEND_URL || process.env.NEXT_PUBLIC_API_URL || 'https://{backend_url}';"
        )
        
        with open(api_file, 'w') as f:
            f.write(new_content)
        
        print(f"✅ Updated {api_file} with new backend URL")
    
    # Update next.config.mjs
    next_config = "next.config.mjs"
    if os.path.exists(next_config):
        with open(next_config, 'r') as f:
            content = f.read()
        
        # Update the environment variable
        new_content = content.replace(
            "NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'https://shine-backend-final.eba-bpcnncyq.us-east-1.elasticbeanstalk.com',",
            f"NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'https://{backend_url}',"
        )
        
        with open(next_config, 'w') as f:
            f.write(new_content)
        
        print(f"✅ Updated {next_config} with new backend URL")
    
    print("🎉 Frontend configuration updated!")
    print("   Next steps:")
    print("   1. Commit and push changes to GitHub")
    print("   2. AWS Amplify will auto-deploy the frontend")
    print("   3. Test the full application")

def main():
    """Main deployment function"""
    print("🚀 Shine Backend AWS Deployment")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    # Check if we're in the right directory
    if not os.path.exists("backend"):
        print("❌ Please run this script from the project root directory")
        return False
    
    # Deploy backend
    if deploy_backend():
        print("🎉 Deployment successful!")
        print("✅ Backend is now live on AWS")
        print("✅ Frontend configuration updated")
        print("✅ Ready for production!")
    else:
        print("❌ Deployment failed")
        print("🔧 Check the errors above and try again")

if __name__ == "__main__":
    main() 