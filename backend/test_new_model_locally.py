#!/usr/bin/env python3
"""
Local Model Testing Script
Test the newly trained model with sample images
"""

import os
import sys
import json
import numpy as np
from pathlib import Path
import tensorflow as tf
from PIL import Image
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LocalModelTester:
    def __init__(self):
        self.models_dir = Path("models")
        self.test_images_dir = Path("data/balanced_medical_dataset/processed")
        self.results_dir = Path("results")
        
        # Class names from our balanced dataset
        self.class_names = [
            "acne", "actinic_keratosis", "basal_cell_carcinoma", 
            "eczema", "healthy", "rosacea"
        ]
        
    def load_latest_model(self):
        """Load the most recently trained model"""
        model_files = list(self.models_dir.glob("comprehensive_model*.h5"))
        
        if not model_files:
            logger.error("❌ No trained models found!")
            return None
            
        # Get the most recent model
        latest_model = max(model_files, key=os.path.getmtime)
        logger.info(f"🤖 Loading model: {latest_model.name}")
        
        try:
            # Custom focal loss function for loading
            def focal_loss(y_true, y_pred):
                alpha = 0.25
                gamma = 2.0
                epsilon = tf.keras.backend.epsilon()
                y_pred = tf.clip_by_value(y_pred, epsilon, 1.0 - epsilon)
                ce_loss = -y_true * tf.math.log(y_pred)
                p_t = y_true * y_pred + (1 - y_true) * (1 - y_pred)
                alpha_t = y_true * alpha + (1 - y_true) * (1 - alpha)
                focal_loss = alpha_t * tf.pow(1 - p_t, gamma) * ce_loss
                return tf.reduce_mean(focal_loss)
            
            model = tf.keras.models.load_model(
                str(latest_model),
                custom_objects={'focal_loss': focal_loss}
            )
            logger.info("✅ Model loaded successfully!")
            return model
            
        except Exception as e:
            logger.error(f"❌ Failed to load model: {e}")
            return None
    
    def preprocess_image(self, image_path):
        """Preprocess image for model prediction"""
        try:
            # Load and resize image
            image = Image.open(image_path).convert('RGB')
            image = image.resize((224, 224))
            
            # Convert to array and normalize
            image_array = np.array(image) / 255.0
            image_array = np.expand_dims(image_array, axis=0)
            
            return image_array
            
        except Exception as e:
            logger.error(f"❌ Failed to preprocess {image_path}: {e}")
            return None
    
    def test_sample_images(self, model, num_samples_per_class=3):
        """Test model on sample images from each class"""
        logger.info("🔍 Testing model on sample images...")
        
        results = {
            "test_results": [],
            "accuracy_by_class": {},
            "overall_accuracy": 0,
            "critical_condition_accuracy": {},
            "common_condition_accuracy": {}
        }
        
        total_correct = 0
        total_tested = 0
        
        critical_conditions = ["basal_cell_carcinoma", "actinic_keratosis"]
        common_conditions = ["acne", "rosacea", "eczema"]
        
        for class_name in self.class_names:
            class_dir = self.test_images_dir / class_name
            
            if not class_dir.exists():
                logger.warning(f"⚠️ No test images found for {class_name}")
                continue
                
            # Get sample images
            image_files = list(class_dir.glob("*.jpg")) + list(class_dir.glob("*.png"))
            sample_images = image_files[:num_samples_per_class]
            
            class_correct = 0
            class_total = len(sample_images)
            
            logger.info(f"🔍 Testing {class_name}: {class_total} images")
            
            for img_path in sample_images:
                # Preprocess image
                processed_img = self.preprocess_image(img_path)
                if processed_img is None:
                    continue
                
                # Make prediction
                prediction = model.predict(processed_img, verbose=0)
                predicted_class_idx = np.argmax(prediction[0])
                predicted_class = self.class_names[predicted_class_idx]
                confidence = float(np.max(prediction[0]))
                
                # Check if correct
                is_correct = (predicted_class == class_name)
                if is_correct:
                    class_correct += 1
                    total_correct += 1
                
                total_tested += 1
                
                # Store result
                result = {
                    "image": str(img_path.name),
                    "true_class": class_name,
                    "predicted_class": predicted_class,
                    "confidence": confidence,
                    "correct": is_correct,
                    "all_probabilities": {
                        self.class_names[i]: float(prediction[0][i]) 
                        for i in range(len(self.class_names))
                    }
                }
                results["test_results"].append(result)
                
                # Print result
                status = "✅" if is_correct else "❌"
                print(f"   {status} {img_path.name}: {predicted_class} ({confidence:.3f})")
            
            # Calculate class accuracy
            class_accuracy = class_correct / class_total if class_total > 0 else 0
            results["accuracy_by_class"][class_name] = {
                "correct": class_correct,
                "total": class_total,
                "accuracy": class_accuracy
            }
            
            # Categorize by condition type
            if class_name in critical_conditions:
                results["critical_condition_accuracy"][class_name] = class_accuracy
            elif class_name in common_conditions:
                results["common_condition_accuracy"][class_name] = class_accuracy
            
            print(f"   📊 {class_name}: {class_correct}/{class_total} ({class_accuracy:.3f})")
        
        # Calculate overall accuracy
        results["overall_accuracy"] = total_correct / total_tested if total_tested > 0 else 0
        
        return results
    
    def print_summary(self, results):
        """Print test summary"""
        print("\n" + "="*60)
        print("🏥 MODEL TESTING SUMMARY")
        print("="*60)
        
        # Overall accuracy
        overall_acc = results["overall_accuracy"]
        print(f"📊 Overall Accuracy: {overall_acc:.3f} ({overall_acc*100:.1f}%)")
        
        # Critical conditions
        print(f"\n🚨 Critical Condition Accuracy:")
        for condition, accuracy in results["critical_condition_accuracy"].items():
            print(f"   {condition:25}: {accuracy:.3f} ({accuracy*100:.1f}%)")
        
        # Common conditions
        print(f"\n🔍 Common Condition Accuracy:")
        for condition, accuracy in results["common_condition_accuracy"].items():
            print(f"   {condition:25}: {accuracy:.3f} ({accuracy*100:.1f}%)")
        
        # Improvement assessment
        print(f"\n📈 IMPROVEMENT ASSESSMENT:")
        acne_acc = results["common_condition_accuracy"].get("acne", 0)
        carcinoma_acc = results["critical_condition_accuracy"].get("basal_cell_carcinoma", 0)
        
        print(f"   🎯 Acne Detection: {acne_acc:.3f} (was 0.000)")
        print(f"   🚨 Carcinoma Detection: {carcinoma_acc:.3f} (was 0.000)")
        
        if acne_acc > 0.5:
            print("   ✅ Acne detection significantly improved!")
        elif acne_acc > 0.2:
            print("   📈 Acne detection showing progress...")
        else:
            print("   ⚠️ Acne detection still needs work")
            
        if carcinoma_acc > 0.7:
            print("   ✅ Carcinoma detection excellent!")
        elif carcinoma_acc > 0.4:
            print("   📈 Carcinoma detection improved...")
        else:
            print("   ⚠️ Carcinoma detection needs attention")
    
    def save_results(self, results):
        """Save test results to file"""
        timestamp = Path(str(self.results_dir / f"local_test_results_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.json"))
        
        with open(timestamp, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"💾 Results saved: {timestamp}")
    
    def run_local_test(self):
        """Run complete local testing"""
        print("🧪 LOCAL MODEL TESTING")
        print("="*40)
        
        # Load model
        model = self.load_latest_model()
        if model is None:
            return False
        
        # Test on sample images
        results = self.test_sample_images(model)
        
        # Print summary
        self.print_summary(results)
        
        # Save results
        self.save_results(results)
        
        return True

if __name__ == "__main__":
    import pandas as pd
    
    tester = LocalModelTester()
    success = tester.run_local_test()
    
    if success:
        print("\n✅ Local testing completed!")
        print("🚀 Ready to deploy if results look good!")
    else:
        print("\n❌ Local testing failed!")
