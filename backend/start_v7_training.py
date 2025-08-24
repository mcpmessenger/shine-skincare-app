#!/usr/bin/env python3
"""
Start V7 Training Script
Can be called from dashboard or command line
"""

import os
import sys
import json
import subprocess
import time
from pathlib import Path
from datetime import datetime

def start_v7_training(training_type="v7_unified", dataset_path="./v7_cleaned_features"):
    """Start V7 training with specified parameters"""
    
    print(f"🚀 Starting V7 {training_type} training...")
    print(f"📊 Dataset: {dataset_path}")
    print(f"⏰ Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    try:
        # Check if dataset exists
        if not Path(dataset_path).exists():
            raise FileNotFoundError(f"Dataset not found: {dataset_path}")
        
        # Check if training script exists
        trainer_script = Path("v7_unified_model_trainer.py")
        if not trainer_script.exists():
            raise FileNotFoundError(f"Training script not found: {trainer_script}")
        
        # Create training output directory
        output_dir = Path(f"v7_{training_type}_training_output")
        output_dir.mkdir(exist_ok=True)
        
        # Create training status file
        status_file = output_dir / "training_status.json"
        status = {
            "training_id": f"v7_{training_type}_{int(time.time())}",
            "training_type": training_type,
            "dataset_path": str(dataset_path),
            "status": "starting",
            "start_time": datetime.now().isoformat(),
            "progress": 0,
            "current_epoch": 0,
            "total_epochs": 100,
            "current_accuracy": 0.0,
            "current_loss": 0.0,
            "estimated_completion": None,
            "logs": []
        }
        
        # Save initial status
        with open(status_file, 'w') as f:
            json.dump(status, f, indent=2)
        
        print(f"✅ Training status file created: {status_file}")
        
        # Start training process
        print("🧠 Starting V7 training process...")
        
        # Run the training script
        cmd = [sys.executable, "v7_unified_model_trainer.py"]
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Update status to running
        status["status"] = "running"
        status["logs"].append(f"Training process started with PID: {process.pid}")
        
        with open(status_file, 'w') as f:
            json.dump(status, f, indent=2)
        
        print(f"✅ Training process started (PID: {process.pid})")
        print("📊 Training is now running in the background...")
        print("📁 Monitor progress in:", output_dir)
        print("📋 Status file:", status_file)
        
        # Return process info for monitoring
        return {
            "success": True,
            "training_id": status["training_id"],
            "process_id": process.pid,
            "status_file": str(status_file),
            "output_dir": str(output_dir),
            "message": f"V7 {training_type} training started successfully"
        }
        
    except Exception as e:
        error_msg = f"Failed to start training: {str(e)}"
        print(f"❌ {error_msg}")
        
        # Save error status
        if 'status' in locals():
            status["status"] = "failed"
            status["error"] = str(e)
            status["end_time"] = datetime.now().isoformat()
            
            try:
                with open(status_file, 'w') as f:
                    json.dump(status, f, indent=2)
            except:
                pass
        
        return {
            "success": False,
            "error": str(e),
            "message": error_msg
        }

def check_training_status(status_file_path):
    """Check current training status"""
    try:
        with open(status_file_path, 'r') as f:
            status = json.load(f)
        return status
    except Exception as e:
        return {"error": f"Failed to read status: {str(e)}"}

def main():
    """Main function for command line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Start V7 Training")
    parser.add_argument("--type", default="v7_unified", 
                       choices=["v7_unified", "v7_condition", "v7_age"],
                       help="Training type")
    parser.add_argument("--dataset", default="./v7_cleaned_features",
                       help="Dataset path")
    
    args = parser.parse_args()
    
    # Start training
    result = start_v7_training(args.type, args.dataset)
    
    if result["success"]:
        print("\n🎉 Training started successfully!")
        print(f"📊 Training ID: {result['training_id']}")
        print(f"📁 Output Directory: {result['output_dir']}")
        print(f"📋 Status File: {result['status_file']}")
        print("\n💡 To monitor progress:")
        print(f"   - Check status file: {result['status_file']}")
        print(f"   - View logs in: {result['output_dir']}")
        print(f"   - Use dashboard at: /training-dashboard")
    else:
        print(f"\n❌ Training failed: {result['error']}")
        sys.exit(1)

if __name__ == "__main__":
    main()
