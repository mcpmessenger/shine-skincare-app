"""
Mock Supabase Service for Vercel deployment
This provides the same interface as SupabaseService but without Supabase dependency
"""
import logging
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

class MockSupabaseService:
    """Mock implementation of Supabase Service for deployment testing"""
    
    def __init__(self, url: str = None, key: str = None):
        self.url = url or "mock://supabase.url"
        self.key = key or "mock_key"
        self._available = True
        
        # In-memory storage for mock data
        self._images = {}
        self._analyses = {}
        self._vectors = {}
        self._users = {}
        
        logger.info("Mock Supabase Service initialized")
    
    def is_available(self):
        """Check if the service is available"""
        return self._available
    
    def upload_image(self, image_data: bytes, filename: str) -> Optional[str]:
        """Mock image upload"""
        try:
            # Generate a mock URL
            image_id = str(uuid.uuid4())
            mock_url = f"https://mock-storage.supabase.co/storage/v1/object/public/images/{image_id}_{filename}"
            
            logger.info(f"Mock image upload: {filename} -> {mock_url}")
            return mock_url
            
        except Exception as e:
            logger.error(f"Mock image upload error: {e}")
            return None
    
    def create_image_record(self, user_id: str, image_url: str) -> Optional[Dict[str, Any]]:
        """Create a mock image record"""
        try:
            image_id = str(uuid.uuid4())
            record = {
                'id': image_id,
                'user_id': user_id,
                'image_url': image_url,
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            self._images[image_id] = record
            logger.info(f"Mock image record created: {image_id}")
            return record
            
        except Exception as e:
            logger.error(f"Mock image record creation error: {e}")
            return None
    
    def create_analysis_record(self, image_id: str, google_vision_result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a mock analysis record"""
        try:
            analysis_id = str(uuid.uuid4())
            record = {
                'id': analysis_id,
                'image_id': image_id,
                'google_vision_result': google_vision_result,
                'created_at': datetime.utcnow().isoformat()
            }
            
            self._analyses[analysis_id] = record
            logger.info(f"Mock analysis record created: {analysis_id}")
            return record
            
        except Exception as e:
            logger.error(f"Mock analysis record creation error: {e}")
            return None
    
    def create_vector_record(self, image_id: str, vector_data: List[float], model_name: str) -> Optional[Dict[str, Any]]:
        """Create a mock vector record"""
        try:
            vector_id = str(uuid.uuid4())
            record = {
                'id': vector_id,
                'image_id': image_id,
                'vector_data': vector_data,
                'model_name': model_name,
                'created_at': datetime.utcnow().isoformat()
            }
            
            self._vectors[vector_id] = record
            logger.info(f"Mock vector record created: {vector_id}")
            return record
            
        except Exception as e:
            logger.error(f"Mock vector record creation error: {e}")
            return None
    
    def get_image_by_id(self, image_id: str) -> Optional[Dict[str, Any]]:
        """Get mock image record by ID"""
        return self._images.get(image_id)
    
    def get_analysis_by_image_id(self, image_id: str) -> Optional[Dict[str, Any]]:
        """Get mock analysis record by image ID"""
        for analysis in self._analyses.values():
            if analysis['image_id'] == image_id:
                return analysis
        return None
    
    def get_vector_by_image_id(self, image_id: str) -> Optional[Dict[str, Any]]:
        """Get mock vector record by image ID"""
        for vector in self._vectors.values():
            if vector['image_id'] == image_id:
                return vector
        return None
    
    def get_images_by_user(self, user_id: str) -> List[Dict[str, Any]]:
        """Get mock images for a user"""
        return [img for img in self._images.values() if img['user_id'] == user_id]
    
    def get_analysis_metadata_batch(self, image_ids: List[str]) -> List[Dict[str, Any]]:
        """Get mock analysis metadata for multiple images"""
        results = []
        for image_id in image_ids:
            analysis = self.get_analysis_by_image_id(image_id)
            if analysis:
                results.append({
                    'image_id': image_id,
                    'analysis_metadata': analysis['google_vision_result'].get('analysis_metadata', {}),
                    'ethnicity': analysis['google_vision_result'].get('ethnicity', ''),
                    'created_at': analysis['created_at']
                })
        return results
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get mock service information"""
        return {
            'name': 'Mock Supabase Service',
            'version': '1.0.0',
            'status': 'available' if self._available else 'unavailable',
            'type': 'mock',
            'url': self.url,
            'records': {
                'images': len(self._images),
                'analyses': len(self._analyses),
                'vectors': len(self._vectors)
            }
        }