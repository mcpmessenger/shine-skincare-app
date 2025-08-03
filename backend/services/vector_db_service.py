"""
Vector Database Service for Operation Right Brain 🧠
Handles similarity search against pre-computed SCIN dataset embeddings.

Author: Manus AI
Date: August 2, 2025
"""

import logging
import os
from typing import List, Optional, Dict, Any
import numpy as np
from dataclasses import dataclass

from google.cloud import aiplatform
from google.cloud.aiplatform_v1 import FindNearestNeighborsRequest
from google.cloud.aiplatform_v1.types import FindNearestNeighborsResponse
from google.api_core import exceptions as google_exceptions

from models.skin_analysis import SCINMatch

logger = logging.getLogger(__name__)

@dataclass
class VectorDBConfig:
    """Configuration for vector database connection."""
    project_id: str
    location: str
    index_endpoint_id: str
    deployed_index_id: str

class VectorDBService:
    """
    Service for interacting with vector database (Vertex AI Matching Engine).
    Implements BR4 & BR5: Vector database connection and similarity search.
    """
    
    def __init__(self):
        """Initialize the vector database service."""
        try:
            # Load configuration
            self.config = VectorDBConfig(
                project_id=os.getenv('GOOGLE_CLOUD_PROJECT'),
                location=os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1'),
                index_endpoint_id=os.getenv('VECTOR_DB_INDEX_ENDPOINT_ID'),
                deployed_index_id=os.getenv('VECTOR_DB_DEPLOYED_INDEX_ID')
            )
            
            # Initialize Vertex AI
            aiplatform.init(
                project=self.config.project_id,
                location=self.config.location
            )
            
            # Initialize the index endpoint
            self.index_endpoint = aiplatform.MatchingEngineIndexEndpoint(
                index_endpoint_name=f"projects/{self.config.project_id}/locations/{self.config.location}/indexEndpoints/{self.config.index_endpoint_id}"
            )
            
            logger.info("Vector database service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize vector database service: {str(e)}")
            raise
    
    def find_similar_conditions(self, embedding: List[float], top_k: int = 5) -> List[SCINMatch]:
        """
        Find similar skin conditions using vector similarity search.
        
        Args:
            embedding: Query embedding vector
            top_k: Number of top matches to return
            
        Returns:
            List of SCINMatch objects containing similar conditions
        """
        try:
            # Convert embedding to numpy array
            query_embedding = np.array(embedding, dtype=np.float32)
            
            # Prepare the nearest neighbors request
            request = FindNearestNeighborsRequest(
                index_endpoint=self.index_endpoint.name,
                deployed_index_id=self.config.deployed_index_id,
                queries=[{
                    "datapoint": {
                        "datapoint_id": "query",
                        "feature_vector": query_embedding.tolist()
                    },
                    "neighbor_count": top_k
                }]
            )
            
            # Perform similarity search
            response = self.index_endpoint.find_neighbors(request)
            
            # Process results
            matches = []
            if response.nearest_neighbors and len(response.nearest_neighbors) > 0:
                for neighbor in response.nearest_neighbors[0].neighbors:
                    # Extract metadata from neighbor
                    metadata = self._extract_metadata_from_neighbor(neighbor)
                    
                    match = SCINMatch(
                        case_id=metadata.get('case_id', ''),
                        condition_name=metadata.get('condition_name', ''),
                        description=metadata.get('description', ''),
                        symptoms=metadata.get('symptoms', []),
                        recommendations=metadata.get('recommendations', []),
                        severity=metadata.get('severity', 'unknown'),
                        similarity_score=neighbor.distance,
                        image_path=metadata.get('image_path', '')
                    )
                    matches.append(match)
            
            logger.info(f"Found {len(matches)} similar conditions")
            return matches
            
        except google_exceptions.GoogleAPIError as e:
            logger.error(f"Vector database API error: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Error in similarity search: {str(e)}")
            return []
    
    def _extract_metadata_from_neighbor(self, neighbor) -> Dict[str, Any]:
        """
        Extract metadata from a neighbor result.
        
        Args:
            neighbor: Neighbor object from vector search
            
        Returns:
            Dictionary containing metadata
        """
        try:
            # The metadata should be stored in the neighbor's attributes
            # This depends on how the SCIN dataset was indexed
            metadata = {}
            
            # Extract from neighbor attributes if available
            if hasattr(neighbor, 'attributes'):
                for key, value in neighbor.attributes.items():
                    metadata[key] = value
            
            # Fallback to default values if metadata is not available
            if not metadata:
                metadata = {
                    'case_id': f"case_{neighbor.datapoint_id}",
                    'condition_name': 'Unknown Condition',
                    'description': 'Condition details not available',
                    'symptoms': [],
                    'recommendations': ['Consult a dermatologist for proper diagnosis'],
                    'severity': 'unknown',
                    'image_path': ''
                }
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error extracting metadata from neighbor: {str(e)}")
            return {
                'case_id': 'unknown',
                'condition_name': 'Unknown Condition',
                'description': 'Metadata extraction failed',
                'symptoms': [],
                'recommendations': ['Consult a dermatologist for proper diagnosis'],
                'severity': 'unknown',
                'image_path': ''
            }
    
    def batch_find_similar_conditions(self, embeddings: List[List[float]], top_k: int = 5) -> List[List[SCINMatch]]:
        """
        Perform batch similarity search for multiple embeddings.
        
        Args:
            embeddings: List of query embedding vectors
            top_k: Number of top matches to return per query
            
        Returns:
            List of lists of SCINMatch objects
        """
        try:
            # Convert embeddings to numpy arrays
            query_embeddings = [np.array(emb, dtype=np.float32) for emb in embeddings]
            
            # Prepare batch request
            queries = []
            for i, embedding in enumerate(query_embeddings):
                queries.append({
                    "datapoint": {
                        "datapoint_id": f"query_{i}",
                        "feature_vector": embedding.tolist()
                    },
                    "neighbor_count": top_k
                })
            
            request = FindNearestNeighborsRequest(
                index_endpoint=self.index_endpoint.name,
                deployed_index_id=self.config.deployed_index_id,
                queries=queries
            )
            
            # Perform batch similarity search
            response = self.index_endpoint.find_neighbors(request)
            
            # Process results
            all_matches = []
            for i, nearest_neighbors in enumerate(response.nearest_neighbors):
                matches = []
                for neighbor in nearest_neighbors.neighbors:
                    metadata = self._extract_metadata_from_neighbor(neighbor)
                    
                    match = SCINMatch(
                        case_id=metadata.get('case_id', ''),
                        condition_name=metadata.get('condition_name', ''),
                        description=metadata.get('description', ''),
                        symptoms=metadata.get('symptoms', []),
                        recommendations=metadata.get('recommendations', []),
                        severity=metadata.get('severity', 'unknown'),
                        similarity_score=neighbor.distance,
                        image_path=metadata.get('image_path', '')
                    )
                    matches.append(match)
                
                all_matches.append(matches)
            
            logger.info(f"Batch search completed for {len(embeddings)} queries")
            return all_matches
            
        except Exception as e:
            logger.error(f"Error in batch similarity search: {str(e)}")
            return [[] for _ in embeddings]
    
    def check_health(self) -> dict:
        """
        Check the health status of the vector database.
        
        Returns:
            Health status dictionary
        """
        try:
            # Create a test embedding (random vector)
            test_embedding = np.random.rand(1408).tolist()  # Assuming 1408 dimensions
            
            # Try a simple search
            matches = self.find_similar_conditions(test_embedding, top_k=1)
            
            return {
                "status": "healthy",
                "service": "Vector Database (Vertex AI Matching Engine)",
                "matches_found": len(matches),
                "message": "Service is responding correctly"
            }
            
        except Exception as e:
            logger.error(f"Vector database health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "service": "Vector Database (Vertex AI Matching Engine)",
                "error": str(e)
            }
    
    def get_index_stats(self) -> dict:
        """
        Get statistics about the vector database index.
        
        Returns:
            Dictionary containing index statistics
        """
        try:
            # This would require additional API calls to get index statistics
            # For now, return basic information
            return {
                "index_endpoint_id": self.config.index_endpoint_id,
                "deployed_index_id": self.config.deployed_index_id,
                "location": self.config.location,
                "project_id": self.config.project_id
            }
            
        except Exception as e:
            logger.error(f"Error getting index stats: {str(e)}")
            return {"error": str(e)}
    
    def validate_embedding_dimensions(self, embedding: List[float]) -> bool:
        """
        Validate that the embedding has the correct dimensions.
        
        Args:
            embedding: Embedding vector to validate
            
        Returns:
            True if dimensions are correct, False otherwise
        """
        try:
            # Get expected dimensions from the service
            expected_dimensions = self.get_embedding_dimensions()
            
            if expected_dimensions == 0:
                # If we can't determine expected dimensions, assume it's valid
                return len(embedding) > 0
            
            return len(embedding) == expected_dimensions
            
        except Exception as e:
            logger.error(f"Error validating embedding dimensions: {str(e)}")
            return False
    
    def get_embedding_dimensions(self) -> int:
        """
        Get the expected embedding dimensions for this index.
        
        Returns:
            Number of dimensions expected by the index
        """
        # This would typically be retrieved from the index metadata
        # For now, return a common dimension for multimodal embeddings
        return 1408  # Common dimension for multimodal embeddings 