#!/usr/bin/env python3
"""
Data Leakage Investigation Script
Investigates the suspicious 100% condition accuracy in V7 training
"""

import numpy as np
import pandas as pd
import json
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import matplotlib.pyplot as plt
import seaborn as sns

def load_v7_dataset():
    """Load V7 unified dataset"""
    print("🔍 Loading V7 unified dataset...")
    
    # Load training manifest
    manifest_path = Path("./v7_unified_dataset/v7_training_manifest.csv")
    if not manifest_path.exists():
        raise FileNotFoundError(f"Training manifest not found: {manifest_path}")
    
    manifest = pd.read_csv(manifest_path)
    print(f"✅ Loaded manifest with {len(manifest)} samples")
    
    # Load features
    features_dir = Path("./v7_unified_dataset/features")
    if not features_dir.exists():
        raise FileNotFoundError(f"Features directory not found: {features_dir}")
    
    # Load features and labels
    features_list = []
    labels_condition = []
    labels_age = []
    labels_gender = []
    labels_ethnicity = []
    source_datasets = []
    
    for _, row in manifest.iterrows():
        try:
            sample_id = row['sample_id']
            source_dataset = row['source_dataset']
            
            # Determine feature file path
            if source_dataset == 'scin':
                feature_file = features_dir / f"{sample_id}_enhanced_features.json"
            else:  # utkface
                feature_file = features_dir / f"{sample_id}_features.json"
            
            if not feature_file.exists():
                print(f"⚠️ Feature file not found: {feature_file}")
                continue
            
            # Load features
            with open(feature_file, 'r') as f:
                feature_data = json.load(f)
            
            # Extract features
            if 'combined_features' in feature_data:
                features = feature_data['combined_features']
            elif 'features' in feature_data:
                features = feature_data['features']
            else:
                print(f"⚠️ No features found in {feature_file}")
                continue
            
            # Convert to numpy array and ensure it's 1D
            features = np.array(features).flatten()
            
            # Pad shorter features to match the longest feature length
            if len(features) < 1306:
                padding_length = 1306 - len(features)
                features = np.pad(features, (0, padding_length), mode='constant', constant_values=0)
            
            features_list.append(features)
            labels_condition.append(row['condition'])
            labels_age.append(row['age_group'])
            labels_gender.append(row['gender'])
            labels_ethnicity.append(row['ethnicity'])
            source_datasets.append(source_dataset)
            
        except Exception as e:
            print(f"❌ Error loading features for sample {sample_id}: {e}")
            continue
    
    if len(features_list) == 0:
        raise ValueError("❌ No features loaded successfully!")
    
    # Convert to numpy arrays
    X = np.array(features_list)
    print(f"✅ Loaded {len(X)} samples with {X.shape[1]} features each")
    
    return X, labels_condition, labels_age, labels_gender, labels_ethnicity, source_datasets

def analyze_feature_distributions(X, labels, source_datasets):
    """Analyze feature distributions by condition and dataset"""
    print("\n📊 Analyzing feature distributions...")
    
    # Convert labels to numpy array
    labels = np.array(labels)
    source_datasets = np.array(source_datasets)
    
    # Get unique conditions
    unique_conditions = np.unique(labels)
    print(f"📋 Found {len(unique_conditions)} conditions: {unique_conditions}")
    
    # Analyze feature variance by condition
    print("\n🔬 Feature variance by condition:")
    for condition in unique_conditions:
        condition_mask = labels == condition
        condition_features = X[condition_mask]
        
        # Calculate statistics
        mean_features = np.mean(condition_features, axis=0)
        std_features = np.std(condition_features, axis=0)
        var_features = np.var(condition_features, axis=0)
        
        print(f"\n{condition}:")
        print(f"  Samples: {np.sum(condition_mask)}")
        print(f"  Mean: {np.mean(mean_features):.6f}")
        print(f"  Std: {np.mean(std_features):.6f}")
        print(f"  Variance: {np.mean(var_features):.6f}")
        
        # Check for zero variance features (potential data leakage)
        zero_var_features = np.sum(var_features == 0)
        if zero_var_features > 0:
            print(f"  ⚠️ Zero variance features: {zero_var_features}")
    
    # Analyze by dataset source
    print("\n🌐 Feature variance by dataset source:")
    for dataset in np.unique(source_datasets):
        dataset_mask = source_datasets == dataset
        dataset_features = X[dataset_mask]
        
        mean_features = np.mean(dataset_features, axis=0)
        std_features = np.std(dataset_features, axis=0)
        var_features = np.var(dataset_features, axis=0)
        
        print(f"\n{dataset}:")
        print(f"  Samples: {np.sum(dataset_mask)}")
        print(f"  Mean: {np.mean(mean_features):.6f}")
        print(f"  Std: {np.mean(std_features):.6f}")
        print(f"  Variance: {np.mean(var_features):.6f}")

def test_feature_condition_correlation(X, labels):
    """Test if features can perfectly predict conditions"""
    print("\n🧪 Testing feature-condition correlation...")
    
    # Use Random Forest to test feature importance
    rf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, labels, test_size=0.2, random_state=42, stratify=labels
    )
    
    # Train model
    print("🌲 Training Random Forest classifier...")
    rf.fit(X_train, y_train)
    
    # Predictions
    y_pred = rf.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"📊 Random Forest Accuracy: {accuracy:.4f}")
    
    if accuracy > 0.95:
        print("🚨 HIGH ACCURACY DETECTED - Potential data leakage!")
    elif accuracy > 0.85:
        print("⚠️ Moderately high accuracy - Check for overfitting")
    else:
        print("✅ Reasonable accuracy level")
    
    # Feature importance
    feature_importance = rf.feature_importances_
    top_features = np.argsort(feature_importance)[-10:]  # Top 10 features
    
    print(f"\n🔝 Top 10 most important features:")
    for i, feature_idx in enumerate(reversed(top_features)):
        print(f"  {i+1}. Feature {feature_idx}: {feature_importance[feature_idx]:.6f}")
    
    return rf, accuracy, feature_importance

def permutation_test(X, labels, n_permutations=5):
    """Test if high accuracy persists with shuffled labels"""
    print(f"\n🎲 Running permutation test ({n_permutations} iterations)...")
    
    accuracies = []
    
    for i in range(n_permutations):
        # Shuffle labels
        shuffled_labels = np.random.permutation(labels)
        
        # Split and train
        X_train, X_test, y_train, y_test = train_test_split(
            X, shuffled_labels, test_size=0.2, random_state=42
        )
        
        # Train simple classifier
        rf = RandomForestClassifier(n_estimators=50, random_state=42, n_jobs=-1)
        rf.fit(X_train, y_train)
        
        # Predict
        y_pred = rf.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        accuracies.append(accuracy)
        
        print(f"  Iteration {i+1}: {accuracy:.4f}")
    
    mean_accuracy = np.mean(accuracies)
    std_accuracy = np.std(accuracies)
    
    print(f"\n📊 Permutation Test Results:")
    print(f"  Mean Accuracy: {mean_accuracy:.4f}")
    print(f"  Std Accuracy: {std_accuracy:.4f}")
    
    if mean_accuracy > 0.8:
        print("🚨 HIGH PERMUTATION ACCURACY - Features contain label information!")
    elif mean_accuracy > 0.6:
        print("⚠️ Moderate permutation accuracy - Some feature contamination")
    else:
        print("✅ Low permutation accuracy - Features are clean")
    
    return accuracies

def cross_dataset_validation(X, labels, source_datasets):
    """Test generalization across datasets"""
    print("\n🌍 Testing cross-dataset generalization...")
    
    # Split by dataset source
    scin_mask = np.array(source_datasets) == 'scin'
    utkface_mask = np.array(source_datasets) == 'utkface'
    
    X_scin = X[scin_mask]
    y_scin = labels[scin_mask]
    X_utkface = X[utkface_mask]
    y_utkface = labels[utkface_mask]
    
    print(f"SCIN: {np.sum(scin_mask)} samples")
    print(f"UTKFace: {np.sum(utkface_mask)} samples")
    
    # Test 1: Train on SCIN, test on UTKFace
    if len(y_scin) > 0 and len(y_utkface) > 0:
        print("\n🧪 Test 1: Train on SCIN, test on UTKFace")
        rf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
        rf.fit(X_scin, y_scin)
        
        y_pred = rf.predict(X_utkface)
        accuracy = accuracy_score(y_utkface, y_pred)
        
        print(f"  Cross-dataset accuracy: {accuracy:.4f}")
        
        if accuracy > 0.9:
            print("  🚨 SUSPICIOUS: High cross-dataset accuracy suggests data leakage")
        elif accuracy > 0.7:
            print("  ⚠️ Moderate: Some generalization but potential overfitting")
        else:
            print("  ✅ Good: Reasonable generalization across datasets")
    
    # Test 2: Train on UTKFace, test on SCIN
    if len(y_scin) > 0 and len(y_utkface) > 0:
        print("\n🧪 Test 2: Train on UTKFace, test on SCIN")
        rf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
        rf.fit(X_utkface, y_utkface)
        
        y_pred = rf.predict(X_scin)
        accuracy = accuracy_score(y_scin, y_pred)
        
        print(f"  Cross-dataset accuracy: {accuracy:.4f}")
        
        if accuracy > 0.9:
            print("  🚨 SUSPICIOUS: High cross-dataset accuracy suggests data leakage")
        elif accuracy > 0.7:
            print("  ⚠️ Moderate: Some generalization but potential overfitting")
        else:
            print("  ✅ Good: Reasonable generalization across datasets")

def main():
    """Main investigation function"""
    print("🚨 V7 Data Leakage Investigation")
    print("=" * 50)
    
    try:
        # Load dataset
        X, labels_condition, labels_age, labels_gender, labels_ethnicity, source_datasets = load_v7_dataset()
        
        # Analyze feature distributions
        analyze_feature_distributions(X, labels_condition, source_datasets)
        
        # Test feature-condition correlation
        rf, accuracy, feature_importance = test_feature_condition_correlation(X, labels_condition)
        
        # Permutation test
        permutation_accuracies = permutation_test(X, labels_condition)
        
        # Cross-dataset validation
        cross_dataset_validation(X, labels_condition, source_datasets)
        
        # Summary
        print("\n" + "=" * 50)
        print("📋 INVESTIGATION SUMMARY")
        print("=" * 50)
        
        if accuracy > 0.95:
            print("🚨 CRITICAL: 100% accuracy detected - HIGH RISK of data leakage")
            print("   Immediate action required before any production use")
        elif accuracy > 0.85:
            print("⚠️ WARNING: High accuracy detected - investigate further")
        else:
            print("✅ ACCEPTABLE: Reasonable accuracy level")
        
        print(f"\n🔍 Next steps:")
        print("   1. Review feature engineering pipeline")
        print("   2. Check for label contamination in features")
        print("   3. Implement proper cross-validation")
        print("   4. Test on completely independent dataset")
        
    except Exception as e:
        print(f"❌ Investigation failed: {e}")
        raise e

if __name__ == '__main__':
    main()
