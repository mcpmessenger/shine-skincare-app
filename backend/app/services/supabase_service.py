import os
import logging
from typing import Optional, Dict, Any, List
from supabase import create_client, Client
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class SupabaseService:
    """Service for Supabase integration"""
    
    def __init__(self, url: Optional[str] = None, key: Optional[str] = None):
        """
        Initialize the Supabase service
        
        Args:
            url: Supabase project URL
            key: Supabase service key
        """
        self.url = url or os.environ.get('SUPABASE_URL')
        self.key = key or os.environ.get('SUPABASE_KEY')
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Supabase client"""
        try:
            if self.url and self.key:
                self.client = create_client(self.url, self.key)
                logger.info("Supabase client initialized successfully")
            else:
                logger.warning("Supabase credentials not found. Service will be disabled.")
                self.client = None
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            self.client = None
    
    def upload_image(self, image_data: bytes, filename: str, bucket_name: str = 'images') -> Optional[str]:
        """
        Upload an image to Supabase Storage
        
        Args:
            image_data: Image data as bytes
            filename: Name of the file
            bucket_name: Name of the storage bucket
            
        Returns:
            Public URL of the uploaded image or None if failed
        """
        if not self.client:
            logger.error("Supabase client not available")
            return None
        
        try:
            # Generate unique filename
            file_extension = filename.split('.')[-1] if '.' in filename else 'jpg'
            unique_filename = f"{uuid.uuid4()}.{file_extension}"
            
            # Upload to Supabase Storage
            response = self.client.storage.from_(bucket_name).upload(
                path=unique_filename,
                file=image_data,
                file_options={"content-type": f"image/{file_extension}"}
            )
            
            # Get public URL
            public_url = self.client.storage.from_(bucket_name).get_public_url(unique_filename)
            
            logger.info(f"Image uploaded successfully: {public_url}")
            return public_url
            
        except Exception as e:
            logger.error(f"Error uploading image to Supabase: {e}")
            return None
    
    def delete_image(self, image_url: str, bucket_name: str = 'images') -> bool:
        """
        Delete an image from Supabase Storage
        
        Args:
            image_url: URL of the image to delete
            bucket_name: Name of the storage bucket
            
        Returns:
            True if successful, False otherwise
        """
        if not self.client:
            logger.error("Supabase client not available")
            return False
        
        try:
            # Extract filename from URL
            filename = image_url.split('/')[-1]
            
            # Delete from Supabase Storage
            self.client.storage.from_(bucket_name).remove([filename])
            
            logger.info(f"Image deleted successfully: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting image from Supabase: {e}")
            return False
    
    def create_image_record(self, user_id: str, image_url: str, faiss_index_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Create an image record in the database
        
        Args:
            user_id: ID of the user
            image_url: URL of the image
            faiss_index_id: ID in the FAISS index
            
        Returns:
            Image record data or None if failed
        """
        if not self.client:
            logger.error("Supabase client not available")
            return None
        
        try:
            image_data = {
                'id': str(uuid.uuid4()),
                'user_id': user_id,
                'image_url': image_url,
                'faiss_index_id': faiss_index_id,
                'created_at': datetime.utcnow().isoformat()
            }
            
            response = self.client.table('images').insert(image_data).execute()
            
            if response.data:
                logger.info(f"Image record created: {image_data['id']}")
                return response.data[0]
            else:
                logger.error("Failed to create image record")
                return None
                
        except Exception as e:
            logger.error(f"Error creating image record: {e}")
            return None
    
    def create_analysis_record(self, image_id: str, google_vision_result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create an analysis record in the database
        
        Args:
            image_id: ID of the image
            google_vision_result: Google Vision AI analysis result
            
        Returns:
            Analysis record data or None if failed
        """
        if not self.client:
            logger.error("Supabase client not available")
            return None
        
        try:
            analysis_data = {
                'id': str(uuid.uuid4()),
                'image_id': image_id,
                'google_vision_result': google_vision_result,
                'created_at': datetime.utcnow().isoformat()
            }
            
            response = self.client.table('analyses').insert(analysis_data).execute()
            
            if response.data:
                logger.info(f"Analysis record created: {analysis_data['id']}")
                return response.data[0]
            else:
                logger.error("Failed to create analysis record")
                return None
                
        except Exception as e:
            logger.error(f"Error creating analysis record: {e}")
            return None
    
    def create_vector_record(self, image_id: str, vector_data: List[float], model_name: str = 'resnet50') -> Optional[Dict[str, Any]]:
        """
        Create a vector record in the database
        
        Args:
            image_id: ID of the image
            vector_data: Vector embedding as list
            model_name: Name of the model used
            
        Returns:
            Vector record data or None if failed
        """
        if not self.client:
            logger.error("Supabase client not available")
            return None
        
        try:
            vector_record = {
                'id': str(uuid.uuid4()),
                'image_id': image_id,
                'vector_data': vector_data,
                'vector_dimension': len(vector_data),
                'model_name': model_name,
                'created_at': datetime.utcnow().isoformat()
            }
            
            response = self.client.table('image_vectors').insert(vector_record).execute()
            
            if response.data:
                logger.info(f"Vector record created: {vector_record['id']}")
                return response.data[0]
            else:
                logger.error("Failed to create vector record")
                return None
                
        except Exception as e:
            logger.error(f"Error creating vector record: {e}")
            return None
    
    def get_image_by_id(self, image_id: str) -> Optional[Dict[str, Any]]:
        """
        Get image record by ID
        
        Args:
            image_id: ID of the image
            
        Returns:
            Image record data or None if not found
        """
        if not self.client:
            logger.error("Supabase client not available")
            return None
        
        try:
            response = self.client.table('images').select('*').eq('id', image_id).execute()
            
            if response.data:
                return response.data[0]
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error getting image by ID: {e}")
            return None
    
    def get_images_by_user(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all images for a user
        
        Args:
            user_id: ID of the user
            
        Returns:
            List of image records
        """
        if not self.client:
            logger.error("Supabase client not available")
            return []
        
        try:
            response = self.client.table('images').select('*').eq('user_id', user_id).execute()
            return response.data or []
                
        except Exception as e:
            logger.error(f"Error getting images by user: {e}")
            return []
    
    def get_analysis_by_image_id(self, image_id: str) -> Optional[Dict[str, Any]]:
        """
        Get analysis record by image ID
        
        Args:
            image_id: ID of the image
            
        Returns:
            Analysis record data or None if not found
        """
        if not self.client:
            logger.error("Supabase client not available")
            return None
        
        try:
            response = self.client.table('analyses').select('*').eq('image_id', image_id).execute()
            
            if response.data:
                return response.data[0]
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error getting analysis by image ID: {e}")
            return None
    
    def get_vector_by_image_id(self, image_id: str) -> Optional[Dict[str, Any]]:
        """
        Get vector record by image ID
        
        Args:
            image_id: ID of the image
            
        Returns:
            Vector record data or None if not found
        """
        if not self.client:
            logger.error("Supabase client not available")
            return None
        
        try:
            response = self.client.table('image_vectors').select('*').eq('image_id', image_id).execute()
            
            if response.data:
                return response.data[0]
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error getting vector by image ID: {e}")
            return None
    
    def create_medical_analysis_record(self, medical_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a medical analysis record in the database
        
        Args:
            medical_data: Medical analysis data
            
        Returns:
            Medical analysis record data or None if failed
        """
        if not self.client:
            logger.error("Supabase client not available")
            return None
        
        try:
            medical_record = {
                'id': str(uuid.uuid4()),
                'user_id': medical_data['user_id'],
                'image_id': medical_data['image_id'],
                'condition_identified': medical_data['condition_identified'],
                'confidence_score': medical_data['confidence_score'],
                'detailed_description': medical_data['detailed_description'],
                'recommended_treatments': medical_data['recommended_treatments'],
                'similar_conditions': medical_data['similar_conditions'],
                'created_at': medical_data['created_at']
            }
            
            response = self.client.table('medical_analyses').insert(medical_record).execute()
            
            if response.data:
                logger.info(f"Medical analysis record created: {medical_record['id']}")
                return response.data[0]
            else:
                logger.error("Failed to create medical analysis record")
                return None
                
        except Exception as e:
            logger.error(f"Error creating medical analysis record: {e}")
            return None
    
    def get_medical_analysis_history(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get medical analysis history for a user
        
        Args:
            user_id: ID of the user
            
        Returns:
            List of medical analysis records
        """
        if not self.client:
            logger.error("Supabase client not available")
            return []
        
        try:
            response = self.client.table('medical_analyses').select('*').eq('user_id', user_id).order('created_at', desc=True).execute()
            return response.data or []
                
        except Exception as e:
            logger.error(f"Error getting medical analysis history: {e}")
            return []
    
    def get_medical_analysis_by_id(self, analysis_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get medical analysis by ID for a specific user
        
        Args:
            analysis_id: ID of the analysis
            user_id: ID of the user
            
        Returns:
            Medical analysis record data or None if not found
        """
        if not self.client:
            logger.error("Supabase client not available")
            return None
        
        try:
            response = self.client.table('medical_analyses').select('*').eq('id', analysis_id).eq('user_id', user_id).execute()
            
            if response.data:
                return response.data[0]
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error getting medical analysis by ID: {e}")
            return None
    
    def is_available(self) -> bool:
        """Check if the service is available"""
        return self.client is not None 