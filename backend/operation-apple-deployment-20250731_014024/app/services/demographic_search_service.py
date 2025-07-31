import logging
import numpy as np
from typing import List, Tuple, Dict, Any, Optional
from .faiss_service import FAISSService
from .supabase_service import SupabaseService

logger = logging.getLogger(__name__)


class DemographicWeightedSearch:
    """
    Service for demographic-weighted similarity search that combines visual similarity
    with demographic context for more personalized and relevant results.
    """
    
    def __init__(self, faiss_service: FAISSService, supabase_service: SupabaseService):
        """
        Initialize the demographic weighted search service
        
        Args:
            faiss_service: FAISS service for visual similarity search
            supabase_service: Supabase service for demographic metadata retrieval
        """
        self.faiss_service = faiss_service
        self.supabase_service = supabase_service
        
        # Configurable weighting parameters
        self.demographic_weight = 0.3  # Weight for demographic similarity (0-1)
        self.visual_weight = 1.0 - self.demographic_weight  # Weight for visual similarity
        
        # Demographic similarity weights
        self.ethnicity_weight = 0.6  # Highest priority for ethnicity matching
        self.skin_type_weight = 0.3  # Medium priority for skin type matching
        self.age_group_weight = 0.1  # Lower priority for age group matching
        
        logger.info(f"Initialized DemographicWeightedSearch with weights: "
                   f"demographic={self.demographic_weight}, visual={self.visual_weight}")
    
    def search_with_demographics(self, query_vector: np.ndarray, user_demographics: Dict[str, str], 
                               k: int = 10) -> List[Tuple[str, float]]:
        """
        Search with demographic weighting
        
        Args:
            query_vector: Feature vector of the query image
            user_demographics: Dict with user demographic info (ethnicity, skin_type, age_group)
            k: Number of results to return
            
        Returns:
            List of tuples (image_id, weighted_distance) sorted by relevance
        """
        try:
            if not self.faiss_service.is_available():
                logger.error("FAISS service not available")
                return []
            
            if not self.supabase_service.is_available():
                logger.warning("Supabase service not available, falling back to visual-only search")
                return self.faiss_service.search_similar(query_vector, k)
            
            # Get a larger set of base results to ensure we have enough candidates after filtering
            base_k = min(k * 3, 50)  # Get 3x more results but cap at 50 for performance
            base_results = self.faiss_service.search_similar(query_vector, base_k)
            
            if not base_results:
                logger.warning("No base results from FAISS search")
                return []
            
            logger.info(f"Retrieved {len(base_results)} base results from FAISS")
            
            weighted_results = []
            processed_count = 0
            
            for image_id, visual_distance in base_results:
                try:
                    # Get image metadata from Supabase
                    image_analysis = self.supabase_service.get_analysis_by_image_id(image_id)
                    if not image_analysis:
                        # If no demographic data available, use visual similarity only
                        weighted_results.append((image_id, visual_distance))
                        processed_count += 1
                        continue
                    
                    # Extract demographics from the analysis results
                    result_demographics = self._extract_demographics(image_analysis)
                    
                    # Calculate the demographic similarity score
                    demographic_similarity = self._calculate_demographic_similarity(
                        user_demographics, result_demographics
                    )
                    
                    # Apply demographic weighting to the distance score
                    # Lower distance = higher similarity, so we subtract demographic similarity
                    weighted_distance = (self.visual_weight * visual_distance - 
                                       self.demographic_weight * demographic_similarity)
                    
                    weighted_results.append((image_id, weighted_distance))
                    processed_count += 1
                    
                except Exception as e:
                    logger.warning(f"Error processing result for image {image_id}: {e}")
                    # Include result with visual similarity only
                    weighted_results.append((image_id, visual_distance))
                    processed_count += 1
            
            # Sort the results by the new weighted distance (lower = better)
            weighted_results.sort(key=lambda x: x[1])
            
            # Return the top k results
            final_results = weighted_results[:k]
            
            logger.info(f"Processed {processed_count} results, returning top {len(final_results)}")
            return final_results
            
        except Exception as e:
            logger.error(f"Error in demographic weighted search: {e}")
            # Fallback to visual-only search
            return self.faiss_service.search_similar(query_vector, k)
    
    def _extract_demographics(self, analysis: Dict[str, Any]) -> Dict[str, str]:
        """
        Extract demographic information from the analysis data
        
        Args:
            analysis: Analysis record from Supabase
            
        Returns:
            Dictionary with demographic information
        """
        demographics = {}
        
        try:
            # Get the Google Vision result from the analysis
            vision_result = analysis.get('google_vision_result', {})
            
            # Extract ethnicity (may be stored directly or in results)
            demographics['ethnicity'] = vision_result.get('ethnicity', '')
            
            # Extract skin type if available
            if 'skin_type' in vision_result:
                demographics['skin_type'] = vision_result['skin_type']
            
            # Extract age group if available
            if 'age_group' in vision_result:
                demographics['age_group'] = vision_result['age_group']
            
            # Check if demographics are in nested results structure
            results = vision_result.get('results', {})
            if results:
                # Look for demographic info in face detection results
                face_data = results.get('face_detection', {})
                if face_data and 'demographic_info' in face_data:
                    demo_info = face_data['demographic_info']
                    if 'ethnicity' in demo_info and not demographics.get('ethnicity'):
                        demographics['ethnicity'] = demo_info['ethnicity']
                    if 'age_group' in demo_info and not demographics.get('age_group'):
                        demographics['age_group'] = demo_info['age_group']
            
            # Clean up empty values
            demographics = {k: v for k, v in demographics.items() if v}
            
            logger.debug(f"Extracted demographics: {demographics}")
            return demographics
            
        except Exception as e:
            logger.warning(f"Error extracting demographics: {e}")
            return {}
    
    def _calculate_demographic_similarity(self, user_demographics: Dict[str, str], 
                                        result_demographics: Dict[str, str]) -> float:
        """
        Calculate the similarity between two demographic profiles
        
        Args:
            user_demographics: User's demographic information
            result_demographics: Result image's demographic information
            
        Returns:
            Similarity score between 0 and 1 (1 = perfect match)
        """
        try:
            similarity = 0.0
            total_weight = 0.0
            
            # Ethnicity similarity (highest weight)
            if ('ethnicity' in user_demographics and 'ethnicity' in result_demographics and
                user_demographics['ethnicity'] and result_demographics['ethnicity']):
                
                weight = self.ethnicity_weight
                if user_demographics['ethnicity'].lower() == result_demographics['ethnicity'].lower():
                    similarity += weight
                total_weight += weight
            
            # Skin type similarity
            if ('skin_type' in user_demographics and 'skin_type' in result_demographics and
                user_demographics['skin_type'] and result_demographics['skin_type']):
                
                weight = self.skin_type_weight
                if user_demographics['skin_type'].lower() == result_demographics['skin_type'].lower():
                    similarity += weight
                total_weight += weight
            
            # Age group similarity
            if ('age_group' in user_demographics and 'age_group' in result_demographics and
                user_demographics['age_group'] and result_demographics['age_group']):
                
                weight = self.age_group_weight
                if user_demographics['age_group'].lower() == result_demographics['age_group'].lower():
                    similarity += weight
                total_weight += weight
            
            # Normalize the similarity score
            if total_weight > 0:
                similarity = similarity / total_weight
            else:
                # No demographic information available for comparison
                similarity = 0.0
            
            logger.debug(f"Demographic similarity: {similarity:.3f} (total_weight: {total_weight:.3f})")
            return similarity
            
        except Exception as e:
            logger.warning(f"Error calculating demographic similarity: {e}")
            return 0.0
    
    def set_demographic_weight(self, weight: float) -> None:
        """
        Set the demographic weighting parameter
        
        Args:
            weight: Weight for demographic similarity (0-1)
        """
        if 0.0 <= weight <= 1.0:
            self.demographic_weight = weight
            self.visual_weight = 1.0 - weight
            logger.info(f"Updated demographic weight to {weight}")
        else:
            logger.warning(f"Invalid demographic weight {weight}, must be between 0 and 1")
    
    def set_demographic_component_weights(self, ethnicity: float = 0.6, 
                                        skin_type: float = 0.3, 
                                        age_group: float = 0.1) -> None:
        """
        Set the weights for different demographic components
        
        Args:
            ethnicity: Weight for ethnicity matching
            skin_type: Weight for skin type matching
            age_group: Weight for age group matching
        """
        total = ethnicity + skin_type + age_group
        if abs(total - 1.0) > 0.01:  # Allow small floating point errors
            logger.warning(f"Demographic component weights sum to {total}, normalizing to 1.0")
            ethnicity = ethnicity / total
            skin_type = skin_type / total
            age_group = age_group / total
        
        self.ethnicity_weight = ethnicity
        self.skin_type_weight = skin_type
        self.age_group_weight = age_group
        
        logger.info(f"Updated demographic component weights: "
                   f"ethnicity={ethnicity:.3f}, skin_type={skin_type:.3f}, age_group={age_group:.3f}")
    
    def get_configuration(self) -> Dict[str, float]:
        """
        Get current configuration parameters
        
        Returns:
            Dictionary with current weight settings
        """
        return {
            'demographic_weight': self.demographic_weight,
            'visual_weight': self.visual_weight,
            'ethnicity_weight': self.ethnicity_weight,
            'skin_type_weight': self.skin_type_weight,
            'age_group_weight': self.age_group_weight
        }
    
    def is_available(self) -> bool:
        """
        Check if the service is available
        
        Returns:
            True if both FAISS and Supabase services are available
        """
        return (self.faiss_service.is_available() and 
                self.supabase_service.is_available())