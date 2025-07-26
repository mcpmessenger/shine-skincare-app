#!/usr/bin/env python3
"""
Check SCIN Dataset Columns

This script checks the actual column names in the SCIN dataset to understand the data structure.
"""

import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.scin_dataset_service import SCINDatasetService

def main():
    """Check SCIN dataset columns"""
    print("=" * 60)
    print("SCIN Dataset Column Analysis")
    print("=" * 60)
    
    try:
        # Initialize service
        service = SCINDatasetService()
        
        # Load metadata
        print("Loading SCIN dataset metadata...")
        if not service.load_metadata():
            print("❌ Failed to load metadata")
            return 1
        
        print(f"✅ Dataset loaded successfully!")
        print(f"Total records: {len(service.merged_df)}")
        print(f"Total columns: {len(service.merged_df.columns)}")
        
        # Show all columns
        print("\n" + "=" * 60)
        print("ALL COLUMNS:")
        print("=" * 60)
        for i, col in enumerate(service.merged_df.columns):
            print(f"{i+1:2d}. {col}")
        
        # Find condition-related columns
        print("\n" + "=" * 60)
        print("CONDITION-RELATED COLUMNS:")
        print("=" * 60)
        condition_cols = [col for col in service.merged_df.columns if 'condition' in col.lower()]
        for col in condition_cols:
            print(f"- {col}")
        
        # Find skin type columns
        print("\n" + "=" * 60)
        print("SKIN TYPE COLUMNS:")
        print("=" * 60)
        skin_cols = [col for col in service.merged_df.columns if 'skin' in col.lower()]
        for col in skin_cols:
            print(f"- {col}")
        
        # Find image-related columns
        print("\n" + "=" * 60)
        print("IMAGE-RELATED COLUMNS:")
        print("=" * 60)
        image_cols = [col for col in service.merged_df.columns if 'image' in col.lower()]
        for col in image_cols:
            print(f"- {col}")
        
        # Show sample data for key columns
        print("\n" + "=" * 60)
        print("SAMPLE DATA:")
        print("=" * 60)
        
        # Check for condition label
        if 'dermatologist_skin_condition_on_label_name' in service.merged_df.columns:
            print("\nCondition labels (first 10):")
            conditions = service.merged_df['dermatologist_skin_condition_on_label_name'].dropna().unique()[:10]
            for condition in conditions:
                print(f"- {condition}")
        
        # Check for skin type
        if 'dermatologist_fitzpatrick_skin_type_label_1' in service.merged_df.columns:
            print("\nSkin types (first 10):")
            skin_types = service.merged_df['dermatologist_fitzpatrick_skin_type_label_1'].dropna().unique()[:10]
            for skin_type in skin_types:
                print(f"- {skin_type}")
        
        # Check for image paths
        if 'image_1_path' in service.merged_df.columns:
            print("\nSample image paths (first 5):")
            image_paths = service.merged_df['image_1_path'].dropna().head()
            for path in image_paths:
                print(f"- {path}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 