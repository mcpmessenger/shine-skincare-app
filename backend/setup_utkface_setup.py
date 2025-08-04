#!/usr/bin/env python3
"""
UTKFace Integration Setup Script
This script sets up the UTKFace integration and demographic baselines.
"""

import sys
import os

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath('.')))

try:
    from utkface_integration import UTKFaceIntegration
    print("Initializing UTKFace integration...")
    utkface = UTKFaceIntegration()
    
    print("Setting up demographic baselines...")
    success = utkface.setup_demographic_baselines(force_rebuild=False)
    
    if success:
        print("✅ Setup completed successfully!")
        print(f"📊 Total baselines: {len(utkface.demographic_baselines)}")
        print("Available demographic keys:")
        for key in list(utkface.demographic_baselines.keys())[:10]:
            print(f"  - {key}")
    else:
        print("❌ Setup failed")
        sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1) 