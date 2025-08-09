#!/usr/bin/env python3
"""
Cleanup script for deployment
Removes development files and keeps only production essentials
"""

import os
import shutil
from pathlib import Path

def cleanup_for_deployment():
    """Clean up development files for deployment"""
    
    backend_dir = Path("backend")
    
    # Files and directories to remove
    items_to_remove = [
        # Data directories (huge!)
        "data",
        "results", 
        
        # Training scripts
        "train_*.py",
        "analyze_*.py",
        "demo_*.py",
        "test_*.py",
        "download_*.py",
        "process_*.py",
        "diagnose_*.py",
        "fix_*.py",
        "create_balanced_dataset.py",
        "monitor_training.py",
        
        # Development docs
        "*.md",
        
        # Development configs
        "requirements_*.txt",
        
        # Development models (keep only final)
        "models/all_data_model_*.h5",
        "models/demo_*.h5", 
        "models/fixed_model_best.h5",
        "models/simple_*.h5",
        "models/model_summary.txt",
        "models/demo_results.json",
        
        # V4 development
        "v4",
        
        # Services (if not used in production)
        "services",
        
        # Other development files
        "enhanced_*.py",
        "integrated_*.py",
        "ml_*.py",
        "real_*.py",
        "comprehensive_*.py",
        "use_*.py",
        "execute_*.py",
        "integrate_*.py",
        "deploy.sh"
    ]
    
    print("🧹 DEPLOYMENT CLEANUP")
    print("=" * 50)
    
    total_size_removed = 0
    
    for pattern in items_to_remove:
        if "*" in pattern:
            # Handle glob patterns
            import glob
            matches = glob.glob(str(backend_dir / pattern))
            for match in matches:
                path = Path(match)
                if path.exists():
                    size = get_size(path)
                    total_size_removed += size
                    print(f"🗑️  Removing: {path.name} ({format_size(size)})")
                    if path.is_dir():
                        shutil.rmtree(path)
                    else:
                        path.unlink()
        else:
            # Handle direct paths
            path = backend_dir / pattern
            if path.exists():
                size = get_size(path)
                total_size_removed += size
                print(f"🗑️  Removing: {path.name} ({format_size(size)})")
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()
    
    print(f"\n✅ Cleanup complete!")
    print(f"📦 Total space saved: {format_size(total_size_removed)}")
    
    # Show remaining files
    print(f"\n📁 REMAINING PRODUCTION FILES:")
    for item in sorted(backend_dir.iterdir()):
        if item.is_file():
            print(f"   📄 {item.name}")
        elif item.is_dir():
            print(f"   📁 {item.name}/")

def get_size(path):
    """Get size of file or directory"""
    if path.is_file():
        return path.stat().st_size
    elif path.is_dir():
        total = 0
        try:
            for item in path.rglob("*"):
                if item.is_file():
                    total += item.stat().st_size
        except (PermissionError, OSError):
            pass
        return total
    return 0

def format_size(size_bytes):
    """Format bytes as human readable"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"

if __name__ == "__main__":
    print("⚠️  WARNING: This will remove development files!")
    print("Make sure you've backed up anything important.")
    
    response = input("\nContinue with cleanup? (y/N): ")
    if response.lower() == 'y':
        cleanup_for_deployment()
    else:
        print("❌ Cleanup cancelled.")
