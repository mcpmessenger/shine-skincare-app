#!/usr/bin/env python3
"""
Check existing embeddings and baselines
"""

import numpy as np
import os
from pathlib import Path

def check_embeddings():
    """Check existing embeddings and baselines"""
    print("🔍 Checking existing embeddings and baselines...")
    
    # Check condition embeddings
    condition_path = Path("data/condition_embeddings.npy")
    if condition_path.exists():
        try:
            condition_data = np.load(condition_path, allow_pickle=True)
            print(f"✅ Condition embeddings found:")
            print(f"   Shape: {condition_data.shape if hasattr(condition_data, 'shape') else len(condition_data)}")
            print(f"   Type: {type(condition_data)}")
            if isinstance(condition_data, dict):
                print(f"   Keys: {list(condition_data.keys())}")
        except Exception as e:
            print(f"❌ Error loading condition embeddings: {e}")
    else:
        print("❌ Condition embeddings not found")
    
    # Check demographic baselines
    baseline_path = Path("data/utkface/demographic_baselines.npy")
    if baseline_path.exists():
        try:
            baseline_data = np.load(baseline_path, allow_pickle=True)
            print(f"✅ Demographic baselines found:")
            print(f"   Shape: {baseline_data.shape if hasattr(baseline_data, 'shape') else len(baseline_data)}")
            print(f"   Type: {type(baseline_data)}")
            if isinstance(baseline_data, dict):
                print(f"   Keys: {list(baseline_data.keys())}")
                print(f"   Number of demographic groups: {len(baseline_data)}")
        except Exception as e:
            print(f"❌ Error loading demographic baselines: {e}")
    else:
        print("❌ Demographic baselines not found")
    
    # Check UTKFace metadata
    metadata_path = Path("data/utkface/utkface_metadata.csv")
    if metadata_path.exists():
        try:
            import pandas as pd
            metadata = pd.read_csv(metadata_path)
            print(f"✅ UTKFace metadata found:")
            print(f"   Total images: {len(metadata)}")
            print(f"   Columns: {list(metadata.columns)}")
            if 'age' in metadata.columns:
                print(f"   Age range: {metadata['age'].min()}-{metadata['age'].max()}")
            if 'gender' in metadata.columns:
                print(f"   Gender distribution: {metadata['gender'].value_counts().to_dict()}")
            if 'ethnicity' in metadata.columns:
                print(f"   Ethnicity distribution: {metadata['ethnicity'].value_counts().to_dict()}")
        except Exception as e:
            print(f"❌ Error loading UTKFace metadata: {e}")
    else:
        print("❌ UTKFace metadata not found")

if __name__ == "__main__":
    check_embeddings() 