#!/usr/bin/env python3
"""
Adjust SWAN CNN Thresholds
Make the model more sensitive to skin conditions
"""

import sys
import traceback
import numpy as np
from PIL import Image
from pathlib import Path

def adjust_swan_thresholds():
    """Adjust SWAN CNN thresholds to be more sensitive"""
    print("🔧 Adjusting SWAN CNN Thresholds")
    print("=" * 60)
    
    try:
        from swan_production_api_fixed import SWANProductionAPIFixed
        
        # Create SWAN API instance
        swan_api = SWANProductionAPIFixed()
        print("✅ SWAN CNN API created")
        
        # Test 1: Check current threshold behavior
        print("\n🧪 Test 1: Current Threshold Behavior")
        
        # Create test image with obvious acne
        test_image = np.ones((200, 200, 3), dtype=np.uint8) * 128
        
        # Add obvious red acne spots
        test_image[50:70, 50:70] = [255, 0, 0]  # Red spot 1
        test_image[100:120, 100:120] = [255, 0, 0]  # Red spot 2
        test_image[150:170, 150:170] = [255, 0, 0]  # Red spot 3
        
        pil_image = Image.fromarray(test_image)
        print(f"✅ Test image created with {3} obvious red spots")
        
        # Get raw prediction probabilities
        features = swan_api.process_image_real_pipeline_from_pil(pil_image)
        if features is not None:
            # Get raw probabilities from the model
            raw_probs = swan_api.model_pipeline['model'].predict_proba([features])[0]
            print(f"✅ Raw probabilities shape: {raw_probs.shape}")
            print(f"✅ Raw probabilities: {raw_probs}")
            
            # Check how many classes we have
            num_classes = len(raw_probs)
            print(f"   Number of classes: {num_classes}")
            
            # Current prediction
            current_pred = swan_api.predict(features)
            print(f"   Current prediction: {current_pred['prediction']}")
            print(f"   Current confidence: {current_pred['confidence']}")
            
            # Test 2: Analyze the model structure
            print("\n🧪 Test 2: Model Structure Analysis")
            
            model = swan_api.model_pipeline['model']
            print(f"   Model type: {type(model).__name__}")
            
            # Check model classes
            if hasattr(model, 'classes_'):
                print(f"   Model classes: {model.classes_}")
                print(f"   Number of classes: {len(model.classes_)}")
            else:
                print("   ❌ Model doesn't have classes_ attribute")
            
            # Check if we can access the model directly
            if hasattr(model, 'feature_importances_'):
                print(f"   Feature importances available: {len(model.feature_importances_)} features")
                
                # Check if any features have high importance
                top_features = np.argsort(model.feature_importances_)[-10:]
                print(f"   Top 10 feature indices: {top_features}")
                print(f"   Top feature importance: {model.feature_importances_[top_features[-1]]:.4f}")
            
            # Test 3: Try different threshold approaches
            print("\n🧪 Test 3: Testing Different Thresholds")
            
            if num_classes == 2:
                # Binary classification (HEALTHY vs CONDITION)
                print("   Binary classification detected")
                healthy_prob = raw_probs[0]
                condition_prob = raw_probs[1]
                
                print(f"      HEALTHY probability: {healthy_prob:.4f}")
                print(f"      CONDITION probability: {condition_prob:.4f}")
                
                # Try different decision thresholds
                thresholds = [0.5, 0.4, 0.3, 0.2, 0.1]
                
                for threshold in thresholds:
                    if condition_prob > threshold:
                        decision = "CONDITION"
                    else:
                        decision = "HEALTHY"
                    
                    print(f"      Threshold {threshold}: {decision} (CONDITION > {threshold})")
                    
            elif num_classes == 1:
                # Single class output - this is unusual
                print("   Single class output detected - this is unusual!")
                single_prob = raw_probs[0]
                print(f"      Single probability: {single_prob:.4f}")
                
                # This might be a regression model or binary threshold model
                print("      This suggests the model might be using a different approach")
                
            else:
                # Multi-class classification
                print(f"   Multi-class classification with {num_classes} classes")
                for i, prob in enumerate(raw_probs):
                    print(f"      Class {i} probability: {prob:.4f}")
            
            # Test 4: Check the predict method implementation
            print("\n🧪 Test 4: Predict Method Analysis")
            
            if hasattr(swan_api, 'predict'):
                print("✅ Predict method exists")
                
                # Let's look at the source code or understand how it works
                print("   Analyzing how predict method works...")
                
                # Check if we can access the decision function
                if hasattr(model, 'decision_function'):
                    print("      ✅ Model has decision_function")
                    
                    # Try decision function
                    try:
                        decision_scores = model.decision_function([features])[0]
                        print(f"      Decision scores: {decision_scores}")
                        
                        # Adjust threshold on decision scores
                        if isinstance(decision_scores, (int, float)):
                            adjusted_thresholds = [-0.5, -0.3, -0.1, 0.0, 0.1]
                            for adj_thresh in adjusted_thresholds:
                                if decision_scores > adj_thresh:
                                    decision = "CONDITION"
                                else:
                                    decision = "HEALTHY"
                                print(f"      Decision threshold {adj_thresh}: {decision}")
                        else:
                            print(f"      Decision scores type: {type(decision_scores)}")
                    except Exception as e:
                        print(f"      ❌ Decision function failed: {e}")
                else:
                    print("      ❌ Model doesn't have decision_function")
                
                # Test 5: Create a custom prediction method
                print("\n🧪 Test 5: Custom Prediction Method")
                
                if num_classes == 2:
                    def custom_predict_with_threshold(features, threshold=0.3):
                        """Custom prediction with adjustable threshold"""
                        probs = model.predict_proba([features])[0]
                        healthy_prob, condition_prob = probs
                        
                        if condition_prob > threshold:
                            return {
                                'prediction': 'CONDITION',
                                'confidence': condition_prob,
                                'probabilities': {'HEALTHY': healthy_prob, 'CONDITION': condition_prob}
                            }
                        else:
                            return {
                                'prediction': 'HEALTHY',
                                'confidence': healthy_prob,
                                'probabilities': {'HEALTHY': healthy_prob, 'CONDITION': condition_prob}
                            }
                    
                    # Test custom method with different thresholds
                    print("   Testing custom prediction method:")
                    for threshold in [0.1, 0.2, 0.3, 0.4, 0.5]:
                        result = custom_predict_with_threshold(features, threshold)
                        print(f"      Threshold {threshold}: {result['prediction']} (confidence: {result['confidence']:.3f})")
                
                # Test 6: Test with real image from Kris directory
                print("\n🧪 Test 6: Testing with Real Image")
                
                kris_dir = Path("../Kris")
                if kris_dir.exists():
                    # Look for acne image
                    acne_image = kris_dir / "acne-2-months-into-doing-light-skincare-routine-and-my-skin-v0-ual1lntun9591.webp"
                    
                    if acne_image.exists():
                        print(f"   Testing with real acne image: {acne_image.name}")
                        
                        with Image.open(acne_image) as img:
                            if img.mode != 'RGB':
                                img = img.convert('RGB')
                            
                            # Test with different thresholds
                            real_features = swan_api.process_image_real_pipeline_from_pil(img)
                            if real_features is not None:
                                print("      Real image features extracted")
                                
                                if num_classes == 2:
                                    for threshold in [0.1, 0.2, 0.3, 0.4, 0.5]:
                                        result = custom_predict_with_threshold(real_features, threshold)
                                        print(f"      Threshold {threshold}: {result['prediction']} (confidence: {result['confidence']:.3f})")
                                else:
                                    print("      ❌ Cannot test custom thresholds with non-binary model")
                            else:
                                print("      ❌ Failed to extract features from real image")
                    else:
                        print("   ❌ Real acne image not found")
                else:
                    print("   ❌ Kris directory not found")
                
            else:
                print("❌ Predict method not found")
                
        else:
            print("❌ Feature extraction failed")
        
        return True
        
    except Exception as e:
        print(f"❌ Threshold adjustment failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Main function"""
    print("🚀 SWAN CNN Threshold Adjustment")
    print("=" * 60)
    
    success = adjust_swan_thresholds()
    
    if success:
        print("\n🔧 Threshold analysis completed.")
        print("Check the results above to see which threshold works best.")
    else:
        print("\n❌ Threshold adjustment failed.")
    
    return success

if __name__ == "__main__":
    main()
