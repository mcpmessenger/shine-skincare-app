"""
SCIN FAISS Integration Service
Combines SCIN dataset access with FAISS similarity search for skin analysis
"""

import os
import logging
import numpy as np
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime
import json
from PIL import Image
import io

# Import our existing services
from .scin_dataset_service import SCINDatasetService
from .enhanced_image_vectorization_service import EnhancedImageVectorizationService
from .faiss_service import FAISSService

logger = logging.getLogger(__name__)

class SCINFAISSIntegration:
    """
    Integrated service for SCIN dataset + FAISS similarity search
    Provides comprehensive skin analysis without Google Vision dependency
    """
    
    def __init__(self, 
                 scin_service: Optional[SCINDatasetService] = None,
                 vectorization_service: Optional[EnhancedImageVectorizationService] = None,
                 faiss_service: Optional[FAISSService] = None):
        """
        Initialize the SCIN FAISS integration
        
        Args:
            scin_service: SCIN dataset service instance
            vectorization_service: Image vectorization service instance
            faiss_service: FAISS similarity search service instance
        """
        self.scin_service = scin_service or SCINDatasetService()
        self.vectorization_service = vectorization_service or EnhancedImageVectorizationService()
        self.faiss_service = faiss_service or FAISSService()
        
        # Integration state
        self.integration_status = {
            'scin_loaded': False,
            'vectors_generated': False,
            'faiss_populated': False,
            'last_update': None,
            'total_images_processed': 0,
            'index_size': 0
        }
        
        # Initialize the integration
        self._initialize_integration()
    
    def _initialize_integration(self):
        """Initialize the SCIN + FAISS integration"""
        try:
            logger.info("Initializing SCIN FAISS integration...")
            
            # Check SCIN service availability
            if not self.scin_service.is_available():
                logger.warning("SCIN service not available")
                return
            
            # Load SCIN metadata
            if self.scin_service.load_metadata():
                self.integration_status['scin_loaded'] = True
                logger.info("SCIN dataset metadata loaded successfully")
            else:
                logger.error("Failed to load SCIN dataset metadata")
                return
            
            # Check vectorization service
            if not self.vectorization_service.is_available():
                logger.warning("Vectorization service not available")
                return
            
            # Check FAISS service
            if not self.faiss_service.is_available():
                logger.warning("FAISS service not available")
                return
            
            self.integration_status['last_update'] = datetime.now().isoformat()
            logger.info("SCIN FAISS integration initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize SCIN FAISS integration: {e}")
    
    def build_similarity_index(self, 
                              conditions: Optional[List[str]] = None,
                              skin_types: Optional[List[str]] = None,
                              skin_tones: Optional[List[str]] = None,
                              max_images: Optional[int] = None,
                              batch_size: int = 50) -> Dict[str, Any]:
        """
        Build similarity search index from SCIN dataset
        
        Args:
            conditions: List of conditions to include
            skin_types: List of skin types to include
            skin_tones: List of skin tones to include
            max_images: Maximum number of images to process
            batch_size: Number of images to process in each batch
            
        Returns:
            Status dictionary with build results
        """
        status = {
            'success': True,
            'errors': [],
            'warnings': [],
            'details': {
                'processed_images': 0,
                'successful_vectors': 0,
                'failed_vectors': 0,
                'faiss_additions': 0,
                'processing_time': 0
            }
        }
        
        if not self.integration_status['scin_loaded']:
            status['success'] = False
            status['errors'].append("SCIN dataset not loaded")
            return status
        
        start_time = datetime.now()
        
        try:
            # Filter dataset
            logger.info("Filtering SCIN dataset...")
            filtered_df = self.scin_service.filter_dataset(
                conditions=conditions,
                skin_types=skin_types,
                skin_tones=skin_tones,
                limit=max_images
            )
            
            if len(filtered_df) == 0:
                status['success'] = False
                status['errors'].append("No images found matching criteria")
                return status
            
            logger.info(f"Processing {len(filtered_df)} images...")
            
            # Process images in batches
            total_batches = (len(filtered_df) + batch_size - 1) // batch_size
            
            for batch_idx in range(0, len(filtered_df), batch_size):
                batch_df = filtered_df.iloc[batch_idx:batch_idx + batch_size]
                batch_num = batch_idx // batch_size + 1
                
                logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch_df)} images)")
                
                batch_status = self._process_batch(batch_df)
                
                # Update status
                status['details']['processed_images'] += batch_status['processed']
                status['details']['successful_vectors'] += batch_status['successful']
                status['details']['failed_vectors'] += batch_status['failed']
                status['details']['faiss_additions'] += batch_status['faiss_added']
                
                if batch_status['errors']:
                    status['errors'].extend(batch_status['errors'])
                
                if batch_status['warnings']:
                    status['warnings'].extend(batch_status['warnings'])
            
            # Update integration status
            if status['details']['faiss_additions'] > 0:
                self.integration_status['vectors_generated'] = True
                self.integration_status['faiss_populated'] = True
                self.integration_status['total_images_processed'] = status['details']['faiss_additions']
                self.integration_status['index_size'] = self.faiss_service.get_index_info()['total_vectors']
            
            processing_time = (datetime.now() - start_time).total_seconds()
            status['details']['processing_time'] = processing_time
            self.integration_status['last_update'] = datetime.now().isoformat()
            
            logger.info(f"Similarity index build completed. Added {status['details']['faiss_additions']} vectors to FAISS in {processing_time:.2f}s")
            
        except Exception as e:
            status['success'] = False
            status['errors'].append(f"Failed to build similarity index: {str(e)}")
            logger.error(f"Error building similarity index: {e}")
        
        return status
    
    def _process_batch(self, batch_df) -> Dict[str, Any]:
        """Process a batch of images"""
        batch_status = {
            'processed': len(batch_df),
            'successful': 0,
            'failed': 0,
            'faiss_added': 0,
            'errors': [],
            'warnings': []
        }
        
        for _, row in batch_df.iterrows():
            try:
                # Get image filename from the dataset
                image_filename = row.get('image_file_name', '')
                if not image_filename:
                    # Try to construct filename from case_id
                    image_filename = f"{row['case_id']}.jpg"
                
                # Load image from GCS
                image = self.scin_service.load_image_from_gcs(image_filename)
                if image is None:
                    batch_status['failed'] += 1
                    batch_status['warnings'].append(f"Failed to load image {image_filename}")
                    continue
                
                # Vectorize image
                vector = self.vectorization_service.vectorize_image_from_pil(
                    image, 
                    image_id=row['case_id']
                )
                
                if vector is None:
                    batch_status['failed'] += 1
                    batch_status['warnings'].append(f"Failed to vectorize image {image_filename}")
                    continue
                
                batch_status['successful'] += 1
                
                # Add to FAISS
                if self.faiss_service.add_vector(vector, row['case_id']):
                    batch_status['faiss_added'] += 1
                else:
                    batch_status['warnings'].append(f"Failed to add vector to FAISS for {row['case_id']}")
                
            except Exception as e:
                batch_status['failed'] += 1
                batch_status['errors'].append(f"Error processing {row['case_id']}: {str(e)}")
        
        return batch_status
    
    def analyze_skin_image(self, 
                          image_data: bytes,
                          k: int = 5,
                          conditions: Optional[List[str]] = None,
                          skin_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Analyze a skin image using SCIN dataset and FAISS similarity search
        
        Args:
            image_data: Image data as bytes
            k: Number of similar images to find
            conditions: Optional filter for conditions
            skin_types: Optional filter for skin types
            
        Returns:
            Analysis results with similar images and recommendations
        """
        results = {
            'success': True,
            'analysis_id': f"scin_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'timestamp': datetime.now().isoformat(),
            'similar_images': [],
            'skin_analysis': {},
            'recommendations': [],
            'error': None
        }
        
        try:
            # Check if services are available
            if not self.integration_status['scin_loaded']:
                results['success'] = False
                results['error'] = "SCIN dataset not loaded"
                return results
            
            if not self.faiss_service.is_available():
                results['success'] = False
                results['error'] = "FAISS service not available"
                return results
            
            # Convert image data to PIL Image
            image = Image.open(io.BytesIO(image_data))
            
            # Vectorize the query image
            query_vector = self.vectorization_service.vectorize_image_from_pil(
                image, 
                image_id="query_image"
            )
            
            if query_vector is None:
                results['success'] = False
                results['error'] = "Failed to vectorize query image"
                return results
            
            # Search for similar images in FAISS
            similar_indices = self.faiss_service.search_similar(query_vector, k)
            
            # Get metadata for similar images
            for case_id, distance in similar_indices:
                image_metadata = self._get_image_metadata(case_id)
                if image_metadata:
                    # Apply filters if specified
                    if conditions and image_metadata['condition'] not in conditions:
                        continue
                    if skin_types and image_metadata['skin_type'] not in skin_types:
                        continue
                    
                    similar_image = {
                        'case_id': case_id,
                        'similarity_score': 1.0 - distance,  # Convert distance to similarity
                        'distance': distance,
                        'image_path': image_metadata['image_path'],
                        'condition': image_metadata['condition'],
                        'skin_type': image_metadata['skin_type'],
                        'skin_tone': image_metadata['skin_tone'],
                        'age': image_metadata.get('age'),
                        'gender': image_metadata.get('gender')
                    }
                    results['similar_images'].append(similar_image)
            
            # Sort by similarity score (descending)
            results['similar_images'].sort(key=lambda x: x['similarity_score'], reverse=True)
            
            # Generate skin analysis based on similar images
            results['skin_analysis'] = self._generate_skin_analysis(results['similar_images'])
            
            # Generate recommendations
            results['recommendations'] = self._generate_recommendations(results['similar_images'])
            
        except Exception as e:
            results['success'] = False
            results['error'] = f"Analysis failed: {str(e)}"
            logger.error(f"Error analyzing skin image: {e}")
        
        return results
    
    def _get_image_metadata(self, case_id: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a specific case ID"""
        if not self.integration_status['scin_loaded']:
            return None
        
        try:
            case_data = self.scin_service.merged_df[
                self.scin_service.merged_df['case_id'] == case_id
            ]
            
            if len(case_data) == 0:
                return None
            
            row = case_data.iloc[0]
            
            # Get image path
            image_path = row.get('image_1_path', '')
            if not image_path:
                image_path = self.scin_service.get_image_path(f"{row['case_id']}.jpg")
            
            return {
                'case_id': row['case_id'],
                'image_path': image_path,
                'condition': row.get('dermatologist_skin_condition_on_label_name'),
                'skin_type': row.get('dermatologist_fitzpatrick_skin_type_label_1'),
                'skin_tone': row.get('monk_skin_tone_label_us'),
                'age': row.get('age_group'),
                'gender': row.get('sex_at_birth')
            }
        except Exception as e:
            logger.error(f"Error getting metadata for case {case_id}: {e}")
            return None
    
    def _generate_skin_analysis(self, similar_images: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate skin analysis based on similar images"""
        if not similar_images:
            return {
                'skin_type': 'Unknown',
                'confidence': 0.0,
                'conditions': [],
                'concerns': []
            }
        
        # Analyze similar images to determine skin characteristics
        skin_types = [img['skin_type'] for img in similar_images if img['skin_type']]
        conditions = [img['condition'] for img in similar_images if img['condition']]
        skin_tones = [img['skin_tone'] for img in similar_images if img['skin_tone']]
        
        # Determine most common skin type
        if skin_types:
            from collections import Counter
            skin_type_counter = Counter(skin_types)
            most_common_skin_type = skin_type_counter.most_common(1)[0][0]
        else:
            most_common_skin_type = 'III'  # Default
        
        # Calculate confidence based on similarity scores
        avg_similarity = sum(img['similarity_score'] for img in similar_images) / len(similar_images)
        confidence = min(0.95, avg_similarity * 1.2)  # Scale up similarity to confidence
        
        # Get unique conditions
        unique_conditions = list(set(conditions))
        
        # Map skin type to user-friendly name
        skin_type_mapping = {
            'I': 'Very Fair',
            'II': 'Fair', 
            'III': 'Light',
            'IV': 'Medium',
            'V': 'Dark',
            'VI': 'Very Dark'
        }
        
        skin_type_name = skin_type_mapping.get(most_common_skin_type, 'Medium')
        
        return {
            'skin_type': skin_type_name,
            'fitzpatrick_type': most_common_skin_type,
            'confidence': confidence,
            'conditions': unique_conditions[:3],  # Top 3 conditions
            'concerns': unique_conditions[:3],  # Use conditions as concerns
            'skin_tone': skin_tones[0] if skin_tones else None,
            'similarity_score': avg_similarity
        }
    
    def _generate_recommendations(self, similar_images: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on similar images"""
        recommendations = []
        
        if not similar_images:
            return ["Consider consulting with a dermatologist for personalized advice"]
        
        # Analyze conditions to generate recommendations
        conditions = [img['condition'] for img in similar_images if img['condition']]
        skin_types = [img['skin_type'] for img in similar_images if img['skin_type']]
        
        # Condition-based recommendations
        condition_recs = {
            'acne': 'Consider salicylic acid cleanser and non-comedogenic products',
            'hyperpigmentation': 'Use products with vitamin C, kojic acid, or arbutin',
            'rosacea': 'Avoid triggers and use gentle, fragrance-free products',
            'eczema': 'Use fragrance-free, hypoallergenic moisturizers',
            'dermatitis': 'Apply gentle, non-irritating skincare products'
        }
        
        for condition in conditions:
            condition_lower = condition.lower()
            for key, rec in condition_recs.items():
                if key in condition_lower:
                    recommendations.append(rec)
                    break
        
        # Skin type-based recommendations
        skin_type_recs = {
            'I': 'Use SPF 50+ daily and gentle, fragrance-free products',
            'II': 'Apply SPF 30+ daily and consider vitamin C for brightening',
            'III': 'Use SPF 30+ daily and maintain consistent hydration',
            'IV': 'Apply SPF 30+ daily and consider niacinamide for even tone',
            'V': 'Use SPF 30+ daily and gentle exfoliation for even skin tone',
            'VI': 'Apply SPF 30+ daily and focus on hydration and even tone'
        }
        
        if skin_types:
            most_common_skin_type = max(set(skin_types), key=skin_types.count)
            if most_common_skin_type in skin_type_recs:
                recommendations.append(skin_type_recs[most_common_skin_type])
        
        # General recommendations
        recommendations.extend([
            'Maintain a consistent skincare routine',
            'Stay hydrated and get adequate sleep',
            'Consider patch testing new products'
        ])
        
        # Remove duplicates and limit to top 6
        unique_recommendations = list(dict.fromkeys(recommendations))
        return unique_recommendations[:6]
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Get current integration status"""
        status = self.integration_status.copy()
        
        # Add service status
        status['services'] = {
            'scin_service': self.scin_service.is_available(),
            'vectorization_service': self.vectorization_service.is_available(),
            'faiss_service': self.faiss_service.is_available()
        }
        
        # Add dataset info if available
        if self.integration_status['scin_loaded']:
            status['dataset_info'] = self.scin_service.get_dataset_info()
        
        # Add FAISS info if available
        if self.faiss_service.is_available():
            status['faiss_info'] = self.faiss_service.get_index_info()
        
        return status
    
    def is_available(self) -> bool:
        """Check if the integration is available"""
        return (self.integration_status['scin_loaded'] and 
                self.integration_status['faiss_populated'] and
                self.faiss_service.is_available()) 