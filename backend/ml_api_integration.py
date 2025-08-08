#!/usr/bin/env python3
"""
ML API Integration for Shine Skincare App
Integrates enhanced ML model with existing Flask API while maintaining backward compatibility
"""

import os
import json
import logging
import numpy as np
import cv2
import tensorflow as tf
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from datetime import datetime
import traceback

# Import existing API components
from enhanced_analysis_api import app
from real_skin_analysis import RealSkinAnalysis

# Import enhanced ML components
from ml_enhanced_model import EnhancedSkinModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedMLIntegration:
    """Integration class for enhanced ML model with existing API"""
    
    def __init__(self, model_path: str = "models/simple_skin_model.h5"):
        """
        Initialize the enhanced ML integration
        
        Args:
            model_path: Path to the trained enhanced model
        """
        self.model_path = Path(model_path)
        self.enhanced_model = None
        self.model_metadata = None
        self.label_encoders = {}
        self.scalers = {}
        
        # Load model and metadata
        self._load_enhanced_model()
        
        # Keep existing analysis system for fallback
        self.existing_analyzer = RealSkinAnalysis()
        
        logger.info("✅ Enhanced ML Integration initialized")
    
    def _load_enhanced_model(self):
        """Load the enhanced ML model and metadata"""
        try:
            # Load model
            if self.model_path.exists():
                self.enhanced_model = EnhancedSkinModel()
                success = self.enhanced_model.load_model(str(self.model_path))
                
                if success:
                    logger.info("✅ Enhanced ML model loaded successfully")
                else:
                    logger.warning("⚠️ Failed to load enhanced model, will use fallback")
                    self.enhanced_model = None
            else:
                logger.warning("⚠️ Enhanced model not found, will use fallback")
                self.enhanced_model = None
            
            # Load metadata
            metadata_path = self.model_path.parent / "model_metadata.json"
            if metadata_path.exists():
                with open(metadata_path, 'r') as f:
                    self.model_metadata = json.load(f)
                
                # Load label encoders and scalers
                self._load_preprocessing_components()
                
                logger.info("✅ Model metadata loaded successfully")
            else:
                logger.warning("⚠️ Model metadata not found")
                
        except Exception as e:
            logger.error(f"❌ Failed to load enhanced model: {e}")
            self.enhanced_model = None
    
    def _load_preprocessing_components(self):
        """Load label encoders and scalers from metadata"""
        try:
            if self.model_metadata and 'label_encoders' in self.model_metadata:
                # In a real implementation, you'd load the actual encoders
                # For now, we'll use the class lists
                self.label_encoders = {
                    'condition_classes': self.model_metadata['label_encoders']['condition_classes'],
                    'gender_classes': self.model_metadata['label_encoders']['gender_classes'],
                    'ethnicity_classes': self.model_metadata['label_encoders']['ethnicity_classes']
                }
            
            if self.model_metadata and 'scalers' in self.model_metadata:
                self.scalers = self.model_metadata['scalers']
                
        except Exception as e:
            logger.warning(f"⚠️ Failed to load preprocessing components: {e}")
    
    def analyze_skin_enhanced(self, image_data: bytes, user_demographics: Dict = None) -> Dict:
        """
        Enhanced skin analysis using the new ML model
        
        Args:
            image_data: Raw image bytes
            user_demographics: Optional user demographic information
            
        Returns:
            Dictionary containing comprehensive analysis results
        """
        try:
            # Convert image data to numpy array
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                raise ValueError("Failed to decode image")
            
            # Use enhanced model if available
            if self.enhanced_model is not None:
                return self._analyze_with_enhanced_model(image, user_demographics)
            else:
                # Fallback to existing analysis
                logger.warning("⚠️ Using fallback analysis system")
                return self._analyze_with_fallback(image, user_demographics)
                
        except Exception as e:
            logger.error(f"❌ Enhanced analysis failed: {e}")
            logger.error(f"❌ Full traceback: {traceback.format_exc()}")
            return self._create_error_response(str(e))
    
    def _analyze_with_enhanced_model(self, image: np.ndarray, user_demographics: Dict = None) -> Dict:
        """Analyze image using the simple ML model"""
        try:
            # Preprocess image for simple model
            processed_image = self._preprocess_for_enhanced_model(image)
            
            # Make prediction with simple model (single output)
            predictions = self.enhanced_model.model.predict(processed_image)
            
            # Simple model only has condition prediction
            condition_pred = predictions[0]
            
            # Decode predictions for simple model
            condition_result = self._decode_condition_prediction(condition_pred)
            
            # Create simplified analysis result for simple model
            analysis_result = {
                'analysis_type': 'simple_ml',
                'timestamp': datetime.now().isoformat(),
                'model_version': 'simple_v1.0',
                
                # Primary condition analysis
                'primary_condition': condition_result,
                
                # Confidence and reliability
                'confidence': {
                    'overall': float(condition_result['confidence']),
                    'condition_detection': float(condition_result['confidence'])
                },
                
                # Severity assessment (simplified)
                'severity': {
                    'level': 'low' if condition_result['confidence'] > 0.5 else 'medium',
                    'description': f"Condition detected with {condition_result['confidence']:.1%} confidence"
                },
                
                # Recommendations (simplified)
                'recommendations': [
                    f"Based on the analysis, you may have {condition_result['condition']}",
                    "Consider consulting with a dermatologist for professional evaluation",
                    "Maintain good skincare hygiene",
                    "Monitor any changes in your skin condition"
                ],
                
                # Analysis summary
                'summary': f"Detected condition: {condition_result['condition']} with {condition_result['confidence']:.1%} confidence",
                
                # Technical details
                'technical_details': {
                    'model_used': 'simple_cnn',
                    'attention_mechanisms': False,
                    'fairness_mitigation': False
                }
            }
            
            logger.info(f"✅ Enhanced analysis completed for condition: {condition_result['condition']}")
            return analysis_result
            
        except Exception as e:
            logger.error(f"❌ Enhanced model analysis failed: {e}")
            return self._create_error_response(str(e))
    
    def _analyze_with_fallback(self, image: np.ndarray, user_demographics: Dict = None) -> Dict:
        """Fallback analysis using existing system"""
        try:
            # Convert image to bytes for existing API
            _, img_encoded = cv2.imencode('.jpg', image)
            image_bytes = img_encoded.tobytes()
            
            # Use existing analysis
            result = self.existing_analyzer.analyze_skin_real(image_bytes, user_demographics)
            
            # Add fallback indicator
            result['analysis_type'] = 'fallback_existing'
            result['model_version'] = 'existing_v1.0'
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Fallback analysis failed: {e}")
            return self._create_error_response(str(e))
    
    def _preprocess_for_enhanced_model(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for enhanced model"""
        # Resize to model input size
        image = cv2.resize(image, (224, 224))
        
        # Convert BGR to RGB
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Normalize to 0-1 range
        image = image.astype(np.float32) / 255.0
        
        # Add batch dimension
        image = np.expand_dims(image, axis=0)
        
        return image
    
    def _decode_condition_prediction(self, pred: np.ndarray) -> Dict:
        """Decode condition classification prediction"""
        conditions = ['healthy', 'acne', 'eczema', 'keratosis', 'milia', 'rosacea']
        condition_idx = np.argmax(pred)
        confidence = float(pred[condition_idx])
        
        return {
            'condition': conditions[condition_idx],
            'confidence': confidence,
            'all_probabilities': pred.tolist(),
            'condition_id': condition_idx
        }
    
    def _decode_age_prediction(self, pred: np.ndarray) -> Dict:
        """Decode age regression prediction"""
        # Denormalize age prediction
        if self.scalers and 'age_mean' in self.scalers and 'age_scale' in self.scalers:
            age = pred[0] * self.scalers['age_scale'] + self.scalers['age_mean']
        else:
            age = float(pred[0])
        
        return {
            'age': max(0, min(100, age)),  # Clamp to reasonable range
            'confidence': 0.8  # Placeholder confidence
        }
    
    def _decode_gender_prediction(self, pred: np.ndarray) -> Dict:
        """Decode gender classification prediction"""
        genders = ['male', 'female']
        gender_idx = np.argmax(pred)
        confidence = float(pred[gender_idx])
        
        return {
            'gender': genders[gender_idx],
            'confidence': confidence
        }
    
    def _decode_ethnicity_prediction(self, pred: np.ndarray) -> Dict:
        """Decode ethnicity classification prediction"""
        ethnicities = ['white', 'black', 'asian', 'indian', 'hispanic', 'middle_eastern', 'other']
        ethnicity_idx = np.argmax(pred)
        confidence = float(pred[ethnicity_idx])
        
        return {
            'ethnicity': ethnicities[ethnicity_idx],
            'confidence': confidence
        }
    
    def _decode_skin_characteristics(self, pred: np.ndarray) -> Dict:
        """Decode skin characteristics prediction"""
        return {
            'redness': float(pred[0]),
            'texture': float(pred[1]),
            'pigmentation': float(pred[2])
        }
    
    def _assess_severity(self, condition_result: Dict, skin_char_result: Dict) -> Dict:
        """Assess condition severity based on predictions"""
        condition = condition_result['condition']
        confidence = condition_result['confidence']
        
        # Base severity on confidence and skin characteristics
        if condition == 'healthy':
            severity = 'none'
        elif confidence > 0.8:
            severity = 'high'
        elif confidence > 0.6:
            severity = 'moderate'
        else:
            severity = 'low'
        
        return {
            'level': severity,
            'confidence': confidence,
            'factors': {
                'condition_confidence': confidence,
                'skin_characteristics': skin_char_result
            }
        }
    
    def _generate_recommendations(self, condition_result: Dict, skin_char_result: Dict, 
                                user_demographics: Dict = None) -> Dict:
        """Generate personalized recommendations"""
        condition = condition_result['condition']
        
        # Base recommendations by condition
        base_recommendations = {
            'healthy': [
                'Maintain current skincare routine',
                'Use daily sunscreen with SPF 30+',
                'Stay hydrated and maintain healthy diet'
            ],
            'acne': [
                'Use gentle cleanser twice daily',
                'Apply benzoyl peroxide or salicylic acid',
                'Avoid touching face frequently',
                'Consider consulting a dermatologist'
            ],
            'eczema': [
                'Use fragrance-free moisturizers',
                'Avoid hot showers and harsh soaps',
                'Apply prescribed topical treatments',
                'Consult dermatologist for severe cases'
            ],
            'keratosis': [
                'Use gentle exfoliation',
                'Apply moisturizing creams',
                'Protect skin from sun exposure',
                'Consider professional treatment'
            ],
            'milia': [
                'Use gentle exfoliation',
                'Avoid heavy creams around eyes',
                'Consider professional extraction',
                'Maintain gentle skincare routine'
            ],
            'rosacea': [
                'Use gentle, fragrance-free products',
                'Avoid triggers (spicy foods, alcohol)',
                'Apply prescribed medications',
                'Protect skin from sun and wind'
            ]
        }
        
        recommendations = base_recommendations.get(condition, [
            'Consult a dermatologist for proper diagnosis',
            'Maintain gentle skincare routine',
            'Protect skin from sun exposure'
        ])
        
        return {
            'primary_recommendations': recommendations[:3],
            'secondary_recommendations': recommendations[3:],
            'consultation_needed': condition != 'healthy',
            'urgency': 'high' if condition_result['confidence'] > 0.8 and condition != 'healthy' else 'normal'
        }
    
    def _generate_analysis_summary(self, condition_result: Dict, skin_char_result: Dict) -> str:
        """Generate human-readable analysis summary"""
        condition = condition_result['condition']
        confidence = condition_result['confidence']
        
        if condition == 'healthy':
            summary = f"Your skin appears healthy with {confidence:.1%} confidence. "
            summary += "Continue with your current skincare routine."
        else:
            summary = f"Analysis detected {condition} with {confidence:.1%} confidence. "
            summary += "Consider the recommendations provided and consult a dermatologist if needed."
        
        return summary
    
    def _calculate_embedding_distinctiveness(self, embedding: np.ndarray) -> float:
        """Calculate embedding distinctiveness score"""
        # This is a simplified calculation
        # In practice, you'd compare with a reference set
        return float(np.linalg.norm(embedding))
    
    def _create_error_response(self, error_message: str) -> Dict:
        """Create standardized error response"""
        return {
            'analysis_type': 'error',
            'timestamp': datetime.now().isoformat(),
            'error': {
                'message': error_message,
                'type': 'analysis_failure'
            },
            'primary_condition': {
                'condition': 'unknown',
                'confidence': 0.0
            },
            'confidence': {
                'overall': 0.0
            },
            'summary': 'Analysis failed. Please try again or contact support.'
        }

# Initialize the integration
enhanced_ml_integration = EnhancedMLIntegration()

# Add new API endpoints
@app.route('/api/v4/skin/analyze-enhanced', methods=['POST'])
def analyze_skin_enhanced_endpoint():
    """Enhanced skin analysis endpoint using new ML model"""
    try:
        # Get request data
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
        
        image_file = request.files['image']
        image_data = image_file.read()
        
        # Get optional demographics
        user_demographics = request.form.get('demographics')
        if user_demographics:
            try:
                user_demographics = json.loads(user_demographics)
            except:
                user_demographics = None
        
        # Perform enhanced analysis
        result = enhanced_ml_integration.analyze_skin_enhanced(image_data, user_demographics)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"❌ Enhanced analysis endpoint failed: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/v4/system/enhanced-status', methods=['GET'])
def get_enhanced_system_status():
    """Get enhanced system status"""
    try:
        status = {
            'enhanced_model_loaded': enhanced_ml_integration.enhanced_model is not None,
            'model_path': str(enhanced_ml_integration.model_path),
            'model_exists': enhanced_ml_integration.model_path.exists(),
            'metadata_loaded': enhanced_ml_integration.model_metadata is not None,
            'analysis_type': 'enhanced' if enhanced_ml_integration.enhanced_model else 'fallback',
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"❌ Enhanced status endpoint failed: {e}")
        return jsonify({'error': str(e)}), 500

# Update existing endpoint to use enhanced analysis when available
@app.route('/api/v3/skin/analyze-real', methods=['POST'])
def analyze_skin_real_enhanced():
    """Enhanced version of existing real analysis endpoint"""
    try:
        # Get request data
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
        
        image_file = request.files['image']
        image_data = image_file.read()
        
        # Get optional demographics
        user_demographics = request.form.get('demographics')
        if user_demographics:
            try:
                user_demographics = json.loads(user_demographics)
            except:
                user_demographics = None
        
        # Use enhanced analysis if available, otherwise fallback
        if enhanced_ml_integration.enhanced_model is not None:
            result = enhanced_ml_integration.analyze_skin_enhanced(image_data, user_demographics)
        else:
            result = enhanced_ml_integration.existing_analyzer.analyze_skin_real(image_data, user_demographics)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"❌ Enhanced real analysis endpoint failed: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    logger.info("🚀 Starting Enhanced ML API Integration")
    logger.info("✅ Enhanced ML integration ready")
    logger.info("📡 API endpoints available:")
    logger.info("   - POST /api/v4/skin/analyze-enhanced")
    logger.info("   - GET /api/v4/system/enhanced-status")
    logger.info("   - POST /api/v3/skin/analyze-real (enhanced)") 