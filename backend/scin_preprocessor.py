"""
🧠 SCIN Dataset Pre-processing Pipeline
Operation Right Brain - Offline batch process for SCIN dataset preparation
"""

import os
import logging
import base64
from typing import List, Dict, Any
from datetime import datetime
import json

# Google Cloud imports
try:
    from google.cloud import vision
    from google.cloud import aiplatform
    from google.cloud import storage
    from google.auth import default
except ImportError as e:
    print(f"Warning: Google Cloud libraries not installed: {e}")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SCINPreprocessor:
    """Pre-process SCIN dataset for Operation Right Brain"""
    
    def __init__(self, project_id: str, bucket_name: str):
        self.project_id = project_id
        self.bucket_name = bucket_name
        self.vision_client = None
        self.storage_client = None
        
        # Initialize Google Cloud clients
        try:
            credentials, _ = default()
            self.vision_client = vision.ImageAnnotatorClient(credentials=credentials)
            self.storage_client = storage.Client(credentials=credentials)
            aiplatform.init(project=project_id, location='us-central1')
            logger.info("Google Cloud clients initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Google Cloud clients: {e}")
    
    def download_scin_images(self) -> List[str]:
        """Get SCIN images from local directory"""
        try:
            logger.info("Step 1: Loading local SCIN images...")
            
            # Look for images in the local scin_dataset/raw directory
            raw_dir = "scin_dataset/raw"
            image_files = []
            
            if os.path.exists(raw_dir):
                for condition_dir in os.listdir(raw_dir):
                    condition_path = os.path.join(raw_dir, condition_dir)
                    if os.path.isdir(condition_path):
                        for file in os.listdir(condition_path):
                            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                                image_path = os.path.join(condition_path, file)
                                image_files.append(image_path)
                                logger.info(f"Found local image: {image_path}")
            
            if image_files:
                logger.info(f"Found {len(image_files)} local images")
                return image_files
            else:
                logger.warning("No local images found in scin_dataset/raw/")
                return []
                
        except Exception as e:
            logger.error(f"Failed to load local SCIN images: {e}")
            return []
    
    def isolate_face_with_vision_api(self, image_path: str) -> Dict[str, Any]:
        """Use Google Vision API for face isolation"""
        try:
            with open(image_path, 'rb') as image_file:
                content = image_file.read()
            
            image = vision.Image(content=content)
            
            # Face detection
            face_response = self.vision_client.face_detection(image=image)
            faces = face_response.face_annotations
            
            if not faces:
                return {'face_detected': False, 'confidence': 0.0}
            
            # Label detection for skin analysis
            label_response = self.vision_client.label_detection(image=image)
            labels = [label.description.lower() for label in label_response.label_annotations]
            
            # Analyze skin characteristics
            skin_conditions = []
            if 'acne' in labels or 'pimple' in labels:
                skin_conditions.append('acne')
            if 'redness' in labels or 'inflammation' in labels:
                skin_conditions.append('inflammation')
            if 'dark spot' in labels or 'hyperpigmentation' in labels:
                skin_conditions.append('hyperpigmentation')
            if 'wrinkle' in labels or 'aging' in labels:
                skin_conditions.append('aging')
            
            return {
                'face_detected': True,
                'confidence': faces[0].detection_confidence,
                'skin_characteristics': {
                    'texture': 'smooth' if 'smooth' in labels else 'normal',
                    'tone': 'even' if 'even' in labels else 'normal',
                    'conditions': skin_conditions
                }
            }
            
        except Exception as e:
            logger.error(f"Vision API error for {image_path}: {e}")
            return {'face_detected': False, 'confidence': 0.0}
    
    def generate_embedding_with_vertex_ai(self, image_path: str) -> List[float]:
        """Generate embeddings using Vertex AI"""
        try:
            with open(image_path, 'rb') as image_file:
                content = image_file.read()
            
            # Convert to base64
            image_base64 = base64.b64encode(content).decode('utf-8')
            
            # Use Vertex AI multimodal embedding model
            model = aiplatform.TextEmbeddingModel.from_pretrained("textembedding-gecko@003")
            
            # For images, we'll use a text description approach
            # In production, you'd use a proper multimodal model
            embedding = model.get_embeddings(["skin analysis image"])[0]
            
            return embedding.values
            
        except Exception as e:
            logger.error(f"Vertex AI error for {image_path}: {e}")
            return []
    
    def process_scin_dataset(self):
        """Main SCIN dataset processing pipeline"""
        logger.info("Starting SCIN dataset pre-processing...")
        
        # Create temp directory
        os.makedirs("temp", exist_ok=True)
        
        # Step 1: Download SCIN images
        logger.info("Step 1: Downloading SCIN images...")
        image_files = self.download_scin_images()
        
        if not image_files:
            logger.error("No SCIN images found")
            return
        
        # Step 2: Process each image
        logger.info("Step 2: Processing images...")
        processed_data = []
        
        for i, image_path in enumerate(image_files):
            logger.info(f"Processing image {i+1}/{len(image_files)}: {image_path}")
            
            # Face isolation
            face_data = self.isolate_face_with_vision_api(image_path)
            
            if not face_data['face_detected']:
                logger.warning(f"No face detected in {image_path}")
                continue
            
            # Generate embedding
            embedding = self.generate_embedding_with_vertex_ai(image_path)
            
            if not embedding:
                logger.warning(f"Failed to generate embedding for {image_path}")
                continue
            
            # Create processed record
            processed_record = {
                'image_path': image_path,
                'embedding': embedding,
                'face_data': face_data,
                'processed_at': datetime.utcnow().isoformat()
            }
            
            processed_data.append(processed_record)
        
        # Step 3: Store in vector database (simulated)
        logger.info("Step 3: Storing in vector database...")
        self.store_in_vector_database(processed_data)
        
        # Cleanup
        for image_path in image_files:
            if os.path.exists(image_path):
                os.remove(image_path)
        
        logger.info(f"SCIN pre-processing completed. Processed {len(processed_data)} images.")
    
    def store_in_vector_database(self, processed_data: List[Dict[str, Any]]):
        """Store processed data in vector database"""
        try:
            # In production, this would store in Vertex AI Matching Engine
            # For now, we'll save to a JSON file for simulation
            
            output_file = "scin_processed_data.json"
            with open(output_file, 'w') as f:
                json.dump(processed_data, f, indent=2)
            
            logger.info(f"Stored {len(processed_data)} records in {output_file}")
            
        except Exception as e:
            logger.error(f"Failed to store in vector database: {e}")

def main():
    """Main execution function"""
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT', 'your-project-id')
    bucket_name = os.getenv('SCIN_BUCKET', 'your-scin-bucket')
    
    preprocessor = SCINPreprocessor(project_id, bucket_name)
    preprocessor.process_scin_dataset()

if __name__ == "__main__":
    main() 