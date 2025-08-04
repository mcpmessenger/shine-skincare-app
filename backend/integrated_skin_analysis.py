#!/usr/bin/env python3
"""
Integrated Skin Analysis System
Combines UTKFace healthy baselines with facial conditions dataset for normalized analysis
"""

import os
import numpy as np
import cv2
import logging
from typing import Dict, List, Optional, Tuple, Union
from pathlib import Path
import json
from datetime import datetime
import pickle
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction import image as skimage
import hashlib

# Import our existing systems
from enhanced_analysis_algorithms import EnhancedSkinAnalyzer
from enhanced_embeddings import EnhancedEmbeddingSystem
from utkface_integration import UTKFaceIntegration
from real_database_integration import RealDatabaseIntegration

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntegratedSkinAnalysis:
    """Integrated skin analysis system with healthy baselines and condition matching"""
    
    def __init__(self):
        """Initialize the integrated skin analysis system"""
        self.analyzer = EnhancedSkinAnalyzer()
        self.embedding_system = EnhancedEmbeddingSystem()
        self.utkface_integration = UTKFaceIntegration()
        self.db_integration = RealDatabaseIntegration()
        
        # Load existing embeddings and baselines
        self.condition_embeddings = self._load_condition_embeddings()
        self.demographic_baselines = self._load_demographic_baselines()
        
        logger.info("✅ Integrated skin analysis system initialized")
    
    def _load_condition_embeddings(self) -> Dict:
        """Load condition embeddings"""
        try:
            embeddings_path = Path("data/condition_embeddings.npy")
            if embeddings_path.exists():
                embeddings = np.load(embeddings_path, allow_pickle=True).item()
                logger.info(f"✅ Loaded {len(embeddings)} condition embeddings")
                return embeddings
            else:
                logger.warning("⚠️ Condition embeddings not found")
                return {}
        except Exception as e:
            logger.error(f"❌ Failed to load condition embeddings: {e}")
            return {}
    
    def _load_demographic_baselines(self) -> Dict:
        """Load demographic baselines"""
        try:
            baselines_path = Path("data/utkface/demographic_baselines.npy")
            if baselines_path.exists():
                baselines = np.load(baselines_path, allow_pickle=True).item()
                logger.info(f"✅ Loaded {len(baselines)} demographic baselines")
                return baselines
            else:
                logger.warning("⚠️ Demographic baselines not found")
                return {}
        except Exception as e:
            logger.error(f"❌ Failed to load demographic baselines: {e}")
            return {}
    
    def analyze_skin_comprehensive(self, image_data: bytes, user_demographics: Dict = None) -> Dict:
        """
        Comprehensive skin analysis with healthy baseline comparison
        
        Args:
            image_data: Image data as bytes
            user_demographics: User demographics (age, gender, ethnicity)
            
        Returns:
            Comprehensive analysis results
        """
        try:
            logger.info("🔄 Starting comprehensive skin analysis...")
            
            # Step 1: Basic skin analysis
            # Convert bytes to numpy array
            nparr = np.frombuffer(image_data, np.uint8)
            img_array = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            basic_analysis = self.analyzer.analyze_skin_conditions(img_array)
            
            # Step 2: Generate embeddings
            embedding_result = self.embedding_system.generate_enhanced_embeddings(image_data)
            user_embedding = embedding_result.get('combined', None)
            
            if user_embedding is None:
                logger.warning("⚠️ Failed to generate user embedding")
                return basic_analysis
            
            # Step 3: Healthy baseline comparison
            baseline_comparison = self._compare_with_healthy_baseline(
                user_embedding, user_demographics
            )
            
            # Step 4: Condition similarity analysis
            condition_analysis = self._analyze_condition_similarity(user_embedding)
            
            # Step 5: Combine results
            comprehensive_results = {
                'timestamp': datetime.now().isoformat(),
                'basic_analysis': basic_analysis,
                'baseline_comparison': baseline_comparison,
                'condition_analysis': condition_analysis,
                'embedding_quality': embedding_result.get('quality', {}),
                'analysis_summary': self._generate_analysis_summary(
                    basic_analysis, baseline_comparison, condition_analysis
                )
            }
            
            logger.info("✅ Comprehensive skin analysis completed")
            return comprehensive_results
            
        except Exception as e:
            logger.error(f"❌ Comprehensive analysis failed: {e}")
            return {'error': str(e)}
    
    def _compare_with_healthy_baseline(self, user_embedding: List[float], 
                                      demographics: Dict = None) -> Dict:
        """Compare user embedding with healthy demographic baseline"""
        try:
            if not self.demographic_baselines:
                return {'status': 'no_baselines_available'}
            
            # Get relevant baseline based on demographics
            if demographics:
                age = demographics.get('age', 30)
                gender = demographics.get('gender', 0)
                ethnicity = demographics.get('ethnicity', 0)
                
                baseline_key = f"{age}_{gender}_{ethnicity}"
                baseline = self.demographic_baselines.get(baseline_key)
                
                if baseline is not None:
                    # Calculate similarity to healthy baseline
                    similarity = np.dot(user_embedding, baseline) / (
                        np.linalg.norm(user_embedding) * np.linalg.norm(baseline)
                    )
                    
                    return {
                        'status': 'baseline_comparison',
                        'demographics': demographics,
                        'baseline_key': baseline_key,
                        'similarity_to_healthy': float(similarity),
                        'health_score': float(similarity * 100),
                        'interpretation': self._interpret_health_score(similarity)
                    }
            
            # Fallback: compare with all baselines
            similarities = {}
            for key, baseline in self.demographic_baselines.items():
                similarity = np.dot(user_embedding, baseline) / (
                    np.linalg.norm(user_embedding) * np.linalg.norm(baseline)
                )
                similarities[key] = float(similarity)
            
            # Find best matching baseline
            best_match = max(similarities.items(), key=lambda x: x[1])
            
            return {
                'status': 'baseline_comparison_fallback',
                'best_matching_baseline': best_match[0],
                'similarity_to_healthy': best_match[1],
                'health_score': float(best_match[1] * 100),
                'all_similarities': similarities,
                'interpretation': self._interpret_health_score(best_match[1])
            }
            
        except Exception as e:
            logger.error(f"❌ Baseline comparison failed: {e}")
            return {'status': 'comparison_failed', 'error': str(e)}
    
    def _analyze_condition_similarity(self, user_embedding: List[float]) -> Dict:
        """Analyze similarity to known skin conditions"""
        try:
            if not self.condition_embeddings:
                return {'status': 'no_condition_embeddings'}
            
            similarities = {}
            for condition, data in self.condition_embeddings.items():
                condition_embedding = data['embedding']
                similarity = np.dot(user_embedding, condition_embedding) / (
                    np.linalg.norm(user_embedding) * np.linalg.norm(condition_embedding)
                )
                similarities[condition] = float(similarity)
            
            # Sort by similarity
            sorted_similarities = sorted(similarities.items(), key=lambda x: x[1], reverse=True)
            
            # Get top matches
            top_matches = sorted_similarities[:3]
            
            return {
                'status': 'condition_analysis_complete',
                'top_matches': [
                    {
                        'condition': condition,
                        'similarity': similarity,
                        'confidence': float(similarity * 100)
                    }
                    for condition, similarity in top_matches
                ],
                'all_similarities': similarities,
                'primary_concern': top_matches[0] if top_matches else None
            }
            
        except Exception as e:
            logger.error(f"❌ Condition similarity analysis failed: {e}")
            return {'status': 'analysis_failed', 'error': str(e)}
    
    def _interpret_health_score(self, similarity: float) -> str:
        """Interpret health score based on similarity to healthy baseline"""
        if similarity >= 0.8:
            return "Excellent skin health - very similar to healthy baseline"
        elif similarity >= 0.6:
            return "Good skin health - generally similar to healthy baseline"
        elif similarity >= 0.4:
            return "Moderate skin health - some deviation from healthy baseline"
        elif similarity >= 0.2:
            return "Below average skin health - significant deviation from healthy baseline"
        else:
            return "Poor skin health - major deviation from healthy baseline"
    
    def _generate_analysis_summary(self, basic_analysis: Dict, 
                                 baseline_comparison: Dict, 
                                 condition_analysis: Dict) -> Dict:
        """Generate comprehensive analysis summary"""
        try:
            summary = {
                'overall_health_score': 0,
                'primary_concerns': [],
                'recommendations': [],
                'confidence_level': 'medium'
            }
            
            # Calculate overall health score
            health_score = baseline_comparison.get('health_score', 50)
            summary['overall_health_score'] = health_score
            
            # Identify primary concerns
            if condition_analysis.get('primary_concern'):
                primary_condition = condition_analysis['primary_concern'][0]
                if primary_condition != 'healthy':
                    summary['primary_concerns'].append(primary_condition)
            
            # Add basic analysis concerns
            if basic_analysis.get('acne_severity', 0) > 0.1:
                summary['primary_concerns'].append('acne')
            if basic_analysis.get('redness_severity', 0) > 0.1:
                summary['primary_concerns'].append('redness')
            if basic_analysis.get('dark_spots_severity', 0) > 0.1:
                summary['primary_concerns'].append('dark_spots')
            
            # Generate recommendations
            if health_score < 50:
                summary['recommendations'].append('Consider consulting a dermatologist')
            if 'acne' in summary['primary_concerns']:
                summary['recommendations'].append('Use gentle, non-comedogenic skincare products')
            if 'redness' in summary['primary_concerns']:
                summary['recommendations'].append('Avoid harsh skincare products and protect from sun')
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ Failed to generate analysis summary: {e}")
            return {'error': str(e)}
    
    def get_system_status(self) -> Dict:
        """Get system status and component information"""
        return {
            'system_status': 'operational',
            'components': {
                'enhanced_analyzer': 'loaded',
                'embedding_system': 'loaded',
                'utkface_integration': 'loaded',
                'db_integration': 'loaded'
            },
            'data_loaded': {
                'condition_embeddings': len(self.condition_embeddings),
                'demographic_baselines': len(self.demographic_baselines),
                'embedding_dimensions': 2304 if self.condition_embeddings else 0
            },
            'timestamp': datetime.now().isoformat()
        }

def main():
    """Test the integrated skin analysis system"""
    print("🔄 Testing Integrated Skin Analysis System")
    print("="*50)
    
    # Initialize system
    integrated_system = IntegratedSkinAnalysis()
    
    # Check system status
    status = integrated_system.get_system_status()
    print(f"System Status: {status['system_status']}")
    print(f"Condition Embeddings: {status['data_loaded']['condition_embeddings']}")
    print(f"Demographic Baselines: {status['data_loaded']['demographic_baselines']}")
    print(f"Embedding Dimensions: {status['data_loaded']['embedding_dimensions']}")
    
    print("✅ Integrated skin analysis system ready!")

if __name__ == "__main__":
    main() 