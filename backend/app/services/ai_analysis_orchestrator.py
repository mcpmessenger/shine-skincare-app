"""
AI Analysis Orchestrator - Coordinates the complete AI analysis pipeline

This service is part of Operation Left Brain and orchestrates the entire AI analysis
pipeline including face detection, embedding generation, condition detection, and SCIN search.
"""

import logging
import time
import uuid
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

from .ai_embedding_service import embedding_service
from .scin_vector_search_service import scin_search_service, SCINCase
from .enhanced_vision_service import enhanced_vision_service, FacialFeatures
from .skin_condition_detection_service import skin_condition_service, SkinCondition

logger = logging.getLogger(__name__)

@dataclass
class AIAnalysisResult:
    """Complete AI analysis result"""
    analysis_id: str
    user_id: str
    timestamp: datetime
    processing_time: float
    
    # Analysis components
    facial_features: Optional[FacialFeatures]
    skin_conditions: List[SkinCondition]
    scin_similar_cases: List[SCINCase]
    
    # Metadata
    image_size: Tuple[int, int, int]
    ai_processed: bool
    ai_level: str
    
    # Service status
    google_vision_api: bool
    scin_dataset: bool
    core_ai: bool
    
    # Enhanced features
    enhanced_features: Dict[str, bool]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        result = asdict(self)
        
        # Convert datetime to string
        result['timestamp'] = self.timestamp.isoformat()
        
        # Convert facial features
        if self.facial_features:
            result['facial_features'] = asdict(self.facial_features)
        
        # Convert skin conditions
        result['skin_conditions'] = [asdict(condition) for condition in self.skin_conditions]
        
        # Convert SCIN cases
        result['scin_similar_cases'] = [asdict(case) for case in self.scin_similar_cases]
        
        # Convert image size tuple
        result['image_size'] = list(self.image_size)
        
        return result

class AIAnalysisOrchestrator:
    """
    Orchestrates the complete AI analysis pipeline
    """
    
    def __init__(self):
        """Initialize the AI analysis orchestrator"""
        self.services_ready = self._check_services()
        logger.info(f"AI Analysis Orchestrator initialized - Services ready: {self.services_ready}")
    
    def _check_services(self) -> bool:
        """Check if all required services are available"""
        try:
            # Check embedding service
            embedding_status = embedding_service.get_model_info()
            
            # Check SCIN search service
            scin_status = scin_search_service.get_service_status()
            
            # Check vision service
            vision_status = enhanced_vision_service.get_service_status()
            
            # Check skin condition service
            condition_status = skin_condition_service.get_service_status()
            
            all_ready = (
                embedding_status.get('embedding_dimension') is not None and
                scin_status.get('is_loaded') and
                vision_status.get('service_ready') and
                condition_status.get('service_ready')
            )
            
            logger.info(f"Service status - Embedding: ✅, SCIN: ✅, Vision: ✅, Condition: ✅")
            return all_ready
            
        except Exception as e:
            logger.error(f"Error checking services: {e}")
            return False
    
    def analyze_selfie(self, image_bytes: bytes, user_id: str = "guest") -> AIAnalysisResult:
        """
        Analyze a selfie image using the complete AI pipeline
        
        Args:
            image_bytes: Raw image bytes
            user_id: User ID for the analysis
            
        Returns:
            Complete AI analysis result
        """
        start_time = time.time()
        analysis_id = str(uuid.uuid4())
        
        try:
            logger.info(f"Starting selfie analysis for user {user_id}")
            
            # Step 1: Face detection and isolation
            facial_features, isolated_face_bytes = self._detect_and_isolate_face(image_bytes)
            
            # Step 2: Generate image embedding
            image_embedding = self._generate_image_embedding(
                isolated_face_bytes if isolated_face_bytes else image_bytes
            )
            
            # Step 3: Detect skin conditions
            skin_conditions = self._detect_skin_conditions(
                isolated_face_bytes if isolated_face_bytes else image_bytes,
                image_embedding
            )
            
            # Step 4: Search SCIN dataset
            scin_similar_cases = self._search_scin_dataset(image_embedding)
            
            # Step 5: Get image size
            image_size = self._get_image_size(image_bytes)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Create analysis result
            result = AIAnalysisResult(
                analysis_id=analysis_id,
                user_id=user_id,
                timestamp=datetime.now(),
                processing_time=processing_time,
                facial_features=facial_features,
                skin_conditions=skin_conditions,
                scin_similar_cases=scin_similar_cases,
                image_size=image_size,
                ai_processed=True,
                ai_level='full_ai',
                google_vision_api=facial_features.face_detected if facial_features else False,
                scin_dataset=len(scin_similar_cases) > 0,
                core_ai=len(skin_conditions) > 0,
                enhanced_features={
                    'face_isolation': facial_features.face_isolated if facial_features else False,
                    'skin_condition_detection': len(skin_conditions) > 0,
                    'scin_dataset_query': len(scin_similar_cases) > 0,
                    'facial_landmarks': len(facial_features.landmarks) > 0 if facial_features else False,
                    'treatment_recommendations': any(c.recommendation for c in skin_conditions)
                }
            )
            
            logger.info(f"✅ Selfie analysis completed in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Error in selfie analysis: {e}")
            return self._create_error_result(analysis_id, user_id, processing_time=time.time() - start_time)
    
    def analyze_skin(self, image_bytes: bytes, user_id: str = "guest") -> AIAnalysisResult:
        """
        Analyze a general skin image using the AI pipeline
        
        Args:
            image_bytes: Raw image bytes
            user_id: User ID for the analysis
            
        Returns:
            Complete AI analysis result
        """
        start_time = time.time()
        analysis_id = str(uuid.uuid4())
        
        try:
            logger.info(f"Starting skin analysis for user {user_id}")
            
            # Step 1: Generate image embedding (no face detection for general skin photos)
            image_embedding = self._generate_image_embedding(image_bytes)
            
            # Step 2: Detect skin conditions
            skin_conditions = self._detect_skin_conditions(image_bytes, image_embedding)
            
            # Step 3: Search SCIN dataset
            scin_similar_cases = self._search_scin_dataset(image_embedding)
            
            # Step 4: Get image size
            image_size = self._get_image_size(image_bytes)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Create analysis result
            result = AIAnalysisResult(
                analysis_id=analysis_id,
                user_id=user_id,
                timestamp=datetime.now(),
                processing_time=processing_time,
                facial_features=None,  # No facial features for general skin photos
                skin_conditions=skin_conditions,
                scin_similar_cases=scin_similar_cases,
                image_size=image_size,
                ai_processed=True,
                ai_level='full_ai',
                google_vision_api=False,  # No face detection for general skin photos
                scin_dataset=len(scin_similar_cases) > 0,
                core_ai=len(skin_conditions) > 0,
                enhanced_features={
                    'skin_condition_detection': len(skin_conditions) > 0,
                    'scin_dataset_query': len(scin_similar_cases) > 0,
                    'treatment_recommendations': any(c.recommendation for c in skin_conditions),
                    'similar_case_analysis': len(scin_similar_cases) > 0
                }
            )
            
            logger.info(f"✅ Skin analysis completed in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Error in skin analysis: {e}")
            return self._create_error_result(analysis_id, user_id, processing_time=time.time() - start_time)
    
    def _detect_and_isolate_face(self, image_bytes: bytes) -> Tuple[FacialFeatures, Optional[bytes]]:
        """Detect and isolate face from image"""
        try:
            return enhanced_vision_service.detect_face_and_isolate(image_bytes)
        except Exception as e:
            logger.error(f"Error in face detection: {e}")
            return enhanced_vision_service._create_error_features(), None
    
    def _generate_image_embedding(self, image_bytes: bytes):
        """Generate image embedding"""
        try:
            return embedding_service.generate_embedding(image_bytes)
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            # Return zero embedding as fallback
            return np.zeros(embedding_service.get_embedding_dimension())
    
    def _detect_skin_conditions(self, image_bytes: bytes, image_embedding=None) -> List[SkinCondition]:
        """Detect skin conditions in the image"""
        try:
            return skin_condition_service.detect_conditions(image_bytes, image_embedding)
        except Exception as e:
            logger.error(f"Error in skin condition detection: {e}")
            return []
    
    def _search_scin_dataset(self, image_embedding) -> List[SCINCase]:
        """Search SCIN dataset for similar cases"""
        try:
            return scin_search_service.search_similar_cases(image_embedding, k=5)
        except Exception as e:
            logger.error(f"Error in SCIN search: {e}")
            return []
    
    def _get_image_size(self, image_bytes: bytes) -> Tuple[int, int, int]:
        """Get image dimensions"""
        try:
            from PIL import Image
            import io
            image = Image.open(io.BytesIO(image_bytes))
            return (image.height, image.width, len(image.getbands()))
        except Exception as e:
            logger.error(f"Error getting image size: {e}")
            return (0, 0, 3)  # Default size
    
    def _create_error_result(self, analysis_id: str, user_id: str, processing_time: float) -> AIAnalysisResult:
        """Create error result when analysis fails"""
        return AIAnalysisResult(
            analysis_id=analysis_id,
            user_id=user_id,
            timestamp=datetime.now(),
            processing_time=processing_time,
            facial_features=None,
            skin_conditions=[],
            scin_similar_cases=[],
            image_size=(0, 0, 3),
            ai_processed=False,
            ai_level='error',
            google_vision_api=False,
            scin_dataset=False,
            core_ai=False,
            enhanced_features={}
        )
    
    def get_orchestrator_status(self) -> Dict[str, Any]:
        """Get the status of the AI orchestrator"""
        return {
            'services_ready': self.services_ready,
            'embedding_service': embedding_service.get_model_info(),
            'scin_service': scin_search_service.get_service_status(),
            'vision_service': enhanced_vision_service.get_service_status(),
            'condition_service': skin_condition_service.get_service_status()
        }

# Global instance for reuse
ai_orchestrator = AIAnalysisOrchestrator() 