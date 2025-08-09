#!/usr/bin/env python3
"""
Real-time Training Monitor
Watch the progress of the medical model training
"""

import time
import os
import json
from pathlib import Path
import pandas as pd

def monitor_training():
    """Monitor training progress in real-time"""
    print("🔍 REAL-TIME TRAINING MONITOR")
    print("="*60)
    print("⏱️  Training: 80 epochs with balanced UTKFace dataset")
    print("🎯 Target: Fix 0% accuracy on acne/carcinoma")
    print("📊 Press Ctrl+C to stop monitoring")
    print("="*60)
    
    results_dir = Path('results')
    models_dir = Path('models')
    
    last_epoch = 0
    last_model_time = 0
    
    try:
        while True:
            print(f"\n🕐 {time.strftime('%H:%M:%S')} - Checking progress...")
            
            # Check for CSV training logs
            csv_files = list(results_dir.glob('*training_log*.csv'))
            
            if csv_files:
                latest_csv = max(csv_files, key=os.path.getmtime)
                
                try:
                    df = pd.read_csv(latest_csv)
                    current_epoch = len(df)
                    
                    if current_epoch > last_epoch:
                        last_epoch = current_epoch
                        
                        if current_epoch > 0:
                            latest_row = df.iloc[-1]
                            
                            print(f"📈 EPOCH {current_epoch}/80:")
                            print(f"   🎯 Accuracy: {latest_row.get('accuracy', 'N/A'):.4f}")
                            print(f"   🔍 Val Accuracy: {latest_row.get('val_accuracy', 'N/A'):.4f}")
                            print(f"   📉 Loss: {latest_row.get('loss', 'N/A'):.4f}")
                            print(f"   📊 Val Loss: {latest_row.get('val_loss', 'N/A'):.4f}")
                            
                            # Progress bar
                            progress = current_epoch / 80
                            bar_length = 30
                            filled_length = int(bar_length * progress)
                            bar = '█' * filled_length + '-' * (bar_length - filled_length)
                            print(f"   ⏳ Progress: |{bar}| {progress*100:.1f}%")
                            
                            # Estimate time remaining
                            if current_epoch > 1:
                                avg_time_per_epoch = (time.time() - os.path.getmtime(latest_csv)) / current_epoch
                                remaining_epochs = 80 - current_epoch
                                eta_minutes = (remaining_epochs * avg_time_per_epoch) / 60
                                print(f"   ⏰ ETA: ~{eta_minutes:.1f} minutes")
                    
                except Exception as e:
                    print(f"   ⚠️ Could not read training log: {e}")
            
            # Check for new model files
            model_files = list(models_dir.glob('*comprehensive*.h5'))
            if model_files:
                latest_model = max(model_files, key=os.path.getmtime)
                model_time = os.path.getmtime(latest_model)
                
                if model_time > last_model_time:
                    last_model_time = model_time
                    print(f"   💾 New model saved: {latest_model.name}")
            
            # Check if training completed
            if last_epoch >= 80:
                print("\n🎉 TRAINING COMPLETED!")
                print("🔬 Running transparency analysis...")
                break
            
            # Wait before next check
            time.sleep(10)  # Check every 10 seconds
            
    except KeyboardInterrupt:
        print("\n⏹️ Monitoring stopped by user")
    
    # Check for final results
    print("\n📊 CHECKING FINAL RESULTS...")
    
    # Look for transparency analysis
    analysis_files = list(results_dir.glob('*transparent_analysis*.json'))
    if analysis_files:
        latest_analysis = max(analysis_files, key=os.path.getmtime)
        print(f"🔍 Latest analysis: {latest_analysis.name}")
        
        try:
            with open(latest_analysis, 'r') as f:
                analysis = json.load(f)
            
            print("\n🏥 MEDICAL ACCURACY RESULTS:")
            print("-" * 40)
            
            # Critical conditions
            critical_performance = analysis.get('critical_condition_performance', {})
            for condition, stats in critical_performance.items():
                accuracy = stats.get('accuracy', 0)
                print(f"🚨 {condition:25}: {accuracy:.3f} ({accuracy*100:.1f}%)")
            
            # Common conditions  
            common_performance = analysis.get('common_condition_performance', {})
            for condition, stats in common_performance.items():
                accuracy = stats.get('accuracy', 0)
                print(f"🔍 {condition:25}: {accuracy:.3f} ({accuracy*100:.1f}%)")
            
            # Overall stats
            total_predictions = analysis.get('total_predictions', 0)
            misclassifications = len(analysis.get('misclassification_details', []))
            overall_accuracy = 1 - (misclassifications / total_predictions) if total_predictions > 0 else 0
            
            print(f"\n📊 Overall Accuracy: {overall_accuracy:.3f} ({overall_accuracy*100:.1f}%)")
            print(f"📈 Total Predictions: {total_predictions}")
            print(f"❌ Misclassifications: {misclassifications}")
            
        except Exception as e:
            print(f"⚠️ Could not read analysis: {e}")
    
    print("\n✅ Monitoring complete!")

if __name__ == "__main__":
    monitor_training()
