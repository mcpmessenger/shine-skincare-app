"""
Mock Demographic Search Service for Vercel deployment
This provides the same interface as DemographicWeightedSearch but without heavy dependencies
"""
import logging
import hashlib
from typing import List, Tuple, Dict, Any, Optional

logger = logging.getLogger(__name__)

class MockDemographicSearchService:
    """Mock implementation of Demographic Weighted Search for deployment testing"""
    
    def __init__(self):
        self.service_name = "mock_demographic_search"
        self._available = True
        self._demographic_weight = 0.3
        self._ethnicity_weight = 0.6
        self._skin_type_weight = 0.3
        self._age_group_weight = 0.1
        logger.info("Mock Demographic Search Service initialized")
    
    def is_available(self):
        """Check if the service is available"""
        return self._available
    
    def search_with_demographics(self, query_vector: List[float], demographics: Dict[str, Any], k: int = 5) -> List[Tuple[str, float]]:
        """
        Mock demographic-weighted search that returns consistent results
        """
        try:
            # Generate mock results based on demographics and query vector
            query_hash = hashlib.md5(str(query_vector).encode()).hexdigest()
            demo_hash = hashlib.md5(str(demographics).encode()).hexdigest()
            combined_hash = hashlib.md5((query_hash + demo_hash).encode()).hexdigest()
            
            # Generate mock similar image IDs and distances
            results = []
            for i in range(min(k, 5)):  # Return up to 5 results
                # Generate consistent image ID
                image_id = f"mock_image_{combined_hash[i*2:(i*2)+8]}"
                
                # Generate mock distance (lower is better)
                base_distance = 0.1 + (int(combined_hash[i*3:(i*3)+2], 16) % 80) / 100.0  # 0.1 to 0.9
                
                # Adjust distance based on demographic similarity
                ethnicity = demographics.get('ethnicity', '')
                if ethnicity:
                    # Mock demographic bonus
                    demographic_bonus = 0.1 * self._demographic_weight
                    base_distance = max(0.05, base_distance - demographic_bonus)
                
                results.append((image_id, base_distance))
            
            # Sort by distance (ascending)
            results.sort(key=lambda x: x[1])
            
            logger.info(f"Mock demographic search returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Mock demographic search error: {e}")
            return []
    
    def set_demographic_weight(self, weight: float) -> None:
        """Set the demographic weight"""
        self._demographic_weight = max(0.0, min(1.0, weight))
        logger.info(f"Mock demographic weight set to: {self._demographic_weight}")
    
    def set_demographic_component_weights(self, ethnicity_weight: float, skin_type_weight: float, age_group_weight: float) -> None:
        """Set the component weights for demographic similarity"""
        total = ethnicity_weight + skin_type_weight + age_group_weight
        if total > 0:
            self._ethnicity_weight = ethnicity_weight / total
            self._skin_type_weight = skin_type_weight / total
            self._age_group_weight = age_group_weight / total
        
        logger.info(f"Mock demographic component weights set: ethnicity={self._ethnicity_weight:.2f}, "
                   f"skin_type={self._skin_type_weight:.2f}, age_group={self._age_group_weight:.2f}")
    
    def get_configuration(self) -> Dict[str, Any]:
        """Get the current configuration"""
        return {
            'service': 'mock_demographic_search',
            'demographic_weight': self._demographic_weight,
            'component_weights': {
                'ethnicity': self._ethnicity_weight,
                'skin_type': self._skin_type_weight,
                'age_group': self._age_group_weight
            },
            'status': 'available' if self._available else 'unavailable',
            'type': 'mock'
        }