#!/usr/bin/env python3
"""
Quick deployment script to fix the /api/v2/analyze/guest endpoint issue
"""
import os
import subprocess
import sys
from pathlib import Path

def deploy_backend_fix():
    """Deploy the backend fix to AWS Elastic Beanstalk"""
    
    # Change to backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    print("🚀 Deploying backend fix to AWS Elastic Beanstalk...")
    
    try:
        # Create deployment package
        print("📦 Creating deployment package...")
        
        # Create a simple deployment archive
        deployment_files = [
            'run.py',
            'requirements.txt',
            'app/',
            'config.py'
        ]
        
        # Create deployment directory
        deploy_dir = Path('deploy_temp')
        deploy_dir.mkdir(exist_ok=True)
        
        # Copy files to deployment directory
        for item in deployment_files:
            src = Path(item)
            dst = deploy_dir / item
            if src.is_file():
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_bytes(src.read_bytes())
            elif src.is_dir():
                subprocess.run(['cp', '-r', str(src), str(deploy_dir)], check=True)
        
        # Create Procfile if it doesn't exist
        procfile = deploy_dir / 'Procfile'
        if not procfile.exists():
            procfile.write_text('web: python run.py\n')
        
        # Deploy to Elastic Beanstalk
        print("🌐 Deploying to AWS Elastic Beanstalk...")
        
        # Use EB CLI to deploy
        result = subprocess.run([
            'eb', 'deploy', 'shine-backend-final',
            '--region', 'us-east-1',
            '--staged'
        ], cwd=deploy_dir, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Backend fix deployed successfully!")
            print("🔗 URL: https://shine-backend-final.eba-bpcnncyq.us-east-1.elasticbeanstalk.com")
        else:
            print("❌ Deployment failed:")
            print(result.stderr)
            return False
            
        # Clean up
        import shutil
        shutil.rmtree(deploy_dir)
        
        return True
        
    except Exception as e:
        print(f"❌ Deployment error: {e}")
        return False

if __name__ == '__main__':
    success = deploy_backend_fix()
    sys.exit(0 if success else 1) 