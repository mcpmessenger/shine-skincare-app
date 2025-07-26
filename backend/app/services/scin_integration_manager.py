import os
import logging
import numpy as np
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime
import json
from tqdm import tqdm

from .scin_dataset_service import SCINDatasetService
from .enhanced_image_vectorization_service import EnhancedImageVectorizationService
from .faiss_service import FAISSService

logger = logging.getLogger(__name__)

class SCINIntegrationManager:
    """Manager for integrating SCIN dataset with similarity search"""
    
    def __init__(self, 
                 scin_service: Optional[SCINDatasetService] = None,
                 vectorization_service: Optional[EnhancedImageVectorizationService] = None,
                 faiss_service: Optional[FAISSService] = None):
        """
        Initialize the SCIN integration manager
        
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
            'last_update': None
        }
    
    def initialize_integration(self) -> Dict[str, Any]:
        """
        Initialize the complete integration pipeline
        
        Returns:
            Status dictionary with initialization results
        """
        status = {
            'success': True,
            'errors': [],
            'warnings': [],
            'details': {}
        }
        
        # Check SCIN service
        if not self.scin_service.is_available():
            status['success'] = False
            status['errors'].append("SCIN service not available")
        else:
            status['details']['scin_service'] = "Available"
        
        # Check vectorization service
        if not self.vectorization_service.is_available():
            status['success'] = False
            status['errors'].append("Vectorization service not available")
        else:
            status['details']['vectorization_service'] = self.vectorization_service.get_model_info()
        
        # Check FAISS service
        if not self.faiss_service.is_available():
            status['warnings'].append("FAISS service not available")
        else:
            status['details']['faiss_service'] = self.faiss_service.get_index_info()
        
        # Load SCIN metadata
        if status['success']:
            logger.info("Loading SCIN dataset metadata...")
            if self.scin_service.load_metadata():
                self.integration_status['scin_loaded'] = True
                status['details']['scin_dataset'] = self.scin_service.get_dataset_info()
                logger.info("SCIN dataset metadata loaded successfully")
            else:
                status['success'] = False
                status['errors'].append("Failed to load SCIN dataset metadata")
        
        self.integration_status['last_update'] = datetime.now().isoformat()
        return status
    
    def build_similarity_index(self, 
                              conditions: Optional[List[str]] = None,
                              skin_types: Optional[List[str]] = None,
                              skin_tones: Optional[List[str]] = None,
                              max_images: Optional[int] = None,
                              batch_size: int = 100) -> Dict[str, Any]:
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
                'faiss_additions': 0
            }
        }
        
        if not self.integration_status['scin_loaded']:
            status['success'] = False
            status['errors'].append("SCIN dataset not loaded")
            return status
        
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
            
            self.integration_status['last_update'] = datetime.now().isoformat()
            
            logger.info(f"Similarity index build completed. Added {status['details']['faiss_additions']} vectors to FAISS")
            
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
                # Load image from GCS
                image = self.scin_service.load_image_from_gcs(row['image_file_name'])
                if image is None:
                    batch_status['failed'] += 1
                    batch_status['warnings'].append(f"Failed to load image {row['image_file_name']}")
                    continue
                
                # Vectorize image
                vector = self.vectorization_service.vectorize_image_from_pil(
                    image, 
                    image_id=row['case_id']
                )
                
                if vector is None:
                    batch_status['failed'] += 1
                    batch_status['warnings'].append(f"Failed to vectorize image {row['image_file_name']}")
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
    
    def search_similar_images(self, 
                            query_image_path: str,
                            k: int = 5,
                            conditions: Optional[List[str]] = None,
                            skin_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Search for similar images in the SCIN dataset
        
        Args:
            query_image_path: Path to the query image
            k: Number of similar images to return
            conditions: Optional filter for conditions
            skin_types: Optional filter for skin types
            
        Returns:
            Search results with similar images and metadata
        """
        results = {
            'success': True,
            'query_image': query_image_path,
            'similar_images': [],
            'error': None
        }
        
        try:
            # Vectorize query image
            query_vector = self.vectorization_service.vectorize_image(query_image_path)
            if query_vector is None:
                results['success'] = False
                results['error'] = "Failed to vectorize query image"
                return results
            
            # Search in FAISS
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
                        'distance': distance,
                        'image_path': image_metadata['image_path'],
                        'condition': image_metadata['condition'],
                        'skin_type': image_metadata['skin_type'],
                        'skin_tone': image_metadata['skin_tone'],
                        'age': image_metadata.get('age'),
                        'gender': image_metadata.get('gender')
                    }
                    results['similar_images'].append(similar_image)
            
            # Sort by distance
            results['similar_images'].sort(key=lambda x: x['distance'])
            
        except Exception as e:
            results['success'] = False
            results['error'] = f"Search failed: {str(e)}"
            logger.error(f"Error searching similar images: {e}")
        
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
            # Get image path from image_1_path column
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
        
        # Add vectorization info
        if self.vectorization_service.is_available():
            status['vectorization_info'] = self.vectorization_service.get_model_info()
            status['cache_info'] = self.vectorization_service.get_cache_info()
        
        return status
    
    def export_integration_report(self, output_path: str) -> bool:
        """
        Export integration status and statistics to a JSON file
        
        Args:
            output_path: Path to save the report
            
        Returns:
            True if successful, False otherwise
        """
        try:
            report = {
                'timestamp': datetime.now().isoformat(),
                'integration_status': self.get_integration_status(),
                'scin_statistics': self.scin_service.get_condition_statistics() if self.integration_status['scin_loaded'] else None
            }
            
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2)
            
            logger.info(f"Integration report exported to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export integration report: {e}")
            return False
    
    def clear_all_data(self):
        """Clear all cached and indexed data"""
        try:
            # Clear FAISS index
            if self.faiss_service.is_available():
                self.faiss_service.clear_index()
            
            # Clear vector cache
            if self.vectorization_service.is_available():
                self.vectorization_service.clear_cache()
            
            # Reset integration status
            self.integration_status = {
                'scin_loaded': False,
                'vectors_generated': False,
                'faiss_populated': False,
                'last_update': datetime.now().isoformat()
            }
            
            logger.info("All cached and indexed data cleared")
            
        except Exception as e:
            logger.error(f"Error clearing data: {e}") 