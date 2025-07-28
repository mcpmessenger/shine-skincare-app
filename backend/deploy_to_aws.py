#!/usr/bin/env python3
"""
AWS Deployment Script for Shine Backend
Bypasses EB CLI issues and deploys directly using AWS CLI
"""
import os
import subprocess
import json
import zipfile
import tempfile
import shutil
from datetime import datetime

def run_command(command, cwd=None):
    """Run a command and return the result"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            cwd=cwd
        )
        print(f"Command: {command}")
        print(f"Return code: {result.returncode}")
        if result.stdout:
            print(f"STDOUT: {result.stdout}")
        if result.stderr:
            print(f"STDERR: {result.stderr}")
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        print(f"Error running command: {e}")
        return False, "", str(e)

def create_deployment_package():
    """Create a deployment package excluding unnecessary files"""
    print("Creating deployment package...")
    
    # Files to include in deployment
    include_files = [
        'real_working_backend.py',
        'requirements.txt',
        'Procfile',
        '.ebextensions/python.config'
    ]
    
    # Create temporary directory for deployment
    temp_dir = tempfile.mkdtemp()
    deployment_dir = os.path.join(temp_dir, 'deployment')
    os.makedirs(deployment_dir)
    
    # Copy necessary files
    for file in include_files:
        if os.path.exists(file):
            shutil.copy2(file, deployment_dir)
            print(f"Copied: {file}")
        else:
            print(f"Warning: {file} not found")
    
    # Copy .ebextensions directory
    if os.path.exists('.ebextensions'):
        shutil.copytree('.ebextensions', os.path.join(deployment_dir, '.ebextensions'))
        print("Copied: .ebextensions/")
    
    # Create zip file
    zip_path = os.path.join(temp_dir, 'deployment.zip')
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(deployment_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, deployment_dir)
                zipf.write(file_path, arcname)
                print(f"Added to zip: {arcname}")
    
    print(f"Deployment package created: {zip_path}")
    return zip_path, temp_dir

def deploy_to_elastic_beanstalk(zip_path):
    """Deploy to Elastic Beanstalk using AWS CLI"""
    print("Deploying to Elastic Beanstalk...")
    
    # Check if environment exists
    success, stdout, stderr = run_command(
        "aws elasticbeanstalk describe-environments --environment-names shine-backend-final --region us-east-1"
    )
    
    if success and '"Status": "Ready"' in stdout:
        print("Environment exists, updating...")
        # Create application version
        version_label = f"v{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        success, stdout, stderr = run_command(
            f"aws elasticbeanstalk create-application-version "
            f"--application-name shine-backend-poc "
            f"--version-label {version_label} "
            f"--source-bundle S3Bucket=shine-backend-poc,S3Key=deployment.zip "
            f"--region us-east-1"
        )
        
        if success:
            # Update environment
            success, stdout, stderr = run_command(
                f"aws elasticbeanstalk update-environment "
                f"--environment-name shine-backend-final "
                f"--version-label {version_label} "
                f"--region us-east-1"
            )
            
            if success:
                print("Deployment initiated successfully!")
                print("Check status with: aws elasticbeanstalk describe-environments --environment-names shine-backend-final")
                return True
            else:
                print("Failed to update environment")
                return False
        else:
            print("Failed to create application version")
            return False
    else:
        print("Environment not found or not ready")
        print("You may need to create the environment first using AWS Console or EB CLI")
        return False

def main():
    """Main deployment function"""
    print("🚀 Starting AWS Deployment for Shine Backend")
    print("=" * 50)
    
    # Check AWS CLI
    success, stdout, stderr = run_command("aws --version")
    if not success:
        print("❌ AWS CLI not found or not configured")
        print("Please install and configure AWS CLI first")
        return False
    
    # Check AWS credentials
    success, stdout, stderr = run_command("aws sts get-caller-identity")
    if not success:
        print("❌ AWS credentials not configured")
        print("Please run: aws configure")
        return False
    
    print("✅ AWS CLI and credentials verified")
    
    # Create deployment package
    zip_path, temp_dir = create_deployment_package()
    
    try:
        # Deploy to Elastic Beanstalk
        success = deploy_to_elastic_beanstalk(zip_path)
        
        if success:
            print("✅ Deployment completed successfully!")
            print("🌐 Your backend should be available at:")
            print("   https://shine-backend-final.eba-bpcnncyq.us-east-1.elasticbeanstalk.com")
            print("\n📋 Next steps:")
            print("1. Test the health endpoint:")
            print("   curl https://shine-backend-final.eba-bpcnncyq.us-east-1.elasticbeanstalk.com/api/health")
            print("2. Update your frontend API URL")
            print("3. Test the full application")
        else:
            print("❌ Deployment failed")
            print("Check the logs above for details")
        
        return success
        
    finally:
        # Clean up temporary files
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            print("🧹 Cleaned up temporary files")

if __name__ == "__main__":
    main() 