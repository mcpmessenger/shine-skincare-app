#!/usr/bin/env python3
"""
Diagnose Zero Accuracy Issues for Shine Skincare App
Analyzes why acne and actinic_keratosis have 0% accuracy despite having 88 images each
"""

import os
import json
import logging
from pathlib import Path
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from PIL import Image
import matplotlib.pyplot as plt

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ZeroAccuracyDiagnostic:
    def __init__(self):
        self.data_dir = Path("data/all_available_data")
        self.splits_dir = self.data_dir / "processed" / "splits"
        self.models_dir = Path("models")
        self.results_dir = Path("results")
        
        # Load the trained model
        self.model_path = self.models_dir / "all_data_model_final.h5"
        
    def check_image_quality(self):
        """Check if images are properly processed and readable"""
        logger.info("Checking image quality...")
        
        problematic_conditions = ["acne", "actinic_keratosis"]
        
        for condition in problematic_conditions:
            print(f"\n🔍 Analyzing {condition} images:")
            
            # Check processed directory
            processed_dir = self.data_dir / "processed" / condition
            if processed_dir.exists():
                image_files = list(processed_dir.glob("*.jpg")) + list(processed_dir.glob("*.png"))
                print(f"  📁 Processed directory: {len(image_files)} images")
                
                # Test first few images
                for i, img_file in enumerate(image_files[:5]):
                    try:
                        with Image.open(img_file) as img:
                            print(f"    ✅ {img_file.name}: {img.size}, mode={img.mode}")
                    except Exception as e:
                        print(f"    ❌ {img_file.name}: Error - {e}")
            
            # Check test directory
            test_dir = self.splits_dir / "test" / condition
            if test_dir.exists():
                test_files = list(test_dir.glob("*.jpg")) + list(test_dir.glob("*.png"))
                print(f"  📁 Test directory: {len(test_files)} images")
                
                # Test first few images
                for i, img_file in enumerate(test_files[:3]):
                    try:
                        with Image.open(img_file) as img:
                            print(f"    ✅ {img_file.name}: {img.size}, mode={img.mode}")
                    except Exception as e:
                        print(f"    ❌ {img_file.name}: Error - {e}")
    
    def analyze_model_predictions(self):
        """Analyze what the model is actually predicting for these classes"""
        logger.info("Analyzing model predictions...")
        
        if not self.model_path.exists():
            print("❌ Model not found!")
            return
        
        # Load model
        model = load_model(self.model_path)
        
        # Load test data
        test_datagen = ImageDataGenerator(rescale=1./255)
        test_generator = test_datagen.flow_from_directory(
            self.splits_dir / "test",
            target_size=(224, 224),
            batch_size=1,
            class_mode='categorical',
            shuffle=False
        )
        
        print(f"\n📊 Test Generator Info:")
        print(f"  Total samples: {test_generator.samples}")
        print(f"  Class indices: {test_generator.class_indices}")
        
        # Get predictions
        test_generator.reset()
        predictions = model.predict(test_generator, verbose=0)
        predicted_classes = np.argmax(predictions, axis=1)
        true_classes = test_generator.classes
        confidence_scores = np.max(predictions, axis=1)
        
        class_names = list(test_generator.class_indices.keys())
        
        print(f"\n🎯 Prediction Analysis:")
        print(f"  Total predictions: {len(predictions)}")
        print(f"  Average confidence: {np.mean(confidence_scores):.3f}")
        
        # Analyze each class
        for i, class_name in enumerate(class_names):
            class_mask = true_classes == i
            if np.sum(class_mask) > 0:
                class_predictions = predicted_classes[class_mask]
                class_confidences = confidence_scores[class_mask]
                
                correct_predictions = np.sum(class_predictions == i)
                total_samples = len(class_predictions)
                accuracy = correct_predictions / total_samples
                
                print(f"\n  📊 {class_name.upper()}:")
                print(f"    Samples: {total_samples}")
                print(f"    Correct: {correct_predictions}")
                print(f"    Accuracy: {accuracy:.1%}")
                print(f"    Avg confidence: {np.mean(class_confidences):.3f}")
                
                # Show what this class is being predicted as
                unique_predictions, counts = np.unique(class_predictions, return_counts=True)
                print(f"    Prediction breakdown:")
                for pred_idx, count in zip(unique_predictions, counts):
                    pred_class = class_names[pred_idx]
                    percentage = (count / total_samples) * 100
                    print(f"      → {pred_class}: {count} ({percentage:.1f}%)")
    
    def check_data_distribution(self):
        """Check the distribution of data across splits"""
        logger.info("Checking data distribution...")
        
        splits = ["train", "val", "test"]
        conditions = ["acne", "actinic_keratosis", "rosacea", "eczema", "basal_cell_carcinoma", "healthy"]
        
        print(f"\n📊 Data Distribution:")
        print(f"{'Condition':<20} {'Train':<8} {'Val':<8} {'Test':<8} {'Total':<8}")
        print("-" * 60)
        
        for condition in conditions:
            train_count = len(list((self.splits_dir / "train" / condition).glob("*.jpg"))) + len(list((self.splits_dir / "train" / condition).glob("*.png")))
            val_count = len(list((self.splits_dir / "val" / condition).glob("*.jpg"))) + len(list((self.splits_dir / "val" / condition).glob("*.png")))
            test_count = len(list((self.splits_dir / "test" / condition).glob("*.jpg"))) + len(list((self.splits_dir / "test" / condition).glob("*.png")))
            total = train_count + val_count + test_count
            
            print(f"{condition:<20} {train_count:<8} {val_count:<8} {test_count:<8} {total:<8}")
    
    def suggest_fixes(self):
        """Suggest fixes for the zero accuracy issue"""
        print(f"\n💡 SUGGESTED FIXES:")
        print(f"  1. 🔍 Check if images are properly processed:")
        print(f"     - Verify all 88 acne and 88 actinic_keratosis images are valid")
        print(f"     - Check for corrupted or empty image files")
        print(f"     - Ensure proper RGB conversion")
        
        print(f"  2. 🎯 Model Bias Issues:")
        print(f"     - The model might be biased toward certain classes")
        print(f"     - Try class weights to balance training")
        print(f"     - Consider data augmentation specific to these classes")
        
        print(f"  3. 📊 Data Quality:")
        print(f"     - Verify image quality and resolution")
        print(f"     - Check for consistent preprocessing")
        print(f"     - Ensure proper train/val/test splits")
        
        print(f"  4. 🔧 Technical Solutions:")
        print(f"     - Retrain with class weights")
        print(f"     - Use focal loss for imbalanced classes")
        print(f"     - Increase data augmentation for problematic classes")
        print(f"     - Try a simpler model architecture")
    
    def run_diagnostic(self):
        """Run complete diagnostic"""
        logger.info("Starting zero accuracy diagnostic...")
        
        print("="*70)
        print("ZERO ACCURACY DIAGNOSTIC")
        print("="*70)
        
        # Step 1: Check image quality
        self.check_image_quality()
        
        # Step 2: Analyze model predictions
        self.analyze_model_predictions()
        
        # Step 3: Check data distribution
        self.check_data_distribution()
        
        # Step 4: Suggest fixes
        self.suggest_fixes()
        
        print(f"\n✅ Diagnostic completed!")
        print(f"📋 Check the analysis above for insights")

def main():
    """Main function"""
    print("="*70)
    print("Shine Skincare App - Zero Accuracy Diagnostic")
    print("="*70)
    print("This analyzes why acne and actinic_keratosis have 0% accuracy")
    print("despite having 88 images each in the medical dataset.")
    print("="*70)
    
    # Create diagnostic
    diagnostic = ZeroAccuracyDiagnostic()
    
    # Run diagnostic
    diagnostic.run_diagnostic()

if __name__ == "__main__":
    main()
