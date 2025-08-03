"""
Vertex AI Service for Operation Right Brain 🧠
Handles image embedding generation using Google Cloud Vertex AI Multimodal Embeddings.

Author: Manus AI
Date: August 2, 2025
"""

import logging
import base64
from typing import Optional, List
import io
from PIL import Image
import numpy as np

from google.cloud import aiplatform
from google.cloud.aiplatform_v1 import PredictRequest
from google.cloud.aiplatform_v1.types import PredictResponse
from google.api_core import exceptions as google_exceptions

logger = logging.getLogger(__name__)

class VertexAIService:
    """
    Service for interacting with Google Cloud Vertex AI Multimodal Embeddings.
    Implements BR3: Integration with Vertex AI Multimodal Embeddings to generate high-dimensional vectors.
    """
    
    def __init__(self):
        """Initialize the Vertex AI service."""
        try:
            # Initialize Vertex AI
            aiplatform.init(
                project=os.getenv('GOOGLE_CLOUD_PROJECT'),
                location=os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1')
            )
            
            # Initialize the multimodal embeddings model
            self.model_name = "multimodalembedding@001"
            self.endpoint = aiplatform.Endpoint(
                endpoint_name=f"projects/{os.getenv('GOOGLE_CLOUD_PROJECT')}/locations/{os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1')}/endpoints/{self.model_name}"
            )
            
            logger.info("Vertex AI Multimodal Embeddings service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Vertex AI service: {str(e)}")
            raise
    
    def generate_image_embedding(self, image_data: bytes) -> Optional[List[float]]:
        """
        Generate high-dimensional embedding for an image using Vertex AI Multimodal Embeddings.
        
        Args:
            image_data: Image bytes (should be isolated face image)
            
        Returns:
            List of float values representing the image embedding, or None if failed
        """
        try:
            # Encode image to base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # Prepare the prediction request
            prediction_request = PredictRequest(
                endpoint=self.endpoint.name,
                instances=[{
                    "image": {
                        "bytesBase64Encoded": image_base64
                    }
                }]
            )
            
            # Make prediction request
            response = self.endpoint.predict(prediction_request)
            
            # Extract embedding from response
            if response.predictions and len(response.predictions) > 0:
                embedding = response.predictions[0].get('embedding', [])
                
                if embedding:
                    logger.info(f"Generated embedding with {len(embedding)} dimensions")
                    return embedding
                else:
                    logger.warning("No embedding found in response")
                    return None
            else:
                logger.warning("No predictions in response")
                return None
                
        except google_exceptions.GoogleAPIError as e:
            logger.error(f"Vertex AI API error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error generating image embedding: {str(e)}")
            return None
    
    def generate_text_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding for text using Vertex AI Multimodal Embeddings.
        
        Args:
            text: Input text
            
        Returns:
            List of float values representing the text embedding, or None if failed
        """
        try:
            # Prepare the prediction request
            prediction_request = PredictRequest(
                endpoint=self.endpoint.name,
                instances=[{
                    "text": text
                }]
            )
            
            # Make prediction request
            response = self.endpoint.predict(prediction_request)
            
            # Extract embedding from response
            if response.predictions and len(response.predictions) > 0:
                embedding = response.predictions[0].get('embedding', [])
                
                if embedding:
                    logger.info(f"Generated text embedding with {len(embedding)} dimensions")
                    return embedding
                else:
                    logger.warning("No text embedding found in response")
                    return None
            else:
                logger.warning("No predictions in response")
                return None
                
        except google_exceptions.GoogleAPIError as e:
            logger.error(f"Vertex AI API error for text embedding: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error generating text embedding: {str(e)}")
            return None
    
    def generate_multimodal_embedding(self, image_data: bytes, text: str) -> Optional[List[float]]:
        """
        Generate embedding for image + text combination.
        
        Args:
            image_data: Image bytes
            text: Associated text
            
        Returns:
            List of float values representing the multimodal embedding, or None if failed
        """
        try:
            # Encode image to base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # Prepare the prediction request
            prediction_request = PredictRequest(
                endpoint=self.endpoint.name,
                instances=[{
                    "image": {
                        "bytesBase64Encoded": image_base64
                    },
                    "text": text
                }]
            )
            
            # Make prediction request
            response = self.endpoint.predict(prediction_request)
            
            # Extract embedding from response
            if response.predictions and len(response.predictions) > 0:
                embedding = response.predictions[0].get('embedding', [])
                
                if embedding:
                    logger.info(f"Generated multimodal embedding with {len(embedding)} dimensions")
                    return embedding
                else:
                    logger.warning("No multimodal embedding found in response")
                    return None
            else:
                logger.warning("No predictions in response")
                return None
                
        except google_exceptions.GoogleAPIError as e:
            logger.error(f"Vertex AI API error for multimodal embedding: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error generating multimodal embedding: {str(e)}")
            return None
    
    def check_health(self) -> dict:
        """
        Check the health status of Vertex AI service.
        
        Returns:
            Health status dictionary
        """
        try:
            # Create a simple test image
            test_image = Image.new('RGB', (100, 100), color='white')
            test_bytes = io.BytesIO()
            test_image.save(test_bytes, format='JPEG')
            test_data = test_bytes.getvalue()
            
            # Test embedding generation
            embedding = self.generate_image_embedding(test_data)
            
            if embedding:
                return {
                    "status": "healthy",
                    "service": "Vertex AI Multimodal Embeddings",
                    "embedding_dimensions": len(embedding),
                    "message": "Service is responding correctly"
                }
            else:
                return {
                    "status": "unhealthy",
                    "service": "Vertex AI Multimodal Embeddings",
                    "error": "Failed to generate test embedding"
                }
            
        except Exception as e:
            logger.error(f"Vertex AI health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "service": "Vertex AI Multimodal Embeddings",
                "error": str(e)
            }
    
    def get_embedding_dimensions(self) -> int:
        """
        Get the dimensionality of embeddings generated by this model.
        
        Returns:
            Number of dimensions in the embedding vector
        """
        try:
            # Generate a test embedding to determine dimensions
            test_image = Image.new('RGB', (100, 100), color='white')
            test_bytes = io.BytesIO()
            test_image.save(test_bytes, format='JPEG')
            test_data = test_bytes.getvalue()
            
            embedding = self.generate_image_embedding(test_data)
            return len(embedding) if embedding else 0
            
        except Exception as e:
            logger.error(f"Error getting embedding dimensions: {str(e)}")
            return 0 