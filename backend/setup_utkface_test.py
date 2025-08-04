#!/usr/bin/env python3
"""
UTKFace Integration Test Script
This script tests the UTKFace integration functionality.
"""

import sys
import os

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath('.')))

try:
    from utkface_integration import UTKFaceIntegration
    print("Testing UTKFace integration...")
    utkface = UTKFaceIntegration()
    
    if len(utkface.demographic_baselines) > 0:
        print(f"✅ Baselines loaded: {len(utkface.demographic_baselines)}")
        
        test_key = utkface.get_demographic_key(25, 0, 0)
        print(f"✅ Demographic key test: {test_key}")
        
        baseline = utkface.get_relevant_baseline(25, 0, 0)
        if baseline is not None:
            print(f"✅ Baseline retrieval test: {baseline.shape}")
        else:
            print("⚠️  No specific baseline found, using fallback")
        
        print("✅ All tests passed!")
    else:
        print("❌ No baselines found")
        sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1) 