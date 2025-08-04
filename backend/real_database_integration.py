#!/usr/bin/env python3
"""
Real Database Integration for Skin Analysis
Actually uses the available datasets for skin condition matching
"""

import os
import json
import logging
import numpy as np
import cv2
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import pickle
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction import image as skimage
import hashlib
from datetime import datetime

logger = logging.getLogger(__name__)

class RealDatabaseIntegration:
    """Real database integration using actual skin condition datasets"""
    
    def __init__(self):
        """Initialize the real database integration system"""
        self.datasets_path = Path("datasets")
        self.facial_conditions_path = self.datasets_path / "facial_skin_diseases" / "DATA"
        
        # Load dataset information
        self.dataset_info = self._load_dataset_info()
        
        # Initialize condition databases
        self.condition_databases = {}
        self.feature_vectors = {}
        self.condition_metadata = {}
        
        # Load all available datasets
        self._load_facial_conditions_database()
        self._load_ham10000_database()
        self._load_dermnet_database()
        
        logger.info(f"✅ Real database integration initialized with {len(self.condition_databases)} datasets")
    
    def _load_dataset_info(self) -> Dict:
        """Load dataset information"""
        try:
            with open(self.datasets_path / "dataset_info.json", 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load dataset info: {e}")
            return {}
    
    def _load_facial_conditions_database(self):
        """Load facial skin conditions database"""
        try:
            train_path = self.facial_conditions_path / "train"
            test_path = self.facial_conditions_path / "testing"
            
            # Add healthy skin as a baseline condition
            conditions = ['Healthy', 'Acne', 'Actinic Keratosis', 'Basal Cell Carcinoma', 'Eczemaa', 'Rosacea']
            
            for condition in conditions:
                condition_key = condition.lower().replace(' ', '_')
                self.condition_databases[condition_key] = []
                self.feature_vectors[condition_key] = []
                self.condition_metadata[condition_key] = []
                
                # Load training data
                train_condition_path = train_path / condition
                if train_condition_path.exists():
                    self._load_condition_images(train_condition_path, condition_key, 'train')
                
                # Load testing data
                test_condition_path = test_path / condition
                if test_condition_path.exists():
                    self._load_condition_images(test_condition_path, condition_key, 'test')
                
                logger.info(f"✅ Loaded {len(self.condition_databases[condition_key])} images for {condition}")
                
        except Exception as e:
            logger.error(f"Failed to load facial conditions database: {e}")
    
    def _load_condition_images(self, condition_path: Path, condition_key: str, split: str):
        """Load images for a specific condition"""
        try:
            image_files = list(condition_path.glob("*.jpg")) + list(condition_path.glob("*.jpeg")) + list(condition_path.glob("*.png"))
            
            for img_file in image_files[:100]:  # Limit to 100 images per condition for performance
                try:
                    # Load and preprocess image
                    img = cv2.imread(str(img_file))
                    if img is not None:
                        # Resize for consistency
                        img = cv2.resize(img, (224, 224))
                        
                        # Extract features
                        features = self._extract_image_features(img)
                        
                        # Store in database
                        self.condition_databases[condition_key].append(img)
                        self.feature_vectors[condition_key].append(features)
                        self.condition_metadata[condition_key].append({
                            'file_path': str(img_file),
                            'condition': condition_key,
                            'split': split,
                            'features_shape': features.shape
                        })
                        
                except Exception as e:
                    logger.warning(f"Failed to load image {img_file}: {e}")
                    
        except Exception as e:
            logger.error(f"Failed to load condition images for {condition_key}: {e}")
    
    def _load_ham10000_database(self):
        """Load HAM10000 dataset for melanoma detection"""
        try:
            ham10000_path = self.datasets_path / "ham10000_scaled"
            if ham10000_path.exists():
                # Load melanoma and benign cases
                conditions = ['melanoma', 'benign_keratosis', 'basal_cell_carcinoma', 'actinic_keratosis', 'nevus']
                
                for condition in conditions:
                    condition_path = ham10000_path / condition
                    if condition_path.exists():
                        self._load_condition_images(condition_path, f"ham10000_{condition}", 'train')
                        
        except Exception as e:
            logger.error(f"Failed to load HAM10000 database: {e}")
    
    def _load_dermnet_database(self):
        """Load DermNet dataset for additional conditions"""
        try:
            dermnet_path = self.datasets_path / "dermnet_scaled"
            if dermnet_path.exists():
                # Load additional skin conditions
                conditions = ['acne', 'eczema', 'psoriasis', 'rosacea']
                
                for condition in conditions:
                    condition_path = dermnet_path / condition
                    if condition_path.exists():
                        self._load_condition_images(condition_path, f"dermnet_{condition}", 'train')
                        
        except Exception as e:
            logger.error(f"Failed to load DermNet database: {e}")
    
    def _extract_image_features(self, img: np.ndarray) -> np.ndarray:
        """Extract comprehensive features from image"""
        try:
            # Convert to different color spaces
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
            
            features = []
            
            # Color features
            features.extend([
                np.mean(img[:, :, 0]), np.mean(img[:, :, 1]), np.mean(img[:, :, 2]),  # BGR means
                np.std(img[:, :, 0]), np.std(img[:, :, 1]), np.std(img[:, :, 2]),      # BGR stds
                np.mean(hsv[:, :, 0]), np.mean(hsv[:, :, 1]), np.mean(hsv[:, :, 2]),  # HSV means
                np.std(hsv[:, :, 0]), np.std(hsv[:, :, 1]), np.std(hsv[:, :, 2]),     # HSV stds
                np.mean(lab[:, :, 0]), np.mean(lab[:, :, 1]), np.mean(lab[:, :, 2]),  # LAB means
                np.std(lab[:, :, 0]), np.std(lab[:, :, 1]), np.std(lab[:, :, 2])      # LAB stds
            ])
            
            # Texture features
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            features.extend([
                np.mean(laplacian), np.std(laplacian), np.var(laplacian),
                np.mean(gray), np.std(gray), np.var(gray)
            ])
            
            # Edge features
            edges = cv2.Canny(gray, 50, 150)
            features.extend([
                np.mean(edges), np.std(edges), np.sum(edges > 0) / edges.size
            ])
            
            # Histogram features
            hist_b = cv2.calcHist([img], [0], None, [256], [0, 256])
            hist_g = cv2.calcHist([img], [1], None, [256], [0, 256])
            hist_r = cv2.calcHist([img], [2], None, [256], [0, 256])
            
            features.extend([
                np.mean(hist_b), np.std(hist_b), np.var(hist_b),
                np.mean(hist_g), np.std(hist_g), np.var(hist_g),
                np.mean(hist_r), np.std(hist_r), np.var(hist_r)
            ])
            
            return np.array(features)
            
        except Exception as e:
            logger.error(f"Feature extraction failed: {e}")
            return np.zeros(50)  # Fallback feature vector
    
    def find_similar_conditions(self, input_img: np.ndarray, top_k: int = 5) -> List[Dict]:
        """Find similar conditions in the database"""
        try:
            # Extract features from input image
            input_features = self._extract_image_features(input_img)
            
            similar_cases = []
            
            # Search through all condition databases
            for condition_key, feature_vectors in self.feature_vectors.items():
                if len(feature_vectors) == 0:
                    continue
                
                # Calculate similarities
                similarities = []
                for i, features in enumerate(feature_vectors):
                    try:
                        # Normalize features
                        input_norm = input_features / (np.linalg.norm(input_features) + 1e-8)
                        features_norm = features / (np.linalg.norm(features) + 1e-8)
                        
                        # Calculate cosine similarity
                        similarity = np.dot(input_norm, features_norm)
                        similarities.append((similarity, i))
                    except Exception as e:
                        logger.warning(f"Similarity calculation failed: {e}")
                        continue
                
                # Sort by similarity
                similarities.sort(key=lambda x: x[0], reverse=True)
                
                # Add top matches
                for similarity, idx in similarities[:top_k]:
                    if similarity > 0.3:  # Minimum similarity threshold
                        metadata = self.condition_metadata[condition_key][idx]
                        similar_cases.append({
                            'condition': condition_key,
                            'similarity_score': float(similarity),
                            'dataset_source': metadata['split'],
                            'file_path': metadata['file_path'],
                            'confidence': min(0.95, similarity * 1.2)  # Scale confidence
                        })
            
            # Sort all cases by similarity
            similar_cases.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            return similar_cases[:top_k]
            
        except Exception as e:
            logger.error(f"Similar condition search failed: {e}")
            return []
    
    def analyze_skin_conditions_real(self, img: np.ndarray) -> Dict:
        """Perform real skin condition analysis using database matching"""
        try:
            # Find similar cases in database
            similar_cases = self.find_similar_conditions(img, top_k=10)
            
            # Analyze detected conditions
            detected_conditions = []
            condition_scores = {}
            
            for case in similar_cases:
                condition = case['condition']
                similarity = case['similarity_score']
                
                if condition not in condition_scores:
                    condition_scores[condition] = []
                
                condition_scores[condition].append(similarity)
            
            # Calculate average scores for each condition
            for condition, scores in condition_scores.items():
                avg_score = np.mean(scores)
                max_score = np.max(scores)
                
                if avg_score > 0.4:  # Detection threshold
                    # Determine severity based on similarity and condition type
                    if max_score > 0.85:
                        severity = 'severe'
                    elif max_score > 0.7:
                        severity = 'moderate'
                    elif max_score > 0.5:
                        severity = 'mild'
                    else:
                        severity = 'very_mild'
                    
                    # Adjust severity based on condition type
                    if condition == 'healthy':
                        # Healthy skin should always be mild severity
                        severity = 'mild'
                    elif condition in ['melanoma', 'basal_cell_carcinoma', 'actinic_keratosis']:
                        # Cancerous conditions should be treated more seriously
                        if severity == 'very_mild':
                            severity = 'mild'
                        elif severity == 'mild':
                            severity = 'moderate'
                    elif condition in ['acne', 'rosacea']:
                        # Common conditions can be less severe
                        if severity == 'severe':
                            severity = 'moderate'
                        elif severity == 'moderate':
                            severity = 'mild'
                    
                    # Calculate realistic confidence based on similarity and database coverage
                    base_confidence = float(max_score)
                    
                    # Apply realistic confidence adjustments
                    if base_confidence > 0.95:
                        # Cap very high similarities to more realistic values
                        confidence = min(base_confidence * 0.85, 0.92)
                    elif base_confidence > 0.8:
                        confidence = base_confidence * 0.9
                    elif base_confidence > 0.6:
                        confidence = base_confidence * 0.95
                    else:
                        confidence = base_confidence
                    
                    # Add some uncertainty based on database coverage
                    db_coverage = len(self.condition_databases.get(condition, []))
                    coverage_factor = min(db_coverage / 100.0, 1.0)  # Normalize to 0-1
                    confidence = confidence * (0.8 + 0.2 * coverage_factor)
                    
                    detected_conditions.append({
                        'condition': condition,
                        'severity': severity,
                        'confidence': round(confidence, 3),  # Round to 3 decimal places
                        'location': 'face',
                        'description': f'Detected {condition} with {severity} severity',
                        'similarity_score': float(avg_score)
                    })
            
            # Calculate overall health score
            if detected_conditions:
                # Check if any detected conditions are actually "healthy"
                healthy_conditions = [c for c in detected_conditions if c['condition'] == 'healthy']
                unhealthy_conditions = [c for c in detected_conditions if c['condition'] != 'healthy']
                
                if healthy_conditions and not unhealthy_conditions:
                    # Only healthy skin detected
                    health_score = 0.95
                elif healthy_conditions and unhealthy_conditions:
                    # Mixed detection - moderate health
                    severity_weights = {'mild': 0.8, 'moderate': 0.6, 'severe': 0.4}
                    health_score = np.mean([severity_weights[c['severity']] for c in unhealthy_conditions]) * 0.8
                else:
                    # Only unhealthy conditions detected
                    severity_weights = {'mild': 0.8, 'moderate': 0.6, 'severe': 0.4}
                    health_score = np.mean([severity_weights[c['severity']] for c in detected_conditions])
            else:
                health_score = 0.9  # Healthy if no conditions detected
            
            return {
                'conditions': detected_conditions,
                'health_score': float(health_score),
                'similar_cases': similar_cases[:5],
                'database_matches': len(similar_cases),
                'analysis_confidence': float(np.mean([c['confidence'] for c in detected_conditions]) if detected_conditions else 0.8)
            }
            
        except Exception as e:
            logger.error(f"Real skin condition analysis failed: {e}")
            return {
                'conditions': [],
                'health_score': 0.5,
                'similar_cases': [],
                'database_matches': 0,
                'analysis_confidence': 0.0,
                'error': str(e)
            }
    
    def get_database_stats(self) -> Dict:
        """Get database statistics"""
        stats = {
            'total_conditions': len(self.condition_databases),
            'total_images': sum(len(images) for images in self.condition_databases.values()),
            'conditions': {}
        }
        
        for condition, images in self.condition_databases.items():
            stats['conditions'][condition] = len(images)
        
        return stats

def main():
    """Test the real database integration"""
    print("🧠 Testing Real Database Integration")
    
    # Initialize system
    db_integration = RealDatabaseIntegration()
    
    # Get database stats
    stats = db_integration.get_database_stats()
    print(f"✅ Database loaded: {stats['total_images']} images across {stats['total_conditions']} conditions")
    
    # Create test image
    test_image = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
    
    # Test analysis
    result = db_integration.analyze_skin_conditions_real(test_image)
    print(f"✅ Analysis completed")
    print(f"📊 Health Score: {result['health_score']:.3f}")
    print(f"🔍 Detected Conditions: {len(result['conditions'])}")
    print(f"📚 Database Matches: {result['database_matches']}")

if __name__ == "__main__":
    main() 